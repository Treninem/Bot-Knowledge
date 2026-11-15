#!/usr/bin/env python3
"""H58–H60: staged-only contextual help, exact counts, privacy and duplicate checks."""
import hashlib
import json
import re
import unittest
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STAGE = "staging/ru/impuls_help_context_h{}_{}.json"
SOURCE = "packs/ru/impuls_help_qa.json"

def read(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))

def norm(value):
    return " ".join(re.findall(r"[^\\W_]+", value.lower().replace("ё", "е")))

def jaccard(a, b):
    a, b = set(norm(a).split()), set(norm(b).split())
    return len(a & b) / max(1, len(a | b))

class StageH58H60(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.qa = read(SOURCE)
        cls.published = {r["id"]: r for r in cls.qa["records"]}
        cls.stages = [read(STAGE.format(i, "20261114" if i <= 30 else "20261115")) for i in range(1, 61)]

    def test_cumulative_counts_and_intents(self):
        counter, ids = Counter(), set()
        for i, stage in enumerate(self.stages, 1):
            self.assertFalse(stage["consumer_registered"])
            for entry in stage["entries"]:
                key = entry["intent_id"]
                self.assertIn(key, self.published)
                self.assertEqual(entry["canonical_question"], self.published[key]["question"])
                self.assertEqual(entry["added_candidates"], len(entry["replies"]))
                if i >= 58:
                    published = 1 + len(self.published[key]["variants"])
                    self.assertEqual(entry["published_count"], published)
                    self.assertEqual(entry["earlier_staged_candidates"], counter[key])
                    self.assertEqual(entry["total_candidates_in_main_and_H" + str(i)],
                                     published + counter[key] + len(entry["replies"]))
                    self.assertEqual(entry["remaining_to_target_excluding_other_prs"],
                                     100 - published - counter[key] - len(entry["replies"]))
                for reply in entry["replies"]:
                    self.assertNotIn(reply["id"], ids)
                    ids.add(reply["id"])
                    counter[key] += 1
            if i >= 58:
                self.assertEqual(len(stage["entries"]), 20)
                self.assertEqual(stage["checkpoint"]["new_candidates"], 20)
                self.assertEqual(stage["checkpoint"]["cumulative_H1_H" + str(i)], 2435 + 20 * (i - 57))
                self.assertEqual(stage["checkpoint"]["remaining_numeric_all_100_intents"], 7290 - 20 * (i - 57))
        self.assertEqual(len(counter), 100)
        self.assertEqual(sum(counter.values()), 2495)
        self.assertEqual(sum(100 - 1 - len(self.published[k]["variants"]) - v for k, v in counter.items()), 7230)

    def test_source_integrity_and_unpublished_scope(self):
        manifest = read("manifest.json")
        expected = next(x["sha256"] for x in manifest["packs"] if x["path"] == SOURCE)
        actual = hashlib.sha256((ROOT / SOURCE).read_bytes()).hexdigest()
        self.assertEqual(expected, actual)
        for i in range(57, 60):
            stage = self.stages[i]
            self.assertEqual(stage["source_pack_manifest_sha256"], actual)
            self.assertEqual(stage["checked_source_main_sha"],
                             "6c9f430da47f137d39a72bbd28c057cfb8f6be96")
            self.assertEqual(stage["checked_impuls_main_sha"],
                             "4a3587db879b8f0b7868c33cd719ba039306dab0")
            self.assertTrue(stage["constraints"]["read_only"])
            self.assertTrue(stage["constraints"]["no_sanctions"])
            for entry in stage["entries"]:
                self.assertEqual(entry["language"], "ru")
                for reply in entry["replies"]:
                    self.assertEqual(reply["response_role"], "assistant_reply")
                    self.assertEqual(reply["audiences"], ["impuls"])
                    self.assertIn(reply["context"], ("group_addressed", "private", "direct"))
                    self.assertEqual(reply["editorial_status"], "candidate_pending_full_semantic_review")
                    self.assertTrue(reply["read_only"])
                    self.assertGreaterEqual(len(reply["text"]), 75)
                    self.assertGreaterEqual(len(reply["context_note"]), 55)
                    self.assertIsNone(re.search(r"https?://|t\\.me/|@[a-z_]|[0-9]{10,}", reply["text"] + " " + reply["context_note"], re.I))
                    self.assertNotIn("я забанил", reply["text"].lower())

    def test_new_exact_and_near_duplicates(self):
        older = [s for record in self.qa["records"] for s in (record["answer"], *record["variants"])]
        notes = defaultdict(list)
        for i, stage in enumerate(self.stages, 1):
            for entry in stage["entries"]:
                for reply in entry["replies"]:
                    if i >= 58:
                        self.assertNotIn(norm(reply["text"]), {norm(s) for s in older}, reply["id"])
                        self.assertTrue(all(jaccard(reply["text"], old) < .70 for old in older), reply["id"])
                        self.assertTrue(all(jaccard(reply["context_note"], old) < .65 for old in notes[entry["intent_id"]]), reply["id"])
                    older.append(reply["text"])
                    notes[entry["intent_id"]].append(reply["context_note"])

if __name__ == "__main__":
    unittest.main()
