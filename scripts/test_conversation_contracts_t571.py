"""T571 stable-intent continuation: 200 candidates, source chain, context isolation."""
import hashlib
import json
import re
import subprocess
import unittest
from pathlib import Path
from scripts.test_conversation_contracts_t570 import norm, candidate_texts

ROOT=Path(__file__).resolve().parents[1]
FILES=["staging/ru/conversation_contracts_t570_context_pool.json",
       "staging/ru/conversation_contracts_t571_context_delta.json"]

class TestT571(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.stages=[json.loads((ROOT/p).read_text(encoding="utf-8")) for p in FILES]
        cls.rows=[r for d in cls.stages for e in d["entries"] for r in e["replies"]]

    def test_provenance_and_chain(self):
        first,second=self.stages
        manifest=json.loads((ROOT/"manifest.json").read_text(encoding="utf-8"))
        src=first["source_pack"]
        digest=hashlib.sha256((ROOT/src).read_bytes()).hexdigest()
        blob=subprocess.check_output(["git","hash-object",src],cwd=ROOT,text=True).strip()
        self.assertIn({"path":src,"sha256":digest},manifest["packs"])
        for d in self.stages:
            self.assertEqual((d["source_pack_manifest_sha256"],d["source_pack_blob_sha"]),(digest,blob))
            self.assertFalse(d["consumer_registered"])
            self.assertEqual((d["language"],d["audiences"]),("ru",["all_ai_bots"]))
            for k in ("read_only","requires_context_match","no_sanctions","no_personal_data","requires_direct_address"):
                self.assertTrue(d["constraints"][k])
        old_blob=subprocess.check_output(["git","hash-object",FILES[0]],cwd=ROOT,text=True).strip()
        self.assertEqual((second["parent_stage"],second["parent_stage_blob_sha"]),(FILES[0],old_blob))

    def test_200_unique_context_bound_responses(self):
        a,b=self.stages
        self.assertEqual((len(a["entries"]),len(b["entries"]),len(self.rows)),(10,10,200))
        self.assertEqual([(e["intent_id"],e["canonical_question"]) for e in a["entries"]],
                         [(e["intent_id"],e["canonical_question"]) for e in b["entries"]])
        self.assertEqual((b["checkpoint"]["prior_candidates"],b["checkpoint"]["added_candidates"],
                          b["checkpoint"]["cumulative_candidates"],b["checkpoint"]["remaining_total"]),(100,100,200,800))
        ids=set();texts=set();contexts=set()
        for stage_index,d in enumerate(self.stages):
            for e in d["entries"]:
                self.assertEqual((e["prior_for_stable_id"],e["added_candidates"],e["total_staged"],e["target"],e["remaining"]),
                                 (stage_index*10,10,(stage_index+1)*10,100,90-stage_index*10))
                for index,r in enumerate(e["replies"],stage_index*10+1):
                    self.assertEqual(r["id"],f"{e['intent_id']}_{index:02d}")
                    self.assertNotIn(r["id"],ids);ids.add(r["id"])
                    for value,seen in ((r["text"],texts),(r["context_note"],contexts)):
                        v=norm(value);self.assertTrue(v)
                        self.assertNotIn(v,seen,r["id"]);seen.add(v)
                    self.assertTrue(r["read_only"])
                    self.assertEqual((r["language"],r["context"],r["audiences"]),("ru","direct",["all_ai_bots"]))
                    self.assertFalse(re.search(r"[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}",r["text"]))
        self.assertEqual((len(ids),len(texts),len(contexts)),(200,200,200))

    def test_not_lexical_swaps_or_external_exact_copies(self):
        tokens=[set(norm(r["text"]).split()) for r in self.rows]
        for i,a in enumerate(tokens):
            for b in tokens[i+1:]:
                self.assertLess(len(a&b)/len(a|b),.78,self.rows[i]["id"])
        fresh={norm(r["text"]) for r in self.stages[1]["entries"] for r in r["replies"]}
        stage_files={(ROOT/p).resolve() for p in FILES}
        for path in (ROOT/"staging/ru").glob("*.json"):
            if path.resolve() in stage_files:continue
            obj=json.loads(path.read_text(encoding="utf-8"))
            for text in candidate_texts(obj):
                self.assertNotIn(norm(text),fresh,str(path))

if __name__=="__main__":unittest.main()
