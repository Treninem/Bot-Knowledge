"""T554 read-only dialogue-repair candidate verification; no consumer actions."""
import hashlib
import json
import re
import subprocess
import unicodedata
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PATH = ROOT / "staging/ru/dialogue_repair_t554_context_pool.json"

def norm(value):
    return " ".join("".join(" " if unicodedata.category(c)[0] in {"P","S"} else c
                 for c in unicodedata.normalize("NFKC", value).casefold().replace("ё","е")).split())

class DialogueRepair554(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pool = json.loads(PATH.read_text(encoding="utf-8"))

    def test_source_and_scope(self):
        p=self.pool
        manifest=json.loads((ROOT/"manifest.json").read_text(encoding="utf-8"))
        raw=(ROOT/p["source_pack"]).read_bytes()
        sha=hashlib.sha256(raw).hexdigest()
        blob=subprocess.check_output(["git","hash-object",p["source_pack"]],cwd=ROOT,text=True).strip()
        self.assertIn({"path":p["source_pack"],"sha256":sha},manifest["packs"])
        self.assertEqual(p["source_pack_manifest_sha256"],sha)
        self.assertEqual(p["source_pack_blob_sha"],blob)
        self.assertFalse(p["consumer_registered"])
        self.assertEqual(p["stage_type"],"supplemental_contextual_reply_pool")
        self.assertEqual(p["language"],"ru")
        self.assertEqual(p["audiences"],["all_ai_bots"])
        self.assertEqual(p["constraints"],{"read_only":True,"requires_direct_address":True,
            "no_personal_data":True,"no_sanctions":True,"requires_context_match":True})

    def test_counts_and_unique_content(self):
        p=self.pool
        self.assertEqual(len(p["entries"]),10)
        ids,txt,notes,intents=set(),set(),set(),set()
        for e in p["entries"]:
            self.assertNotIn(e["intent_id"],intents)
            intents.add(e["intent_id"])
            self.assertEqual(e["audiences"],["all_ai_bots"])
            self.assertEqual(e["language"],"ru")
            self.assertEqual((e["total_staged"],e["target"],e["remaining"]),(12,100,88))
            self.assertEqual(e["prior_for_stable_id"]+e["added_candidates"],12)
            self.assertEqual(len(e["replies"]),12)
            for i,r in enumerate(e["replies"],1):
                self.assertEqual(r["id"],f'{e["intent_id"]}_{i:02d}')
                self.assertNotIn(r["id"],ids)
                ids.add(r["id"])
                self.assertTrue(r["read_only"])
                self.assertEqual(r["context"],"direct")
                self.assertEqual(r["language"],"ru")
                self.assertEqual(r["audiences"],["all_ai_bots"])
                for v,seen in ((r["text"],txt),(r["context_note"],notes)):
                    normalized=norm(v)
                    self.assertTrue(normalized)
                    self.assertNotIn(normalized,seen)
                    seen.add(normalized)
                self.assertNotRegex(r["text"].casefold(),r"\b(?:я забанил|я замутил|я удалил|я оплатил|я получил доступ)\b")
        self.assertEqual(len(ids),120)
        c=p["checkpoint"]
        self.assertEqual(c["processed_intents"],10)
        self.assertEqual(c["prior_candidates"]+c["added_candidates"],120)
        self.assertEqual((c["cumulative_candidates"],c["finished_100"],c["partial_intents"],c["remaining_total"]),(120,0,10,880))

    def test_near_and_cross_pool_duplicates(self):
        entries=self.pool["entries"]
        responses=[r["text"] for e in entries for r in e["replies"]]
        words=[set(norm(v).split()) for v in responses]
        for i,a in enumerate(words):
            for b in words[i+1:]:
                self.assertLess(len(a&b)/len(a|b),0.78)
        all_normalized={norm(x) for x in responses}
        for f in sorted((ROOT/"staging/ru").glob("*.json")):
            if f==PATH:continue
            other=json.loads(f.read_text(encoding="utf-8"))
            if not isinstance(other,dict):continue
            for entry in other.get("entries",[]):
                if not isinstance(entry,dict):continue
                for item in entry.get("replies",[]):
                    value=item.get("text") if isinstance(item,dict) else item
                    if isinstance(value,str):
                        self.assertNotIn(norm(value),all_normalized,f"cross-stage duplicate: {f.name}")

if __name__ == "__main__":
    unittest.main()
