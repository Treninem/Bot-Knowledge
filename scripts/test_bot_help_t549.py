"""Read-only validation for contextual T549–T551 language candidates.

This test validates examples and source integrity, never grants permissions.
"""
import hashlib
import json
import re
import subprocess
import unicodedata
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
POOL = ROOT / "staging/ru/bot_help_t549_context_pool.json"


def norm(value):
    return " ".join(
        "".join(
            " " if unicodedata.category(char)[0] in {"P", "S"} else char
            for char in unicodedata.normalize("NFKC", value).casefold().replace("ё", "е")
        ).split()
    )


def jaccard(a, b):
    aa, bb = set(norm(a).split()), set(norm(b).split())
    return len(aa & bb) / len(aa | bb) if aa | bb else 0


class ContextualBotHelp(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pool = json.loads(POOL.read_text(encoding="utf-8"))

    def test_source_integrity_and_permissions(self):
        pool = self.pool
        manifest = json.loads((ROOT / "manifest.json").read_text(encoding="utf-8"))
        source = ROOT / pool["source_pack"]
        digest = hashlib.sha256(source.read_bytes()).hexdigest()
        blob = subprocess.check_output(
            ["git", "hash-object", str(source)], cwd=ROOT, text=True
        ).strip()
        self.assertIn({"path": pool["source_pack"], "sha256": digest}, manifest["packs"])
        self.assertEqual(pool["source_pack_manifest_sha256"], digest)
        self.assertEqual(pool["source_pack_blob_sha"], blob)
        self.assertFalse(pool["consumer_registered"])
        self.assertEqual(pool["stage_type"], "supplemental_contextual_reply_pool")
        self.assertEqual(pool["audiences"], ["all_ai_bots"])
        self.assertEqual(pool["language"], "ru")
        self.assertEqual(
            pool["constraints"],
            {"read_only": True, "requires_direct_address": True,
             "no_personal_data": True, "no_sanctions": True,
             "requires_context_match": True},
        )

    def test_exact_counts_and_normalized_uniqueness(self):
        pool = self.pool
        checkpoint = pool["checkpoint"]
        entries = pool["entries"]
        self.assertEqual(len(entries), 5)
        ids, texts, notes, intents = set(), set(), set(), set()
        expected_each = checkpoint["cumulative_candidates"] // 5
        self.assertEqual(expected_each * 5, checkpoint["cumulative_candidates"])
        self.assertGreaterEqual(expected_each, 40)
        self.assertLessEqual(expected_each, 100)
        total = 0
        for entry in entries:
            intent = entry["intent_id"]
            self.assertNotIn(intent, intents)
            intents.add(intent)
            self.assertEqual(entry["language"], "ru")
            self.assertEqual(entry["audiences"], ["all_ai_bots"])
            self.assertEqual(entry["target"], 100)
            self.assertEqual(entry["total_staged"], expected_each)
            self.assertEqual(entry["remaining"], 100 - expected_each)
            self.assertEqual(
                entry["prior_for_stable_id"] + entry["added_candidates"], expected_each
            )
            self.assertEqual(len(entry["replies"]), expected_each)
            for i, reply in enumerate(entry["replies"], 1):
                self.assertEqual(reply["id"], f"{intent}_{i:02d}")
                self.assertNotIn(reply["id"], ids)
                ids.add(reply["id"])
                self.assertTrue(reply["read_only"])
                self.assertEqual(reply["audiences"], ["all_ai_bots"])
                self.assertEqual(reply["language"], "ru")
                self.assertEqual(reply["context"], "direct")
                self.assertIn("адресации", reply["avoid"])
                for value, target in (
                    (reply["text"], texts),
                    (reply["context_note"], notes),
                ):
                    key = norm(value)
                    self.assertTrue(key)
                    self.assertNotIn(key, target, f"Repeated content: {reply['id']}")
                    target.add(key)
                self.assertNotRegex(
                    reply["text"].casefold(),
                    r"\b(?:я забанил|я замутил|я удалил|я настроил|я оплатил)\b",
                )
                total += 1
        self.assertEqual(total, checkpoint["cumulative_candidates"])
        self.assertEqual(
            checkpoint["prior_candidates"] + checkpoint["added_candidates"], total
        )
        self.assertEqual(checkpoint["remaining_total"], 500 - total)
        self.assertEqual(checkpoint["finished_100"], 5 if total == 500 else 0)
        self.assertEqual(checkpoint["partial_intents"], 0 if total == 500 else 5)

    def test_similarity_and_cross_stage_exact_duplicates(self):
        pool = self.pool
        replies = [r["text"] for e in pool["entries"] for r in e["replies"]]
        for i, left in enumerate(replies):
            for right in replies[i + 1:]:
                self.assertLess(jaccard(left, right), 0.78, "Near duplicate")
        normalized = {norm(text) for text in replies}
        for path in sorted((ROOT / "staging/ru").glob("*.json")):
            if path == POOL:
                continue
            other = json.loads(path.read_text(encoding="utf-8"))
            if not isinstance(other, dict):
                continue
            for entry in other.get("entries", []):
                if not isinstance(entry, dict):
                    continue
                for item in entry.get("replies", []):
                    val = item.get("text") if isinstance(item, dict) else item
                    if isinstance(val, str):
                        self.assertNotIn(norm(val), normalized,
                                         f"Cross-pool duplicate in {path.name}")


if __name__ == "__main__":
    unittest.main()
