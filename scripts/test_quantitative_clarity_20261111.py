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
if __name__ == "__main__":
    unittest.main()
