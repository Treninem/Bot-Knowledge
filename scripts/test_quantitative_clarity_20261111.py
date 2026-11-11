"""Deterministic read-only QA for synthetic quantitative-clarity stage A."""
import hashlib
import json
import re
import unittest
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "staging/ru/quantitative_clarity_20261111_context_pool.json"
def norm(s):
    return " ".join(re.findall(r"[^\W_]+", s.casefold().replace("ё","е")))
def git_blob(raw):
    return hashlib.sha1(b"blob "+str(len(raw)).encode()+b"\0"+raw).hexdigest()
class QuantitativeClarityTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = json.loads(DATA.read_text(encoding="utf-8"))
    def test_source_and_isolation(self):
        d=self.data
        source=(ROOT/d["source_pack"]).read_bytes()
        manifest=json.loads((ROOT/"manifest.json").read_text(encoding="utf-8"))
        self.assertIn({"path":d["source_pack"],"sha256":hashlib.sha256(source).hexdigest()},manifest["packs"])
        self.assertEqual(d["source_pack_manifest_sha256"],hashlib.sha256(source).hexdigest())
        self.assertEqual(d["source_pack_blob_sha"],git_blob(source))
        self.assertFalse(d["consumer_registered"])
        self.assertNotIn("staging/ru/quantitative_clarity_20261111_context_pool.json",[x["path"] for x in manifest["packs"]])
        self.assertEqual(d["audiences"],["all_ai_bots"])
        self.assertTrue(all(d["constraints"].values()))
    def test_ids_metadata_privacy_and_duplicates(self):
        d=self.data
        self.assertEqual((len(d["entries"]),d["checkpoint"]["added_candidates"],d["checkpoint"]["remaining_total"]),(10,100,900))
        ids=set();texts=set();notes=set();sets=[]
        for entry in d["entries"]:
            self.assertEqual((entry["prior_for_stable_id"],entry["total_staged"],entry["remaining"]),(0,10,90))
            self.assertEqual(entry["audiences"],["all_ai_bots"])
            self.assertEqual(len(entry["replies"]),10)
            for i,r in enumerate(entry["replies"],1):
                self.assertEqual(r["id"],f'{entry["intent_id"]}_{i:02d}')
                self.assertNotIn(r["id"],ids); ids.add(r["id"])
                for key,target in (("text",texts),("context_note",notes)):
                    value=norm(r[key]);self.assertGreater(len(value),16);self.assertNotIn(value,target);target.add(value)
                self.assertEqual(r["context"],"direct");self.assertTrue(r["read_only"])
                self.assertIn("не применять санкции",r["avoid"])
                self.assertNotRegex(r["text"],r"(?i)[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,}")
                self.assertNotRegex(r["text"],r"\b(?:\+?\d[ -]?){11,}\b")
                sets.append(set(norm(r["text"]).split()))
        self.assertEqual((len(ids),len(texts),len(notes)),(100,100,100))
        for i,a in enumerate(sets):
            for b in sets[i+1:]:
                self.assertLess(len(a&b)/len(a|b),0.8)

    def test_stage_b_lineage_and_200_unique_replies(self):
        first=json.loads(DATA.read_text(encoding="utf-8"))
        second=json.loads((ROOT/"staging/ru/quantitative_clarity_20261111_context_delta_b.json").read_text(encoding="utf-8"))
        self.assertEqual(second["parent_stage"],"staging/ru/quantitative_clarity_20261111_context_pool.json")
        self.assertEqual(second["parent_stage_blob_sha"],git_blob(DATA.read_bytes()))
        for key in ("source_pack","source_pack_manifest_sha256","source_pack_blob_sha"):
            self.assertEqual(second[key],first[key])
        self.assertFalse(second["consumer_registered"])
        self.assertTrue(all(second["constraints"].values()))
        self.assertEqual((second["checkpoint"]["prior_candidates"],second["checkpoint"]["cumulative_candidates"],second["checkpoint"]["remaining_total"]),(100,200,800))
        self.assertEqual({e["intent_id"] for e in first["entries"]},{e["intent_id"] for e in second["entries"]})
        ids=set();texts=set();contexts=set();wordsets=[]
        for stage in (first,second):
            for entry in stage["entries"]:
                self.assertEqual(len(entry["replies"]),10)
                if stage is second:
                    self.assertEqual((entry["prior_for_stable_id"],entry["total_staged"],entry["remaining"]),(10,20,80))
                for j,r in enumerate(entry["replies"],11 if stage is second else 1):
                    self.assertEqual(r["id"],f'{entry["intent_id"]}_{j:02d}')
                    self.assertTrue(r["read_only"])
                    self.assertEqual(r["audiences"],["all_ai_bots"])
                    self.assertEqual(r["context"],"direct")
                    self.assertIn("не применять санкции",r["avoid"])
                    self.assertNotRegex(r["text"],r"(?i)[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,}")
                    for value,destination in ((r["id"],ids),(norm(r["text"]),texts),(norm(r["context_note"]),contexts)):
                        self.assertNotIn(value,destination)
                        destination.add(value)
                    wordsets.append(set(norm(r["text"]).split()))
        self.assertEqual((len(ids),len(texts),len(contexts)),(200,200,200))
        for i,left in enumerate(wordsets):
            for right in wordsets[i+1:]:
                self.assertLess(len(left&right)/len(left|right),.8)

if __name__ == "__main__":
    unittest.main()
