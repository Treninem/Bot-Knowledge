"""Read-only QA for original RU evidence-bound reasoning stage A."""
from __future__ import annotations
import hashlib,json,re,unicodedata,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/"staging/ru/reasoning_risks_20261111_context_pool.json"
NORMAL=re.compile(r"[^\W_]+",re.UNICODE)
def norm(t):
    return " ".join(NORMAL.findall(unicodedata.normalize("NFKC",t).casefold().replace("ё","е")))
def gitblob(b):
    return hashlib.sha1(b"blob "+str(len(b)).encode()+b"\0"+b).hexdigest()
class ReasoningStage(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.obj=json.loads(SOURCE.read_bytes())
        cls.replies=[r for e in cls.obj["entries"] for r in e["replies"]]
    def test_provenance(self):
        s=self.obj
        m=json.loads((ROOT/"manifest.json").read_text("utf-8"))
        src=(ROOT/s["source_pack"]).read_bytes()
        sha=hashlib.sha256(src).hexdigest()
        hashes={x["path"]:x["sha256"] for x in m["packs"]}
        self.assertEqual(sha,s["source_pack_manifest_sha256"])
        self.assertEqual(sha,hashes[s["source_pack"]])
        self.assertEqual(gitblob(src),s["source_pack_blob_sha"])
        self.assertNotIn(str(SOURCE.relative_to(ROOT)),hashes)
        self.assertIs(s["consumer_registered"],False)
        self.assertEqual(s["audiences"],["all_ai_bots"])
        for key in ("read_only","requires_direct_address","no_personal_data","no_sanctions","requires_context_match"):
            self.assertIs(s["constraints"][key],True)
    def test_counts_and_scope(self):
        s=self.obj
        self.assertEqual(len(s["entries"]),10)
        self.assertEqual(len(self.replies),100)
        self.assertEqual(s["checkpoint"]["prior_candidates"],0)
        self.assertEqual(s["checkpoint"]["cumulative_candidates"],100)
        self.assertEqual(s["checkpoint"]["remaining_total"],900)
        for e in s["entries"]:
            self.assertEqual(len(e["replies"]),10)
            self.assertEqual(e["total_staged"],10)
            self.assertEqual(e["remaining"],90)
            self.assertEqual(e["target"],100)
            for n,r in enumerate(e["replies"],1):
                self.assertEqual(r["id"],f'{e["intent_id"]}_{n:02}')
                self.assertEqual(r["language"],"ru")
                self.assertEqual(r["context"],"direct")
                self.assertEqual(r["audiences"],["all_ai_bots"])
                self.assertTrue(r["read_only"])
                self.assertIn("не применять санкции",r["avoid"])
                self.assertGreaterEqual(len(r["text"]),70)
                self.assertGreaterEqual(len(r["context_note"]),23)
    def test_uniqueness_and_privacy(self):
        rs=self.replies
        for k in ("id","text","context_note"):
            vals=[r[k] if k=="id" else norm(r[k]) for r in rs]
            self.assertEqual(len(vals),len(set(vals)),k)
        tokens=[set(norm(r["text"]).split()) for r in rs]
        for i,a in enumerate(tokens):
            for b in tokens[i+1:]:
                self.assertLess(len(a&b)/len(a|b),0.8,rs[i]["id"])
        for r in rs:
            self.assertNotRegex(r["text"],r"(?i)[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,}")
            self.assertNotIn("ghp_",r["text"])
            self.assertNotRegex(norm(r["text"]),r"\b(?:я|бот) (?:забанил|замутил|удалил сообщение)\b")
    def test_against_registered_answers(self):
        manifest=json.loads((ROOT/"manifest.json").read_text("utf-8"))
        old=set()
        for pack in manifest["packs"]:
            o=json.loads((ROOT/pack["path"]).read_text("utf-8"))
            def walk(v):
                if isinstance(v,dict):
                    for k,x in v.items():
                        if k in ("answer","response","text") and isinstance(x,str):old.add(norm(x))
                        elif isinstance(x,(dict,list)):walk(x)
                elif isinstance(v,list):
                    for x in v:walk(x)
            walk(o)
        self.assertFalse(old.intersection(norm(r["text"]) for r in self.replies))
if __name__=="__main__":
    unittest.main()
