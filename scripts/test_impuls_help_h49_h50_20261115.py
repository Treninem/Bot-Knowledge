#!/usr/bin/env python3
"""H49-H50: cumulative counts, contextual boundaries and lexical screening."""
import hashlib
import json
import re
import unittest
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = "packs/ru/impuls_help_qa.json"

def load(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))

def normalized(text):
    return " ".join(re.findall(r"[^\W_]+", text.casefold().replace("ё", "е"), re.UNICODE))

def overlap(a, b):
    x, y = set(normalized(a).split()), set(normalized(b).split())
    return len(x & y) / max(1, len(x | y))

class ContextualH49H50(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.manifest = load("manifest.json")
        cls.faq = load(SOURCE)
        cls.records = {r["id"]: r for r in cls.faq["records"]}
        cls.stages = [
            load("staging/ru/impuls_help_context_h%d_%s.json" % (
                n, "20261114" if n <= 30 else "20261115"
            )) for n in range(1, 51)
        ]

    def test_cumulative_progress_and_unique_ids(self):
        counts = Counter()
        ids = set()
        for n, stage in enumerate(self.stages, 1):
            for entry in stage["entries"]:
                key = entry["intent_id"]
                self.assertIn(key, self.records)
                self.assertEqual(entry["canonical_question"], self.records[key]["question"])
                self.assertEqual(len(entry["replies"]), entry["added_candidates"])
                if n >= 49:
                    published = 1 + len(self.records[key]["variants"])
                    self.assertEqual(entry["published_count"], published)
                    self.assertEqual(entry["earlier_staged_candidates"], counts[key])
                    self.assertEqual(entry["remaining_to_target_excluding_other_prs"], 100 - published - counts[key] - len(entry["replies"]))
                    self.assertEqual(entry["total_candidates_in_main_and_H%d" % n], published + counts[key] + len(entry["replies"]))
                for reply in entry["replies"]:
                    self.assertNotIn(reply["id"], ids, reply["id"])
                    ids.add(reply["id"])
                    counts[key] += 1
        self.assertEqual(len(counts), 100)
        self.assertEqual(sum(counts.values()), 2155)
        self.assertEqual(sum(100 - 1 - len(self.records[k]["variants"]) - counts[k] for k in counts), 7570)
        self.assertEqual([sum(len(e["replies"]) for e in s["entries"]) for s in self.stages[-2:]], [40, 40])

    def test_sha_and_nonpublished_scope(self):
        expected = next(p["sha256"] for p in self.manifest["packs"] if p["path"] == SOURCE)
        self.assertEqual(hashlib.sha256((ROOT / SOURCE).read_bytes()).hexdigest(), expected)
        for n, stage in zip((49, 50), self.stages[-2:]):
            self.assertFalse(stage["consumer_registered"])
            self.assertEqual(stage["source_pack_manifest_sha256"], expected)
            self.assertEqual(stage["checked_source_main_sha"], "6c9f430da47f137d39a72bbd28c057cfb8f6be96")
            self.assertEqual(stage["checked_impuls_main_sha"], "d815dc6338808c881c5ff613c9550dc42e74b44f")
            self.assertEqual(stage["audiences"], ["impuls"])
            self.assertEqual(len(stage["entries"]), 20)
            self.assertEqual(stage["checkpoint"]["new_candidates"], 40)
            self.assertEqual(stage["checkpoint"]["remaining_numeric_all_100_intents"], 7610 if n == 49 else 7570)
            for flag in ("read_only", "requires_direct_address", "requires_context_match", "no_personal_data", "no_sanctions"):
                self.assertIs(stage["constraints"][flag], True)
            for entry in stage["entries"]:
                self.assertEqual(entry["audiences"], ["impuls"])
                self.assertEqual(entry["response_role"], "assistant_reply")
                for reply in entry["replies"]:
                    self.assertEqual(reply["language"], "ru")
                    self.assertEqual(reply["audiences"], ["impuls"])
                    self.assertEqual(reply["response_role"], "assistant_reply")
                    self.assertEqual(reply["editorial_status"], "candidate_pending_full_semantic_review")
                    self.assertIs(reply["read_only"], True)
                    self.assertIn(reply["context"], ("direct", "private", "group_addressed"))
                    self.assertGreaterEqual(len(reply["text"]), 75, reply["id"])
                    self.assertGreaterEqual(len(reply["context_note"]), 55, reply["id"])
                    self.assertTrue(reply["avoid"])
                    self.assertIsNone(re.search(r"https?://|t\.me/|@[a-z_]|\d{10,}", reply["text"] + reply["context_note"], re.I))

    def test_new_answers_against_existing_text(self):
        earlier = [s for record in self.faq["records"] for s in (record["answer"], *record["variants"])]
        notes = defaultdict(list)
        seen = {normalized(s) for s in earlier}
        for n, stage in enumerate(self.stages, 1):
            for entry in stage["entries"]:
                for reply in entry["replies"]:
                    if n >= 49:
                        self.assertNotIn(normalized(reply["text"]), seen, reply["id"])
                        self.assertTrue(all(overlap(reply["text"], s) < .70 for s in earlier), reply["id"])
                        self.assertTrue(all(overlap(reply["context_note"], s) < .65 for s in notes[entry["intent_id"]]), reply["id"])
                    seen.add(normalized(reply["text"]))
                    earlier.append(reply["text"])
                    notes[entry["intent_id"]].append(reply["context_note"])

    def test_no_unauthorized_actions_or_mislabelled_context(self):
        for stage in self.stages[-2:]:
            for entry in stage["entries"]:
                for reply in entry["replies"]:
                    self.assertNotEqual(normalized(reply["text"]), normalized(reply["context_note"]))
                    self.assertNotIn("автоматически забаню", reply["text"].lower())
                    self.assertNotIn("я удалил сообщение", reply["text"].lower())
                    self.assertNotIn("я начислил", reply["text"].lower())
                    self.assertNotIn("я включил антиспам", reply["text"].lower())

if __name__ == "__main__":
    unittest.main()
