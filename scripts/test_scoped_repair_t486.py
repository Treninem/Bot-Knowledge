"""T486: 80 original scoped synthetic conversational repair replies, dependent on #548."""
import hashlib
import json
import re
import unicodedata
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = "packs/ru/dialogue.json"
STAGE = "staging/ru/scoped_repair_t486_context_pool.json"
SOURCE_SHA = "3e63012f2823ea1896e9d9612f68f19a3cf2fe6bbf2c8296fc98ac29fb18a024"
SOURCE_BLOB = "b881d145f634b6104c8538fef708d45162ef3125"
COUNTS = {"clarify_previous": 18, "disagreement": 17, "unknown_fact": 17, "ambiguous": 17}
SECRET = re.compile(r"(?i)(ghp_[a-z0-9]{12,}|sk-[a-z0-9]{12,}|bot_token|chat_id|user_id|https?://|@[a-z0-9_]+|[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,})")

def normalize(s):
    s = unicodedata.normalize("NFKC", s).lower().replace("ё", "е")
    return " ".join(re.findall(r"\w+", s))

def blob(raw):
    return hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()

class T486Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source_raw = (ROOT / SOURCE).read_bytes()
        cls.source = json.loads(cls.source_raw)
        cls.stage = json.loads((ROOT / STAGE).read_text(encoding="utf-8"))

    def test_source_and_catalog_not_replaced(self):
        self.assertEqual(hashlib.sha256(self.source_raw).hexdigest(), SOURCE_SHA)
        self.assertEqual(blob(self.source_raw), SOURCE_BLOB)
        manifest = json.loads((ROOT / "manifest.json").read_text("utf-8"))
        self.assertEqual(next(p["sha256"] for p in manifest["packs"] if p["path"] == SOURCE), SOURCE_SHA)
        self.assertEqual(self.stage["source_pack_manifest_sha256"], SOURCE_SHA)
        self.assertEqual(self.stage["source_pack_blob_sha"], SOURCE_BLOB)
        self.assertEqual(self.stage["consumer_registered"], False)
        self.assertEqual(self.source["pack_version"], "2026.11.09.2")

    def test_counts_scope_and_privacy(self):
        entries = self.stage["entries"]
        self.assertEqual(set(e["intent_id"] for e in entries), set(COUNTS))
        self.assertEqual(self.stage["checkpoint"], dict(stage_id="T486", processed_intents=4,
            source_legacy_and_scoped=69, added_candidates=80, finished_100=0,
            partial_intents=4, remaining_total=251, rejected=0))
        seen_id, seen_norm = set(), set()
        previous = []
        for intent in COUNTS:
            previous.extend(self.source["reactions"][intent])
            previous.extend(r["text"] for group in
                self.source["scoped_repair_reactions"]["intents"][intent]["contexts"].values()
                for r in group["replies"])
        baseline = {normalize(s) for s in previous}
        self.assertEqual(len(previous), 69)
        for e in entries:
            self.assertEqual(e["baseline_registered"], COUNTS[e["intent_id"]])
            self.assertEqual(e["new_staged"], 20)
            self.assertEqual(len(e["replies"]), 20)
            for r in e["replies"]:
                self.assertNotIn(r["id"], seen_id)
                seen_id.add(r["id"])
                n=normalize(r["text"])
                self.assertNotIn(n, seen_norm)
                self.assertNotIn(n, baseline)
                seen_norm.add(n)
                self.assertEqual(r["audiences"], ["all_ai_bots"])
                self.assertIn(r["context"], ("direct", "private", "group_addressed"))
                self.assertTrue(r["context_note"].strip())
                self.assertTrue(r["avoid"].strip())
                self.assertIs(r["read_only"], True)
                self.assertEqual(r["language"], "ru")
                self.assertFalse(SECRET.search(r["text"]))
        self.assertEqual(len(seen_norm),80)
        self.assertEqual(self.stage["checkpoint"]["remaining_total"], 400 - 69 - len(seen_norm))

    def test_no_near_lexical_clones(self):
        old = [r for x in self.source["scoped_repair_reactions"]["intents"].values()
            for g in x["contexts"].values() for r in g["replies"]]
        all_text = [r["text"] for e in self.stage["entries"] for r in e["replies"]]
        prior = [r["text"] for r in old] + [
            x for key in COUNTS for x in self.source["reactions"][key]]
        def tokens(v): return set(normalize(v).split())
        prior_t = [tokens(v) for v in prior]
        for i,t in enumerate(all_text):
            a = tokens(t)
            for p in prior_t + [tokens(v) for v in all_text[:i]]:
                j = len(a & p) / len(a | p)
                self.assertLess(j, 0.78, msg=t)

if __name__ == "__main__":
    unittest.main()
