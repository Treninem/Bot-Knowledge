#!/usr/bin/env python3
"""H31-H32 staged replies: counts, safe roles, context, normalized dedup and QA anchors.

These are unregistered candidates, never live bot behavior.
"""
import hashlib
import json
import re
import unittest
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FAQ_PATH = ROOT / "packs/ru/impuls_help_qa.json"


def norm(s):
    return " ".join(re.findall(r"\w+", s.lower().replace("ё", "е")))


def overlap(a, b):
    a, b = set(norm(a).split()), set(norm(b).split())
    return len(a & b) / max(1, len(a | b))


class H31H32QA(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.faq = json.loads(FAQ_PATH.read_text(encoding="utf-8"))
        cls.main_records = {x["id"]: x for x in cls.faq["records"]}
        cls.stages = [
            json.loads((ROOT / "staging/ru" /
                f"impuls_help_context_h{i}_{'20261115' if i >= 31 else '20261114'}.json"
            ).read_text(encoding="utf-8"))
            for i in range(1, 33)
        ]

    def test_total_and_registered_source(self):
        totals = Counter()
        ids = set()
        for stage in self.stages:
            self.assertFalse(stage["consumer_registered"])
            self.assertEqual(stage["stage_type"], "supplemental_contextual_reply_pool")
            self.assertEqual(stage["audiences"], ["impuls"])
            self.assertTrue(stage["constraints"]["no_sanctions"])
            self.assertTrue(stage["constraints"]["read_only"])
            for entry in stage["entries"]:
                self.assertIn(entry["intent_id"], self.main_records)
                self.assertEqual(entry["canonical_question"],
                                 self.main_records[entry["intent_id"]]["question"])
                totals[entry["intent_id"]] += len(entry["replies"])
                for reply in entry["replies"]:
                    self.assertNotIn(reply["id"], ids)
                    ids.add(reply["id"])
                    self.assertEqual(reply["response_role"], "assistant_reply")
        self.assertEqual(len(totals), 100)
        self.assertEqual(sum(totals.values()), 1596)
        remaining = sum(100 - (1 + len(self.main_records[k]["variants"]) + n)
                        for k, n in totals.items())
        self.assertEqual(remaining, 8129)
        self.assertEqual(self.stages[-1]["checkpoint"]["remaining_numeric_all_100_intents"], remaining)
        self.assertEqual(self.stages[-1]["checkpoint"]["cumulative_H1_H32"], 1596)

    def test_new_stages_have_clear_safe_answer_roles(self):
        older_texts = [
            r["text"] for stage in self.stages[:30]
            for entry in stage["entries"] for r in entry["replies"]
        ]
        older_texts += [
            x for entry in self.faq["records"]
            for x in [entry["answer"], *entry["variants"]]
        ]
        old_notes = defaultdict(list)
        for stage in self.stages[:30]:
            for entry in stage["entries"]:
                old_notes[entry["intent_id"]].extend(
                    r["context_note"] for r in entry["replies"]
                )
        self.assertEqual([len(s["entries"]) for s in self.stages[30:]], [30, 31])
        for i, stage in enumerate(self.stages[30:], 31):
            self.assertEqual(stage["checkpoint"]["new_candidates"], len(stage["entries"]))
            self.assertEqual(len({e["intent_id"] for e in stage["entries"]}),
                             len(stage["entries"]))
            for entry in stage["entries"]:
                self.assertEqual(len(entry["replies"]), 1)
                r = entry["replies"][0]
                self.assertEqual(r["id"], f"impuls_help_{entry['intent_id']}_h{i}_01")
                self.assertEqual(r["audiences"], ["impuls"])
                self.assertTrue(r["read_only"])
                self.assertEqual(r["editorial_status"], "candidate_pending_full_semantic_review")
                self.assertIn(r["context"], {"direct", "private", "group_addressed"})
                self.assertGreater(len(r["text"]), 54)
                self.assertGreater(len(r["context_note"]), 39)
                self.assertNotEqual(norm(r["text"]), norm(r["context_note"]))
                self.assertNotIn(norm(r["text"]), {norm(s) for s in older_texts})
                self.assertTrue(
                    all(overlap(r["text"], t) < 0.70 for t in older_texts),
                    r["id"] + ": close lexical answer duplicate"
                )
                self.assertTrue(
                    all(overlap(r["context_note"], t) < 0.58
                        for t in old_notes[entry["intent_id"]]),
                    r["id"] + ": close scenario duplicate"
                )
                self.assertFalse(re.search(r"https?://|t\.me/|@[A-Za-z_]|[0-9]{10,}",
                                           r["text"] + r["context_note"]))
                self.assertFalse(any(token in r["text"].lower()
                    for token in ("я уже удалил", "я забанил", "я включил режим",
                                  "я назначил администратора")))
                self.assertEqual(entry["remaining_to_target_excluding_other_prs"],
                                 100 - entry[f"total_candidates_in_main_and_H{i}"])
                older_texts.append(r["text"])
                old_notes[entry["intent_id"]].append(r["context_note"])

    def test_genuine_answers_not_swapped_scenarios(self):
        entries = {
            entry["intent_id"]: entry["replies"][0]["text"]
            for stage in self.stages[30:] for entry in stage["entries"]
        }
        for intent, required in {
            "silent_group": ["вопрос", "обращен"],
            "pulses": ["пульсы", "telegram"],
            "greeting": [],
            "quoted_setting": ["команд", "менять"],
            "request_to_stop": ["прекратить", "шут"],
            "moderation_swearing": ["мат", "адрес"],
            "pulses_vs_stars": ["пульсы", "stars"],
        }.items():
            if intent == "greeting":
                continue
            if intent not in entries:
                continue
            t = norm(entries[intent])
            self.assertTrue(all(norm(word) in t for word in required),
                            f"{intent} has an unexpected reply text")

    def test_source_hash_match_registered_pack(self):
        import hashlib
        manifest = json.loads((ROOT / "manifest.json").read_text(encoding="utf-8"))
        expected = next(item["sha256"] for item in manifest["packs"]
                        if item["path"] == "packs/ru/impuls_help_qa.json")
        self.assertEqual(hashlib.sha256(FAQ_PATH.read_bytes()).hexdigest(), expected)
        for stage in self.stages[30:]:
            self.assertEqual(stage["source_pack_manifest_sha256"], expected)
            self.assertEqual(stage["checked_source_main_sha"],
                             "6c9f430da47f137d39a72bbd28c057cfb8f6be96")


if __name__ == "__main__":
    unittest.main()
