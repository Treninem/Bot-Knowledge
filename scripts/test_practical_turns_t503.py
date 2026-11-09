"""T503 independent universal practical-language candidate pool (read-only)."""
import hashlib
import json
import re
import unicodedata
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
STAGE=ROOT/"staging/ru/practical_turns_t503_context_pool.json"
SOURCE=ROOT/"packs/ru/dialogue.json"
SOURCE_SHA="3e63012f2823ea1896e9d9612f68f19a3cf2fe6bbf2c8296fc98ac29fb18a024"
SOURCE_BLOB="b881d145f634b6104c8538fef708d45162ef3125"
def blob(raw):
    return hashlib.sha1(b"blob "+str(len(raw)).encode()+b"\0"+raw).hexdigest()
def norm(t):
    return " ".join(re.findall(r"\w+", unicodedata.normalize("NFKC", t).lower().replace("ё","е")))
def strings(v):
    if isinstance(v,list):
        for x in v: yield from strings(x)
    elif isinstance(v,dict):
        for k,x in v.items():
            if k in {"text","answer","reply","response"} and isinstance(x,str): yield x
            else: yield from strings(x)
class T503Tests(unittest.TestCase):
    def test_schema_lineage_and_scope(self):
        s=json.loads(STAGE.read_text("utf-8"))
        raw=SOURCE.read_bytes()
        manifest=json.loads((ROOT/"manifest.json").read_text("utf-8"))
        self.assertEqual(hashlib.sha256(raw).hexdigest(),SOURCE_SHA)
        self.assertEqual(blob(raw),SOURCE_BLOB)
        self.assertIn({"path":"packs/ru/dialogue.json","sha256":SOURCE_SHA},manifest["packs"])
        self.assertEqual(s["source_pack_manifest_sha256"],SOURCE_SHA)
        self.assertEqual(s["source_pack_blob_sha"],SOURCE_BLOB)
        self.assertEqual(s["checkpoint"]["stage_id"],"T503")
        self.assertFalse(s["consumer_registered"])
        self.assertEqual(s["audiences"],["all_ai_bots"])
        self.assertTrue(s["constraints"]["read_only"])
        self.assertTrue(s["constraints"]["requires_context_match"])
        self.assertEqual(len(s["entries"]),10)
        self.assertEqual(sum(len(e["replies"]) for e in s["entries"]),100)
        self.assertEqual(len({e["intent_id"] for e in s["entries"]}),10)
        for e in s["entries"]:
            self.assertEqual((e["prior_for_stable_id"],e["added_candidates"],e["target"],e["total_staged"],e["remaining"]),(0,10,100,10,90))
    def test_privacy_and_cross_stage_originality(self):
        s=json.loads(STAGE.read_text("utf-8"))
        history=set()
        for d in ("packs/ru","staging/ru"):
            for p in (ROOT/d).glob("*.json"):
                if p==STAGE:continue
                history.update(norm(t) for t in strings(json.loads(p.read_text("utf-8"))) if t.strip())
        history.discard("")
        ids=set();notes=set()
        for e in s["entries"]:
            for v in e["replies"]:
                self.assertNotIn(v["id"],ids);ids.add(v["id"])
                self.assertEqual(v["language"],"ru")
                self.assertEqual(v["audiences"],["all_ai_bots"])
                self.assertTrue(v["read_only"])
                self.assertTrue(v["context_note"])
                self.assertNotIn(norm(v["context_note"]),notes)
                notes.add(norm(v["context_note"]))
                self.assertFalse(re.search(r"(?i)(ghp_[a-z0-9]{12,}|sk-[a-z0-9]{12,}|https?://|@[a-z0-9_]+)",v["text"]))
                self.assertFalse(re.search(r"(?i)\b(забань|замуть|заблокируй пользователя|удали чужое сообщение)\b",v["text"]))
                n=norm(v["text"]);self.assertNotIn(n,history,v["id"])
                t=set(n.split())
                for old in history:
                    if abs(len(t)-len(old.split()))>10:continue
                    o=set(old.split());j=len(t&o)/len(t|o)
                    self.assertLess(j,.78,v["id"])
                history.add(n)
        self.assertEqual(len(ids),100)
if __name__=="__main__":unittest.main()
