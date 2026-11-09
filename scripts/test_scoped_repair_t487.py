"""T487: 120 independently authored opt-in RU repair replies; immutable source + prior staged pool."""
import hashlib
import json
import re
import unicodedata
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = "packs/ru/dialogue.json"
PREV = "staging/ru/scoped_repair_t486_context_pool.json"
STAGE = "staging/ru/scoped_repair_t487_context_pool.json"
SOURCE_SHA = "3e63012f2823ea1896e9d9612f68f19a3cf2fe6bbf2c8296fc98ac29fb18a024"
SOURCE_BLOB = "b881d145f634b6104c8538fef708d45162ef3125"
PREV_BLOB = "dd53223fa409ebde1a7abe9243919fc1c8e9001c"
COUNTS = {"clarify_previous": 38, "disagreement": 37, "unknown_fact": 37, "ambiguous": 37}
SECRET = re.compile(r"(?i)(ghp_[a-z0-9]{12,}|sk-[a-z0-9]{12,}|bot_token|chat_id|user_id|https?://|@[a-z0-9_]+|[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,})")

def norm(s):
    s = unicodedata.normalize("NFKC", s).lower().replace("ё", "е")
    return " ".join(re.findall(r"\w+", s))

def blob(data):
    return hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()

class T487Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.src_raw = (ROOT / SOURCE).read_bytes()
        cls.old_raw = (ROOT / PREV).read_bytes()
        cls.src = json.loads(cls.src_raw)
        cls.old = json.loads(cls.old_raw)
        cls.new = json.loads((ROOT / STAGE).read_text("utf-8"))

    def test_pins_and_progress(self):
        self.assertEqual(hashlib.sha256(self.src_raw).hexdigest(), SOURCE_SHA)
        self.assertEqual(blob(self.src_raw), SOURCE_BLOB)
        self.assertEqual(blob(self.old_raw), PREV_BLOB)
        manifest = json.loads((ROOT / "manifest.json").read_text("utf-8"))
        self.assertEqual(next(x["sha256"] for x in manifest["packs"] if x["path"] == SOURCE), SOURCE_SHA)
        self.assertEqual(self.new["source_pack_manifest_sha256"], SOURCE_SHA)
        self.assertEqual(self.new["source_pack_blob_sha"], SOURCE_BLOB)
        self.assertEqual(self.new["previous_stage_blob_sha"], PREV_BLOB)
        self.assertIs(self.new["consumer_registered"], False)
        self.assertEqual(self.new["checkpoint"], {"stage_id": "T487", "processed_intents": 4,
            "registered_from_pr548": 69, "previous_staged": 80, "added_candidates": 120,
            "total": 269, "finished_100": 0, "partial_intents": 4, "remaining_total": 131, "rejected": 0})

    def test_scoped_replies_have_unique_texts_and_ids(self):
        old = list(self.old["entries"])
        previous = [r["text"] for e in old for r in e["replies"]]
        for intent in COUNTS:
            previous.extend(self.src["reactions"][intent])
            previous.extend(r["text"] for part in
                self.src["scoped_repair_reactions"]["intents"][intent]["contexts"].values()
                for r in part["replies"])
        seen_text = {norm(t) for t in previous}
        tokens_seen = [set(norm(t).split()) for t in previous]
        ids = {r["id"] for e in old for r in e["replies"]}
        self.assertEqual(len(previous), 149)
        self.assertEqual(len(self.new["entries"]), 4)
        total = 0
        for entry in self.new["entries"]:
            self.assertEqual(entry["baseline_including_previous_stage"], COUNTS[entry["intent_id"]])
            self.assertEqual(entry["new_staged"], 30)
            self.assertEqual(len(entry["replies"]), 30)
            for r in entry["replies"]:
                self.assertNotIn(r["id"], ids)
                ids.add(r["id"])
                self.assertEqual(r["language"], "ru")
                self.assertEqual(r["audiences"], ["all_ai_bots"])
                self.assertTrue(r["read_only"])
                self.assertIn(r["context"], ("direct", "private", "group_addressed"))
                self.assertTrue(r["context_note"].strip())
                self.assertTrue(r["avoid"].strip())
                self.assertFalse(SECRET.search(r["text"]))
                t = norm(r["text"])
                self.assertNotIn(t, seen_text)
                seen_text.add(t)
                tok=set(t.split())
                for prior in tokens_seen:
                    jac = len(tok & prior) / len(tok | prior)
                    self.assertLess(jac, 0.78)
                tokens_seen.append(tok)
                total += 1
        self.assertEqual(total, 120)
        self.assertEqual(self.new["checkpoint"]["remaining_total"], 400 - (len(previous)+total))

if __name__ == "__main__":
    unittest.main()
