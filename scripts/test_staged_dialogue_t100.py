#!/usr/bin/env python3
"""Offline, stdlib-only checks for T96–T100 staged conversational candidates.

Run: python -B scripts/test_staged_dialogue_t100.py
Only candidate staging is checked; this does not establish live consumer behavior.
"""
import json
import re
import string
import unittest
import unicodedata
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = "staging/ru/dialogue_repair_t96.qa.v1.json"
DELTA = [
    "staging/ru/dialogue_repair_t97_delta.json",
    "staging/ru/dialogue_repair_t98_context_delta.json",
    "staging/ru/dialogue_repair_t99_context_delta.json",
    "staging/ru/dialogue_repair_t100_context_delta.json",
]
SENSITIVE = re.compile(
    r"(?i)(?:ghp_[a-z0-9]{12,}|sk-[a-z0-9]{12,}|"
    r"bearer\s+[a-z0-9._-]{12,}|"
    r"[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,})"
)


def read_json(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def normalized(text):
    text = unicodedata.normalize("NFKC", text).casefold().replace("ё", "е")
    text = "".join(" " if unicodedata.category(c)[0] in ("P", "S") else c for c in text)
    return " ".join(text.split())


def collect():
    base = read_json(BASE)
    deltas = [read_json(path) for path in DELTA]
    initial = {r["id"]: [r["answer"], *r["variants"]] for r in base["records"]}
    for i, doc in enumerate(deltas):
        for entry in doc["entries"]:
            extra = ([entry["reply"], *entry["additional_replies"]]
                     if i == 0 else [v["text"] for v in entry["replies"]])
            initial[entry["intent_id"]].extend(extra)
    return base, deltas, initial


class StagedDialogueT100(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.base, cls.deltas, cls.by_intent = collect()

    def test_intent_and_answer_counts(self):
        self.assertEqual(len(self.by_intent), 45)
        self.assertEqual(set(map(len, self.by_intent.values())), {13})
        self.assertEqual(sum(map(len, self.by_intent.values())), 585)

    def test_normalized_answer_uniqueness(self):
        answers = [normalized(v) for vs in self.by_intent.values() for v in vs]
        self.assertEqual(len(answers), len(set(answers)))

    def test_question_and_alias_uniqueness(self):
        questions = [normalized(s) for r in self.base["records"]
                     for s in [r["question"], *r["aliases"]]]
        self.assertEqual(len(questions), 135)
        self.assertEqual(len(questions), len(set(questions)))

    def test_stable_ids_and_contexts(self):
        source = {r["id"]: r for r in self.base["records"]}
        self.assertEqual(len(source), 45)
        self.assertEqual(len(self.base["records"]), 45)
        for doc in self.deltas:
            self.assertEqual(len(doc["entries"]), 45)
            self.assertEqual(len({e["intent_id"] for e in doc["entries"]}), 45)
            for e in doc["entries"]:
                self.assertIn(e["intent_id"], source)
                self.assertEqual(e["contexts"], source[e["intent_id"]]["contexts"])
        self.assertEqual(source["dialogue_t96_041"]["contexts"], ["group_addressed"])

    def test_contextual_candidates_are_scoped(self):
        for doc in self.deltas[1:]:
            for e in doc["entries"]:
                for v in e["replies"]:
                    self.assertTrue(v["context_note"].strip())
                    self.assertTrue(v["avoid"].strip())
                    self.assertGreater(len(v["text"]), 30)

    def test_t99_t100_selection_notes_differ(self):
        notes = [normalized(v["context_note"]) for d in self.deltas[2:]
                 for e in d["entries"] for v in e["replies"]]
        self.assertEqual(len(notes), 90)
        self.assertEqual(len(notes), len(set(notes)))

    def test_privacy_tokens_not_present_in_new_answers(self):
        for d in self.deltas[2:]:
            for e in d["entries"]:
                for v in e["replies"]:
                    self.assertIsNone(SENSITIVE.search(v["text"]))

    def test_unregistered_and_manifest_unchanged(self):
        manifest = read_json("manifest.json")
        registered = {p["path"] for p in manifest["packs"]}
        for p in [BASE, *DELTA]:
            self.assertNotIn(p, registered)
        for d in self.deltas:
            self.assertFalse(d["consumer_registered"])
        self.assertEqual(len(manifest["packs"]), 38)

    def test_each_batch_is_exactly_45_new_replies(self):
        self.assertEqual(len(self.deltas[2]["entries"]), 45)
        self.assertEqual(len(self.deltas[3]["entries"]), 45)
        self.assertTrue(all(len(e["replies"]) == 1
                            for d in self.deltas[2:] for e in d["entries"]))


if __name__ == "__main__":
    unittest.main()
