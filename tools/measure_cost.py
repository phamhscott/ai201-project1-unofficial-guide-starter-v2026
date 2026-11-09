"""Measure ten uncached requests to an already running local service.

This operational sample assigns no acceptance verdicts and does not change
the service. API token counts are read from its actual JSONL request records.
"""

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import statistics
import time
from urllib.error import HTTPError
from urllib.request import Request, urlopen


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--url", default="http://127.0.0.1:5000")
    parser.add_argument("--log", type=Path, default=Path("logs/requests.jsonl"))
    parser.add_argument("--output", type=Path, default=Path("results/capstone_milestone3_cost.json"))
    parser.add_argument("--question", default="When should I visit Kestrelford?")
    args = parser.parse_args()
    samples = []
    summary = {
        "purpose": "Milestone 3 operational cost sample, not acceptance evaluation",
        "started_at": datetime.now(timezone.utc).isoformat(),
        "question": args.question,
        "planned_requests": 10,
        "unit": "API-reported tokens per uncached question request",
        "samples": samples,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)

    try:
        for number in range(1, 11):
            payload = json.dumps({"question": args.question}).encode("utf-8")
            request = Request(args.url.rstrip("/") + "/ask", data=payload,
                              headers={"Content-Type": "application/json"})
            started = time.perf_counter()
            try:
                connection = urlopen(request, timeout=120)
            except HTTPError as error:
                connection = error
            with connection:
                body = json.loads(connection.read())
                status = connection.code
                request_id = connection.headers.get("X-Request-ID")
            elapsed_ms = (time.perf_counter() - started) * 1000
            records = [json.loads(line) for line in args.log.read_text(encoding="utf-8").splitlines()]
            matching = [record for record in records if record["request_id"] == request_id]
            if len(matching) != 1:
                raise RuntimeError("Expected exactly one request record matching the response")
            record = matching[0]
            sample = {
                "run": number,
                "request_id": request_id,
                "status_code": status,
                "duration_ms": record["duration_ms"],
                "client_duration_ms": round(elapsed_ms, 3),
                "model": record["model"],
                "usage": record["usage"],
            }
            samples.append(sample)
            usage = record["usage"]
            if status != 200 or body.get("refused") or record["cache_enabled"]:
                raise RuntimeError("Cost sample requires an answered question with server caching disabled")
            if not usage["usage_complete"] or usage["model_calls"] != 1 or usage["cache_hits"] != 0:
                raise RuntimeError("Cost sample requires one real API call with complete usage per request")
            print(f"Run {number}: {usage['total_tokens']} tokens, {record['duration_ms']} ms, request_id={request_id}", flush=True)
        summary.update({
            "completed_requests": len(samples),
            "model_calls": sum(sample["usage"]["model_calls"] for sample in samples),
            "cache_hits": sum(sample["usage"]["cache_hits"] for sample in samples),
            "total_prompt_tokens": sum(sample["usage"]["prompt_tokens"] for sample in samples),
            "total_output_tokens": sum(sample["usage"]["output_tokens"] for sample in samples),
            "total_tokens": sum(sample["usage"]["total_tokens"] for sample in samples),
            "mean_prompt_tokens": statistics.mean(sample["usage"]["prompt_tokens"] for sample in samples),
            "mean_output_tokens": statistics.mean(sample["usage"]["output_tokens"] for sample in samples),
            "mean_total_tokens": statistics.mean(sample["usage"]["total_tokens"] for sample in samples),
            "mean_duration_ms": statistics.mean(sample["duration_ms"] for sample in samples),
            "measurement_complete": True,
        })
        print(f"Mean API tokens per request: {summary['mean_total_tokens']}")
        print(f"Mean server duration: {summary['mean_duration_ms']:.3f} ms")
        print(f"Total API tokens: {summary['total_tokens']} across 10 requests")
        print(f"Summary saved to {args.output}")
    except Exception as error:
        summary["measurement_complete"] = False
        summary["error_type"] = type(error).__name__
        raise
    finally:
        args.output.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
