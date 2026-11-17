#!/usr/bin/env python3
"""H36–H37: all-stage progress, reply-role, privacy and duplication checks."""
import json
import re
import unittest
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def norm(s):
    return " ".join(re.findall(r"\w+", s.casefold().replace("ё", "е")))


def similarity(a, b):
    x, y = set(norm(a).split()), set(norm(b).split())
    return len(x & y) / max(1, len(x | y))


class H36H37QA(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.faq = json.loads((ROOT / "packs/ru/impuls_help_qa.json").read_text(encoding="utf-8"))
        cls.by_id = {r["id"]: r for r in cls.faq["records"]}
        cls.stages = []
        for i in range(1, 38):
            date = "20261115" if i >= 31 else "20261114"
            path = ROOT / f"staging/ru/impuls_help_context_h{i}_{date}.json"
            cls.stages.append(json.loads(path.read_text(encoding="utf-8")))
        cls.h36, cls.h37 = cls.stages[-2:]

    def test_counts_and_no_consumer_activation(self):
        counts = Counter()
        ids = set()
        for stage in self.stages:
            self.assertFalse(stage["consumer_registered"])
            self.assertTrue(stage["constraints"]["read_only"])
            self.assertTrue(stage["constraints"]["no_sanctions"])
            for entry in stage["entries"]:
                self.assertIn(entry["intent_id"], self.by_id)
                for reply in entry["replies"]:
                    self.assertNotIn(reply["id"], ids, reply["id"])
                    ids.add(reply["id"])
                    counts[entry["intent_id"]] += 1
        self.assertEqual(len(counts), 100)
        self.assertEqual(sum(counts.values()), 1795)
        self.assertEqual(
            sum(100 - (1 + len(self.by_id[key]["variants"]) + value)
                for key, value in counts.items()), 7930
        )
        self.assertEqual(self.h36["checkpoint"]["cumulative_H1_H36"], 1755)
        self.assertEqual(self.h36["checkpoint"]["remaining_numeric_all_100_intents"], 7970)
        self.assertEqual(self.h37["checkpoint"]["cumulative_H1_H37"], 1795)
        self.assertEqual(self.h37["checkpoint"]["remaining_numeric_all_100_intents"], 7930)
        self.assertEqual(self.h37["checkpoint"]["certified_100_sets"], 0)
        self.assertEqual(self.h37["checkpoint"]["editorially_approved_new"], 0)

    def test_schema_role_context_and_source(self):
        manifest = json.loads((ROOT / "manifest.json").read_text(encoding="utf-8"))
        sha = {r["path"]: r["sha256"] for r in manifest["packs"]}
        for i, stage, previous in [(36, self.h36, self.stages[:35]),
                                    (37, self.h37, self.stages[:36])]:
            self.assertEqual(stage["source_pack_manifest_sha256"], sha[stage["source_pack"]])
            seen = set()
            previous_counts = Counter()
            for old in previous:
                for e in old["entries"]:
                    previous_counts[e["intent_id"]] += len(e["replies"])
            self.assertEqual(len(stage["entries"]), 20)
            self.assertEqual(sum(len(e["replies"]) for e in stage["entries"]), 40)
            for e in stage["entries"]:
                key = e["intent_id"]
                self.assertNotIn(key, seen)
                seen.add(key)
                self.assertEqual(e["canonical_question"], self.by_id[key]["question"])
                base = 1 + len(self.by_id[key]["variants"])
                self.assertEqual(e["published_count"], base)
                self.assertEqual(e["earlier_staged_candidates"], previous_counts[key])
                self.assertEqual(e["remaining_to_target_excluding_other_prs"], 98-base-previous_counts[key])
                self.assertEqual(e[f"total_candidates_in_main_and_H{i}"], base+previous_counts[key]+2)
                self.assertEqual(len(e["replies"]), 2)
                for j, reply in enumerate(e["replies"], 1):
                    self.assertEqual(reply["id"], f"impuls_help_{key}_h{i}_{j:02d}")
                    self.assertEqual(reply["response_role"], "assistant_reply")
                    self.assertEqual(reply["editorial_status"], "candidate_pending_full_semantic_review")
                    self.assertTrue(reply["read_only"])
                    self.assertIn(reply["context"], {"private", "direct", "group_addressed"})
                    self.assertGreaterEqual(len(reply["text"]), 75)
                    self.assertGreaterEqual(len(reply["context_note"]), 55)
                    self.assertNotEqual(norm(reply["text"]), norm(reply["context_note"]))
                    self.assertFalse(re.search(r"https?://|t\.me/|@[A-Za-z_]|[0-9]{10,}",
                                               reply["text"] + reply["context_note"]))

    def test_lexical_uniqueness_and_situational_differences(self):
        baseline = [s for r in self.faq["records"] for s in [r["answer"], *r["variants"]]]
        old = defaultdict(list)
        for stage in self.stages[:35]:
            for e in stage["entries"]:
                for reply in e["replies"]:
                    baseline.append(reply["text"])
                    old[e["intent_id"]].append(reply["context_note"])
        normalized = set(map(norm, baseline))
        for stage in (self.h36, self.h37):
            for e in stage["entries"]:
                for reply in e["replies"]:
                    s = reply["text"]
                    self.assertNotIn(norm(s), normalized, reply["id"])
                    self.assertTrue(all(similarity(s, item) < .70 for item in baseline), reply["id"])
                    self.assertTrue(all(similarity(reply["context_note"], item) < .58
                                        for item in old[e["intent_id"]]), reply["id"])
                    baseline.append(s)
                    normalized.add(norm(s))
                    old[e["intent_id"]].append(reply["context_note"])

    def test_greeting_and_moderation_boundaries(self):
        greetings = next(e for e in self.h37["entries"] if e["intent_id"] == "greeting")
        for reply in greetings["replies"]:
            self.assertTrue(any(x in reply["text"].casefold()
                                for x in ("приветств", "здравств", "поздор")))
            self.assertNotIn("включи санкц", reply["text"].casefold())
        for stage in (self.h36, self.h37):
            self.assertTrue(stage["constraints"]["requires_context_match"])
            self.assertTrue(stage["constraints"]["no_personal_data"])
            for e in stage["entries"]:
                for r in e["replies"]:
                    self.assertNotIn("автоматически выдам бан", r["text"].casefold())


if __name__ == "__main__":
    unittest.main()
