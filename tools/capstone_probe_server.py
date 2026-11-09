"""Evaluation-only server wrapper for isolated faults and independent API captures.

The normal endpoint and timing trials run serve.py directly. This wrapper
changes only in-memory test configuration and the model-client boundary.
"""

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import sys
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

MISSING_METADATA = "When should someone visit Kestrelford?"
FAILED_CALL = "What seasons does the guide recommend for visiting Kestrelford?"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mode", choices=["missing-index", "failed-call", "accounting"], required=True)
    parser.add_argument("--index", type=Path, required=True)
    parser.add_argument("--cache", type=Path, required=True)
    parser.add_argument("--capture", type=Path, required=True)
    args = parser.parse_args()

    import config
    import generate

    config.CHROMA_DIR = args.index
    config.CACHE_DIR = args.cache
    if args.mode != "missing-index":
        from flask import g, request

        original_client = generate._get_client
        attempts = 0

        def observed_call(**kwargs):
            nonlocal attempts
            attempts += 1
            question = (request.get_json(silent=True) or {}).get("question")
            synthetic = args.mode == "failed-call" or question in {MISSING_METADATA, FAILED_CALL}
            record = {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "request_id": g.request_id,
                "attempt": attempts,
                "model": kwargs.get("model"),
                "source": "synthetic_fault_probe" if synthetic else "real_api",
                "question": question,
            }
            try:
                if args.mode == "failed-call" or question == FAILED_CALL:
                    raise RuntimeError("Deliberately injected model-call failure")
                if question == MISSING_METADATA:
                    response = SimpleNamespace(
                        text="Synthetic fault probe response without usage metadata.",
                        usage_metadata=None,
                    )
                else:
                    response = original_client().models.generate_content(**kwargs)
                metadata = getattr(response, "usage_metadata", None)
                record["usage_metadata"] = metadata.model_dump(mode="json") if metadata is not None else None
                record["outcome"] = "response"
                return response
            except Exception as error:
                # Do not preserve service exception text that could contain a key.
                record["outcome"] = "exception"
                record["exception_type"] = type(error).__name__
                record["usage_metadata"] = None
                raise
            finally:
                args.capture.parent.mkdir(parents=True, exist_ok=True)
                with args.capture.open("a", encoding="utf-8") as stream:
                    stream.write(json.dumps(record, ensure_ascii=False) + "\n")

        proxy = SimpleNamespace(models=SimpleNamespace(generate_content=observed_call))
        generate._get_client = lambda: proxy

    from serve import main as serve_main

    serve_main()


if __name__ == "__main__":
    main()
