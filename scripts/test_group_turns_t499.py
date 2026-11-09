"""T499: six unfinished group intents, original 120 scoped replies, source and full-history gates."""
import hashlib
import json
import re
import unicodedata
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STAGE = ROOT / "staging/ru/group_turns_t499_context_pool.json"
SOURCE_SHA = "3e63012f2823ea1896e9d9612f68f19a3cf2fe6bbf2c8296fc98ac29fb18a024"
SOURCE_BLOB = "b881d145f634b6104c8538fef708d45162ef3125"
PARENT_BLOB = "32e5d1d96a555471c9accb35b8c4aa7c7b2a23ce"
INTENTS = (
    "group_addressed_thread", "group_private_boundary",
    "humor_consent_withdrawn", "rudeness_without_retaliation",
    "group_dispute_neutrality", "group_roles_readonly",
)

def blob(raw):
    return hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()

def norm(s):
    return " ".join(re.findall(r"\w+", unicodedata.normalize("NFKC", s).lower().replace("ё", "е")))

def extract(obj):
    if isinstance(obj, dict):
        for key, val in obj.items():
            if key in ("text", "answer", "reply", "response", "assistant_response", "response_text", "reply_text") and isinstance(val, str):
                yield val
            else:
                yield from extract(val)
    elif isinstance(obj, list):
        for item in obj:
            yield from extract(item)

class GroupT499Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source_raw = (ROOT / "packs/ru/dialogue.json").read_bytes()
        cls.parent_raw = (ROOT / "staging/ru/group_turns_t495_context_pool.json").read_bytes()
        cls.parent = json.loads(cls.parent_raw)
        cls.stage = json.loads(STAGE.read_text("utf-8"))

    def test_lineage_and_counts(self):
        self.assertEqual(hashlib.sha256(self.source_raw).hexdigest(), SOURCE_SHA)
        self.assertEqual(blob(self.source_raw), SOURCE_BLOB)
        self.assertEqual(blob(self.parent_raw), PARENT_BLOB)
        manifest = json.loads((ROOT / "manifest.json").read_text("utf-8"))
        self.assertEqual(next(p["sha256"] for p in manifest["packs"] if p["path"] == "packs/ru/dialogue.json"), SOURCE_SHA)
        s = self.stage
        self.assertEqual(s["source_pack_blob_sha"], SOURCE_BLOB)
        self.assertEqual(s["source_pack_manifest_sha256"], SOURCE_SHA)
        self.assertFalse(s["consumer_registered"])
        self.assertTrue(s["constraints"]["read_only"])
        self.assertTrue(s["constraints"]["requires_direct_address"])
        self.assertEqual(s["audiences"], ["all_ai_bots"])
        self.assertEqual(s["checkpoint"]["stage_id"], "T499")
        self.assertEqual(s["checkpoint"]["baseline_in_previous_stages"], 300)
        self.assertEqual(s["checkpoint"]["added_candidates"], 120)
        self.assertEqual(s["checkpoint"]["total_staged"], 420)
        self.assertEqual(s["checkpoint"]["remaining_total"], 180)
        self.assertEqual(s["checkpoint"]["partial_intents"], 6)
        self.assertEqual(s["checkpoint"]["finished_100"], 0)
        self.assertEqual(set(INTENTS), {e["intent_id"] for e in s["entries"]})
        self.assertEqual(s["previous_stages"][-1]["git_blob"], PARENT_BLOB)
        for prev in s["previous_stages"]:
            self.assertEqual(blob((ROOT / prev["path"]).read_bytes()), prev["git_blob"])
        for entry in s["entries"]:
            old = next(e for e in self.parent["entries"] if e["intent_id"] == entry["intent_id"])
            self.assertEqual(old["total_staged"], 50)
            self.assertEqual(entry["baseline_including_previous_stages"], old["total_staged"])
            self.assertEqual(entry["target"], 100)
            self.assertEqual(entry["added_candidates"], len(entry["replies"]))
            self.assertEqual(entry["added_candidates"], 20)
            self.assertEqual(entry["total_staged"], 70)
            self.assertEqual(entry["remaining"], 30)

    def test_privacy_intent_and_full_history_dedup(self):
        history = set()
        for directory in (ROOT / "packs/ru", ROOT / "staging/ru"):
            for path in directory.glob("*.json"):
                if path == STAGE:
                    continue
                obj = json.loads(path.read_text("utf-8"))
                history.update(norm(text) for text in extract(obj) if text.strip())
        history.update(norm(text) for arr in json.loads(self.source_raw)["reactions"].values() for text in arr)
        history.discard("")
        buckets = {}
        for line in history:
            tokens = frozenset(line.split())
            buckets.setdefault(len(tokens), []).append(tokens)
        ids = set()
        seen = set()
        contexts = set()
        for entry in self.stage["entries"]:
            for reply in entry["replies"]:
                self.assertNotIn(reply["id"], ids)
                ids.add(reply["id"])
                self.assertEqual(reply["language"], "ru")
                self.assertEqual(reply["style"], "neutral")
                self.assertEqual(reply["audiences"], ["all_ai_bots"])
                self.assertEqual(reply["context"], "group_addressed")
                self.assertTrue(reply["read_only"])
                self.assertGreater(len(reply["context_note"]), 34)
                self.assertGreater(len(reply["avoid"]), 110)
                self.assertNotIn(norm(reply["context_note"]), contexts)
                contexts.add(norm(reply["context_note"]))
                self.assertFalse(re.search(r"(?i)(ghp_[a-z0-9]{12,}|sk-[a-z0-9]{12,}|https?://|@[a-z0-9_]+)", reply["text"]))
                self.assertFalse(re.search(r"(?i)\b(забань|замуть|заблокируй пользователя|удали чужое сообщение)\b", reply["text"]))
                key = norm(reply["text"])
                self.assertNotIn(key, history, reply["id"])
                self.assertNotIn(key, seen, reply["id"])
                seen.add(key)
                tokens = frozenset(key.split())
                for size in range(max(1, int(len(tokens)*.78)), int(len(tokens)/.78)+2):
                    for old in buckets.get(size, ()):
                        shared = len(tokens & old)
                        self.assertLess(shared/(len(tokens)+len(old)-shared), .78, reply["id"])
                buckets.setdefault(len(tokens), []).append(tokens)
        self.assertEqual(len(ids), 120)

if __name__ == "__main__":
    unittest.main()
