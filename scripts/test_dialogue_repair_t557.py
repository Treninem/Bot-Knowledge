"""T557 160 context-bound originals, three immutable ancestors, cross-stage safety."""
import hashlib
import json
import subprocess
import unicodedata
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
PATHS=[ROOT/("staging/ru/dialogue_repair_t"+s+"_context_"+("pool" if s=="554" else "delta")+".json") for s in ["554","555","556","557"]]
def norm(s):
    return " ".join("".join(" " if unicodedata.category(c)[0] in {"P","S"} else c
        for c in unicodedata.normalize("NFKC",s).casefold().replace("ё","е")).split())
class DialogueRepair557(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.parts=[json.loads(p.read_text(encoding="utf-8")) for p in PATHS]
    def test_pinned_sources_and_scope(self):
        p=self.parts
        new=p[-1]
        manifest=json.loads((ROOT/"manifest.json").read_text(encoding="utf-8"))
        digest=hashlib.sha256((ROOT/new["source_pack"]).read_bytes()).hexdigest()
        self.assertIn({"path":new["source_pack"],"sha256":digest},manifest["packs"])
        self.assertEqual(new["source_pack_manifest_sha256"],digest)
        self.assertEqual(new["source_pack_blob_sha"],
          subprocess.check_output(["git","hash-object",new["source_pack"]],cwd=ROOT,text=True).strip())
        self.assertEqual(new["parent_stage"],str(PATHS[-2].relative_to(ROOT)))
        self.assertEqual(new["parent_stage_blob_sha"],
          subprocess.check_output(["git","hash-object",str(PATHS[-2])],cwd=ROOT,text=True).strip())
        for d in p:
            self.assertFalse(d["consumer_registered"])
            self.assertEqual(d["audiences"],["all_ai_bots"])
            self.assertEqual(d["constraints"],new["constraints"])
            self.assertTrue(d["constraints"]["no_sanctions"])
            self.assertTrue(d["constraints"]["read_only"])
            self.assertTrue(d["constraints"]["requires_context_match"])
    def test_600_exact_and_context_unique(self):
        d=self.parts
        by=[{e["intent_id"]:e for e in p["entries"]} for p in d]
        self.assertEqual(len(by[0]),len(by[1]),len(by[2]),len(by[3]),10)
        ids,txt,notes=set(),set(),set()
        for e in d[-1]["entries"]:
            k=e["intent_id"]
            self.assertEqual([x[k]["canonical_question"] for x in by],[e["canonical_question"]]*4)
            self.assertEqual((e["prior_for_stable_id"],e["added_candidates"],e["total_staged"],e["target"],e["remaining"]),(44,16,60,100,40))
            self.assertEqual(len(e["replies"]),16)
            rs=[r for lookup in by for r in lookup[k]["replies"]]
            self.assertEqual(len(rs),60)
            for i,r in enumerate(rs,1):
                self.assertEqual(r["id"],f"{k}_{i:02d}")
                self.assertNotIn(r["id"],ids)
                ids.add(r["id"])
                for raw,s in [(r["text"],txt),(r["context_note"],notes)]:
                    v=norm(raw)
                    self.assertTrue(v)
                    self.assertNotIn(v,s)
                    s.add(v)
                self.assertTrue(r["read_only"])
                self.assertEqual(r["language"],"ru")
                self.assertEqual(r["audiences"],["all_ai_bots"])
                self.assertEqual(r["context"],"direct")
        self.assertEqual((len(ids),len(txt),len(notes)),(600,600,600))
        c=d[-1]["checkpoint"]
        self.assertEqual((c["prior_candidates"],c["added_candidates"],c["cumulative_candidates"],c["partial_intents"],c["remaining_total"]),(440,160,600,10,400))
    def test_near_and_other_stages(self):
        texts=[r["text"] for d in self.parts for e in d["entries"] for r in e["replies"]]
        tokens=[set(norm(t).split()) for t in texts]
        for i,a in enumerate(tokens):
            for b in tokens[i+1:]:
                self.assertLess(len(a&b)/len(a|b),.78)
        normalized={norm(s) for s in texts}
        for path in (ROOT/"staging/ru").glob("*.json"):
            if path in PATHS: continue
            data=json.loads(path.read_text(encoding="utf-8"))
            if not isinstance(data,dict):continue
            for entry in data.get("entries",[]):
                if not isinstance(entry,dict):continue
                for r in entry.get("replies",[]):
                    s=r.get("text") if isinstance(r,dict) else r
                    if isinstance(s,str):self.assertNotIn(norm(s),normalized,f"duplicate in {path.name}")
if __name__=="__main__":
    unittest.main()
