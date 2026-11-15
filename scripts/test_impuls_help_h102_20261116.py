#!/usr/bin/env python3
"""H102: exact staged lineage, safe context, PII, and duplicate guards."""
import hashlib
import re
import unittest
from collections import Counter
from test_impuls_help_h101_20261116 import load as earlier_load, ROOT, read, normalized, similarity

PACK = "packs/ru/impuls_help_qa.json"
PATH = "staging/ru/impuls_help_context_h102_20261116.json"

class H102QA(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.src = {r["id"]: r for r in read(PACK)["records"]}
        cls.prior = [earlier_load(i) for i in range(1, 102)]
        cls.current = read(PATH)

    def test_manifest_and_context_restrictions(self):
        manifest = read("manifest.json")
        real = hashlib.sha256((ROOT / PACK).read_bytes()).hexdigest()
        self.assertEqual(real, next(p["sha256"] for p in manifest["packs"] if p["path"] == PACK))
        self.assertEqual(self.current["source_pack_manifest_sha256"], real)
        self.assertNotIn(PATH, {p["path"] for p in manifest["packs"]})
        self.assertFalse(self.current["consumer_registered"])
        self.assertEqual(self.current["audiences"], ["impuls"])
        self.assertEqual(self.current["constraints"], dict(read_only=True,
            requires_direct_address=True, requires_context_match=True,
            no_personal_data=True, no_sanctions=True))
        self.assertEqual(self.current["checked_source_main_sha"],
                         "6c9f430da47f137d39a72bbd28c057cfb8f6be96")

    def test_complete_lineage_and_100_intents(self):
        counts = Counter()
        ids = set()
        for stage in self.prior:
            for item in stage["entries"]:
                for reply in item["replies"]:
                    self.assertNotIn(reply["id"], ids)
                    ids.add(reply["id"])
                counts[item["intent_id"]] += len(item["replies"])
        self.assertEqual(len(counts), 100)
        self.assertEqual(sum(counts.values()), 4198)
        found = set()
        new = 0
        for e in self.current["entries"]:
            key = e["intent_id"]
            self.assertIn(key, self.src)
            self.assertNotIn(key, found)
            found.add(key)
            baseline = 1 + len(self.src[key]["variants"])
            self.assertEqual(e["canonical_question"], self.src[key]["question"])
            self.assertEqual(e["published_count"], baseline)
            self.assertEqual(e["earlier_staged_candidates"], counts[key])
            self.assertEqual(e["added_candidates"], len(e["replies"]))
            self.assertEqual(e["total_candidates_in_main_and_H102"],
                             baseline + counts[key] + len(e["replies"]))
            self.assertEqual(e["remaining_to_target_excluding_other_prs"],
                             100 - e["total_candidates_in_main_and_H102"])
            self.assertGreater(e["remaining_to_target_excluding_other_prs"], 0)
            new += len(e["replies"])
            counts[key] += len(e["replies"])
        self.assertEqual(len(found), 100)
        self.assertEqual(new, 102)
        self.assertEqual(sum(counts.values()), 4300)
        self.assertEqual(sum(100 - 1 - len(self.src[k]["variants"]) - v
                             for k, v in counts.items()), 5425)
        c = self.current["checkpoint"]
        self.assertEqual(c["new_candidates"], new)
        self.assertEqual(c["processed_intents"], 100)
        self.assertEqual(c["cumulative_H1_H102"], 4300)
        self.assertEqual(c["remaining_numeric_all_100_intents"], 5425)
        self.assertEqual(c["certified_100_sets"], 0)
        self.assertEqual(c["editorially_approved_new"], 0)

    def test_reply_ids_privacy_and_cross_lineage_lexical_duplicates(self):
        old = [t for r in self.src.values() for t in [r["answer"], *r["variants"]]]
        old.extend(r["text"] for stage in self.prior
                   for e in stage["entries"] for r in e["replies"])
        norms = {normalized(s) for s in old}
        ids = set()
        for e in self.current["entries"]:
            for j, r in enumerate(e["replies"], 1):
                self.assertEqual(r["id"], f'impuls_help_{e["intent_id"]}_h102_{j:02d}')
                self.assertNotIn(r["id"], ids)
                ids.add(r["id"])
                self.assertEqual(r["language"], "ru")
                self.assertEqual(r["audiences"], ["impuls"])
                self.assertEqual(r["response_role"], "assistant_reply")
                self.assertEqual(r["editorial_status"], "candidate_pending_full_semantic_review")
                self.assertTrue(r["read_only"])
                self.assertIn(r["context"], ("private", "direct", "group_addressed"))
                self.assertGreaterEqual(len(r["text"]), 75)
                self.assertGreaterEqual(len(r["context_note"]), 55)
                self.assertIn("без санкций", r["avoid"])
                self.assertFalse(re.search(r"https?://|t\\.me/|@[a-z_]|[0-9]{10,}",
                                           r["text"] + r["context_note"], re.I))
                self.assertNotIn(normalized(r["text"]), norms)
                self.assertTrue(all(similarity(r["text"], p) < .70 for p in old), r["id"])
                norms.add(normalized(r["text"]))
                old.append(r["text"])

if __name__ == "__main__":
    unittest.main()
