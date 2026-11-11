"""QA for 228 original RU structured-information replies: stages E and F."""
from __future__ import annotations

import hashlib
import json
import re
import unicodedata
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PREFIX = "staging/ru/structured_information_20261111_delta_"
STAGES = [ROOT / (PREFIX + letter + ".json") for letter in "abcdef"]
EXPECTED_SIZES = [150, 150, 75, 87, 108, 120]
SOURCE = "packs/ru/structured_information_qa.json"
SOURCE_SHA256 = "55b3f6126d36cd92687d005b7fedf5a11df9ee61cf453103accdf1f13c8498f0"
SOURCE_BLOB_SHA = "8b3d596b5b50d3d319ebf450c96d5623fc99d26a"
TOKENS = re.compile(r"[^\W_]+", re.UNICODE)


def normal(text: str) -> str:
    return " ".join(TOKENS.findall(unicodedata.normalize("NFKC", text).casefold().replace("ё", "е")))


def git_blob_sha(raw: bytes) -> str:
    return hashlib.sha1(b"blob " + str(len(raw)).encode("ascii") + b"\0" + raw).hexdigest()


class StructuredFollowupQA(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.docs = [json.loads(path.read_text(encoding="utf-8")) for path in STAGES]
        cls.groups = [[(e, r) for e in doc["entries"] for r in e["replies"]] for doc in cls.docs]
        cls.all_replies = [r for group in cls.groups for _, r in group]

    def test_exact_registered_source_sha_and_unregistered_scope(self) -> None:
        manifest = json.loads((ROOT / "manifest.json").read_text(encoding="utf-8"))
        registered = {item["path"]: item["sha256"] for item in manifest["packs"]}
        raw = (ROOT / SOURCE).read_bytes()
        self.assertEqual(hashlib.sha256(raw).hexdigest(), SOURCE_SHA256)
        self.assertEqual(registered[SOURCE], SOURCE_SHA256)
        self.assertEqual(git_blob_sha(raw), SOURCE_BLOB_SHA)
        source = json.loads(raw)
        self.assertEqual(len(source["records"]), 114)
        self.assertEqual({x["id"] for x in source["records"]}, {e["intent_id"] for d in self.docs for e in d["entries"]})
        for path, stage in zip(STAGES, self.docs):
            self.assertNotIn(path.relative_to(ROOT).as_posix(), registered)
            self.assertIs(stage["consumer_registered"], False)
            self.assertEqual(stage["stage_type"], "supplemental_contextual_reply_pool")
            self.assertEqual(stage["language"], "ru")
            self.assertEqual(stage["audiences"], ["all_ai_bots"])
            self.assertEqual(stage["source_pack"], SOURCE)
            self.assertEqual(stage["source_pack_manifest_sha256"], SOURCE_SHA256)
            self.assertEqual(stage["source_pack_blob_sha"], SOURCE_BLOB_SHA)
            for guard in ("read_only", "requires_direct_address", "requires_context_match", "no_personal_data", "no_sanctions"):
                self.assertIs(stage["constraints"][guard], True)

    def test_exact_incremental_counts_and_stable_intents(self) -> None:
        self.assertEqual([len(g) for g in self.groups], EXPECTED_SIZES)
        self.assertEqual(len(self.all_replies), 690)
        self.assertEqual(len(self.groups[4]) + len(self.groups[5]), 228)
        self.assertEqual(len(self.docs[4]["entries"]), 54)
        self.assertEqual(len(self.docs[5]["entries"]), 60)
        ids = [e["intent_id"] for d in self.docs for e in d["entries"]]
        self.assertEqual(len(set(ids)), 114)
        for e in self.docs[4]["entries"]:
            self.assertEqual((e["published_count"], e["previous_staged_count"], e["added_candidates"], e["total_candidates_with_published"], e["remaining"]), (3, 3, 2, 8, 92))
            self.assertEqual([r["id"] for r in e["replies"]], [e["intent_id"] + "_supp_13", e["intent_id"] + "_supp_14"])
        for e in self.docs[5]["entries"]:
            self.assertEqual((e["published_count"], e["previous_staged_count"], e["added_candidates"], e["total_candidates_with_published"], e["remaining"]), (3, 5, 2, 10, 90))
            self.assertEqual([r["id"] for r in e["replies"]], [e["intent_id"] + "_supp_15", e["intent_id"] + "_supp_16"])
        self.assertEqual(self.docs[4]["checkpoint"]["remaining_total"], 4968)
        self.assertEqual(self.docs[5]["checkpoint"]["remaining_total"], 5400)

    def test_identifiers_and_normalized_texts_and_contexts_unique(self) -> None:
        ids = [r["id"] for r in self.all_replies]
        texts = [normal(r["text"]) for r in self.all_replies]
        notes = [normal(r["context_note"]) for r in self.all_replies]
        for values in (ids, texts, notes):
            self.assertTrue(all(values))
            self.assertEqual(len(values), len(set(values)))

    def test_direct_context_privacy_and_no_actions(self) -> None:
        for e, r in [pair for group in self.groups for pair in group]:
            self.assertTrue(r["id"].startswith(e["intent_id"] + "_"))
            self.assertEqual(r["language"], "ru")
            self.assertEqual(r["audiences"], ["all_ai_bots"])
            self.assertEqual(r["context"], "direct")
            self.assertIs(r["read_only"], True)
            self.assertIn("санкци", normal(r["avoid"]))
            self.assertTrue(r["context_note"].strip())
            self.assertFalse(re.search(r"[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}", r["text"] + r["context_note"]))
            self.assertFalse(re.search(r"(?i)(?:bot[_-]?token|password|api[_-]?key)\s*[:=]", r["text"] + r["context_note"]))
            self.assertFalse(re.search(r"(?i)\b(я (?:забаню|замьючу|удалю сообщение)|выдаю бан|уже наказал)\b", r["text"]))

    def test_registered_reply_exact_overlap(self) -> None:
        source = json.loads((ROOT / SOURCE).read_text(encoding="utf-8"))
        registered = {normal(t) for rec in source["records"] for t in [rec["answer"], *rec["variants"]]}
        self.assertFalse(registered.intersection({normal(r["text"]) for r in self.all_replies}))

    def test_lexical_similarity_review_gate(self) -> None:
        # Lexical screening is not a semantic-quality guarantee.
        wordsets = [set(TOKENS.findall(normal(r["text"]))) for r in self.all_replies]
        for i, a in enumerate(wordsets):
            for b in wordsets[i+1:]:
                overlap = len(a & b)
                union = len(a) + len(b) - overlap
                self.assertLess(overlap / union if union else 1.0, 0.75)

    def test_complete_checkpoint_accounting(self) -> None:
        self.assertEqual(sum(len(d["entries"]) for d in self.docs[:4]), 114)
        self.assertEqual(sum(len(d["entries"]) for d in self.docs[4:]), 114)
        self.assertEqual(54 * 8 + 60 * 10, 1032)
        self.assertEqual(54 * 92 + 60 * 90, 10368)
        self.assertEqual(self.docs[4]["checkpoint"]["finished_100"], 0)
        self.assertEqual(self.docs[5]["checkpoint"]["finished_100"], 0)


if __name__ == "__main__":
    unittest.main()
