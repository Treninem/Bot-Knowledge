"""Read-only T555 exact delta and full T554→T555 original language verification."""
import hashlib
import json
import subprocess
import unicodedata
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/"staging/ru/dialogue_repair_t554_context_pool.json"
DELTA=ROOT/"staging/ru/dialogue_repair_t555_context_delta.json"

def norm(value):
    return " ".join("".join(" " if unicodedata.category(c)[0] in {"P","S"} else c
            for c in unicodedata.normalize("NFKC",value).casefold().replace("ё","е")).split())

class DialogueRepair555(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.base=json.loads(BASE.read_text(encoding="utf-8"))
        cls.delta=json.loads(DELTA.read_text(encoding="utf-8"))

    def test_chain_source_and_permissions(self):
        b,d=self.base,self.delta
        manifest=json.loads((ROOT/"manifest.json").read_text(encoding="utf-8"))
        raw=(ROOT/d["source_pack"]).read_bytes()
        digest=hashlib.sha256(raw).hexdigest()
        blob=subprocess.check_output(["git","hash-object",d["source_pack"]],cwd=ROOT,text=True).strip()
        stage_blob=subprocess.check_output(["git","hash-object",str(BASE)],cwd=ROOT,text=True).strip()
        self.assertIn({"path":d["source_pack"],"sha256":digest},manifest["packs"])
        self.assertEqual(d["source_pack_manifest_sha256"],digest)
        self.assertEqual(d["source_pack_blob_sha"],blob)
        self.assertEqual(d["parent_stage_blob_sha"],stage_blob)
        self.assertEqual(d["parent_stage"],str(BASE.relative_to(ROOT)))
        self.assertFalse(b["consumer_registered"])
        self.assertFalse(d["consumer_registered"])
        self.assertEqual(d["stage_type"],"supplemental_contextual_reply_delta")
        self.assertEqual(d["audiences"],["all_ai_bots"])
        self.assertEqual(d["constraints"],b["constraints"])
        self.assertTrue(d["constraints"]["no_sanctions"])
        self.assertTrue(d["constraints"]["read_only"])

    def test_stable_intents_and_240_unique_replies(self):
        b,d=self.base,self.delta
        old={e["intent_id"]:e for e in b["entries"]}
        self.assertEqual(len(old),10)
        self.assertEqual(len(d["entries"]),10)
        ids,txt,notes=set(),set(),set()
        for e in d["entries"]:
            ident=e["intent_id"]
            self.assertIn(ident,old)
            self.assertEqual(e["canonical_question"],old[ident]["canonical_question"])
            self.assertEqual((e["prior_for_stable_id"],e["added_candidates"],e["total_staged"],e["target"],e["remaining"]),(12,12,24,100,76))
            self.assertEqual(len(e["replies"]),12)
            combined=old[ident]["replies"]+e["replies"]
            self.assertEqual(len(combined),24)
            for i,r in enumerate(combined,1):
                self.assertEqual(r["id"],f"{ident}_{i:02d}")
                self.assertNotIn(r["id"],ids)
                ids.add(r["id"])
                for value,seen in ((r["text"],txt),(r["context_note"],notes)):
                    key=norm(value)
                    self.assertTrue(key)
                    self.assertNotIn(key,seen)
                    seen.add(key)
                self.assertTrue(r["read_only"])
                self.assertEqual(r["language"],"ru")
                self.assertEqual(r["audiences"],["all_ai_bots"])
                self.assertEqual(r["context"],"direct")
        self.assertEqual((len(ids),len(txt),len(notes)),(240,240,240))
        c=d["checkpoint"]
        self.assertEqual(c["prior_candidates"]+c["added_candidates"],240)
        self.assertEqual((c["cumulative_candidates"],c["finished_100"],c["partial_intents"],c["remaining_total"]),(240,0,10,760))

    def test_near_and_other_stage_dedup(self):
        b,d=self.base,self.delta
        texts=[r["text"] for e in b["entries"] for r in e["replies"]]
        texts.extend(r["text"] for e in d["entries"] for r in e["replies"])
        words=[set(norm(x).split()) for x in texts]
        for i,a in enumerate(words):
            for b in words[i+1:]:
                self.assertLess(len(a&b)/len(a|b),.78)
        normalized={norm(t) for t in texts}
        for path in (ROOT/"staging/ru").glob("*.json"):
            if path in (BASE,DELTA):continue
            other=json.loads(path.read_text(encoding="utf-8"))
            if not isinstance(other,dict):continue
            for entry in other.get("entries",[]):
                if not isinstance(entry,dict):continue
                for reply in entry.get("replies",[]):
                    value=reply.get("text") if isinstance(reply,dict) else reply
                    if isinstance(value,str):
                        self.assertNotIn(norm(value),normalized,f"cross-stage duplicate: {path.name}")

if __name__=="__main__":
    unittest.main()
