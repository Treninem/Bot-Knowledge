"""Regression QA for new unregistered structured-information stages G and H."""
from __future__ import annotations

import hashlib
import json
import re
import unicodedata
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = "packs/ru/structured_information_qa.json"
EXPECTED_SHA256 = "55b3f6126d36cd92687d005b7fedf5a11df9ee61cf453103accdf1f13c8498f0"
EXPECTED_BLOB = "8b3d596b5b50d3d319ebf450c96d5623fc99d26a"
STAGES = [ROOT / f"staging/ru/structured_information_20261111_delta_{letter}.json" for letter in "abcdefgh"]
EXPECTED = [150, 150, 75, 87, 108, 120, 108, 120]
TOKENS = re.compile(r"[^\W_]+", re.UNICODE)


def normalized(value: str) -> str:
    """Normalize casing, punctuation, whitespace, ё, and decorative emoji."""
    return " ".join(TOKENS.findall(unicodedata.normalize("NFKC", value).casefold().replace("ё", "е")))


def git_blob_sha(raw: bytes) -> str:
    return hashlib.sha1(b"blob " + str(len(raw)).encode("ascii") + b"\0" + raw).hexdigest()


def walk_strings(node):
    if isinstance(node, str):
        yield node
    elif isinstance(node, list):
        for item in node:
            yield from walk_strings(item)
    elif isinstance(node, dict):
        for item in node.values():
            yield from walk_strings(item)


class StructuredGHQA(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.documents = [json.loads(path.read_text(encoding="utf-8")) for path in STAGES]
        cls.groups = [[(e, r) for e in doc["entries"] for r in e["replies"]] for doc in cls.documents]
        cls.registered_raw = (ROOT / SOURCE).read_bytes()
        cls.registered = json.loads(cls.registered_raw)
        cls.registered_texts = {
            normalized(t)
            for rec in cls.registered["records"]
            for t in [rec["answer"], *rec["variants"]]
        }
        cls.old = [r for group in cls.groups[:6] for e, r in group]
        cls.new = [r for group in cls.groups[6:] for e, r in group]
        cls.all_replies = cls.old + cls.new

    def test_real_manifest_source_hash_and_schema_compatibility(self):
        manifest = json.loads((ROOT / "manifest.json").read_text(encoding="utf-8"))
        registered = {p["path"]: p["sha256"] for p in manifest["packs"]}
        self.assertEqual(hashlib.sha256(self.registered_raw).hexdigest(), EXPECTED_SHA256)
        self.assertEqual(git_blob_sha(self.registered_raw), EXPECTED_BLOB)
        self.assertEqual(registered.get(SOURCE), EXPECTED_SHA256)
        self.assertEqual(len(self.registered["records"]), 114)
        expected_ids = {r["id"] for r in self.registered["records"]}
        seen_ids = {e["intent_id"] for doc in self.documents for e in doc["entries"]}
        self.assertEqual(expected_ids, seen_ids)
        for path, doc in zip(STAGES, self.documents):
            self.assertNotIn(path.relative_to(ROOT).as_posix(), registered)
            self.assertEqual(doc["schema_version"], 1)
            self.assertEqual(doc["stage_type"], "supplemental_contextual_reply_pool")
            self.assertIs(doc["consumer_registered"], False)
            self.assertEqual(doc["language"], "ru")
            self.assertEqual(doc["audiences"], ["all_ai_bots"])
            self.assertEqual(doc["source_pack"], SOURCE)
            self.assertEqual(doc["source_pack_manifest_sha256"], EXPECTED_SHA256)
            self.assertEqual(doc["source_pack_blob_sha"], EXPECTED_BLOB)
            for guard in ("read_only", "requires_direct_address", "requires_context_match", "no_personal_data", "no_sanctions"):
                self.assertIs(doc["constraints"][guard], True)

    def test_stage_increment_and_checkpoint(self):
        self.assertEqual([len(group) for group in self.groups], EXPECTED)
        self.assertEqual(len(self.old), 690)
        self.assertEqual(len(self.new), 228)
        self.assertEqual(len(self.all_replies), 918)
        g, h = self.documents[-2:]
        self.assertEqual((len(g["entries"]), len(h["entries"])), (54, 60))
        self.assertEqual({e["intent_id"] for e in g["entries"]} & {e["intent_id"] for e in h["entries"]}, set())
        self.assertEqual(g["checkpoint"]["remaining_total"], 4860)
        self.assertEqual(h["checkpoint"]["remaining_total"], 5280)
        self.assertEqual(g["checkpoint"]["finished_100"], 0)
        self.assertEqual(h["checkpoint"]["finished_100"], 0)
        for doc, prev, after, suffixes in [(g, 5, 10, (15, 16)), (h, 7, 12, (17, 18))]:
            for entry in doc["entries"]:
                self.assertEqual((entry["published_count"], entry["previous_staged_count"], entry["added_candidates"], entry["total_candidates_with_published"], entry["remaining"]), (3, prev, 2, after, 100 - after))
                self.assertEqual([r["id"] for r in entry["replies"]], [entry["intent_id"] + f"_supp_{s}" for s in suffixes])
        self.assertEqual(54 * 10 + 60 * 12, 1260)
        self.assertEqual(54 * 90 + 60 * 88, 10140)

    def test_exact_uniqueness_across_all_8_stages_and_registered(self):
        ids = [r["id"] for r in self.all_replies]
        answer_texts = [normalized(r["text"]) for r in self.all_replies]
        notes = [normalized(r["context_note"]) for r in self.all_replies]
        for collection in (ids, answer_texts, notes):
            self.assertTrue(all(collection))
            self.assertEqual(len(collection), len(set(collection)))
        self.assertFalse(self.registered_texts.intersection(answer_texts))

    def test_context_privacy_and_no_powers(self):
        for doc in self.documents[6:]:
            for entry in doc["entries"]:
                self.assertEqual(entry["language"], "ru")
                self.assertEqual(entry["audiences"], ["all_ai_bots"])
                for r in entry["replies"]:
                    self.assertTrue(r["id"].startswith(entry["intent_id"] + "_"))
                    self.assertEqual(r["language"], "ru")
                    self.assertEqual(r["audiences"], ["all_ai_bots"])
                    self.assertEqual(r["response_role"], "assistant_reply")
                    self.assertEqual(r["context"], "direct")
                    self.assertIs(r["read_only"], True)
                    self.assertIn("санкци", normalized(r["avoid"]))
                    self.assertGreater(len(r["text"].strip()), 35)
                    self.assertTrue(r["context_note"].strip())
                    body = r["text"] + " " + r["context_note"]
                    self.assertIsNone(re.search(r"[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}", body))
                    self.assertIsNone(re.search(r"(?i)(?:api[_-]?key|bot[_-]?token|password)\s*[:=]", body))
                    self.assertIsNone(re.search(r"(?i)\b(?:забаню|замьючу|выдаю бан|уже наказал)\b", r["text"]))

    def test_no_exact_overlap_with_any_registered_pack(self):
        manifest = json.loads((ROOT / "manifest.json").read_text(encoding="utf-8"))
        registered_strings = set()
        for pack in manifest["packs"]:
            try:
                data = json.loads((ROOT / pack["path"]).read_text(encoding="utf-8"))
            except (ValueError, UnicodeError):
                continue
            registered_strings.update(
                n for text in walk_strings(data)
                if len(text.strip()) >= 35
                if (n := normalized(text))
            )
        self.assertFalse({normalized(r["text"]) for r in self.new} & registered_strings)

    def test_close_lexical_duplicates_screened_for_new_replies(self):
        # Lexical screen is deliberately not presented as full semantic audit.
        sets = [set(TOKENS.findall(normalized(r["text"]))) for r in self.all_replies]
        prior = len(self.old)
        for i in range(prior, len(sets)):
            a = sets[i]
            for j in range(i):
                b = sets[j]
                union = len(a | b)
                score = len(a & b) / union if union else 1.0
                self.assertLess(score, 0.70, (self.all_replies[i]["id"], self.all_replies[j]["id"], score))


if __name__ == "__main__":
    unittest.main()
