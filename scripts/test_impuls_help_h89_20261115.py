#!/usr/bin/env python3
"""H89 staged RU contextual responses: full lineage and conservative candidate QA.

This only checks the repository candidate pool. It cannot prove a live ImPULS
consumer routes, authorizes or publishes any of these responses.
"""
import hashlib
import re
import unittest
from collections import Counter, defaultdict

from test_impuls_help_h65_20261115 import ROOT, read, normalized, similarity

PACK = "packs/ru/impuls_help_qa.json"
H89_PATH = "staging/ru/impuls_help_context_h89_20261115.json"
EXPECTED_NEW = 100
EXPECTED_STAGED = 3465
EXPECTED_GAP = 6260
EXPECTED_TOTAL = 3740


def stage(n):
    date = "20261114" if n <= 30 else "20261115"
    return read(f"staging/ru/impuls_help_context_h{n}_{date}.json")


class H89FullLineage(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = read(PACK)
        cls.records = {r["id"]: r for r in cls.source["records"]}
        cls.stages = [stage(i) for i in range(1, 90)]
        cls.new = cls.stages[-1]

    def test_source_and_scope(self):
        manifest = read("manifest.json")
        source_sha = hashlib.sha256((ROOT / PACK).read_bytes()).hexdigest()
        self.assertEqual(
            source_sha,
            next(e["sha256"] for e in manifest["packs"] if e["path"] == PACK),
        )
        self.assertEqual(self.new["source_pack_manifest_sha256"], source_sha)
        self.assertEqual(
            self.new["source_pack_blob_sha"],
            "430f78f7bf43940b112978bc5087b5cb6002eabe",
        )
        self.assertEqual(
            self.new["checked_source_main_sha"],
            "6c9f430da47f137d39a72bbd28c057cfb8f6be96",
        )
        self.assertEqual(
            self.new["checked_impuls_main_sha"],
            "54b8a3a813fec82c1f953408942ba327eb181c37",
        )
        self.assertEqual(self.new["audiences"], ["impuls"])
        self.assertFalse(self.new["consumer_registered"])
        self.assertEqual(self.new["stage_type"], "supplemental_contextual_reply_pool")
        for key in (
            "read_only", "requires_direct_address", "requires_context_match",
            "no_personal_data", "no_sanctions",
        ):
            self.assertTrue(self.new["constraints"][key])

    def test_100_distinct_intents_counts_and_unique_ids(self):
        staged = Counter()
        identifiers = set()
        updated = set()
        for number, s in enumerate(self.stages, start=1):
            for entry in s["entries"]:
                intent = entry["intent_id"]
                self.assertIn(intent, self.records)
                replies = entry["replies"]
                if number == 89:
                    original = self.records[intent]
                    published = 1 + len(original["variants"])
                    total = published + staged[intent] + len(replies)
                    self.assertNotIn(intent, updated)
                    updated.add(intent)
                    self.assertEqual(entry["canonical_question"], original["question"])
                    self.assertEqual(entry["published_count"], published)
                    self.assertEqual(entry["earlier_staged_candidates"], staged[intent])
                    self.assertEqual(entry["added_candidates"], 1)
                    self.assertEqual(len(replies), 1)
                    self.assertEqual(entry["target"], 100)
                    self.assertEqual(entry["total_candidates_in_main_and_H89"], total)
                    self.assertEqual(entry["remaining_to_target_excluding_other_prs"], 100 - total)
                    self.assertLess(total, 100)
                for reply in replies:
                    self.assertNotIn(reply["id"], identifiers)
                    identifiers.add(reply["id"])
                staged[intent] += len(replies)
        self.assertEqual(updated, {e["intent_id"] for e in self.new["entries"]})
        self.assertEqual(len(self.new["entries"]), EXPECTED_NEW)
        self.assertEqual(len(staged), 100)
        self.assertEqual(sum(staged.values()), EXPECTED_STAGED)
        gaps = sum(100 - 1 - len(self.records[i]["variants"]) - n
                   for i, n in staged.items())
        self.assertEqual(gaps, EXPECTED_GAP)
        self.assertEqual(EXPECTED_STAGED + sum(
            1 + len(self.records[i]["variants"]) for i in updated
        ), EXPECTED_TOTAL)
        checkpoint = self.new["checkpoint"]
        self.assertEqual(checkpoint["processed_intents"], EXPECTED_NEW)
        self.assertEqual(checkpoint["new_candidates"], EXPECTED_NEW)
        self.assertEqual(checkpoint["cumulative_H1_H89"], EXPECTED_STAGED)
        self.assertEqual(checkpoint["remaining_numeric_all_100_intents"], EXPECTED_GAP)
        self.assertEqual(checkpoint["editorially_approved_new"], 0)
        self.assertEqual(checkpoint["certified_100_sets"], 0)

    def test_normalized_dedup_semantic_proxy_context_and_privacy(self):
        previous_texts = []
        previous_by_intent = defaultdict(list)
        for r in self.records.values():
            previous_texts.extend([r["answer"], *r["variants"]])
        seen = {normalized(t) for t in previous_texts}
        for number, s in enumerate(self.stages, start=1):
            for entry in s["entries"]:
                for reply in entry["replies"]:
                    if number == 89:
                        text = reply["text"]
                        note = reply["context_note"]
                        self.assertEqual(reply["id"], f"impuls_help_{entry['intent_id']}_h89_01")
                        self.assertEqual(reply["language"], "ru")
                        self.assertEqual(reply["audiences"], ["impuls"])
                        self.assertEqual(reply["response_role"], "assistant_reply")
                        self.assertEqual(reply["editorial_status"], "candidate_pending_full_semantic_review")
                        self.assertTrue(reply["read_only"])
                        self.assertIn(reply["context"], ("private", "direct", "group_addressed"))
                        self.assertGreaterEqual(len(text), 75)
                        self.assertGreaterEqual(len(note), 55)
                        self.assertGreaterEqual(len(reply["avoid"]), 70)
                        self.assertNotIn(normalized(text), seen)
                        self.assertFalse(re.search(
                            r"https?://|t\.me/|@[a-z_]|[0-9]{10,}",
                            text + " " + note, re.I,
                        ))
                        self.assertFalse(re.search(
                            r"я (?:удалил|забанил|выдал санкцию|изменил настройки)",
                            text, re.I,
                        ))
                        for old in previous_by_intent[entry["intent_id"]]:
                            self.assertLess(similarity(text, old), 0.70, reply["id"])
                    seen.add(normalized(reply["text"]))
                    previous_by_intent[entry["intent_id"]].append(reply["text"])


if __name__ == "__main__":
    unittest.main()
