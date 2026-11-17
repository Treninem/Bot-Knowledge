#!/usr/bin/env python3
"""H98 candidate QA: full lineage, source integrity, scope and duplicate guards."""
import hashlib
import re
import unittest
from collections import Counter

from test_impuls_help_h65_20261115 import ROOT, read, normalized, similarity

PACK = "packs/ru/impuls_help_qa.json"
STAGE = "staging/ru/impuls_help_context_h98_20261115.json"

def stage(number):
    day = "20261114" if number <= 30 else "20261115"
    return read(f"staging/ru/impuls_help_context_h{number}_{day}.json")


class H98QA(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = {r["id"]: r for r in read(PACK)["records"]}
        cls.all = [stage(i) for i in range(1, 99)]
        cls.new = cls.all[-1]

    def test_source_manifest_and_stage_boundaries(self):
        manifest = read("manifest.json")
        hashes = {x["path"]: x["sha256"] for x in manifest["packs"]}
        actual = hashlib.sha256((ROOT / PACK).read_bytes()).hexdigest()
        self.assertEqual(hashes[PACK], actual)
        self.assertEqual(self.new["source_pack_manifest_sha256"], actual)
        self.assertEqual(self.new["source_pack"], PACK)
        self.assertFalse(self.new["consumer_registered"])
        self.assertNotIn(STAGE, hashes)
        self.assertEqual(self.new["audiences"], ["impuls"])
        self.assertEqual(self.new["constraints"], dict(
            read_only=True, requires_direct_address=True,
            requires_context_match=True, no_personal_data=True,
            no_sanctions=True,
        ))

    def test_complete_lineage_and_exact_partial_counters(self):
        staged = Counter()
        seen = set()
        current = set()
        for number, data in enumerate(self.all, 1):
            for e in data["entries"]:
                intent = e["intent_id"]
                self.assertIn(intent, self.source)
                if number == 98:
                    self.assertNotIn(intent, current)
                    current.add(intent)
                    pub = 1 + len(self.source[intent]["variants"])
                    self.assertEqual(e["canonical_question"], self.source[intent]["question"])
                    self.assertEqual(e["published_count"], pub)
                    self.assertEqual(e["earlier_staged_candidates"], staged[intent])
                    self.assertEqual(e["added_candidates"], len(e["replies"]))
                    self.assertEqual(e["total_candidates_in_main_and_H98"], pub + staged[intent] + len(e["replies"]))
                    self.assertEqual(e["remaining_to_target_excluding_other_prs"], 100 - e["total_candidates_in_main_and_H98"])
                for r in e["replies"]:
                    self.assertNotIn(r["id"], seen)
                    seen.add(r["id"])
                staged[intent] += len(e["replies"])
        self.assertEqual(len(current), 48)
        self.assertEqual(len(staged), 100)
        self.assertEqual(sum(staged.values()), 4016)
        self.assertEqual(sum(100 - 1 - len(self.source[k]["variants"]) - n for k, n in staged.items()), 5709)
        self.assertEqual(self.new["checkpoint"]["processed_intents"], 48)
        self.assertEqual(self.new["checkpoint"]["new_candidates"], 50)
        self.assertEqual(self.new["checkpoint"]["cumulative_H1_H98"], 4016)
        self.assertEqual(self.new["checkpoint"]["remaining_numeric_all_100_intents"], 5709)
        self.assertEqual(self.new["checkpoint"]["editorially_approved_new"], 0)
        self.assertEqual(self.new["checkpoint"]["certified_100_sets"], 0)

    def test_non_repeated_read_only_originals(self):
        previous = [t for r in self.source.values() for t in [r["answer"], *r["variants"]]]
        previous.extend(r["text"] for s in self.all[:-1] for e in s["entries"] for r in e["replies"])
        seen = {normalized(t) for t in previous}
        count = Counter()
        for e in self.new["entries"]:
            intent = e["intent_id"]
            self.assertEqual(e["language"], "ru")
            self.assertEqual(e["audiences"], ["impuls"])
            for r in e["replies"]:
                count[intent] += 1
                self.assertEqual(r["id"], f"impuls_help_{intent}_h98_{count[intent]:02d}")
                self.assertEqual(r["response_role"], "assistant_reply")
                self.assertEqual(r["audiences"], ["impuls"])
                self.assertEqual(r["language"], "ru")
                self.assertTrue(r["read_only"])
                self.assertEqual(r["editorial_status"], "candidate_pending_full_semantic_review")
                self.assertIn(r["context"], ("private", "direct", "group_addressed"))
                self.assertGreaterEqual(len(r["text"]), 75)
                self.assertGreaterEqual(len(r["context_note"]), 55)
                self.assertIn("без санкций", r["avoid"])
                self.assertNotIn(normalized(r["text"]), seen)
                self.assertTrue(all(similarity(r["text"], p) < .70 for p in previous), r["id"])
                self.assertFalse(re.search(
                    r"https?://|t\.me/|@[a-z_]|[0-9]{10,}",
                    r["text"] + r["context_note"], re.I))
                seen.add(normalized(r["text"]))
                previous.append(r["text"])
        self.assertEqual(sum(count.values()), 50)
        self.assertEqual(count["greeting"], 3)


if __name__ == "__main__":
    unittest.main()
