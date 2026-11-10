"""T539: direct, context-guarded original Russian social replies (staging only)."""
from __future__ import annotations
import hashlib
import json
import re
import subprocess
import unicodedata
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
POOL = ROOT / "staging/ru/conversation_t539_context_pool.json"
SOURCE = "packs/ru/social_dialogues.json"
EXPECTED_PREFIX = "convo_t539_"

def norm(value: str) -> str:
    value = unicodedata.normalize("NFKC", value).casefold().replace("ё", "е")
    value = "".join(" " if unicodedata.category(c)[0] in {"P", "S"} else c for c in value)
    return " ".join(value.split())

def previous_replies():
    """Collect comparable direct-response strings from all other staged pools.

    Other staging shapes may include separate instructional examples; this
    deliberately does not call them all semantically equivalent direct replies.
    """
    for path in sorted((ROOT / "staging/ru").glob("*.json")):
        if path == POOL:
            continue
        data = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(data, dict):
            continue
        for entry in data.get("entries", []):
            if not isinstance(entry, dict):
                continue
            for row in entry.get("replies", []):
                if isinstance(row, dict) and isinstance(row.get("text"), str):
                    yield path.name, row["text"]
                elif isinstance(row, str):
                    yield path.name, row

class ConversationT539(unittest.TestCase):
    def test_source_scope_counts_privacy_and_dedup(self):
        stage = json.loads(POOL.read_text(encoding="utf-8"))
        manifest = json.loads((ROOT / "manifest.json").read_text(encoding="utf-8"))
        source = ROOT / SOURCE
        digest = hashlib.sha256(source.read_bytes()).hexdigest()
        blob = subprocess.check_output(["git", "hash-object", str(source)],
                                       cwd=ROOT, text=True).strip()
        self.assertIn({"path": SOURCE, "sha256": digest}, manifest["packs"])
        self.assertEqual(stage["source_pack"], SOURCE)
        self.assertEqual(stage["source_pack_manifest_sha256"], digest)
        self.assertEqual(stage["source_pack_blob_sha"], blob)
        self.assertNotIn({"path": str(POOL.relative_to(ROOT)), "sha256": digest},
                         manifest["packs"])
        self.assertFalse(stage["consumer_registered"])
        self.assertEqual(stage["audiences"], ["all_ai_bots"])
        self.assertEqual(stage["stage_type"], "supplemental_contextual_reply_pool")
        for key in ("read_only", "requires_direct_address", "no_personal_data",
                    "no_sanctions", "requires_context_match"):
            self.assertTrue(stage["constraints"][key])

        entries = stage["entries"]
        self.assertEqual(len(entries), 10)
        ids, answers, notes = set(), set(), set()
        bags = []
        for entry in entries:
            self.assertTrue(entry["intent_id"].startswith(EXPECTED_PREFIX))
            self.assertEqual(entry["audiences"], ["all_ai_bots"])
            self.assertEqual(entry["language"], "ru")
            self.assertEqual(entry["target"], 100)
            self.assertEqual((entry["baseline_registered"], entry["prior_for_stable_id"]),
                             (0, 76))
            self.assertEqual((entry["added_candidates"], entry["total_staged"],
                              entry["remaining"]), (12, 88, 12))
            self.assertEqual(len(entry["replies"]), 88)
            for position, item in enumerate(entry["replies"], 1):
                self.assertEqual(item["id"],
                                 "{}_{:02d}".format(entry["intent_id"], position))
                self.assertNotIn(item["id"], ids)
                ids.add(item["id"])
                for value, store in ((item["text"], answers),
                                     (item["context_note"], notes)):
                    key = norm(value)
                    self.assertTrue(key)
                    self.assertNotIn(key, store)
                    store.add(key)
                self.assertEqual(item["language"], "ru")
                self.assertEqual(item["audiences"], ["all_ai_bots"])
                self.assertEqual(item["context"], "direct")
                self.assertTrue(item["read_only"])
                self.assertGreaterEqual(len(item["text"]), 28)
                self.assertNotRegex(item["text"].lower(),
                                    r"\b(?:забанил|замутил|выдал бан|удалил сообщение)\b")
                self.assertNotRegex(item["text"],
                                    r"(?:ghp_[A-Za-z0-9]{12,}|sk-[A-Za-z0-9]{12,}|"
                                    r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,})")
                self.assertIn("прямом обращении", item["avoid"])
                bag = set(norm(item["text"]).split())
                for old in bags:
                    score = len(bag & old) / len(bag | old)
                    self.assertLess(score, 0.78)
                bags.append(bag)
        self.assertEqual((len(ids), len(answers), len(notes)), (880, 880, 880))
        self.assertEqual(stage["checkpoint"]["added_candidates"], 120)
        self.assertEqual(stage["checkpoint"]["remaining_total"], 120)
        self.assertEqual(stage["checkpoint"]["finished_100"], 0)
        self.assertEqual(stage["checkpoint"]["partial_intents"], 10)

        # Exact overlap against all comparable staged reply lists; this does
        # not claim complete semantic equivalence or coverage of every format.
        external = {}
        for filename, text in previous_replies():
            external.setdefault(norm(text), filename)
        self.assertFalse(answers & external.keys(),
                         "Exact normalized overlap with another staged pool")
        # A quick lexical near-duplicate check over comparable staged replies.
        indexed = {}
        external_bags = []
        for text, filename in external.items():
            words = frozenset(text.split())
            if len(words) < 5:
                continue
            idx = len(external_bags)
            external_bags.append((words, filename))
            for word in words:
                indexed.setdefault(word, set()).add(idx)
        for reply in answers:
            words = set(reply.split())
            if len(words) < 5:
                continue
            candidate_ids = set()
            for token in words:
                candidate_ids.update(indexed.get(token, ()))
            for idx in candidate_ids:
                other, filename = external_bags[idx]
                score = len(words & other) / len(words | other)
                self.assertLess(score, 0.78,
                                "Near duplicate against {}".format(filename))

if __name__ == "__main__":
    unittest.main()
