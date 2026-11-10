"""Read-only validation for T549 practical bot-help, five new scoped intents."""
import hashlib
import json
import re
import subprocess
import unicodedata
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
POOL = ROOT / "staging/ru/bot_help_t549_context_pool.json"

def norm(s):
    return " ".join("".join(" " if unicodedata.category(c)[0] in {"P","S"} else c
                for c in unicodedata.normalize("NFKC", s).casefold().replace("ё","е")).split())

class T549(unittest.TestCase):
    def test_stage_qa(self):
        p = json.loads(POOL.read_text(encoding="utf-8"))
        mf = json.loads((ROOT / "manifest.json").read_text(encoding="utf-8"))
        source = ROOT / p["source_pack"]
        digest = hashlib.sha256(source.read_bytes()).hexdigest()
        blob = subprocess.check_output(["git","hash-object",str(source)],cwd=ROOT,text=True).strip()
        self.assertIn({"path": p["source_pack"],"sha256":digest},mf["packs"])
        self.assertEqual((p["source_pack_manifest_sha256"],p["source_pack_blob_sha"]),(digest,blob))
        self.assertEqual((p["consumer_registered"],p["stage_type"],p["audiences"]),
                         (False,"supplemental_contextual_reply_pool",["all_ai_bots"]))
        self.assertEqual(len(p["entries"]),5)
        ids,texts,notes=set(),set(),set()
        for e in p["entries"]:
            self.assertEqual((e["prior_for_stable_id"],e["added_candidates"],e["total_staged"],e["remaining"]), (0,20,20,80))
            self.assertEqual(len(e["replies"]),20)
            for i,r in enumerate(e["replies"],1):
                self.assertEqual(r["id"],e["intent_id"]+"_%02d"%i)
                self.assertNotIn(r["id"],ids); ids.add(r["id"])
                self.assertTrue(r["read_only"])
                self.assertEqual(r["audiences"],["all_ai_bots"])
                self.assertEqual(r["context"],"direct")
                self.assertIn("адресации",r["avoid"])
                for val,seen in ((r["text"],texts),(r["context_note"],notes)):
                    k=norm(val); self.assertTrue(k); self.assertNotIn(k,seen); seen.add(k)
                self.assertNotRegex(r["text"].casefold(),r"\\b(?:я забанил|я замутил|я удалил|я настроил|я оплатил)\\b")
        self.assertEqual((len(ids),len(texts),len(notes)),(100,100,100))
        self.assertEqual((p["checkpoint"]["cumulative_candidates"],p["checkpoint"]["remaining_total"]), (100,400))
        # Scan staged replies outside this pool for exact matches without assuming every source shares this schema.
        for path in sorted((ROOT/"staging/ru").glob("*.json")):
            if path==POOL: continue
            other=json.loads(path.read_text(encoding="utf-8"))
            if not isinstance(other,dict): continue
            for entry in other.get("entries",[]):
                if not isinstance(entry,dict): continue
                for item in entry.get("replies",[]):
                    val=item.get("text") if isinstance(item,dict) else item
                    if isinstance(val,str):
                        self.assertNotIn(norm(val),texts,"Cross-pool duplicate in "+path.name)

if __name__ == "__main__":
    unittest.main()
