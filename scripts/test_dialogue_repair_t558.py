"""T558: context-bound RU continuation 61–80, full original lineage and scopes."""
import hashlib
import json
import subprocess
import unicodedata
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
PATHS=[ROOT/("staging/ru/dialogue_repair_t"+s+"_context_"+("pool" if s=="554" else "delta")+".json") for s in ["554","555","556","557","558"]]
def norm(s):
    return " ".join("".join(" " if unicodedata.category(c)[0] in {"P","S"} else c
        for c in unicodedata.normalize("NFKC",s).casefold().replace("ё","е")).split())
class DialogueRepair558(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.parts=[json.loads(p.read_text(encoding="utf-8")) for p in PATHS]
    def test_source_and_immutable_parent(self):
        d=self.parts[-1]
        manifest=json.loads((ROOT/"manifest.json").read_text(encoding="utf-8"))
        actual=hashlib.sha256((ROOT/d["source_pack"]).read_bytes()).hexdigest()
        self.assertEqual(d["source_pack_manifest_sha256"],actual)
        self.assertIn({"path":d["source_pack"],"sha256":actual},manifest["packs"])
        self.assertEqual(d["source_pack_blob_sha"],subprocess.check_output(["git","hash-object",d["source_pack"]],cwd=ROOT,text=True).strip())
        self.assertEqual(d["parent_stage"],str(PATHS[-2].relative_to(ROOT)))
        self.assertEqual(d["parent_stage_blob_sha"],subprocess.check_output(["git","hash-object",str(PATHS[-2])],cwd=ROOT,text=True).strip())
        for p in self.parts:
            self.assertFalse(p["consumer_registered"])
            self.assertEqual(p["audiences"],["all_ai_bots"])
            self.assertEqual(p["constraints"],d["constraints"])
            self.assertTrue(p["constraints"]["no_sanctions"])
            self.assertTrue(p["constraints"]["read_only"])
            self.assertTrue(p["constraints"]["requires_context_match"])
    def test_800_contextual_replies(self):
        grouped=[{e["intent_id"]:e for e in p["entries"]} for p in self.parts]
        self.assertEqual([len(x) for x in grouped],[10]*5)
        ids,txt,notes=set(),set(),set()
        for e in self.parts[-1]["entries"]:
            key=e["intent_id"]
            self.assertEqual([g[key]["canonical_question"] for g in grouped],[e["canonical_question"]]*5)
            self.assertEqual((e["prior_for_stable_id"],e["added_candidates"],e["total_staged"],e["target"],e["remaining"]),(60,20,80,100,20))
            self.assertEqual(len(e["replies"]),20)
            rs=[r for g in grouped for r in g[key]["replies"]]
            self.assertEqual(len(rs),80)
            for i,r in enumerate(rs,1):
                self.assertEqual(r["id"],f"{key}_{i:02d}")
                self.assertNotIn(r["id"],ids);ids.add(r["id"])
                for value,dest in [(r["text"],txt),(r["context_note"],notes)]:
                    v=norm(value);self.assertTrue(v);self.assertNotIn(v,dest);dest.add(v)
                self.assertEqual((r["read_only"],r["language"],r["audiences"],r["context"]),(True,"ru",["all_ai_bots"],"direct"))
        self.assertEqual((len(ids),len(txt),len(notes)),(800,800,800))
        c=self.parts[-1]["checkpoint"]
        self.assertEqual((c["prior_candidates"],c["added_candidates"],c["cumulative_candidates"],c["remaining_total"]),(600,200,800,200))
    def test_near_and_cross_stage_exact(self):
        lines=[r["text"] for d in self.parts for e in d["entries"] for r in e["replies"]]
        vectors=[set(norm(t).split()) for t in lines]
        for i,a in enumerate(vectors):
            for b in vectors[i+1:]:
                self.assertLess(len(a&b)/len(a|b),.78)
        current={norm(x) for x in lines}
        for path in (ROOT/"staging/ru").glob("*.json"):
            if path in PATHS:continue
            data=json.loads(path.read_text(encoding="utf-8"))
            if not isinstance(data,dict):continue
            for entry in data.get("entries",[]):
                if not isinstance(entry,dict):continue
                for reply in entry.get("replies",[]):
                    t=reply.get("text") if isinstance(reply,dict) else reply
                    if isinstance(t,str):self.assertNotIn(norm(t),current,f"cross-stage duplicate {path.name}")
if __name__=="__main__":unittest.main()
