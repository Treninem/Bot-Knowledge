"""Read-only exact QA for staged prompt-literacy A–H responses."""
from __future__ import annotations
import hashlib
import json
import re
import unicodedata
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
STAGES=["staging/ru/prompt_literacy_20261111_context_pool.json"] + [
    f"staging/ru/prompt_literacy_20261111_context_delta_{suffix}.json"
    for suffix in "bcdefgh"
]
TOKENS=re.compile(r"[^\W_]+",re.UNICODE)
def normalize(t):
    return " ".join(TOKENS.findall(unicodedata.normalize("NFKC",t).casefold().replace("ё","е")))
def blob(data):
    return hashlib.sha1(b"blob "+str(len(data)).encode()+b"\0"+data).hexdigest()

class Continuation(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.raw=[(ROOT/path).read_bytes() for path in STAGES]
        cls.data=[json.loads(b) for b in cls.raw]
        cls.replies=[r for s in cls.data for e in s["entries"] for r in e["replies"]]
    def test_provenance(self):
        manifest=json.loads((ROOT/"manifest.json").read_text("utf-8"))
        source=(ROOT/self.data[0]["source_pack"]).read_bytes()
        sha=hashlib.sha256(source).hexdigest()
        expected={x["path"]:x["sha256"] for x in manifest["packs"]}
        self.assertEqual(manifest["knowledge_version"],"2026.11.09.003")
        self.assertEqual(expected[self.data[0]["source_pack"]],sha)
        for i,s in enumerate(self.data):
            self.assertIs(s["consumer_registered"],False)
            self.assertEqual(s["audiences"],["all_ai_bots"])
            self.assertEqual(s["source_pack_manifest_sha256"],sha)
            self.assertEqual(s["source_pack_blob_sha"],blob(source))
            self.assertNotIn(STAGES[i],expected)
            for k in ("read_only","no_personal_data","no_sanctions","requires_context_match","requires_direct_address"):
                self.assertIs(s["constraints"][k],True)
            if i:
                self.assertEqual(s["parent_stage_blob_sha"],blob(self.raw[i-1]))
    def test_counts(self):
        self.assertEqual(len(self.replies),800)
        ids=[e["intent_id"] for e in self.data[0]["entries"]]
        self.assertEqual(len(set(ids)),10)
        for i,s in enumerate(self.data):
            self.assertEqual([e["intent_id"] for e in s["entries"]],ids)
            self.assertEqual(s["checkpoint"]["prior_candidates"],i*100)
            self.assertEqual(s["checkpoint"]["added_candidates"],100)
            self.assertEqual(s["checkpoint"]["cumulative_candidates"],(i+1)*100)
            self.assertEqual(s["checkpoint"]["remaining_total"],1000-(i+1)*100)
            for e in s["entries"]:
                self.assertEqual(e["prior_for_stable_id"],i*10)
                self.assertEqual(e["total_staged"],(i+1)*10)
                self.assertEqual(e["remaining"],100-(i+1)*10)
                self.assertEqual(len(e["replies"]),10)
                for n,r in enumerate(e["replies"],i*10+1):
                    self.assertEqual(r["id"],f'{e["intent_id"]}_{n:02}')
                    self.assertEqual(r["language"],"ru")
                    self.assertEqual(r["context"],"direct")
                    self.assertEqual(r["audiences"],["all_ai_bots"])
                    self.assertTrue(r["read_only"])
                    self.assertIn("не применять санкции",r["avoid"])
                    self.assertGreaterEqual(len(r["text"]),45)
                    self.assertGreaterEqual(len(r["context_note"]),18)
    def test_unique_quality_and_privacy(self):
        for k in ("id","text","context_note"):
            vals=[r[k] if k=="id" else normalize(r[k]) for r in self.replies]
            self.assertEqual(len(set(vals)),800,k)
        tokens=[set(normalize(r["text"]).split()) for r in self.replies]
        for i,a in enumerate(tokens):
            for b in tokens[i+1:]:
                self.assertLess(len(a&b)/len(a|b),0.80,self.replies[i]["id"])
        for r in self.replies:
            self.assertNotRegex(r["text"],r"(?i)[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,}")
            self.assertNotIn("ghp_",r["text"])
            self.assertNotRegex(r["text"],r"(?i)(?:я|бот) (?:забанил|замутил|отправил сообщение|изменил настройки)")
    def test_registered_overlap(self):
        manifest=json.loads((ROOT/"manifest.json").read_text("utf-8"))
        seen=set()
        for p in manifest["packs"]:
            obj=json.loads((ROOT/p["path"]).read_text("utf-8"))
            if isinstance(obj,dict):
                for record in obj.get("records",[]):
                    if isinstance(record,dict):
                        for v in [record.get("answer"),*(record.get("variants",[]) or [])]:
                            if isinstance(v,str):seen.add(normalize(v))
        self.assertTrue(seen)
        for r in self.replies:self.assertNotIn(normalize(r["text"]),seen)
if __name__=="__main__":unittest.main()
