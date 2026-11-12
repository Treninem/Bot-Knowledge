"""T501: privacy, revoked humor consent, and firm non-retaliatory replies."""
import hashlib
import json
import re
import unicodedata
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STAGE = ROOT / "staging/ru/group_turns_t501_context_pool.json"
PARENT = ROOT / "staging/ru/group_turns_t499_context_pool.json"
SOURCE = ROOT / "packs/ru/dialogue.json"
SOURCE_SHA = "3e63012f2823ea1896e9d9612f68f19a3cf2fe6bbf2c8296fc98ac29fb18a024"
SOURCE_BLOB = "b881d145f634b6104c8538fef708d45162ef3125"
PARENT_BLOB = "b6ee77de813846515fe411df11253aeec88853fc"
INTENTS = (
    "group_private_boundary", "humor_consent_withdrawn",
    "rudeness_without_retaliation",
)

def git_blob(raw):
    return hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()

def norm(text):
    return " ".join(re.findall(r"\w+", unicodedata.normalize("NFKC", text).lower().replace("ё", "е")))

def extract(obj):
    if isinstance(obj, dict):
        for key, value in obj.items():
            if key in ("text", "answer", "reply", "response", "assistant_response", "response_text", "reply_text") and isinstance(value, str):
                yield value
            else:
                yield from extract(value)
    elif isinstance(obj, list):
        for value in obj:
            yield from extract(value)

class GroupT501Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.stage = json.loads(STAGE.read_text("utf-8"))
        cls.parent = json.loads(PARENT.read_text("utf-8"))

    def test_source_and_parent_integrity(self):
        source_raw = SOURCE.read_bytes()
        parent_raw = PARENT.read_bytes()
        self.assertEqual(hashlib.sha256(source_raw).hexdigest(), SOURCE_SHA)
        self.assertEqual(git_blob(source_raw), SOURCE_BLOB)
        self.assertEqual(git_blob(parent_raw), PARENT_BLOB)
        manifest = json.loads((ROOT / "manifest.json").read_text("utf-8"))
        registered = next(x["sha256"] for x in manifest["packs"] if x["path"] == "packs/ru/dialogue.json")
        self.assertEqual(registered, SOURCE_SHA)
        s = self.stage
        self.assertEqual(s["source_pack_manifest_sha256"], SOURCE_SHA)
        self.assertEqual(s["source_pack_blob_sha"], SOURCE_BLOB)
        self.assertEqual(s["previous_stage"]["git_blob"], PARENT_BLOB)
        self.assertFalse(s["consumer_registered"])
        self.assertTrue(s["constraints"]["read_only"])
        self.assertTrue(s["constraints"]["requires_direct_address"])
        self.assertEqual(s["audiences"], ["all_ai_bots"])

    def test_verified_continuation_counts_and_scope(self):
        s = self.stage
        self.assertEqual(s["checkpoint"]["stage_id"], "T501")
        self.assertEqual(s["checkpoint"]["baseline_in_previous_stages"], 210)
        self.assertEqual(s["checkpoint"]["added_candidates"], 90)
        self.assertEqual(s["checkpoint"]["finished_100"], 3)
        self.assertEqual(s["checkpoint"]["remaining_for_three"], 0)
        self.assertEqual({e["intent_id"] for e in s["entries"]}, set(INTENTS))
        self.assertEqual(sum(len(e["replies"]) for e in s["entries"]), 90)
        for entry in s["entries"]:
            prev = next(x for x in self.parent["entries"] if x["intent_id"] == entry["intent_id"])
            self.assertEqual(prev["total_staged"], 70)
            self.assertEqual(entry["baseline_including_previous_stages"], prev["total_staged"])
            self.assertEqual((entry["added_candidates"], entry["target"], entry["total_staged"], entry["remaining"]), (30, 100, 100, 0))
            self.assertEqual(len(entry["replies"]), 30)

    def test_originality_privacy_and_non_action(self):
        stage = self.stage
        history = set()
        for directory in (ROOT / "packs/ru", ROOT / "staging/ru"):
            for path in directory.glob("*.json"):
                if path == STAGE:
                    continue
                obj = json.loads(path.read_text("utf-8"))
                history.update(norm(x) for x in extract(obj) if x.strip())
        history.discard("")
        sizes = {}
        for line in history:
            tokens = frozenset(line.split())
            sizes.setdefault(len(tokens), []).append(tokens)
        ids = set()
        contexts = set()
        for entry in stage["entries"]:
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
                context = norm(reply["context_note"])
                self.assertNotIn(context, contexts)
                contexts.add(context)
                self.assertFalse(re.search(r"(?i)(ghp_[a-z0-9]{12,}|sk-[a-z0-9]{12,}|https?://|@[a-z0-9_]+)", reply["text"]))
                self.assertFalse(re.search(r"(?i)\b(забань|замуть|заблокируй пользователя|удали чужое сообщение)\b", reply["text"]))
                normalized = norm(reply["text"])
                self.assertTrue(normalized)
                self.assertNotIn(normalized, history, reply["id"])
                tokens = frozenset(normalized.split())
                for size in range(max(1, int(len(tokens) * .78)), int(len(tokens) / .78) + 2):
                    for old in sizes.get(size, ()):
                        shared = len(tokens & old)
                        self.assertLess(shared / (len(tokens) + len(old) - shared), .78, reply["id"])
                history.add(normalized)
                sizes.setdefault(len(tokens), []).append(tokens)
        self.assertEqual(len(ids), 90)

if __name__ == "__main__":
    unittest.main()
