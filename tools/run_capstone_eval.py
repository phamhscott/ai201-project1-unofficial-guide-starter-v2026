"""Run the committed capstone criteria three times without changing the system.

Use an isolated checkout prepared through RUNNING.md. Results are never
overwritten. The normal HTTP trials use the documented serve.py command.
"""

import argparse
from collections import Counter
from contextlib import contextmanager
from datetime import datetime, timedelta, timezone
import hashlib
import json
import math
from pathlib import Path
import re
import subprocess
import sys
import time
import os
import traceback
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parent.parent
TARGETS = {"1": 5, "2": 6, "3": 11, "4": 5, "5": 6}
TITLES = {
    "1": "Local endpoint answer contract",
    "2": "Expected error responses",
    "3": "Complete matching request records",
    "4": "Independent timing agreement",
    "5": "Per-request usage attribution",
}


def write_json(path, value):
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def read_jsonl(path):
    if not path.exists():
        return []
    records = []
    for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        try:
            records.append(json.loads(line))
        except ValueError:
            records.append({"parse_error_line": number, "raw": line})
    return records


def git(checkout, *arguments):
    return subprocess.check_output(
        ["git", "-c", "safe.directory=" + checkout.as_posix(), *arguments],
        cwd=checkout, text=True, encoding="utf-8",
    ).strip()


def digest(path):
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def fingerprints(checkout):
    files = sorted(checkout.glob("*.py")) + sorted((checkout / "corpora").rglob("*.md"))
    files += sorted((checkout / "corpora").rglob("*.txt"))
    files += sorted((checkout / "corpora").rglob("*.json"))
    files += [checkout / "criteria.md", checkout / "requirements-lock.txt"]
    files += [checkout / "tools" / "run_capstone_eval.py", checkout / "tools" / "capstone_probe_server.py"]
    return {path.relative_to(checkout).as_posix(): digest(path) for path in files}


def finite_number(value):
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value)


def answer_contract(observation):
    body = observation.get("response")
    return (
        observation.get("status_code") == 200 and isinstance(body, dict)
        and body.get("question") == observation["input"]["question"]
        and isinstance(body.get("answer"), str) and bool(body["answer"].strip())
        and body.get("refused") is False
        and isinstance(body.get("sources"), list) and bool(body["sources"])
        and all(isinstance(source, str) and bool(source.strip()) for source in body["sources"])
        and finite_number(body.get("best_distance")) and finite_number(body.get("threshold"))
        and body.get("corpus") == "city_guides"
    )


def error_contract(observation):
    body = observation.get("response")
    return (
        observation.get("status_code") == observation["expected_status"]
        and isinstance(body, dict) and isinstance(body.get("error"), str)
        and bool(body["error"].strip()) and "answer" not in body
    )


def matching_record(observation, records):
    identifier = observation.get("request_id")
    matched = [record for record in records if record.get("request_id") == identifier]
    return matched[0] if isinstance(identifier, str) and identifier and len(matched) == 1 else None


def log_contract(observation, records, id_counts):
    record = matching_record(observation, records)
    if record is None or id_counts[observation.get("request_id")] != 1:
        return False
    required = {"timestamp", "input", "output", "status_code", "duration_ms", "method",
                "path", "corpus", "model", "cache_enabled", "usage", "request_id"}
    if not required.issubset(record):
        return False
    try:
        utc = datetime.fromisoformat(record["timestamp"]).utcoffset() == timedelta(0)
    except (ValueError, TypeError):
        return False
    return (
        utc and record["input"] == observation["input"]
        and record["output"] == observation.get("response")
        and observation.get("status_code") is not None
        and record["status_code"] == observation["status_code"]
        and finite_number(record["duration_ms"]) and record["duration_ms"] >= 0
        and record["method"] == "POST" and record["path"] == "/ask"
        and record["corpus"] == "city_guides"
        and isinstance(record["model"], str) and bool(record["model"])
        and isinstance(record["cache_enabled"], bool) and isinstance(record["usage"], dict)
    )


def timing_comparison(observation, records):
    record = matching_record(observation, records)
    client_ms = observation.get("client_ms")
    logged_ms = record.get("duration_ms") if record else None
    valid = observation.get("status_code") is not None and finite_number(client_ms) and finite_number(logged_ms)
    difference = abs(client_ms - logged_ms) if valid else None
    allowed = max(50, 0.10 * client_ms) if valid else None
    return {
        "case": observation["case"], "request_id": observation.get("request_id"),
        "client_ms": client_ms, "logged_ms": logged_ms,
        "difference_ms": difference, "allowed_ms": allowed,
        "passed": bool(valid and difference <= allowed),
    }


def usage_comparison(observation, records, captures):
    record = matching_record(observation, records)
    identifier = observation.get("request_id")
    calls = [call for call in captures if call.get("request_id") == identifier]
    case = observation["case"]
    expected_calls = 1 if case in {"usage_first", "usage_missing_metadata", "usage_failed_call"} else 0
    expected_hits = 1 if case == "usage_cached" else 0
    fields = ("prompt_token_count", "candidates_token_count", "total_token_count")
    complete = all(
        call.get("outcome") == "response" and isinstance(call.get("usage_metadata"), dict)
        and all(isinstance(call["usage_metadata"].get(field), int)
                and call["usage_metadata"][field] >= 0 for field in fields)
        for call in calls
    )
    tokens = [sum(call["usage_metadata"][field] for call in calls) for field in fields] if complete else [None] * 3
    expected = {
        "model_calls": len(calls), "cache_hits": expected_hits, "usage_complete": complete,
        "prompt_tokens": tokens[0], "output_tokens": tokens[1], "total_tokens": tokens[2],
    }
    body = observation.get("response") or {}
    branch_ok = observation.get("status_code") == (500 if case == "usage_failed_call" else 400 if case == "usage_blank" else 200)
    if case == "usage_refused":
        branch_ok = branch_ok and body.get("refused") is True
    if case in {"usage_first", "usage_cached", "usage_missing_metadata"}:
        branch_ok = branch_ok and body.get("refused") is False and bool(body.get("answer"))
    if case == "usage_first":
        branch_ok = branch_ok and all(call.get("source") == "real_api" for call in calls)
    if case in {"usage_missing_metadata", "usage_failed_call"}:
        branch_ok = branch_ok and all(call.get("source") == "synthetic_fault_probe" for call in calls)
    actual = record.get("usage") if record else None
    return {
        "case": case, "request_id": identifier, "expected": expected, "actual": actual,
        "independently_observed_calls": len(calls),
        "passed": bool(record and isinstance(actual, dict) and branch_ok and len(calls) == expected_calls
                       and all(actual.get(key) == value for key, value in expected.items())
                       and record.get("cache_enabled") is True),
    }


class Trial:
    def __init__(self, checkout, directory, workspace, number):
        self.checkout, self.directory, self.workspace = checkout, directory, workspace
        self.number = number
        self.python = checkout / ".venv" / "Scripts" / "python.exe"
        self.observations = []
        self.phase_logs = []
        directory.mkdir()
        workspace.mkdir(parents=True)

    def emit(self, message):
        print(f"Trial {self.number}: {message}", flush=True)
        with (self.directory / "output.txt").open("a", encoding="utf-8") as stream:
            stream.write(message + "\n")

    def command(self, command):
        self.emit("> " + " ".join(str(part) for part in command))
        result = subprocess.run(command, cwd=self.checkout, capture_output=True, text=True,
                                encoding="utf-8", errors="replace", timeout=120)
        self.emit(result.stdout.strip())
        if result.stderr:
            self.emit(result.stderr.strip())
        if result.returncode:
            self.emit("Command failed with exit code " + str(result.returncode))
            raise RuntimeError("Trial setup command failed")

    @contextmanager
    def server(self, phase, cache=False):
        log = self.directory / (phase + "_requests.jsonl")
        self.phase_logs.append(log)
        environment = os.environ.copy()
        environment.update({"PORT": "5000", "AI201_DEBUG": "0", "PYTHONUNBUFFERED": "1",
                            "AI201_CORPUS": "city_guides", "AI201_CACHE": "1" if cache else "0",
                            "AI201_RUN_LOG": str(log)})
        if environment.get("AI201_FAKE_EMBEDDINGS") == "1":
            raise RuntimeError("Formal trials require real embeddings")
        command = [str(self.python), "serve.py"]
        if phase != "normal":
            index = self.workspace / "empty_index" if phase == "missing-index" else self.checkout / "chroma_db"
            command = [str(self.python), "tools/capstone_probe_server.py", "--mode", phase,
                       "--index", str(index), "--cache", str(self.workspace / (phase + "_cache")),
                       "--capture", str(self.directory / (phase + "_api_capture.jsonl"))]
        self.emit("> " + " ".join(command))
        console_path = self.directory / (phase + "_console.txt")
        with console_path.open("w", encoding="utf-8") as console:
            process = subprocess.Popen(command, cwd=self.checkout, env=environment, stdout=console, stderr=console)
            try:
                deadline = time.monotonic() + 45
                while True:
                    if process.poll() is not None:
                        raise RuntimeError("Server exited before becoming ready")
                    # Wait for this process to bind, rather than probing the
                    # port before startup or mistaking another listener for it.
                    if "Running on http://127.0.0.1:5000" not in console_path.read_text(encoding="utf-8"):
                        if time.monotonic() >= deadline:
                            raise RuntimeError("Server did not announce a successful bind")
                        time.sleep(0.2)
                        continue
                    try:
                        with urlopen("http://127.0.0.1:5000/health", timeout=5) as response:
                            health = json.loads(response.read())
                        break
                    except (URLError, TimeoutError):
                        if process.poll() is not None or time.monotonic() >= deadline:
                            raise RuntimeError("Server failed to become reachable")
                        time.sleep(0.2)
                self.emit("GET /health " + json.dumps(health, sort_keys=True))
                if health.get("index_ready") != (phase != "missing-index"):
                    raise RuntimeError("Unexpected index readiness for trial phase")
                yield
            finally:
                if process.poll() is None:
                    if os.name == "nt":
                        # The Windows venv redirector can have a child Python
                        # process. Stop only this runner's server process tree.
                        subprocess.run(["taskkill", "/PID", str(process.pid), "/T", "/F"],
                                       capture_output=True, timeout=10)
                    else:
                        process.terminate()
                process.wait(timeout=10)

    def post(self, case, phase, payload=None, expected_status=200, raw=None):
        data = raw.encode("utf-8") if raw is not None else json.dumps(payload).encode("utf-8")
        request = Request("http://127.0.0.1:5000/ask", data=data,
                          headers={"Content-Type": "application/json"})
        observation = {"case": case, "phase": phase, "input": payload, "raw_input": data.decode("utf-8"),
                       "expected_status": expected_status, "request_id": None, "status_code": None,
                       "response": None}
        started = time.perf_counter()
        try:
            try:
                connection = urlopen(request, timeout=120)
            except HTTPError as error:
                connection = error
            with connection:
                raw_response = connection.read()
                observation["client_ms"] = (time.perf_counter() - started) * 1000
                observation["status_code"] = connection.code
                observation["request_id"] = connection.headers.get("X-Request-ID")
                observation["raw_response"] = raw_response.decode("utf-8", errors="replace")
            try:
                observation["response"] = json.loads(observation["raw_response"])
            except ValueError:
                observation["response_parse_error"] = True
        except (OSError, TimeoutError) as error:
            observation["client_ms"] = (time.perf_counter() - started) * 1000
            observation["transport_error_type"] = type(error).__name__
        self.observations.append(observation)
        with (self.directory / "observations.jsonl").open("a", encoding="utf-8") as stream:
            stream.write(json.dumps(observation, ensure_ascii=False) + "\n")
        self.emit("HTTP " + json.dumps(observation, ensure_ascii=False))

    def execute(self, questions):
        self.command([str(self.python), "app.py", "--corpus", "city_guides", "index"])
        with self.server("normal"):
            for number, question in enumerate(questions, 1):
                self.post(f"answer_{number}", "normal", {"question": question})
            for case, payload in [("missing", {}), ("blank", {"question": " "}), ("wrong_type", {"question": 42})]:
                self.post("error_" + case, "normal", payload, 400)
            self.post("error_malformed", "normal", None, 400, raw="{broken")
        with self.server("missing-index"):
            self.post("error_missing_index", "missing-index", {"question": questions[4]}, 500)
        with self.server("failed-call"):
            self.post("error_failed_call", "failed-call", {"question": questions[4]}, 500)
        with self.server("accounting", cache=True):
            for case, question, status in [
                ("first", "When should I visit Kestrelford?", 200),
                ("cached", "When should I visit Kestrelford?", 200),
                ("refused", "How do I write a for loop in Rust?", 200),
                ("blank", " ", 400),
                ("missing_metadata", "When should someone visit Kestrelford?", 200),
                ("failed_call", "What seasons does the guide recommend for visiting Kestrelford?", 500),
            ]:
                self.post("usage_" + case, "accounting", {"question": question}, status)

    def grade(self):
        combined = "".join(path.read_text(encoding="utf-8") for path in self.phase_logs if path.exists())
        (self.directory / "requests.jsonl").write_text(combined, encoding="utf-8")
        records = read_jsonl(self.directory / "requests.jsonl")
        captures = read_jsonl(self.directory / "accounting_api_capture.jsonl")
        answers = [item for item in self.observations if item["case"].startswith("answer_")]
        errors = [item for item in self.observations if item["case"].startswith("error_")]
        core = answers + errors
        id_counts = Counter(item.get("request_id") for item in self.observations)
        timing = [timing_comparison(item, records) for item in answers]
        usage = [usage_comparison(item, records, captures) for item in self.observations if item["phase"] == "accounting"]
        details = {
            "1": [{"case": item["case"], "passed": bool(answer_contract(item))} for item in answers],
            "2": [{"case": item["case"], "passed": bool(error_contract(item))} for item in errors],
            "3": [{"case": item["case"], "request_id": item.get("request_id"),
                   "passed": bool(log_contract(item, records, id_counts))} for item in core],
            "4": timing, "5": usage,
        }
        counts = {number: sum(item["passed"] for item in checks) for number, checks in details.items()}
        result = {"trial": self.number, "counts": counts, "targets": TARGETS, "details": details,
                  "observed_requests": len(self.observations), "recorded_requests": len(records)}
        for number in TARGETS:
            self.emit(f"Criterion {number}: {counts[number]}/{TARGETS[number]}")
        for item in timing:
            self.emit("TIMING " + json.dumps(item))
        for item in usage:
            self.emit("USAGE " + json.dumps(item))
        write_json(self.directory / "result.json", result)
        return result


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--checkout", type=Path, required=True)
    parser.add_argument("--label", choices=["before", "after"], default="before")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    checkout = args.checkout.resolve()
    output = (args.output or ROOT / "results" / ("capstone_" + args.label)).resolve()
    if output.exists():
        raise RuntimeError("Results directory already exists. Choose a new directory to preserve all runs")
    baseline = fingerprints(checkout)
    if baseline != fingerprints(ROOT):
        raise RuntimeError("Checkout runtime or committed criteria differ from the active source")
    criteria_commit = git(checkout, "log", "-1", "--format=%H", "--", "criteria.md")
    committed = subprocess.check_output(
        ["git", "-c", "safe.directory=" + checkout.as_posix(), "show", criteria_commit + ":criteria.md"],
        cwd=checkout,
    ).replace(b"\r\n", b"\n")
    if hashlib.sha256(committed).hexdigest() != baseline["criteria.md"]:
        raise RuntimeError("Criteria must be committed before formal evaluation")
    questions = re.findall(r"^[1-5]\. (.+\?)$", (checkout / "criteria.md").read_text(encoding="utf-8"), re.M)
    if len(questions) != 5:
        raise RuntimeError("Expected the five fixed questions in the committed criteria")
    if git(checkout, "rev-parse", "HEAD") != git(ROOT, "rev-parse", "HEAD"):
        raise RuntimeError("Evaluation checkout must be at the active source commit")
    output.mkdir(parents=True)
    workspace = checkout / ".cache" / ("capstone_" + args.label + "_" + output.name)
    if workspace.exists():
        raise RuntimeError("Evaluation workspace already exists")
    manifest = {
        "started_at": datetime.now(timezone.utc).isoformat(), "label": args.label,
        "source_commit": git(checkout, "rev-parse", "HEAD"), "criteria_commit": criteria_commit,
        "checkout": str(checkout), "python": str(checkout / ".venv" / "Scripts" / "python.exe"),
        "fingerprints": baseline, "questions": questions,
        "faults": "Synthetic faults are injected only by tools/capstone_probe_server.py",
        "command": subprocess.list2cmdline([sys.executable, *sys.argv]),
    }
    write_json(output / "manifest.json", manifest)
    trials = []
    for number in range(1, 4):
        if fingerprints(checkout) != baseline or fingerprints(ROOT) != baseline:
            raise RuntimeError("Source or criteria changed between trials")
        trial = Trial(checkout, output / ("trial_" + str(number)), workspace / ("trial_" + str(number)), number)
        try:
            trial.execute(questions)
        except Exception as error:
            trial.emit("INFRASTRUCTURE FAILURE " + type(error).__name__)
            write_json(trial.directory / "infrastructure_error.json", {
                "type": type(error).__name__, "traceback": traceback.format_exc(),
            })
        result = trial.grade()
        trials.append(result)
        write_json(output / "progress.json", trials)
    if fingerprints(checkout) != baseline or fingerprints(ROOT) != baseline:
        raise RuntimeError("Source or criteria changed during the trials")
    verdicts = {number: "MET" if all(trial["counts"][number] == target for trial in trials) else "MISSED"
                for number, target in TARGETS.items()}
    write_json(output / "summary.json", {"label": args.label, "trials": trials, "verdicts": verdicts,
                                         "source_unchanged": True, "criteria_commit": criteria_commit})
    lines = ["| Criterion | Target | Run 1 | Run 2 | Run 3 | Verdict |", "|---|---|---|---|---|---|"]
    for number, target in TARGETS.items():
        values = [str(trial["counts"][number]) + "/" + str(target) for trial in trials]
        lines.append("| " + " | ".join([number + ". " + TITLES[number], str(target) + "/" + str(target),
                                          *values, verdicts[number]]) + " |")
    table = "\n".join(lines) + "\n"
    (output / "run_log.md").write_text(table, encoding="utf-8")
    print(table, flush=True)


if __name__ == "__main__":
    main()
