"""T509: read-only Russian contextual response pool integrity and continuity."""
import hashlib
import json
import re
import unicodedata
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
NEW = ROOT / "staging/ru/precision_t509_context_pool.json"
OLD = ROOT / "staging/ru/precision_t508_context_pool.json"
FIRST = ROOT / "staging/ru/precision_t507_context_pool.json"
SOURCE = ROOT / "packs/ru/dialogue.json"
LIMIT = .78

def norm(value):
    value = unicodedata.normalize("NFKC", value).casefold().replace("ё", "е")
    return " ".join(re.findall(r"\w+", value))

def similarity(a,b):
    left, right = set(a.split()), set(b.split())
    return len(left & right) / len(left | right) if left or right else 1

class T509Integrity(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.current=json.loads(NEW.read_text(encoding="utf-8"))
        cls.old=json.loads(OLD.read_text(encoding="utf-8"))
        cls.first=json.loads(FIRST.read_text(encoding="utf-8"))

    def test_source_sha_and_scope(self):
        s=self.current
        raw=SOURCE.read_bytes()
        actual=hashlib.sha256(raw).hexdigest()
        manifest=json.loads((ROOT/"manifest.json").read_text(encoding="utf-8"))
        self.assertIn({"path":"packs/ru/dialogue.json","sha256":actual},manifest["packs"])
        blob=hashlib.sha1(b"blob "+str(len(raw)).encode()+b"\0"+raw).hexdigest()
        self.assertEqual(s["source_pack"],"packs/ru/dialogue.json")
        self.assertEqual(s["source_pack_manifest_sha256"],actual)
        self.assertEqual(s["source_pack_blob_sha"],blob)
        self.assertEqual(s["stage_type"],"supplemental_contextual_reply_pool")
        self.assertFalse(s["consumer_registered"])
        self.assertEqual(s["language"],"ru")
        self.assertEqual(s["audiences"],["all_ai_bots"])
        self.assertTrue(all(s["constraints"].values()))
        self.assertEqual(s["checkpoint"]["previous_stage"],"T508")
        self.assertEqual(s["checkpoint"]["base_commit"],"2d1c4a7f885c66ea5c8be4e81293ea643aa9a7d4")

    def test_continuation_and_near_duplicates(self):
        current=self.current
        old={e["intent_id"]:e for e in self.old["entries"]}
        first={e["intent_id"]:e for e in self.first["entries"]}
        self.assertEqual(set(old), set(first))
        self.assertEqual({e["intent_id"] for e in current["entries"]},set(old))
        self.assertEqual(current["checkpoint"]["processed_intents"],7)
        self.assertEqual(current["checkpoint"]["added_candidates"],140)
        self.assertEqual(current["checkpoint"]["finished_100"],0)
        self.assertEqual(current["checkpoint"]["remaining_total"],320)
        old_ids=set()
        old_texts=[]
        for stage in (self.old,self.first):
            for entry in stage["entries"]:
                for rep in entry["replies"]:
                    old_ids.add(rep["id"])
                    old_texts.append(norm(rep["text"]))
        seen_ids=set(old_ids)
        seen_text=set(old_texts)
        seen_notes=set()
        new_texts=[]
        for entry in current["entries"]:
            prior=old[entry["intent_id"]]
            self.assertEqual(entry["canonical_question"],prior["canonical_question"])
            self.assertEqual(entry["prior_for_stable_id"],prior["total_staged"])
            self.assertEqual(entry["added_candidates"],20)
            self.assertEqual(len(entry["replies"]),20)
            self.assertEqual(entry["total_staged"],prior["total_staged"]+20)
            self.assertEqual(entry["target"],100)
            self.assertEqual(entry["remaining"],100-entry["total_staged"])
            for item in entry["replies"]:
                self.assertNotIn(item["id"],seen_ids)
                n=norm(item["text"]);note=norm(item["context_note"])
                self.assertNotIn(n,seen_text)
                self.assertNotIn(note,seen_notes)
                self.assertGreater(len(n),50)
                self.assertGreater(len(note),30)
                self.assertEqual(item["language"],"ru")
                self.assertEqual(item["audiences"],["all_ai_bots"])
                self.assertEqual(item["context"],"direct")
                self.assertTrue(item["read_only"])
                self.assertTrue(item["avoid"])
                self.assertFalse(re.search(r"(?i)(ghp_[a-z0-9]{12,}|sk-[a-z0-9]{12,}|https?://|@[a-z0-9_]+)",item["text"]))
                self.assertFalse(re.search(r"(?i)\b(забань|замуть|удали чужое сообщение)\b",item["text"]))
                seen_ids.add(item["id"]);seen_text.add(n);seen_notes.add(note)
                new_texts.append(n)
        self.assertEqual(len(new_texts),140)
        self.assertEqual(sum(e["total_staged"] for e in current["entries"]),380)
        self.assertEqual(sum(e["remaining"] for e in current["entries"]),320)
        for i,text in enumerate(new_texts):
            for prev in old_texts:
                self.assertLess(similarity(text,prev),LIMIT)
            for other in new_texts[:i]:
                self.assertLess(similarity(text,other),LIMIT)

    def test_unrelated_stage_overlap(self):
        new={norm(rep["text"]) for e in self.current["entries"] for rep in e["replies"]}
        for stage_id in ("t503","t504","t505","t506"):
            path=ROOT/f"staging/ru/practical_turns_{stage_id}_context_pool.json"
            if not path.exists():
                continue
            stage=json.loads(path.read_text(encoding="utf-8"))
            for entry in stage["entries"]:
                for item in entry["replies"]:
                    self.assertNotIn(norm(item["text"]),new)

if __name__ == "__main__":
    unittest.main()
