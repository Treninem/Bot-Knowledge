"""Regression tests for the conservative ImPULS #383 snapshot budget guard.

Run: python scripts/test_consumer_snapshot_budget.py
This test exercises pure arithmetic only; it does not prove consumer loading.
"""
from __future__ import annotations

import unittest

from validate_pack import MAX_CONSUMER_SNAPSHOT_BYTES, evaluate_snapshot_budget


class SnapshotBudgetTests(unittest.TestCase):
    def test_counts_manifest_and_all_registered_pack_bytes(self) -> None:
        self.assertEqual(evaluate_snapshot_budget(100, [1000, 500]), (1600, MAX_CONSUMER_SNAPSHOT_BYTES - 1600))

    def test_exact_limit_is_allowed(self) -> None:
        self.assertEqual(evaluate_snapshot_budget(8, [MAX_CONSUMER_SNAPSHOT_BYTES - 8])[1], 0)

    def test_one_byte_above_limit_is_rejected(self) -> None:
        self.assertEqual(evaluate_snapshot_budget(9, [MAX_CONSUMER_SNAPSHOT_BYTES - 8])[1], -1)

    def test_aggregate_limit_applies_even_with_small_individual_packs(self) -> None:
        sizes = [2 * 1024 * 1024] * 4
        self.assertEqual(evaluate_snapshot_budget(1, sizes)[1], -1)

    def test_negative_or_boolean_length_is_invalid(self) -> None:
        for manifest_bytes, pack_sizes in ((-1, []), (0, [-1]), (True, []), (0, [False])):
            with self.subTest(manifest_bytes=manifest_bytes, pack_sizes=pack_sizes):
                with self.assertRaises(ValueError):
                    evaluate_snapshot_budget(manifest_bytes, pack_sizes)

    def test_invalid_budget_is_not_silently_accepted(self) -> None:
        for limit in (0, -1, True):
            with self.subTest(limit=limit):
                with self.assertRaises(ValueError):
                    evaluate_snapshot_budget(0, [], limit=limit)


if __name__ == "__main__":
    unittest.main()
