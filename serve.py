#!/usr/bin/env python3
"""
The Unofficial Guide — the same pipeline, over HTTP.

    python serve.py                          run it locally on port 5000
    gunicorn serve:app                       run it the way a host runs it

This is a wrapper: a request comes in, it
hands the question to `app.py::ask_pipeline` — the exact function the command
line uses — and hands the answer back as JSON. Retrieval, the relevance gate
and the grounded prompt all still live where they lived. If you change how
your system answers, you change it in those files and this one follows.

Two routes:

    POST /ask       {"question": "..."} in, the answer and its sources out
    GET  /health    is the service up, and is there an index to search

Why this exists: `app.py` runs once and exits, which is fine on your laptop
and impossible to deploy. A hosted service has to stay up and wait for
requests. This is the smallest thing that does that.

Unit 9 adds request timing and structured records in logs/requests.jsonl.
The response header X-Request-ID links a question request to its record.
Health checks stay outside the question log.
"""

import os
import time
from datetime import datetime, timezone
from uuid import uuid4

from flask import Flask, g, jsonify, request

import config
from generate import RequestUsage, measure_usage
from request_log import append_record

app = Flask(__name__)


@app.before_request
def start_request_record():
    """Time question requests from entry through creation of the response."""
    if request.endpoint == "ask":
        g.started = time.perf_counter()
        g.timestamp = datetime.now(timezone.utc).isoformat()
        g.request_id = uuid4().hex
        g.usage = RequestUsage()


@app.after_request
def finish_request_record(response):
    """Log successful answers, refusals, and errors through the same path."""
    if hasattr(g, "request_id"):
        response.headers["X-Request-ID"] = g.request_id
        append_record(
            {
                "timestamp": g.timestamp,
                "request_id": g.request_id,
                "method": request.method,
                "path": request.path,
                "corpus": config.CORPUS,
                "model": config.MODEL,
                "cache_enabled": config.CACHE_ENABLED,
                "usage": g.usage.as_dict(),
                "input": request.get_json(silent=True),
                "output": response.get_json(silent=True),
                "status_code": response.status_code,
                "duration_ms": round((time.perf_counter() - g.started) * 1000, 3),
            }
        )
    return response


@app.get("/health")
def health():
    """Is the service up, and is there an index to search?

    Two different questions, and the second one is the one that bites. A
    freshly deployed service answers this route happily while every /ask
    returns "no index" — hosts give you no disk that survives a restart, so
    the index has to be built as part of getting the service up. Checking
    here means you find that out in one request instead of five.
    """
    from store import index_exists

    ready = index_exists(config.CORPUS)
    return jsonify(
        {
            "status": "ok",
            "corpus": config.CORPUS,
            "index_ready": ready,
            "detail": (
                "ready"
                if ready
                else "no index for this corpus — run `python app.py index`"
            ),
        }
    )


@app.post("/ask")
def ask():
    """One question in, one grounded answer out.

    A refused question is a 200, not an error. The gate refusing is your
    system working — it is an answer, and the JSON says so with
    `"refused": true` so whatever calls this can tell the two apart.
    """
    from app import ask_pipeline

    payload = request.get_json(silent=True)
    value = payload.get("question") if isinstance(payload, dict) else None
    question = value.strip() if isinstance(value, str) else ""

    if not question:
        return (
            jsonify(
                {
                    "error": "Send JSON with a question in it, like "
                    '{"question": "When should I visit Kestrelford?"}'
                }
            ),
            400,
        )

    try:
        with measure_usage() as usage:
            g.usage = usage
            outcome = ask_pipeline(question, corpus=config.CORPUS)
    except Exception as exc:  # noqa: BLE001 — a reader gets this, not a traceback
        # Exception text can contain service URLs and credentials.
        return jsonify({"error": f"{type(exc).__name__}: unable to answer question"}), 500

    return jsonify(
        {
            "question": question,
            "answer": outcome["answer"],
            "refused": outcome["refused"],
            "sources": outcome["sources"],
            "best_distance": round(outcome["best_distance"], 4),
            "threshold": outcome["threshold"],
            "corpus": config.CORPUS,
        }
    )


def main():
    # Hosts tell you which port to listen on through PORT, and they expect you
    # on 0.0.0.0. Binding 127.0.0.1 instead works perfectly on your laptop and
    # then answers nothing at all once deployed, because the host's router
    # can't reach a socket that only accepts connections from inside the
    # container. It is the single most common way a first deploy "succeeds"
    # and is unreachable.
    port = int(os.getenv("PORT", "5000"))

    # Debug mode reloads on save, which is handy, and prints a console that
    # runs arbitrary code, which is not something to leave switched on where
    # strangers can reach it. Off unless you ask for it.
    debug = os.getenv("AI201_DEBUG", "0") == "1"

    print(f"Serving The Unofficial Guide on http://localhost:{port}")
    print(f"Corpus: {config.CORPUS}    (Ctrl-C to stop)\n")
    print("Try it from another terminal:\n")
    print(f"  curl http://localhost:{port}/health")
    print(
        f"  curl -X POST http://localhost:{port}/ask \\\n"
        f"    -H 'Content-Type: application/json' \\\n"
        f"    -d '{{\"question\": \"is the housing lottery random?\"}}'\n"
    )

    app.run(host="0.0.0.0", port=port, debug=debug)


if __name__ == "__main__":
    main()
