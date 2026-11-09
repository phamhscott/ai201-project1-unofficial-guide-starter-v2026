"""One real local development session, not the three-trial capstone evaluation.

Run from the repository root with the project Python interpreter.
Starts serve.py, checks HTTP and CLI behavior, and stops the server on exit.
"""

import json
import os
from pathlib import Path
import socket
import subprocess
import sys
import time
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))


def main():
    import config

    if os.getenv("AI201_FAKE_EMBEDDINGS") == "1":
        raise RuntimeError("This development session requires real embeddings")
    with socket.socket() as reservation:
        reservation.bind(("127.0.0.1", 0))
        port = reservation.getsockname()[1]

    environment = os.environ.copy()
    environment.update({"PORT": str(port), "AI201_DEBUG": "0", "PYTHONUNBUFFERED": "1"})
    config.RUN_LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    console_path = config.RUN_LOG_PATH.with_suffix(".server.txt")
    transcript_path = config.RUN_LOG_PATH.with_suffix(".session.txt")
    transcript = []

    def emit(message):
        print(message, flush=True)
        transcript.append(message)

    def call(path, payload=None):
        data = json.dumps(payload).encode("utf-8") if payload is not None else None
        req = Request(f"http://127.0.0.1:{port}{path}", data=data,
                      headers={"Content-Type": "application/json"})
        try:
            connection = urlopen(req, timeout=90)
        except HTTPError as error:
            connection = error
        with connection:
            result = json.loads(connection.read())
            return connection.code, connection.headers.get("X-Request-ID"), result

    try:
        with console_path.open("w", encoding="utf-8") as console:
            process = subprocess.Popen([sys.executable, "serve.py"], cwd=ROOT,
                                       env=environment, stdout=console, stderr=console)
            try:
                deadline = time.monotonic() + 45
                while True:
                    try:
                        status, _, health = call("/health")
                        break
                    except URLError:
                        if process.poll() is not None or time.monotonic() >= deadline:
                            raise RuntimeError(f"Server did not become ready. See {console_path}")
                        time.sleep(0.2)
                emit("Development smoke check with real embeddings and the configured Gemini model")
                emit(f"GET /health -> {status} {json.dumps(health, sort_keys=True)}")
                assert status == 200 and health["index_ready"], "Build the index first"
                question = "When should I visit Kestrelford, according to the city guide?"
                cases = [
                    ({"question": question}, 200, False),
                    ({"question": question}, 200, False),
                    ({"question": "How do I write a for loop in Rust?"}, 200, True),
                    ({"question": " "}, 400, None),
                ]
                ids = []
                for payload, expected_status, refused in cases:
                    status, request_id, output = call("/ask", payload)
                    ids.append(request_id)
                    emit(f"POST /ask -> {status} request_id={request_id} {json.dumps(output, sort_keys=True)}")
                    assert status == expected_status, "Unexpected HTTP status"
                    if refused is not None:
                        assert output["refused"] == refused, "Unexpected gate decision"
                    if refused is False:
                        assert output["answer"] and "guide_kestrelford.md" in output["sources"]
                cli = subprocess.run([sys.executable, "app.py", "ask", question], cwd=ROOT,
                                     env=environment, capture_output=True, text=True,
                                     encoding="utf-8", timeout=90)
                emit(f"CLI exit code: {cli.returncode}\n{cli.stdout.strip()}")
                assert cli.returncode == 0 and "guide_kestrelford.md" in cli.stdout
                records = [json.loads(line) for line in config.RUN_LOG_PATH.read_text(encoding="utf-8").splitlines()]
                selected = [record for record in records if record["request_id"] in ids]
                assert len(selected) == 4 and len(set(ids)) == 4
                emit("Verified four matching request records and the original CLI answer path")
                emit("Development checks passed. No capstone acceptance verdicts were assigned.")
            finally:
                process.terminate()
                process.wait(timeout=10)
    finally:
        transcript_path.write_text("\n".join(transcript) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
