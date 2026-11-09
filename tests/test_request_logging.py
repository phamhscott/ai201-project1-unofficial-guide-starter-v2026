"""Development checks with stubbed pipeline outputs, not capstone trials."""

import json
import tempfile
import unittest
from datetime import datetime
from pathlib import Path
from unittest.mock import patch

import config
from serve import app


class RequestLoggingTests(unittest.TestCase):
    def setUp(self):
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.log_path = Path(directory.name) / "nested" / "requests.jsonl"
        override = patch.object(config, "RUN_LOG_PATH", self.log_path)
        override.start()
        self.addCleanup(override.stop)
        self.client = app.test_client()

    def records(self):
        return [json.loads(line) for line in self.log_path.read_text(encoding="utf-8").splitlines()]

    def test_success_record_matches_response(self):
        outcome = {
            "answer": "A sourced answer from guide_kestrelford.md.",
            "refused": False,
            "sources": ["guide_kestrelford.md"],
            "best_distance": 0.3,
            "threshold": 0.65,
        }
        question = {"question": "When should I visit Kestrelford?"}
        with patch("app.ask_pipeline", return_value=outcome):
            response = self.client.post("/ask", json=question)
        self.assertEqual(response.status_code, 200)
        records = self.records()
        self.assertEqual(len(records), 1)
        record = records[0]
        self.assertEqual(record["input"], question)
        self.assertEqual(record["output"], response.get_json())
        self.assertEqual(record["request_id"], response.headers["X-Request-ID"])
        self.assertEqual(record["status_code"], 200)
        self.assertGreaterEqual(record["duration_ms"], 0)
        self.assertIsNotNone(datetime.fromisoformat(record["timestamp"]).tzinfo)

    def test_invalid_inputs_each_get_one_record_without_running_pipeline(self):
        payloads = [{}, {"question": " "}, {"question": 42}, [], None]
        with patch("app.ask_pipeline") as pipeline:
            for payload in payloads:
                response = self.client.post("/ask", json=payload)
                self.assertEqual(response.status_code, 400)
            response = self.client.post("/ask", data="{broken", content_type="application/json")
            self.assertEqual(response.status_code, 400)
            pipeline.assert_not_called()
        records = self.records()
        self.assertEqual(len(records), len(payloads) + 1)
        self.assertTrue(all(record["status_code"] == 400 for record in records))
        self.assertEqual(len({record["request_id"] for record in records}), len(records))

    def test_pipeline_error_is_logged_without_exception_details(self):
        with patch("app.ask_pipeline", side_effect=RuntimeError("private-credential-marker")):
            response = self.client.post("/ask", json={"question": "A question"})
        self.assertEqual(response.status_code, 500)
        self.assertEqual(self.records()[0]["output"], response.get_json())
        self.assertNotIn("private-credential-marker", self.log_path.read_text(encoding="utf-8"))

    def test_refusal_is_a_successful_response(self):
        outcome = {
            "answer": "I don't have enough information about that.",
            "refused": True,
            "sources": [],
            "best_distance": 0.9,
            "threshold": 0.65,
        }
        with patch("app.ask_pipeline", return_value=outcome):
            response = self.client.post("/ask", json={"question": "Outside the corpus"})
        self.assertEqual(response.status_code, 200)
        self.assertTrue(self.records()[0]["output"]["refused"])


if __name__ == "__main__":
    unittest.main()
