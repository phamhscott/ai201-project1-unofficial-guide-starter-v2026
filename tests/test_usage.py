"""Synthetic accounting checks. These do not measure real API cost."""

import tempfile
import unittest
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from threading import Barrier
from types import SimpleNamespace
from unittest.mock import Mock, patch

import config
import generate


def response(prompt_tokens=10, output_tokens=3, total_tokens=15):
    return SimpleNamespace(
        text="A test answer",
        usage_metadata=SimpleNamespace(
            prompt_token_count=prompt_tokens,
            candidates_token_count=output_tokens,
            total_token_count=total_tokens,
        ),
    )


class UsageTests(unittest.TestCase):
    def setUp(self):
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        for target, attribute, value in (
            (config, "CACHE_DIR", Path(directory.name)),
            (config, "CACHE_ENABLED", True),
            (generate, "_call_times", []),
            (generate, "_session_calls", 0),
            (generate, "_session_prompt_tokens", 0),
            (generate, "_session_output_tokens", 0),
            (generate, "_cache_hits", 0),
        ):
            override = patch.object(target, attribute, value)
            override.start()
            self.addCleanup(override.stop)

    def client(self, **kwargs):
        call = Mock(**kwargs)
        override = patch.object(generate, "_get_client", return_value=SimpleNamespace(
            models=SimpleNamespace(generate_content=call)
        ))
        override.start()
        self.addCleanup(override.stop)
        return call

    def test_real_call_and_cache_hit_have_separate_usage(self):
        call = self.client(return_value=response())
        with generate.measure_usage() as first:
            generate.generate("same prompt")
        with generate.measure_usage() as cached:
            generate.generate("same prompt")
        call.assert_called_once()
        self.assertEqual(first.as_dict(), {
            "model_calls": 1, "cache_hits": 0, "usage_complete": True,
            "prompt_tokens": 10, "output_tokens": 3, "total_tokens": 15,
        })
        self.assertEqual(cached.as_dict(), {
            "model_calls": 0, "cache_hits": 1, "usage_complete": True,
            "prompt_tokens": 0, "output_tokens": 0, "total_tokens": 0,
        })
        self.assertEqual(generate.call_count(), 1)
        self.assertEqual(generate.token_counts(), {"prompt": 10, "output": 3, "total": 13})
        self.assertIsNone(generate._request_usage.get())

    def test_missing_metadata_is_unknown_instead_of_zero(self):
        self.client(return_value=SimpleNamespace(text="An answer", usage_metadata=None))
        with generate.measure_usage() as usage:
            generate.generate("not cached", cache=False)
        self.assertEqual(usage.model_calls, 1)
        self.assertFalse(usage.as_dict()["usage_complete"])
        self.assertIsNone(usage.as_dict()["total_tokens"])

    def test_retry_counts_attempts_and_marks_unreported_usage_unknown(self):
        self.client(side_effect=[RuntimeError("429 rate limit"), response()])
        with patch.object(generate.time, "sleep"):
            with generate.measure_usage() as usage:
                generate.generate("retry", cache=False)
        self.assertEqual(usage.model_calls, 2)
        self.assertFalse(usage.as_dict()["usage_complete"])

    def test_concurrent_requests_keep_their_own_usage(self):
        barrier = Barrier(2)

        def model_call(**kwargs):
            barrier.wait(timeout=5)
            count = int(kwargs["contents"])
            return response(count, 1, count + 1)

        self.client(side_effect=model_call)

        def run(count):
            with generate.measure_usage() as usage:
                generate.generate(str(count), cache=False)
            return usage.as_dict()

        with ThreadPoolExecutor(max_workers=2) as pool:
            records = list(pool.map(run, [11, 27]))
        self.assertEqual([record["prompt_tokens"] for record in records], [11, 27])
        self.assertTrue(all(record["model_calls"] == 1 for record in records))

    def test_usage_context_resets_after_failure(self):
        self.client(side_effect=RuntimeError("service unavailable"))
        with self.assertRaises(RuntimeError):
            with generate.measure_usage() as usage:
                generate.generate("failure", cache=False)
        self.assertEqual(usage.model_calls, 1)
        self.assertFalse(usage.as_dict()["usage_complete"])
        self.assertIsNone(generate._request_usage.get())


if __name__ == "__main__":
    unittest.main()
