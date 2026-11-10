"""T570: check synthetic RU conversation contracts, stable IDs, context and provenance."""
import hashlib
import json
import re
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PATH = ROOT / "staging/ru/conversation_contracts_t570_context_pool.json"

def norm(value):
    import unicodedata
    value = unicodedata.normalize("NFKC", value).lower().replace("ё", "е")
    return " ".join(re.findall(r"[^\\W_]+", value, flags=re.UNICODE))

def candidate_texts(obj):
    if isinstance(obj, dict):
        for key in ("text", "answer", "reply", "response"):
            if isinstance(obj.get(key), str):
                yield obj[key]
        for value in obj.values():
            if isinstance(value, (dict, list)):
                yield from candidate_texts(value)
    elif isinstance(obj, list):
        for item in obj:
            yield from candidate_texts(item)

class TestT570(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = json.loads(PATH.read_text(encoding="utf-8"))
        cls.replies = [r for e in cls.data["entries"] for r in e["replies"]]

    def test_provenance_and_read_only(self):
        data = self.data
        manifest = json.loads((ROOT/"manifest.json").read_text(encoding="utf-8"))
        src = data["source_pack"]
        sha = hashlib.sha256((ROOT/src).read_bytes()).hexdigest()
        blob = subprocess.check_output(["git", "hash-object", src], cwd=ROOT, text=True).strip()
        self.assertIn({"path": src, "sha256": sha}, manifest["packs"])
        self.assertEqual(data["source_pack_manifest_sha256"], sha)
        self.assertEqual(data["source_pack_blob_sha"], blob)
        self.assertFalse(data["consumer_registered"])
        self.assertIsNone(data["parent_stage"])
        self.assertEqual((data["language"], data["audiences"]), ("ru", ["all_ai_bots"]))
        for constraint in ("read_only", "requires_direct_address", "no_personal_data", "no_sanctions", "requires_context_match"):
            self.assertTrue(data["constraints"][constraint])

    def test_counts_ids_contexts_and_safety(self):
        self.assertEqual((len(self.data["entries"]), len(self.replies)), (10,100))
        cp=self.data["checkpoint"]
        self.assertEqual((cp["prior_candidates"],cp["added_candidates"],cp["cumulative_candidates"],cp["processed_intents"],cp["finished_100"],cp["partial_intents"],cp["remaining_total"]), (0,100,100,10,0,10,900))
        ids=set(); texts=set(); notes=set(); questions=set()
        for e in self.data["entries"]:
            self.assertNotIn(norm(e["canonical_question"]), questions)
            questions.add(norm(e["canonical_question"]))
            self.assertEqual((e["prior_for_stable_id"], e["added_candidates"], e["total_staged"],e["target"],e["remaining"]),(0,10,10,100,90))
            self.assertEqual(len(e["replies"]),10)
            for i,r in enumerate(e["replies"],1):
                self.assertEqual(r["id"],f"{e['intent_id']}_{i:02d}")
                self.assertNotIn(r["id"],ids); ids.add(r["id"])
                for value,collection in ((r["text"],texts),(r["context_note"],notes)):
                    self.assertTrue(value.strip()); k=norm(value)
                    self.assertNotIn(k,collection,r["id"]); collection.add(k)
                self.assertEqual((r["language"],r["audiences"],r["context"],r["read_only"]),("ru",["all_ai_bots"],"direct",True))
                self.assertTrue(r["avoid"]); self.assertFalse(re.search(r"[\\w.+-]+@[\\w.-]+\\.[A-Za-z]{2,}",r["text"]))
        self.assertEqual((len(ids),len(texts),len(notes)),(100,100,100))

    def test_lexical_independence_and_unrelated_stages(self):
        vec=[set(norm(r["text"]).split()) for r in self.replies]
        for i,a in enumerate(vec):
            for b in vec[i+1:]:
                self.assertLess(len(a&b)/len(a|b),.78,self.replies[i]["id"])
        fresh={norm(r["text"]) for r in self.replies}
        for path in (ROOT/"staging/ru").glob("*.json"):
            if path.resolve()==PATH.resolve(): continue
            try: obj=json.loads(path.read_text(encoding="utf-8"))
            except (UnicodeError, json.JSONDecodeError): self.fail(f"Invalid JSON in {path}")
            for t in candidate_texts(obj):
                self.assertNotIn(norm(t),fresh,f"Exact duplicate in {path}")
            if isinstance(obj,dict):
                existing={norm(e["canonical_question"]) for e in obj.get("entries",[]) if isinstance(e,dict) and isinstance(e.get("canonical_question"),str)}
                for e in self.data["entries"]:
                    self.assertNotIn(norm(e["canonical_question"]),existing,f"Duplicate canonical question in {path}")

if __name__=="__main__":
    unittest.main()
