"""T572 cumulative regression: stable intents, SHA parents, 300 unique safe replies."""
import hashlib
import json
import subprocess
import unittest
from pathlib import Path
from scripts.test_conversation_contracts_t570 import norm, candidate_texts

ROOT=Path(__file__).resolve().parents[1]
FILES=["staging/ru/conversation_contracts_t570_context_pool.json",
       "staging/ru/conversation_contracts_t571_context_delta.json",
       "staging/ru/conversation_contracts_t572_context_delta.json"]

class TestT572(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.stages=[json.loads((ROOT/p).read_text(encoding="utf-8")) for p in FILES]
        cls.replies=[r for d in cls.stages for e in d["entries"] for r in e["replies"]]

    def test_source_chain_and_privacy_boundary(self):
        src=self.stages[0]["source_pack"]
        manifest=json.loads((ROOT/"manifest.json").read_text(encoding="utf-8"))
        digest=hashlib.sha256((ROOT/src).read_bytes()).hexdigest()
        blob=subprocess.check_output(["git","hash-object",src],cwd=ROOT,text=True).strip()
        self.assertIn({"path":src,"sha256":digest},manifest["packs"])
        for i,d in enumerate(self.stages):
            self.assertEqual((d["source_pack_manifest_sha256"],d["source_pack_blob_sha"]),(digest,blob))
            self.assertEqual((d["language"],d["audiences"],d["consumer_registered"]),("ru",["all_ai_bots"],False))
            for k in ("no_sanctions","read_only","requires_context_match","requires_direct_address","no_personal_data"):
                self.assertTrue(d["constraints"][k])
            if i:
                parent_blob=subprocess.check_output(["git","hash-object",FILES[i-1]],cwd=ROOT,text=True).strip()
                self.assertEqual((d["parent_stage"],d["parent_stage_blob_sha"]),(FILES[i-1],parent_blob))

    def test_300_unique_and_consistent_intents(self):
        self.assertEqual((len(self.stages),len(self.replies)),(3,300))
        origin=[(e["intent_id"],e["canonical_question"]) for e in self.stages[0]["entries"]]
        ids=set();textkeys=set();notes=set()
        for i,d in enumerate(self.stages):
            self.assertEqual([(e["intent_id"],e["canonical_question"]) for e in d["entries"]],origin)
            cp=d["checkpoint"]
            self.assertEqual((cp["prior_candidates"],cp["added_candidates"],cp["cumulative_candidates"],cp["remaining_total"]), (i*100,100,(i+1)*100,1000-(i+1)*100))
            self.assertEqual((cp["finished_100"],cp["partial_intents"]), (0,10))
            for e in d["entries"]:
                self.assertEqual((e["prior_for_stable_id"],e["added_candidates"],e["total_staged"],e["target"],e["remaining"]), (i*10,10,(i+1)*10,100,90-i*10))
                self.assertEqual(len(e["replies"]),10)
                for j,r in enumerate(e["replies"],i*10+1):
                    self.assertEqual(r["id"],f"{e['intent_id']}_{j:02d}")
                    self.assertNotIn(r["id"],ids);ids.add(r["id"])
                    for field,target in ((r["text"],textkeys),(r["context_note"],notes)):
                        key=norm(field);self.assertTrue(key)
                        self.assertNotIn(key,target,r["id"]);target.add(key)
                    self.assertEqual((r["audiences"],r["context"],r["read_only"]),(["all_ai_bots"],"direct",True))
                    self.assertIn("контексте",r["avoid"])
        self.assertEqual((len(ids),len(textkeys),len(notes)),(300,300,300))

    def test_lexical_distance_and_external_exact_duplicates(self):
        vectors=[set(norm(r["text"]).split()) for r in self.replies]
        for i,a in enumerate(vectors):
            for b in vectors[i+1:]:
                self.assertLess(len(a&b)/len(a|b),.78,self.replies[i]["id"])
        stage_files={(ROOT/p).resolve() for p in FILES}
        added={norm(r["text"]) for e in self.stages[2]["entries"] for r in e["replies"]}
        for path in (ROOT/"staging/ru").glob("*.json"):
            if path.resolve() in stage_files:continue
            obj=json.loads(path.read_text(encoding="utf-8"))
            for t in candidate_texts(obj):
                self.assertNotIn(norm(t),added,str(path))

if __name__=="__main__":unittest.main()
