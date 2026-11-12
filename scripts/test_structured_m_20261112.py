"""Staging-only continuation of 60 structured intents, suffixes 52 through 56."""
import hashlib
import json
import re
import unicodedata
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "packs/ru/structured_information_qa.json"
MANIFEST = ROOT / "manifest.json"
L = ROOT / "staging/ru/structured_information_20261111_delta_l.json"
M = ROOT / "staging/ru/structured_information_20261112_delta_m.json"
EARLIER = [
    ROOT / f"staging/ru/structured_information_20261111_delta_{letter}.json"
    for letter in "abcdefghij"
]
SOURCE_SHA = "55b3f6126d36cd92687d005b7fedf5a11df9ee61cf453103accdf1f13c8498f0"
SOURCE_BLOB = "8b3d596b5b50d3d319ebf450c96d5623fc99d26a"
WORDS = re.compile(r"[^\W_]+", re.UNICODE)
MAIL = re.compile(r"[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}")


def normalized(value):
    return " ".join(WORDS.findall(unicodedata.normalize("NFKC", value).casefold().replace("ё", "е")))


def replies(data):
    return [reply for entry in data["entries"] for reply in entry["replies"]]


class StructuredMContinuation(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.l = json.loads(L.read_text("utf-8"))
        cls.m = json.loads(M.read_text("utf-8"))
        cls.current = replies(cls.m)
        cls.prior = replies(cls.l)
        for path in EARLIER:
            cls.prior.extend(replies(json.loads(path.read_text("utf-8"))))
        source = json.loads(SOURCE.read_text("utf-8"))
        cls.source_answers = [
            text for item in source["records"]
            for text in (item["answer"], *item["variants"])
        ]

    def test_source_integrity_and_no_registration(self):
        raw = SOURCE.read_bytes()
        self.assertEqual(hashlib.sha256(raw).hexdigest(), SOURCE_SHA)
        blob_header = b"blob " + str(len(raw)).encode() + b"\0"
        self.assertEqual(hashlib.sha1(blob_header + raw).hexdigest(), SOURCE_BLOB)
        manifest = json.loads(MANIFEST.read_text("utf-8"))
        packs = {p["path"]: p["sha256"] for p in manifest["packs"]}
        self.assertEqual(packs["packs/ru/structured_information_qa.json"], SOURCE_SHA)
        self.assertNotIn("staging/ru/structured_information_20261112_delta_m.json", packs)

    def test_per_intent_progress_and_context(self):
        data = self.m
        self.assertEqual(data["audiences"], ["all_ai_bots"])
        self.assertEqual(data["language"], "ru")
        self.assertFalse(data["consumer_registered"])
        for k in ("read_only", "requires_direct_address", "requires_context_match", "no_personal_data", "no_sanctions"):
            self.assertTrue(data["constraints"][k], k)
        self.assertEqual(len(data["entries"]), 60)
        self.assertEqual(len(self.current), 300)
        self.assertEqual(len(replies(self.l)), 1860)
        self.assertEqual(data["checkpoint"]["combined_L_M_replies"], 2160)
        self.assertEqual(data["checkpoint"]["remaining_total"], 3000)
        self.assertEqual(data["checkpoint"]["next_suffix"], 57)
        self.assertEqual([e["intent_id"] for e in data["entries"]], [e["intent_id"] for e in self.l["entries"]])
        for e in data["entries"]:
            self.assertEqual((e["published_count"], e["previous_staged_count"], e["prior_L_count"]), (3, 11, 31))
            self.assertEqual((e["added_candidates"], e["total_candidates_with_published"], e["remaining"], e["target"]), (5, 50, 50, 100))
            self.assertEqual([r["id"] for r in e["replies"]], [f"{e['intent_id']}_supp_52", f"{e['intent_id']}_supp_53", f"{e['intent_id']}_supp_54", f"{e['intent_id']}_supp_55", f"{e['intent_id']}_supp_56"])

    def test_unique_safe_and_lexical_distance(self):
        older_text = self.source_answers + [r["text"] for r in self.prior]
        known = {normalized(s) for s in older_text}
        token_sets = [set(s.split()) for s in known if s]
        ids, notes = set(), set()
        for r in self.current:
            n, context_note = normalized(r["text"]), normalized(r["context_note"])
            self.assertTrue(r["id"] not in ids, r["id"])
            self.assertTrue(n not in known, r["id"])
            self.assertTrue(context_note not in notes, r["id"])
            self.assertGreaterEqual(len(r["text"]), 45)
            self.assertGreaterEqual(len(r["context_note"]), 35)
            self.assertEqual(r["language"], "ru")
            self.assertEqual(r["context"], "direct")
            self.assertEqual(r["audiences"], ["all_ai_bots"])
            self.assertEqual(r["response_role"], "assistant_reply")
            self.assertTrue(r["read_only"])
            self.assertIsNone(MAIL.search(r["text"] + " " + r["context_note"]))
            tokens = set(n.split())
            for prior in token_sets:
                self.assertLess(len(tokens & prior) / len(tokens | prior), .70, r["id"])
            known.add(n)
            ids.add(r["id"])
            notes.add(context_note)
            token_sets.append(tokens)


if __name__ == "__main__":
    unittest.main()
