#!/usr/bin/env python3
"""Offline checks for unregistered T96–T102 dialogue candidates.

Usage: python -B scripts/test_staged_dialogue_t102.py
No GitHub Actions, network, consumer deployment or paid services required.
This is not a substitute for consumer E2E, semantic review or exact-head CI.
"""
import json
import re
import unittest
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = "staging/ru/dialogue_repair_t96.qa.v1.json"
DELTA = [
    "staging/ru/dialogue_repair_t97_delta.json",
    "staging/ru/dialogue_repair_t98_context_delta.json",
    "staging/ru/dialogue_repair_t99_context_delta.json",
    "staging/ru/dialogue_repair_t100_context_delta.json",
    "staging/ru/dialogue_repair_t101_context_delta.json",
    "staging/ru/dialogue_repair_t102_context_delta.json",
]
SENSITIVE = re.compile(
    r"(?i)(?:ghp_[a-z0-9]{12,}|sk-[a-z0-9]{12,}|"
    r"bearer\s+[a-z0-9._-]{12,}|"
    r"[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,}|"
    r"\b(?:user_id|chat_id|bot_token|ban_chat_member|kick_chat_member)\b)"
)

def read(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))

def norm(text):
    text = unicodedata.normalize("NFKC", text).casefold().replace("ё", "е")
    text = "".join(" " if unicodedata.category(c)[0] in ("P", "S") else c for c in text)
    return " ".join(text.split())

def collect():
    base = read(BASE)
    deltas = [read(p) for p in DELTA]
    by_id = {rec["id"]: [rec["answer"], *rec["variants"]]
             for rec in base["records"]}
    for index, d in enumerate(deltas):
        for entry in d["entries"]:
            replies = ([entry["reply"], *entry["additional_replies"]] if index == 0
                       else [item["text"] for item in entry["replies"]])
            by_id[entry["intent_id"]].extend(replies)
    return base, deltas, by_id

class StagedDialogueT102(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.base, cls.deltas, cls.by_id = collect()

    def test_stable_intents_and_total(self):
        self.assertEqual(len(self.base["records"]), 45)
        self.assertEqual(len(self.by_id), 45)
        self.assertEqual({len(v) for v in self.by_id.values()}, {17})
        self.assertEqual(sum(map(len, self.by_id.values())), 765)

    def test_unique_canonical_questions_aliases_and_ids(self):
        records = self.base["records"]
        self.assertEqual(len({r["id"] for r in records}), 45)
        queries = [norm(q) for r in records for q in [r["question"], *r["aliases"]]]
        self.assertEqual(len(queries), 135)
        self.assertEqual(len(queries), len(set(queries)))

    def test_no_exact_duplicate_answers(self):
        all_answers = [norm(x) for answers in self.by_id.values() for x in answers]
        self.assertEqual(len(all_answers), len(set(all_answers)))

    def test_each_delta_preserves_intent_and_context(self):
        base_map = {r["id"]: r for r in self.base["records"]}
        self.assertEqual(base_map["dialogue_t96_041"]["contexts"], ["group_addressed"])
        for delta in self.deltas:
            self.assertEqual(delta["consumer_registered"], False)
            self.assertEqual(delta["language"], "ru")
            self.assertEqual(len(delta["entries"]), 45)
            self.assertEqual(len({e["intent_id"] for e in delta["entries"]}), 45)
            for entry in delta["entries"]:
                rec = base_map[entry["intent_id"]]
                self.assertEqual(entry["contexts"], rec["contexts"])

    def test_t102_shape_and_conditions(self):
        latest = self.deltas[-1]
        self.assertEqual(latest["stage_type"], "supplemental_contextual_reply_pool")
        self.assertEqual(latest["base_intent_file"], BASE)
        self.assertEqual(len(latest["entries"]), 45)
        notes = []
        for entry in latest["entries"]:
            self.assertEqual(len(entry["replies"]), 2)
            for reply in entry["replies"]:
                self.assertGreaterEqual(len(reply["text"].strip()), 35)
                self.assertGreaterEqual(len(reply["context_note"].strip()), 10)
                self.assertGreaterEqual(len(reply["avoid"].strip()), 10)
                self.assertLessEqual(len(reply["text"]), 1600)
                self.assertIsNone(SENSITIVE.search(reply["text"]))
                self.assertIsNone(SENSITIVE.search(reply["context_note"]))
                self.assertIsNone(SENSITIVE.search(reply["avoid"]))
                notes.append(norm(reply["context_note"]))
        self.assertEqual(len(notes), 90)
        self.assertEqual(len(set(notes)), 90)

    def test_t102_checkpoint(self):
        c = self.deltas[-1]["checkpoint"]
        self.assertEqual(c["previous_candidates"], 675)
        self.assertEqual(c["added_candidates"], 90)
        self.assertEqual(c["total_candidates"], 765)
        self.assertEqual(c["distinct_intents"], 45)
        self.assertEqual(c["replies_per_intent"], 17)
        self.assertEqual(c["remaining_per_intent"], 83)
        self.assertEqual(c["completed_100"], 0)

    def test_staging_not_registered_in_consumer_snapshot(self):
        manifest = read("manifest.json")
        registered = {p["path"] for p in manifest["packs"]}
        self.assertEqual(len(registered), len(manifest["packs"]))
        for candidate in [BASE, *DELTA]:
            self.assertNotIn(candidate, registered)
        for record in self.base["records"]:
            self.assertLessEqual(len(record.get("variants", [])), 8)
            self.assertEqual(record["constraints"]["read_only"], True)
            self.assertEqual(record["constraints"]["no_personal_data"], True)

    def test_t102_exact_nonoverlap_with_registered_qa(self):
        candidates = {norm(r["text"]) for e in self.deltas[-1]["entries"] for r in e["replies"]}
        other = set()
        checked = 0
        for p in read("manifest.json")["packs"]:
            if not p["path"].endswith("_qa.json"):
                continue
            data = read(p["path"])
            for r in data["records"]:
                for value in [r["answer"], *r.get("variants", [])]:
                    other.add(norm(value))
                checked += 1
        self.assertGreaterEqual(checked, 100)
        self.assertFalse(candidates.intersection(other))

    def test_all_new_replies_are_nonempty_and_safe(self):
        latest = [v["text"] for e in self.deltas[-1]["entries"] for v in e["replies"]]
        for reply in latest:
            self.assertTrue(reply.strip())
            self.assertIsNone(SENSITIVE.search(reply))
            self.assertNotIn("https://t.me/", reply)

if __name__ == "__main__":
    unittest.main()
