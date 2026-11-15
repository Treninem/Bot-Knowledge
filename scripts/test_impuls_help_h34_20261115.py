#!/usr/bin/env python3
"""Validate H34 staged context answers against the registered FAQ and all H1-H33."""
import json
import re
import unittest
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def norm(text):
    return " ".join(re.findall(r"\w+", text.casefold().replace("ё", "е")))


def jac(a, b):
    x, y = set(norm(a).split()), set(norm(b).split())
    return len(x & y) / max(1, len(x | y))


class H34QA(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.faq = json.loads((ROOT / "packs/ru/impuls_help_qa.json").read_text(encoding="utf-8"))
        cls.faq_by_id = {r["id"]: r for r in cls.faq["records"]}
        cls.stages = [
            json.loads((ROOT / f"staging/ru/impuls_help_context_h{i}_{'20261115' if i >= 31 else '20261114'}.json").read_text(encoding="utf-8"))
            for i in range(1, 35)
        ]
        cls.stage = cls.stages[-1]

    def test_counts_and_source_contract(self):
        counter = Counter()
        seen_ids = set()
        for st in self.stages:
            self.assertFalse(st["consumer_registered"])
            self.assertTrue(st["constraints"]["no_sanctions"])
            for entry in st["entries"]:
                self.assertIn(entry["intent_id"], self.faq_by_id)
                for reply in entry["replies"]:
                    self.assertNotIn(reply["id"], seen_ids, reply["id"])
                    seen_ids.add(reply["id"])
                    counter[entry["intent_id"]] += 1
        self.assertEqual(len(counter), 100)
        self.assertEqual(sum(counter.values()), 1675)
        self.assertEqual(sum(100 - (1 + len(self.faq_by_id[k]["variants"]) + n) for k, n in counter.items()), 8050)
        self.assertEqual(self.stage["source_pack_manifest_sha256"],
                         next(pack["sha256"] for pack in json.loads((ROOT / "manifest.json").read_text(encoding="utf-8"))["packs"]
                              if pack["path"] == "packs/ru/impuls_help_qa.json"))
        self.assertEqual(self.stage["checkpoint"]["cumulative_H1_H34"], 1675)
        self.assertEqual(self.stage["checkpoint"]["remaining_numeric_all_100_intents"], 8050)
        self.assertEqual(self.stage["checkpoint"]["editorially_approved_new"], 0)

    def test_h34_40_replies_20_intents(self):
        self.assertEqual(len(self.stage["entries"]), 20)
        self.assertEqual(sum(len(e["replies"]) for e in self.stage["entries"]), 40)
        older = Counter()
        for st in self.stages[:-1]:
            for entry in st["entries"]:
                older[entry["intent_id"]] += len(entry["replies"])
        for entry in self.stage["entries"]:
            key = entry["intent_id"]
            base = 1 + len(self.faq_by_id[key]["variants"])
            self.assertEqual(entry["canonical_question"], self.faq_by_id[key]["question"])
            self.assertEqual(entry["published_count"], base)
            self.assertEqual(entry["earlier_staged_candidates"], older[key])
            self.assertEqual(entry["added_candidates"], 2)
            self.assertEqual(len(entry["replies"]), 2)
            self.assertEqual(entry["total_candidates_in_main_and_H34"], base + older[key] + 2)
            self.assertEqual(entry["remaining_to_target_excluding_other_prs"],
                             100 - entry["total_candidates_in_main_and_H34"])
            for idx, reply in enumerate(entry["replies"], 1):
                self.assertEqual(reply["id"], f"impuls_help_{key}_h34_{idx:02d}")
                self.assertEqual(reply["response_role"], "assistant_reply")
                self.assertEqual(reply["editorial_status"], "candidate_pending_full_semantic_review")
                self.assertTrue(reply["read_only"])
                self.assertIn(reply["context"], {"private", "direct", "group_addressed"})
                self.assertGreaterEqual(len(reply["text"]), 75)
                self.assertGreaterEqual(len(reply["context_note"]), 55)
                self.assertNotEqual(norm(reply["text"]), norm(reply["context_note"]))
                self.assertFalse(re.search(r"https?://|t\.me/|@[A-Za-z_]|[0-9]{10,}",
                                           reply["text"] + reply["context_note"]))

    def test_no_new_exact_or_high_lexical_duplicates(self):
        old_texts = [x for r in self.faq["records"] for x in [r["answer"], *r["variants"]]]
        old_notes = defaultdict(list)
        for st in self.stages[:-1]:
            for e in st["entries"]:
                old_texts += [r["text"] for r in e["replies"]]
                old_notes[e["intent_id"]] += [r["context_note"] for r in e["replies"]]
        old_normalized = set(map(norm, old_texts))
        for e in self.stage["entries"]:
            for r in e["replies"]:
                self.assertNotIn(norm(r["text"]), old_normalized, r["id"])
                self.assertTrue(all(jac(r["text"], old) < .70 for old in old_texts), r["id"])
                self.assertTrue(all(jac(r["context_note"], old) < .58
                                    for old in old_notes[e["intent_id"]]), r["id"])
                old_texts.append(r["text"])
                old_normalized.add(norm(r["text"]))
                old_notes[e["intent_id"]].append(r["context_note"])

    def test_greeting_intent_semantics_repaired(self):
        """Answer the canonical question about rules, not merely the actual greeting."""
        count = 0
        for st in self.stages:
            for entry in st["entries"]:
                if entry["intent_id"] != "greeting":
                    continue
                self.assertEqual(entry["canonical_question"],
                                 self.faq_by_id["greeting"]["question"])
                for reply in entry["replies"]:
                    answer = norm(reply["text"])
                    self.assertRegex(answer, r"правил|запрет|справк", reply["id"])
                    self.assertGreater(len(reply["text"]), 55)
                    count += 1
        self.assertGreaterEqual(count, 19)


if __name__ == "__main__":
    unittest.main()
