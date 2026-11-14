"""Read-only checks for H7/H8 context-gated ImPULS reply candidates."""
from __future__ import annotations
import hashlib
import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STAGES = [ROOT / f"staging/ru/impuls_help_context_h{i}_20261114.json"
          for i in range(1, 9)]
SOURCE = ROOT / "packs/ru/impuls_help_qa.json"


def normalize(text: str) -> str:
    return " ".join(re.findall(r"[^\\W_]+", text.casefold().replace("ё", "е")))


def tokens(text: str) -> set[str]:
    return set(normalize(text).split())


def jaccard(a: set[str], b: set[str]) -> float:
    return len(a & b) / len(a | b) if a | b else 1.0


class H7H8QA(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.stages = [json.loads(p.read_text(encoding="utf-8")) for p in STAGES]
        cls.source = json.loads(SOURCE.read_text(encoding="utf-8"))
        cls.manifest = json.loads((ROOT / "manifest.json").read_text(encoding="utf-8"))
        cls.registered = {r["id"]: r for r in cls.source["records"]}

    def test_manifest_and_no_consumer_registration(self):
        packs = {p["path"]: p["sha256"] for p in self.manifest["packs"]}
        actual = hashlib.sha256(SOURCE.read_bytes()).hexdigest()
        self.assertEqual(actual, packs["packs/ru/impuls_help_qa.json"])
        for path, stage in zip(STAGES, self.stages):
            self.assertFalse(stage["consumer_registered"])
            self.assertEqual(stage["source_pack_manifest_sha256"], actual)
            self.assertEqual(stage["checked_source_main_sha"],
                             "6c9f430da47f137d39a72bbd28c057cfb8f6be96")
            self.assertNotIn(path.relative_to(ROOT).as_posix(), packs)
            self.assertTrue(all(stage["constraints"].values()))
            self.assertLess(path.stat().st_size, 2 * 1024 * 1024)

    def test_counts_stable_ids_and_context_selection_contract(self):
        self.assertEqual([len(s["entries"]) for s in self.stages],
                         [15, 15, 15, 45, 25, 30, 55, 45])
        self.assertEqual([sum(len(e["replies"]) for e in s["entries"])
                          for s in self.stages],
                         [45, 45, 45, 90, 50, 60, 55, 45])
        self.assertEqual(sum(len(e["replies"]) for s in self.stages
                             for e in s["entries"]), 435)
        old = {e["intent_id"] for s in self.stages[:6] for e in s["entries"]}
        h7 = {e["intent_id"] for e in self.stages[6]["entries"]}
        h8 = {e["intent_id"] for e in self.stages[7]["entries"]}
        self.assertEqual((len(old), len(h7), len(h8), len(h7 & h8)),
                         (100, 55, 45, 0))
        self.assertEqual(h7 | h8, old)
        reply_ids = set()
        for stage_i, stage in enumerate(self.stages):
            for entry in stage["entries"]:
                ref = self.registered[entry["intent_id"]]
                self.assertEqual(entry["canonical_question"], ref["question"])
                self.assertEqual(entry["published_count"],
                                 1 + len(ref["variants"]))
                if stage_i >= 6:
                    earlier = sum(len(x["replies"]) for past in self.stages[:stage_i]
                                  for x in past["entries"]
                                  if x["intent_id"] == entry["intent_id"])
                    self.assertEqual(entry["earlier_staged_candidates"], earlier)
                    self.assertEqual(entry["remaining_to_target_excluding_other_prs"],
                                     100 - entry["published_count"] - earlier - 1)
                    self.assertEqual(len(entry["replies"]), 1)
                for reply in entry["replies"]:
                    self.assertNotIn(reply["id"], reply_ids)
                    reply_ids.add(reply["id"])
                    self.assertTrue(reply["read_only"])
                    self.assertEqual(reply["audiences"], ["impuls"])
                    self.assertEqual(reply["response_role"], "assistant_reply")
                    self.assertIn(reply["context"],
                                  ("private", "direct", "group_addressed"))
                    self.assertGreaterEqual(len(reply["context_note"]), 25)
                    self.assertEqual(reply["editorial_status"],
                                     "candidate_pending_full_semantic_review")
                    self.assertFalse(re.search(r"https?://|@|\\b(?:ban_user|kick_chat_member)\\b",
                                               reply["text"], re.I))
        self.assertEqual(len(reply_ids), 435)

    def test_no_lexical_collisions_with_published_or_earlier_stages(self):
        published = [value for record in self.source["records"]
                     for value in [record["answer"], *record["variants"]]]
        seen = {normalize(s) for s in published}
        previous = [tokens(s) for s in published]
        for stage in self.stages:
            for entry in stage["entries"]:
                for reply in entry["replies"]:
                    value = normalize(reply["text"])
                    self.assertNotIn(value, seen, reply["id"])
                    bag = tokens(reply["text"])
                    self.assertLess(max(jaccard(bag, previous_item)
                                        for previous_item in previous),
                                    0.70, reply["id"])
                    seen.add(value)
                    previous.append(bag)

    def test_progress_is_numerical_not_editorial(self):
        latest = self.stages[-1]["checkpoint"]
        self.assertEqual(latest["cumulative_H1_H8"], 435)
        self.assertEqual(latest["distinct_intents_H1_H8"], 100)
        self.assertEqual(latest["editorially_approved_new"], 0)
        self.assertEqual(latest["certified_100_sets"], 0)
        counts = {}
        for stage in self.stages:
            for entry in stage["entries"]:
                counts.setdefault(entry["intent_id"], entry["published_count"])
                counts[entry["intent_id"]] += len(entry["replies"])
        self.assertEqual(len(counts), 100)
        self.assertEqual(sum(100-v for v in counts.values()), 9290)
        self.assertTrue(all(v < 100 for v in counts.values()))


if __name__ == "__main__":
    unittest.main()
