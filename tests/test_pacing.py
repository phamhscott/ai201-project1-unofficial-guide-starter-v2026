"""Test preventive pacing using a virtual clock, without API calls or real sleeps."""

from threading import Lock
import unittest
from unittest.mock import patch

import generate
from tools.probe_pacing import measure


class PacingTests(unittest.TestCase):
    def test_initial_delay_and_minimum_spacing(self):
        result = measure()
        self.assertEqual(result["real_api_calls"], 0)
        self.assertEqual(result["call_start_seconds"], [2.0, 4.0, 6.0, 8.0, 10.0])
        self.assertEqual(result["minimum_gap_seconds"], 2.0)
        self.assertEqual(result["total_pacing_wait_seconds"], 9.6)

    def test_full_window_cannot_be_bypassed_by_spacing(self):
        now = [1000.0]

        def sleep(seconds):
            now[0] += seconds

        # Thirty recent reservations must still enforce the rolling window.
        with patch.object(generate, "_call_times", [999.0] * 30):
            with patch.object(generate, "_pacing_lock", Lock()):
                with patch.object(generate.time, "monotonic", side_effect=lambda: now[0]):
                    with patch.object(generate.time, "sleep", side_effect=sleep):
                        generate._wait_for_slot()
                        self.assertGreaterEqual(now[0], 1059.0)
                        self.assertEqual(len(generate._call_times), 1)


if __name__ == "__main__":
    unittest.main()
