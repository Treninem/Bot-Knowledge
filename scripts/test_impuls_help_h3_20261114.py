"""ImPULS H3 candidate QA; no consumer registration or mod sanctions."""
import hashlib
import json
import re
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
STAGE=ROOT/"staging/ru/impuls_help_context_h3_20261114.json"
SOURCE=ROOT/"packs/ru/impuls_help_qa.json"
EARLIER=[ROOT/"staging/ru/impuls_help_context_h1_20261114.json",ROOT/"staging/ru/impuls_help_context_h2_20261114.json"]

def norm(s):
    return " ".join(re.findall(r"[^\W_]+",s.casefold().replace("ё","е")))

class HelpH3(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.stage=json.loads(STAGE.read_text(encoding="utf-8"))
        cls.source=json.loads(SOURCE.read_text(encoding="utf-8"))
        cls.manifest=json.loads((ROOT/"manifest.json").read_text(encoding="utf-8"))
        cls.older=[json.loads(f.read_text(encoding="utf-8")) for f in EARLIER]

    def test_manifest_and_no_live_delivery(self):
        m={v["path"]:v["sha256"] for v in self.manifest["packs"]}
        self.assertNotIn(STAGE.relative_to(ROOT).as_posix(),m)
        self.assertEqual(self.stage["source_pack_manifest_sha256"],m[self.stage["source_pack"]])
        self.assertEqual(hashlib.sha256(SOURCE.read_bytes()).hexdigest(),m[self.stage["source_pack"]])
        self.assertFalse(self.stage["consumer_registered"])
        self.assertTrue(all(self.stage["constraints"].values()))
        self.assertLess(STAGE.stat().st_size,2*1024*1024)

    def test_counts_context_and_id_scope(self):
        entries=self.stage["entries"]
        self.assertEqual((len(entries),sum(len(e["replies"]) for e in entries)),(15,45))
        self.assertEqual((self.stage["checkpoint"]["aggregate_new_in_H1_H2_H3"],self.stage["checkpoint"]["distinct_intents_in_H1_H2_H3"]),(135,45))
        before={e["intent_id"] for stage in self.older for e in stage["entries"]}
        self.assertFalse(before.intersection(e["intent_id"] for e in entries))
        published={e["id"]:e for e in self.source["records"]}
        ids=set()
        for e in entries:
            self.assertEqual(e["canonical_question"],published[e["intent_id"]]["question"])
            self.assertEqual(e["published_count"],1+len(published[e["intent_id"]]["variants"]))
            self.assertEqual(e["remaining_to_target_excluding_other_prs"],100-e["published_count"]-3)
            for v in e["replies"]:
                self.assertNotIn(v["id"],ids)
                ids.add(v["id"])
                self.assertEqual(v["audiences"],["impuls"])
                self.assertEqual(v["editorial_status"],"candidate_pending_full_semantic_review")
                self.assertTrue(v["read_only"])
                self.assertGreater(len(v["context_note"]),33)
                self.assertIn("прямом вопросе",v["avoid"])
                self.assertIn(v["context"],("direct","private","group_addressed"))

    def test_no_exact_normalized_overlap(self):
        seen={norm(t) for e in self.source["records"] for t in [e["answer"],*e["variants"]]}
        seen.update(norm(v["text"]) for stage in self.older for e in stage["entries"] for v in e["replies"])
        for e in self.stage["entries"]:
            for v in e["replies"]:
                t=norm(v["text"])
                self.assertNotIn(t,seen)
                seen.add(t)
                self.assertNotIn("@",v["text"])

if __name__=="__main__":
    unittest.main()
