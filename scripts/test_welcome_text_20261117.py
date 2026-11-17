"""Two 100-answer newcomer sets: source-pinned, scoped, privacy-safe staging QA."""
import hashlib
import json
import re
import subprocess
import unicodedata
import unittest
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
POOL = ROOT / "staging/ru/newcomer_welcome_20261117_context_pool.json"
SOURCE = "packs/ru/intents.json"
EXPECTED_MAIN = "d43134b9072c7ceff44cfcf63d5d11c0d0771d7a"
EXPECTED_SOURCE_SHA256 = "0bd5810de43f14e0c8cb454f71adbf11bf2e92e00477bf841bb66db477a7c39b"
EXPECTED_SOURCE_BLOB = "71be015a85471c22697f16f5dd3246d126be290c"
EXPECTED = {"welcome_text", "newcomer_help", "respond_to_self_introduction"}
ALLOWED_CONTEXTS = {"direct", "group_addressed"}

def norm(value):
    value = unicodedata.normalize("NFKC", value).casefold().replace("ё", "е")
    return " ".join("".join(" " if unicodedata.category(c)[0] in {"P", "S"} else c for c in value).split())

def collect_strings(value):
    if isinstance(value, dict):
        for item in value.values():
            yield from collect_strings(item)
    elif isinstance(value, list):
        for item in value:
            yield from collect_strings(item)
    elif isinstance(value, str):
        yield value

def collect_reply_texts(value):
    if isinstance(value, dict):
        replies = value.get("replies")
        if isinstance(replies, list):
            for reply in replies:
                if isinstance(reply, dict) and isinstance(reply.get("text"), str):
                    yield reply["text"]
                elif isinstance(reply, str):
                    yield reply
        for item in value.values():
            if isinstance(item, (dict, list)):
                yield from collect_reply_texts(item)
    elif isinstance(value, list):
        for item in value:
            if isinstance(item, (dict, list)):
                yield from collect_reply_texts(item)

def jaccard(left, right):
    a, b = set(norm(left).split()), set(norm(right).split())
    return len(a & b) / len(a | b) if a or b else 1.0

class NewcomerWelcome20261117(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pool = json.loads(POOL.read_text(encoding="utf-8"))
        cls.manifest = json.loads((ROOT / "manifest.json").read_text(encoding="utf-8"))
        cls.styles = json.loads((ROOT / "packs/ru/styles.json").read_text(encoding="utf-8"))["styles"]

    def test_source_sha_blob_and_non_registration(self):
        digest = hashlib.sha256((ROOT / SOURCE).read_bytes()).hexdigest()
        blob = subprocess.check_output(["git", "hash-object", str(ROOT / SOURCE)], cwd=ROOT, text=True).strip()
        declared = {item["path"]: item["sha256"] for item in self.manifest["packs"]}
        self.assertEqual(declared[SOURCE], EXPECTED_SOURCE_SHA256)
        self.assertEqual(digest, EXPECTED_SOURCE_SHA256)
        self.assertEqual(blob, EXPECTED_SOURCE_BLOB)
        source_intents = {item["id"] for item in json.loads((ROOT / SOURCE).read_text(encoding="utf-8"))["intents"]}
        self.assertTrue({"welcome_text", "newcomer_help"} <= source_intents)
        self.assertNotIn("respond_to_self_introduction", source_intents, "New intent must remain unregistered until consumer routing is designed")
        self.assertEqual(self.pool["source_pack"], SOURCE)
        self.assertEqual(self.pool["source_pack_manifest_sha256"], digest)
        self.assertEqual(self.pool["source_pack_blob_sha"], blob)
        self.assertEqual(self.pool["checkpoint"]["base_main_sha"], EXPECTED_MAIN)
        self.assertFalse(self.pool["consumer_registered"])
        self.assertNotIn("staging/ru/newcomer_welcome_20261117_context_pool.json", declared)

    def test_two_stable_intents_and_exact_counts(self):
        self.assertEqual(self.pool["schema_version"], 1)
        self.assertEqual(self.pool["stage_type"], "supplemental_contextual_reply_pool")
        self.assertEqual(self.pool["audiences"], ["all_ai_bots"])
        self.assertEqual(self.pool["language"], "ru")
        self.assertEqual(self.pool["constraints"], {
            "read_only": True, "requires_direct_address": True,
            "no_personal_data": True, "no_sanctions": True,
            "requires_context_match": True, "synthetic_examples_only": True,
            "no_unverified_product_claims": True
        })
        self.assertEqual({entry["intent_id"] for entry in self.pool["entries"]}, EXPECTED)
        self.assertEqual(self.pool["checkpoint"]["intent_count"], 3)
        self.assertEqual(self.pool["checkpoint"]["cumulative_candidates"], 300)
        self.assertEqual(self.pool["checkpoint"]["remaining_total"], 0)
        for entry in self.pool["entries"]:
            self.assertEqual(entry["baseline_registered"], 0)
            self.assertEqual(entry["prior_for_stable_id"], 0)
            self.assertEqual(entry["added_candidates"], 100)
            self.assertEqual(entry["total_staged"], 100)
            self.assertEqual(entry["target"], 100)
            self.assertEqual(entry["remaining"], 0)
            self.assertEqual(len(entry["replies"]), 100)

    def test_ids_context_families_style_and_privacy(self):
        ids, texts, notes = set(), set(), set()
        all_replies = []
        for entry in self.pool["entries"]:
            family_counts = Counter()
            for number, reply in enumerate(entry["replies"], 1):
                self.assertEqual(reply["id"], f'{entry["intent_id"]}_{number:02d}')
                self.assertNotIn(reply["id"], ids)
                ids.add(reply["id"])
                key = norm(reply["text"])
                self.assertTrue(key)
                self.assertNotIn(key, texts)
                texts.add(key)
                note = norm(reply["context_note"])
                self.assertTrue(note)
                self.assertNotIn(note, notes)
                notes.add(note)
                self.assertEqual(reply["language"], "ru")
                self.assertEqual(reply["audiences"], ["all_ai_bots"])
                self.assertIn(reply["style"], self.styles)
                self.assertIn(reply["context"], ALLOWED_CONTEXTS)
                self.assertTrue(reply["read_only"])
                self.assertTrue(reply["context_family"])
                family_counts[reply["context_family"]] += 1
                self.assertNotRegex(reply["text"], r'(?i)\b(?:забанить|банить|замутить|выдать мут|выдать бан|удалить сообщение|наказать|заблокировать пользователя)\b')
                self.assertNotRegex(reply["text"], r'(?i)(?:https?://|[\w.+-]+@[\w.-]+\.[a-z]{2,}|@\w{4,}|\b\d{6,}\b)')
                all_replies.append(reply)
            self.assertEqual(len(family_counts), 10)
            self.assertTrue(all(count == 10 for count in family_counts.values()))
        self.assertEqual(len(ids), 200)
        self.assertEqual(len(texts), 200)
        self.assertEqual(len(notes), 200)
        for i, left in enumerate(all_replies):
            for right in all_replies[i + 1:]:
                self.assertLess(jaccard(left["text"], right["text"]), 0.78)

    def test_no_exact_answer_collision_with_registered_or_staged_data(self):
        candidates = {norm(reply["text"]) for entry in self.pool["entries"] for reply in entry["replies"]}
        registered = set()
        for item in self.manifest["packs"]:
            data = json.loads((ROOT / item["path"]).read_text(encoding="utf-8"))
            registered.update(norm(value) for value in collect_strings(data) if norm(value))
        self.assertFalse(candidates & registered, "Exact duplicate against a registered pack")
        staged = set()
        for path in sorted((ROOT / "staging/ru").glob("*.json")):
            if path == POOL:
                continue
            data = json.loads(path.read_text(encoding="utf-8"))
            staged.update(norm(value) for value in collect_reply_texts(data) if norm(value))
        self.assertFalse(candidates & staged, "Exact duplicate against another staged reply pool")

if __name__ == "__main__":
    unittest.main()
