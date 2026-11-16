#!/usr/bin/env python3
"""H103: exact 100-intent lineage, stage isolation, privacy and duplicate guards."""
import hashlib
import re
import unittest
from collections import Counter
from test_impuls_help_h101_20261116 import ROOT, load, read, normalized, similarity

PACK = "packs/ru/impuls_help_qa.json"
STAGE = "staging/ru/impuls_help_context_h103_20261116.json"

class H103QA(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.src = {r["id"]: r for r in read(PACK)["records"]}
        cls.prior = [load(i) for i in range(1, 102)] + [
            read("staging/ru/impuls_help_context_h102_20261116.json")
        ]
        cls.stage = read(STAGE)

    def test_registered_pack_integrity_and_isolation(self):
        manifest = read("manifest.json")
        actual = hashlib.sha256((ROOT / PACK).read_bytes()).hexdigest()
        registered = next(p["sha256"] for p in manifest["packs"] if p["path"] == PACK)
        self.assertEqual(actual, registered)
        self.assertEqual(self.stage["source_pack_manifest_sha256"], actual)
        self.assertNotIn(STAGE, {p["path"] for p in manifest["packs"]})
        self.assertFalse(self.stage["consumer_registered"])
        self.assertEqual(self.stage["audiences"], ["impuls"])
        self.assertEqual(self.stage["constraints"], dict(
            read_only=True, requires_direct_address=True,
            requires_context_match=True, no_personal_data=True, no_sanctions=True
        ))
        self.assertEqual(self.stage["checked_source_main_sha"],
                         "6c9f430da47f137d39a72bbd28c057cfb8f6be96")

    def test_lineage_full_100_intents_and_real_deltas(self):
        counts = Counter()
        ids = set()
        for stage in self.prior:
            for e in stage["entries"]:
                for reply in e["replies"]:
                    self.assertNotIn(reply["id"], ids)
                    ids.add(reply["id"])
                counts[e["intent_id"]] += len(e["replies"])
        self.assertEqual(len(counts), 100)
        self.assertEqual(sum(counts.values()), 4300)
        found = set()
        n = 0
        for e in self.stage["entries"]:
            key = e["intent_id"]
            self.assertIn(key, self.src)
            self.assertNotIn(key, found)
            found.add(key)
            pub = 1 + len(self.src[key]["variants"])
            self.assertEqual(e["published_count"], pub)
            self.assertEqual(e["canonical_question"], self.src[key]["question"])
            self.assertEqual(e["earlier_staged_candidates"], counts[key])
            self.assertEqual(e["added_candidates"], len(e["replies"]))
            self.assertEqual(e["total_candidates_in_main_and_H103"],
                             pub + counts[key] + len(e["replies"]))
            self.assertEqual(e["remaining_to_target_excluding_other_prs"],
                             100 - e["total_candidates_in_main_and_H103"])
            self.assertGreater(e["remaining_to_target_excluding_other_prs"], 0)
            counts[key] += len(e["replies"])
            n += len(e["replies"])
        self.assertEqual(len(found), 100)
        self.assertEqual(n, 102)
        self.assertEqual(sum(counts.values()), 4402)
        self.assertEqual(sum(100 - 1 - len(self.src[k]["variants"]) - v
                             for k, v in counts.items()), 5323)
        self.assertEqual(self.stage["checkpoint"]["new_candidates"], 102)
        self.assertEqual(self.stage["checkpoint"]["cumulative_H1_H103"], 4402)
        self.assertEqual(self.stage["checkpoint"]["remaining_numeric_all_100_intents"], 5323)
        self.assertEqual(self.stage["checkpoint"]["certified_100_sets"], 0)
        self.assertEqual(self.stage["checkpoint"]["editorially_approved_new"], 0)

    def test_new_reply_texts_id_privacy_and_context(self):
        before = [t for e in self.src.values() for t in [e["answer"], *e["variants"]]]
        before.extend(r["text"] for stage in self.prior
                      for e in stage["entries"] for r in e["replies"])
        norms = {normalized(v) for v in before}
        new_ids = set()
        notes = set()
        for e in self.stage["entries"]:
            for j, r in enumerate(e["replies"], 1):
                self.assertEqual(r["id"], f'impuls_help_{e["intent_id"]}_h103_{j:02d}')
                self.assertNotIn(r["id"], new_ids)
                new_ids.add(r["id"])
                self.assertEqual(r["language"], "ru")
                self.assertEqual(r["audiences"], ["impuls"])
                self.assertEqual(r["response_role"], "assistant_reply")
                self.assertEqual(r["editorial_status"], "candidate_pending_full_semantic_review")
                self.assertTrue(r["read_only"])
                self.assertIn(r["context"], ("private", "direct", "group_addressed"))
                self.assertGreaterEqual(len(r["text"]), 75)
                self.assertGreaterEqual(len(r["context_note"]), 55)
                self.assertIn("без санкций", r["avoid"])
                self.assertFalse(re.search(
                    r"https?://|t\.me/|@[a-z_]|[0-9]{10,}",
                    r["text"] + r["context_note"], re.I
                ))
                note = normalized(r["context_note"])
                self.assertNotIn(note, notes)
                notes.add(note)
                norm = normalized(r["text"])
                self.assertNotIn(norm, norms)
                self.assertTrue(all(similarity(r["text"], old) < 0.70 for old in before), r["id"])
                before.append(r["text"])
                norms.add(norm)

if __name__ == "__main__":
    unittest.main()
