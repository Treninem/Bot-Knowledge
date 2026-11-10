"""T593–T594: test context-bound interpersonal data against registered source and prior stages."""
import hashlib
import json
import re
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STAGES = [f"staging/ru/interpersonal_t{n}_context_{'pool' if n == 590 else 'delta'}.json" for n in range(590, 597)]
# Note: stage 590 uses context_pool, and all subsequent stages context_delta.
def normalize(s):
    return " ".join(re.findall(r"[^\W_]+", s.casefold().replace("ё", "е")))
def git_blob(path):
    return subprocess.check_output(["git", "hash-object", path], cwd=ROOT, text=True).strip()

class TestInterpersonalContinuation(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.docs = [json.loads((ROOT / p).read_text(encoding="utf-8")) for p in STAGES]
    def test_source_and_chain(self):
        m = json.loads((ROOT / "manifest.json").read_text(encoding="utf-8"))
        first = self.docs[0]
        sha = hashlib.sha256((ROOT / first["source_pack"]).read_bytes()).hexdigest()
        self.assertEqual(sha, first["source_pack_manifest_sha256"])
        self.assertIn({"path": first["source_pack"], "sha256": sha}, m["packs"])
        self.assertEqual(git_blob(first["source_pack"]), first["source_pack_blob_sha"])
        for index, d in enumerate(self.docs):
            self.assertFalse(d["consumer_registered"])
            self.assertEqual((d["language"], d["audiences"]), ("ru", ["all_ai_bots"]))
            for flag in ("read_only","no_sanctions","requires_context_match","no_personal_data","requires_direct_address"):
                self.assertTrue(d["constraints"][flag])
            for key in ("source_pack", "source_pack_blob_sha", "source_pack_manifest_sha256","checked_source_main_sha","scope"):
                self.assertEqual(d[key], first[key])
            if index:
                self.assertEqual(d["parent_stage"], STAGES[index-1])
                self.assertEqual(d["parent_stage_blob_sha"], git_blob(STAGES[index-1]))
    def test_counts_and_distinctness(self):
        seen_id, seen_text, seen_note = set(), set(), set()
        vector = []
        roles = {e["intent_id"]: e["response_role"] for e in self.docs[0]["entries"]}
        for idx, doc in enumerate(self.docs):
            start, count = [(1,12), (13,8), (21,10), (31,10), (41,10), (51,10), (61,10)][idx]
            self.assertEqual(len(doc["entries"]), 10)
            self.assertEqual(doc["checkpoint"]["cumulative_candidates"], [120,200,300,400,500,600,700][idx])
            self.assertEqual(doc["checkpoint"]["remaining_total"], [880,800,700,600,500,400,300][idx])
            self.assertEqual({e["intent_id"] for e in doc["entries"]}, set(roles))
            for e in doc["entries"]:
                self.assertEqual(e["response_role"], roles[e["intent_id"]])
                self.assertEqual((e["prior_for_stable_id"], e["added_candidates"], e["total_staged"], e["target"], e["remaining"]),tuple(([0,12,12,100,88],[12,8,20,100,80],[20,10,30,100,70],[30,10,40,100,60],[40,10,50,100,50],[50,10,60,100,40],[60,10,70,100,30])[idx]))
                self.assertEqual(len(e["replies"]), count)
                for offset, r in enumerate(e["replies"]):
                    self.assertEqual(r["id"], f'{e["intent_id"]}_{start+offset:02d}')
                    self.assertEqual((r["language"],r["audiences"],r["read_only"],r["context"]),("ru",["all_ai_bots"],True,"direct"))
                    self.assertIn("совпадении контекста",r["avoid"])
                    self.assertFalse(re.search(r"(?i)https?://|@[a-z0-9_]+|\b\+?\d[\d -]{7,}\d\b",r["text"]))
                    for v,s in ((r["id"],seen_id),(normalize(r["text"]),seen_text),(normalize(r["context_note"]),seen_note)):
                        self.assertTrue(v)
                        self.assertNotIn(v,s)
                        s.add(v)
                    vector.append(set(normalize(r["text"]).split()))
        self.assertEqual((len(seen_id),len(seen_text),len(seen_note)),(700,700,700))
        for i,a in enumerate(vector):
            for b in vector[i+1:]:
                self.assertLess(len(a&b)/len(a|b), .8)

if __name__ == "__main__":
    unittest.main()
