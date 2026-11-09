"""Write one JSONL record for each POST /ask in the local server process."""

import json
from threading import Lock

import config

_write_lock = Lock()


def append_record(record: dict) -> None:
    """Keep records on separate lines even when requests finish together."""
    line = json.dumps(record, ensure_ascii=False)
    with _write_lock:
        config.RUN_LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
        with config.RUN_LOG_PATH.open("a", encoding="utf-8") as stream:
            stream.write(line + "\n")
