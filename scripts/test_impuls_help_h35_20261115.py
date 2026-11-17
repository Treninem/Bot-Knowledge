#!/usr/bin/env python3
"""H35: exact-head QA for 40 context replies on 20 further stable ImPULS intents."""
import json
import re
import unittest
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def norm(value):
    return " ".join(re.findall(r"\w+", value.casefold().replace("ё", "е")))


def jac(a, b):
    x, y = set(norm(a).split()), set(norm(b).split())
    return len(x & y) / max(1, len(x | y))


class H35QA(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.faq = json.loads((ROOT / "packs/ru/impuls_help_qa.json").read_text(encoding="utf-8"))
        cls.by_id = {r["id"]: r for r in cls.faq["records"]}
        cls.stages = [
            json.loads((ROOT / f"staging/ru/impuls_help_context_h{i}_{'20261115' if i >= 31 else '20261114'}.json").read_text(encoding="utf-8"))
            for i in range(1, 36)
        ]
        cls.current = cls.stages[-1]

    def test_counts_ids_and_contract(self):
        counts = Counter()
        ids = set()
        for stage in self.stages:
            self.assertFalse(stage["consumer_registered"])
            self.assertTrue(stage["constraints"]["read_only"])
            self.assertTrue(stage["constraints"]["no_sanctions"])
            for e in stage["entries"]:
                self.assertIn(e["intent_id"], self.by_id)
                for r in e["replies"]:
                    self.assertNotIn(r["id"], ids, r["id"])
                    ids.add(r["id"])
                    counts[e["intent_id"]] += 1
        self.assertEqual(len(counts), 100)
        self.assertEqual(sum(counts.values()), 1715)
        self.assertEqual(sum(100 - (1 + len(self.by_id[i]["variants"]) + n) for i, n in counts.items()), 8010)
        self.assertEqual(self.current["checkpoint"]["cumulative_H1_H35"], 1715)
        self.assertEqual(self.current["checkpoint"]["remaining_numeric_all_100_intents"], 8010)
        self.assertEqual(self.current["checkpoint"]["editorially_approved_new"], 0)
        manifest = json.loads((ROOT / "manifest.json").read_text(encoding="utf-8"))
        sha = next(p["sha256"] for p in manifest["packs"] if p["path"] == self.current["source_pack"])
        self.assertEqual(self.current["source_pack_manifest_sha256"], sha)

    def test_original_contextual_pairs(self):
        previous = Counter()
        for stage in self.stages[:-1]:
            for e in stage["entries"]:
                previous[e["intent_id"]] += len(e["replies"])
        self.assertEqual(len(self.current["entries"]), 20)
        self.assertEqual(len(set(e["intent_id"] for e in self.current["entries"])), 20)
        self.assertEqual(sum(len(e["replies"]) for e in self.current["entries"]), 40)
        previous_h34 = {e["intent_id"] for e in self.stages[-2]["entries"]}
        for e in self.current["entries"]:
            key = e["intent_id"]
            self.assertNotIn(key, previous_h34)
            base = 1 + len(self.by_id[key]["variants"])
            self.assertEqual(e["canonical_question"], self.by_id[key]["question"])
            self.assertEqual(e["published_count"], base)
            self.assertEqual(e["earlier_staged_candidates"], previous[key])
            self.assertEqual(e["total_candidates_in_main_and_H35"], base + previous[key] + 2)
            self.assertEqual(e["remaining_to_target_excluding_other_prs"], 100 - e["total_candidates_in_main_and_H35"])
            for index, reply in enumerate(e["replies"], 1):
                self.assertEqual(reply["id"], f"impuls_help_{key}_h35_{index:02d}")
                self.assertEqual(reply["response_role"], "assistant_reply")
                self.assertEqual(reply["editorial_status"], "candidate_pending_full_semantic_review")
                self.assertTrue(reply["read_only"])
                self.assertIn(reply["context"], {"private", "direct", "group_addressed"})
                self.assertGreaterEqual(len(reply["text"]), 75)
                self.assertGreaterEqual(len(reply["context_note"]), 55)
                self.assertNotEqual(norm(reply["text"]), norm(reply["context_note"]))
                self.assertFalse(re.search(r"https?://|t\.me/|@[A-Za-z_]|[0-9]{10,}", reply["text"] + reply["context_note"]))

    def test_duplicates_vs_every_earlier_stage(self):
        old_texts = [x for r in self.faq["records"] for x in [r["answer"], *r["variants"]]]
        old_notes = defaultdict(list)
        for stage in self.stages[:-1]:
            for e in stage["entries"]:
                old_texts.extend(r["text"] for r in e["replies"])
                old_notes[e["intent_id"]].extend(r["context_note"] for r in e["replies"])
        normalized = set(map(norm, old_texts))
        for e in self.current["entries"]:
            for reply in e["replies"]:
                self.assertNotIn(norm(reply["text"]), normalized, reply["id"])
                self.assertTrue(all(jac(reply["text"], p) < .70 for p in old_texts), reply["id"])
                self.assertTrue(all(jac(reply["context_note"], p) < .58 for p in old_notes[e["intent_id"]]), reply["id"])
                old_texts.append(reply["text"])
                normalized.add(norm(reply["text"]))
                old_notes[e["intent_id"]].append(reply["context_note"])

    def test_semantic_anchors(self):
        by_id = {e["intent_id"]: [r["text"] for r in e["replies"]] for e in self.current["entries"]}
        checks = {
            "acknowledgement_only": ("понятно", "ок"),
            "game_start_diagnosis": ("игра", "игр"),
            "settings_two_admins": ("просьб", "администратор"),
            "version_runtime": ("README", "верс"),
            "request_to_stop": ("прекратить", "закончить"),
        }
        for key, tokens in checks.items():
            answers = by_id[key]
            for text, token in zip(answers, tokens):
                self.assertIn(token.casefold(), text.casefold(), key)


if __name__ == "__main__":
    unittest.main()
