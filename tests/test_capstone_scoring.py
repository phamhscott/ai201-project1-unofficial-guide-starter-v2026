"""Synthetic checks of the evaluator's ability to reject incorrect evidence."""

from collections import Counter
import copy
import unittest

from tools.run_capstone_eval import answer_contract, error_contract, log_contract, timing_comparison, usage_comparison


class CapstoneScoringTests(unittest.TestCase):
    def setUp(self):
        self.observation = {
            "case": "answer_1", "input": {"question": "A fixed question"},
            "request_id": "test-request", "status_code": 200, "client_ms": 1100,
            "response": {"question": "A fixed question", "answer": "An answer",
                         "refused": False, "sources": ["guide.md"], "best_distance": 0.3,
                         "threshold": 0.65, "corpus": "city_guides"},
        }
        self.record = {
            "request_id": "test-request", "timestamp": "2026-11-09T00:00:00+00:00",
            "input": self.observation["input"], "output": self.observation["response"],
            "status_code": 200, "duration_ms": 1000, "method": "POST", "path": "/ask",
            "corpus": "city_guides", "model": "test-model", "cache_enabled": True, "usage": {},
        }

    def test_answer_schema_rejects_wrong_types_and_empty_sources(self):
        self.assertTrue(answer_contract(self.observation))
        for field, value in [("answer", " "), ("sources", []), ("best_distance", True), ("refused", True)]:
            wrong = copy.deepcopy(self.observation)
            wrong["response"][field] = value
            self.assertFalse(answer_contract(wrong), field)

    def test_error_contract_checks_status_and_rejects_answer_body(self):
        observation = {"status_code": 500, "expected_status": 500, "response": {"error": "Failure"}}
        self.assertTrue(error_contract(observation))
        observation["response"]["answer"] = "This must not be an answer"
        self.assertFalse(error_contract(observation))
        observation["response"] = {"error": "Failure"}
        observation["status_code"] = 200
        self.assertFalse(error_contract(observation))

    def test_log_checker_rejects_duplicate_and_mismatched_records(self):
        counts = Counter({"test-request": 1})
        self.assertTrue(log_contract(self.observation, [self.record], counts))
        self.assertFalse(log_contract(self.observation, [self.record, self.record], counts))
        for field, value in [("output", {"answer": "Wrong"}), ("timestamp", "invalid"), ("duration_ms", float("nan"))]:
            wrong = dict(self.record, **{field: value})
            self.assertFalse(log_contract(self.observation, [wrong], counts), field)

    def test_timing_uses_external_elapsed_time_and_both_tolerance_branches(self):
        self.assertTrue(timing_comparison(self.observation, [self.record])["passed"])
        self.record["duration_ms"] = 800
        self.assertFalse(timing_comparison(self.observation, [self.record])["passed"])
        self.observation["client_ms"] = 100
        self.record["duration_ms"] = 60
        self.assertTrue(timing_comparison(self.observation, [self.record])["passed"])
        self.record["duration_ms"] = 0
        self.assertFalse(timing_comparison(self.observation, [self.record])["passed"])

    def test_usage_requires_independent_metadata_and_exact_attribution(self):
        self.observation["case"] = "usage_first"
        capture = {"request_id": "test-request", "source": "real_api", "outcome": "response",
                   "usage_metadata": {"prompt_token_count": 10, "candidates_token_count": 3, "total_token_count": 15}}
        self.record["usage"] = {"model_calls": 1, "cache_hits": 0, "usage_complete": True,
                                "prompt_tokens": 10, "output_tokens": 3, "total_tokens": 15}
        self.assertTrue(usage_comparison(self.observation, [self.record], [capture])["passed"])
        self.record["usage"]["total_tokens"] = 13
        self.assertFalse(usage_comparison(self.observation, [self.record], [capture])["passed"])
        self.assertFalse(usage_comparison(self.observation, [self.record], [])["passed"])

    def test_missing_metadata_cannot_be_reported_as_zero_tokens(self):
        self.observation["case"] = "usage_missing_metadata"
        capture = {"request_id": "test-request", "source": "synthetic_fault_probe",
                   "outcome": "response", "usage_metadata": None}
        self.record["usage"] = {"model_calls": 1, "cache_hits": 0, "usage_complete": False,
                                "prompt_tokens": None, "output_tokens": None, "total_tokens": None}
        self.assertTrue(usage_comparison(self.observation, [self.record], [capture])["passed"])
        self.record["usage"]["total_tokens"] = 0
        self.assertFalse(usage_comparison(self.observation, [self.record], [capture])["passed"])


if __name__ == "__main__":
    unittest.main()
