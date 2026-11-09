"""Controlled pacing measurement with a virtual clock and no real API calls."""

import argparse
from contextlib import redirect_stderr
from io import StringIO
import json
from pathlib import Path
import sys
from types import SimpleNamespace
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import config
import generate


def measure():
    now = [1000.0]
    starts = []
    waits = []

    def sleep(seconds):
        waits.append(seconds)
        now[0] += seconds

    def model_call(**kwargs):
        starts.append(round(now[0] - 1000.0, 6))
        now[0] += 0.1
        return SimpleNamespace(text="Synthetic pacing probe", usage_metadata=None)

    client = SimpleNamespace(models=SimpleNamespace(generate_content=model_call))
    with patch.object(generate, "_call_times", []), patch.object(generate, "_session_calls", 0):
        with patch.object(generate, "_get_client", return_value=client):
            with patch.object(generate.time, "monotonic", side_effect=lambda: now[0]):
                with patch.object(generate.time, "sleep", side_effect=sleep):
                    with redirect_stderr(StringIO()):
                        for number in range(5):
                            generate.generate("pacing probe " + str(number), cache=False)
    gaps = [round(right - left, 6) for left, right in zip(starts, starts[1:])]
    return {
        "kind": "synthetic_virtual_clock_probe",
        "real_api_calls": 0,
        "configured_requests_per_minute": config.REQUESTS_PER_MINUTE,
        "simulated_model_response_seconds": 0.1,
        "call_start_seconds": starts,
        "inter_call_gap_seconds": gaps,
        "minimum_gap_seconds": min(gaps),
        "total_pacing_wait_seconds": round(sum(waits), 6),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise RuntimeError("Probe output already exists. Preserve it and use a new filename")
    result = measure()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    text = json.dumps(result, indent=2) + "\n"
    args.output.write_text(text, encoding="utf-8")
    print(text)


if __name__ == "__main__":
    main()
