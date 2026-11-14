"""H1: ImPULS contextual FAQ stage, read-only and not consumer published."""
import hashlib
import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STAGE = ROOT / "staging/ru/impuls_help_context_h1_20261114.json"
SOURCE = ROOT / "packs/ru/impuls_help_qa.json"

def norm(s):
    return " ".join(re.findall(r"[^\W_]+", s.casefold().replace("ё", "е")))

class ContextHelpH1(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.stage = json.loads(STAGE.read_text(encoding="utf-8"))
        cls.source = json.loads(SOURCE.read_text(encoding="utf-8"))
        cls.manifest = json.loads((ROOT / "manifest.json").read_text(encoding="utf-8"))

    def test_isolation_source_and_real_bytes(self):
        s=self.stage
        self.assertFalse(s["consumer_registered"])
        registered={v["path"]:v["sha256"] for v in self.manifest["packs"]}
        self.assertNotIn(STAGE.relative_to(ROOT).as_posix(),registered)
        self.assertEqual(s["source_pack_manifest_sha256"], registered[s["source_pack"]])
        self.assertEqual(hashlib.sha256(SOURCE.read_bytes()).hexdigest(),registered[s["source_pack"]])
        self.assertLess(STAGE.stat().st_size,2*1024*1024)
        self.assertTrue(all(s["constraints"].values()))

    def test_counts_scope_and_unique_ids(self):
        s=self.stage
        es=s["entries"]
        self.assertEqual((len(es),sum(len(e["replies"]) for e in es)),(15,45))
        self.assertEqual((s["checkpoint"]["newly_editorially_approved"],s["checkpoint"]["approved_sets_at_100"]),(0,0))
        src={x["id"]:x for x in self.source["records"]}
        ids=set()
        texts=set()
        for e in es:
            old=src[e["intent_id"]]
            self.assertEqual(e["canonical_question"],old["question"])
            self.assertEqual(e["published_count"],1+len(old["variants"]))
            self.assertEqual(e["total_candidates_in_main_and_this_stage"],e["published_count"]+3)
            self.assertEqual(e["remaining_to_target_excluding_other_prs"],100-e["published_count"]-3)
            for v in e["replies"]:
                self.assertNotIn(v["id"],ids)
                ids.add(v["id"])
                t=norm(v["text"])
                self.assertNotIn(t,texts)
                texts.add(t)
                self.assertEqual(v["editorial_status"],"candidate_pending_full_semantic_review")
                self.assertEqual(v["audiences"],["impuls"])
                self.assertTrue(v["read_only"])
                self.assertIn(v["context"],("direct","private","group_addressed"))
                self.assertIn("совпадении условий",v["avoid"])
                self.assertGreater(len(v["context_note"]),34)

    def test_no_exact_published_overlap(self):
        all_published={norm(t) for e in self.source["records"] for t in [e["answer"],*e["variants"]]}
        for e in self.stage["entries"]:
            for v in e["replies"]:
                self.assertNotIn(norm(v["text"]),all_published)
                self.assertNotIn("@",v["text"])

if __name__=="__main__":
    unittest.main()
