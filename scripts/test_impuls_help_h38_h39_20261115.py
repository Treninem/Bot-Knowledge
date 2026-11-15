#!/usr/bin/env python3
"""H38-H39: actual progress, context, role, privacy, and lexical regression checks."""
import json
import re
import unittest
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def norm(text):
    return " ".join(re.findall(r"\w+", text.casefold().replace("ё", "е")))


def overlap(left, right):
    a, b = set(norm(left).split()), set(norm(right).split())
    return len(a & b) / max(1, len(a | b))


class H38H39QA(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.faq = json.loads((ROOT / "packs/ru/impuls_help_qa.json").read_text("utf-8"))
        cls.known = {r["id"]: r for r in cls.faq["records"]}
        cls.stages = []
        for number in range(1, 40):
            date = "20261115" if number >= 31 else "20261114"
            path = ROOT / f"staging/ru/impuls_help_context_h{number}_{date}.json"
            cls.stages.append(json.loads(path.read_text("utf-8")))
        cls.new = cls.stages[37:39]

    def test_full_unique_counts(self):
        counts = Counter()
        ids = set()
        for stage in self.stages:
            self.assertFalse(stage["consumer_registered"])
            self.assertTrue(stage["constraints"]["read_only"])
            self.assertTrue(stage["constraints"]["no_sanctions"])
            for entry in stage["entries"]:
                self.assertIn(entry["intent_id"], self.known)
                for reply in entry["replies"]:
                    self.assertNotIn(reply["id"], ids, reply["id"])
                    ids.add(reply["id"])
                    counts[entry["intent_id"]] += 1
        self.assertEqual(len(counts), 100)
        self.assertEqual(sum(counts.values()), 1835)
        self.assertEqual(sum(100 - 1 - len(self.known[k]["variants"]) - n
                             for k, n in counts.items()), 7890)
        self.assertEqual(self.new[0]["checkpoint"]["cumulative_H1_H38"], 1815)
        self.assertEqual(self.new[1]["checkpoint"]["cumulative_H1_H39"], 1835)
        self.assertEqual(self.new[1]["checkpoint"]["remaining_numeric_all_100_intents"], 7890)
        self.assertEqual(self.new[1]["checkpoint"]["editorially_approved_new"], 0)
        self.assertEqual(self.new[1]["checkpoint"]["certified_100_sets"], 0)

    def test_context_semantics_and_source(self):
        import hashlib
        manifest = json.loads((ROOT / "manifest.json").read_text("utf-8"))
        registered = {x["path"]: x["sha256"] for x in manifest["packs"]}
        for i, stage in enumerate(self.new, start=38):
            self.assertEqual(stage["source_pack_manifest_sha256"], registered[stage["source_pack"]])
            self.assertEqual(hashlib.sha256((ROOT / stage["source_pack"]).read_bytes()).hexdigest(),
                             registered[stage["source_pack"]])
            previous = Counter()
            for old in self.stages[:i-1]:
                for entry in old["entries"]:
                    previous[entry["intent_id"]] += len(entry["replies"])
            self.assertEqual(len(stage["entries"]), 20)
            self.assertEqual(len({e["intent_id"] for e in stage["entries"]}), 20)
            for entry in stage["entries"]:
                key = entry["intent_id"]
                base = 1 + len(self.known[key]["variants"])
                self.assertEqual(entry["canonical_question"], self.known[key]["question"])
                self.assertEqual(entry["published_count"], base)
                self.assertEqual(entry["earlier_staged_candidates"], previous[key])
                self.assertEqual(entry["added_candidates"], 1)
                self.assertEqual(entry["remaining_to_target_excluding_other_prs"],
                                 99 - base - previous[key])
                self.assertEqual(entry[f"total_candidates_in_main_and_H{i}"],
                                 base + previous[key] + 1)
                self.assertEqual(len(entry["replies"]), 1)
                r = entry["replies"][0]
                self.assertEqual(r["id"], f"impuls_help_{key}_h{i}_01")
                self.assertEqual(r["language"], "ru")
                self.assertEqual(r["response_role"], "assistant_reply")
                self.assertEqual(r["editorial_status"], "candidate_pending_full_semantic_review")
                self.assertTrue(r["read_only"])
                self.assertIn(r["context"], ("private", "direct", "group_addressed"))
                self.assertGreaterEqual(len(r["text"]), 75)
                self.assertGreaterEqual(len(r["context_note"]), 55)
                self.assertNotEqual(norm(r["text"]), norm(r["context_note"]))
                self.assertFalse(re.search(r"https?://|t\.me/|@[A-Za-z_]|[0-9]{10,}",
                                           r["text"] + r["context_note"]))

    def test_exact_and_near_replies_and_scenarios(self):
        baseline = [s for r in self.faq["records"] for s in (r["answer"], *r["variants"])]
        scenarios = defaultdict(list)
        for stage in self.stages[:37]:
            for entry in stage["entries"]:
                for r in entry["replies"]:
                    baseline.append(r["text"])
                    scenarios[entry["intent_id"]].append(r["context_note"])
        seen = set(map(norm, baseline))
        for stage in self.new:
            for entry in stage["entries"]:
                for r in entry["replies"]:
                    self.assertNotIn(norm(r["text"]), seen, r["id"])
                    self.assertTrue(all(overlap(r["text"], text) < .72 for text in baseline), r["id"])
                    self.assertTrue(all(overlap(r["context_note"], old) < .60
                                        for old in scenarios[entry["intent_id"]]), r["id"])
                    baseline.append(r["text"])
                    seen.add(norm(r["text"]))
                    scenarios[entry["intent_id"]].append(r["context_note"])

    def test_no_action_from_language_and_manual_anchors(self):
        for stage in self.new:
            for entry in stage["entries"]:
                for r in entry["replies"]:
                    text = r["text"].casefold()
                    self.assertNotIn("автоматически выдам бан", text)
                    self.assertNotIn("сам удалю сообщение", text)
                    self.assertNotIn("передам вашу переписку в github", text)
        greetings = next(e for e in self.new[0]["entries"] if e["intent_id"] == "greeting")
        self.assertIn("привет", greetings["replies"][0]["text"].casefold())
        privacy = next(e for e in self.new[0]["entries"] if e["intent_id"] == "privacy")
        self.assertIn("имени", privacy["replies"][0]["text"].casefold())
        stopped = next(e for e in self.new[1]["entries"] if e["intent_id"] == "request_to_stop")
        self.assertIn("закончить", stopped["replies"][0]["text"].casefold())


if __name__ == "__main__":
    unittest.main()
