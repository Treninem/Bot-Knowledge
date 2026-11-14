"""Read-only H11/H12 candidate checks against all prior ImPULS FAQ stages."""
from __future__ import annotations

import hashlib
import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PACK = ROOT / "packs/ru/impuls_help_qa.json"
STAGES = [ROOT / f"staging/ru/impuls_help_context_h{i}_20261114.json"
          for i in range(1, 13)]


def normalize(value: str) -> str:
    return " ".join(re.findall(r"[^\\W_]+", value.casefold().replace("ё", "е")))


def terms(value: str) -> set[str]:
    return set(normalize(value).split())


def jaccard(left: set[str], right: set[str]) -> float:
    both = left | right
    return len(left & right) / len(both) if both else 1.0


class ContextHelpH11H12(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.published = json.loads(PACK.read_text(encoding="utf-8"))
        cls.records = {row["id"]: row for row in cls.published["records"]}
        cls.stages = [json.loads(p.read_text(encoding="utf-8")) for p in STAGES]
        cls.manifest = json.loads((ROOT / "manifest.json").read_text(encoding="utf-8"))

    def test_manifest_provenance_and_unregistered_state(self):
        registered = {p["path"]: p["sha256"] for p in self.manifest["packs"]}
        actual = hashlib.sha256(PACK.read_bytes()).hexdigest()
        self.assertEqual(actual, registered["packs/ru/impuls_help_qa.json"])
        for file, stage in zip(STAGES, self.stages):
            self.assertLess(file.stat().st_size, 2 * 1024 * 1024)
            self.assertNotIn(file.relative_to(ROOT).as_posix(), registered)
            self.assertFalse(stage["consumer_registered"])
            self.assertEqual(stage["source_pack_manifest_sha256"], actual)
            self.assertEqual(stage["checked_source_main_sha"],
                             "6c9f430da47f137d39a72bbd28c057cfb8f6be96")
            self.assertTrue(all(stage["constraints"].values()))
        for stage in self.stages[10:]:
            self.assertEqual(stage["checked_impuls_main_sha"],
                             "e94e34e1717231a4788f8d8447d760d2e5e2ba8d")
            self.assertEqual(stage["audiences"], ["impuls"])

    def test_100_existing_intents_and_exact_numeric_progress(self):
        expected = [45, 45, 45, 90, 50, 60, 55, 45, 45, 55, 50, 50]
        self.assertEqual([sum(len(e["replies"]) for e in s["entries"])
                          for s in self.stages], expected)
        self.assertEqual(sum(expected), 635)
        earlier = {}
        for i, stage in enumerate(self.stages):
            for entry in stage["entries"]:
                ident = entry["intent_id"]
                rec = self.records[ident]
                self.assertEqual(entry["canonical_question"], rec["question"])
                start = 1 + len(rec["variants"])
                self.assertEqual(entry["published_count"], start)
                previous = earlier.get(ident, 0)
                if i >= 10:
                    self.assertEqual(entry["earlier_staged_candidates"], previous)
                    self.assertEqual(entry["added_candidates"], 1)
                    self.assertEqual(len(entry["replies"]), 1)
                    self.assertEqual(entry[f"total_candidates_in_main_and_H1_H{i+1}"],
                                     start + previous + 1)
                    self.assertEqual(entry["remaining_to_target_excluding_other_prs"],
                                     100 - start - previous - 1)
                earlier[ident] = previous + len(entry["replies"])
        self.assertEqual(len(earlier), 100)
        self.assertEqual(sum(100 - (1 + len(self.records[k]["variants"]) + v)
                             for k, v in earlier.items()), 9090)
        self.assertTrue(all(1 + len(self.records[k]["variants"]) + v < 100
                            for k, v in earlier.items()))
        self.assertEqual({e["intent_id"] for e in self.stages[10]["entries"]}
                         & {e["intent_id"] for e in self.stages[11]["entries"]}, set())
        self.assertEqual({e["intent_id"] for e in self.stages[10]["entries"]}
                         | {e["intent_id"] for e in self.stages[11]["entries"]},
                         set(earlier))
        self.assertEqual(self.stages[-1]["checkpoint"]["cumulative_H1_H12"], 635)
        self.assertEqual(self.stages[-1]["checkpoint"]["remaining_numeric_all_100_intents"],
                         9090)
        self.assertEqual(self.stages[-1]["checkpoint"]["editorially_approved_new"], 0)
        self.assertEqual(self.stages[-1]["checkpoint"]["certified_100_sets"], 0)

    def test_ids_context_privacy_and_lexical_repeats(self):
        previous_texts = [t for r in self.published["records"]
                          for t in [r["answer"], *r["variants"]]]
        normalized_seen = {normalize(t) for t in previous_texts}
        wordsets = [terms(t) for t in previous_texts]
        ids = set()
        contexts = {}
        total = 0
        for stage in self.stages:
            for entry in stage["entries"]:
                self.assertEqual(entry["audiences"], ["impuls"])
                for reply in entry["replies"]:
                    total += 1
                    self.assertNotIn(reply["id"], ids)
                    ids.add(reply["id"])
                    self.assertTrue(reply["read_only"])
                    self.assertEqual(reply["response_role"], "assistant_reply")
                    self.assertEqual(reply["audiences"], ["impuls"])
                    self.assertEqual(reply["editorial_status"],
                                     "candidate_pending_full_semantic_review")
                    self.assertIn(reply["context"],
                                  {"direct", "private", "group_addressed"})
                    self.assertGreaterEqual(len(reply["context_note"]), 25)
                    self.assertGreaterEqual(len(reply["text"]), 30)
                    self.assertFalse(re.search(
                        r"https?://|@|\\b(?:ban_user|kick_chat_member)\\b",
                        reply["text"], re.I))
                    key = (entry["intent_id"], normalize(reply["context_note"]))
                    self.assertNotIn(key, contexts)
                    contexts[key] = reply["id"]
                    n = normalize(reply["text"])
                    self.assertNotIn(n, normalized_seen, reply["id"])
                    w = terms(reply["text"])
                    self.assertLess(max(jaccard(w, prior) for prior in wordsets),
                                    .70, reply["id"])
                    wordsets.append(w)
                    normalized_seen.add(n)
        self.assertEqual(total, 635)
        self.assertEqual(len(ids), 635)

    def test_duplicate_detector_negative_controls(self):
        self.assertEqual(normalize("Ёж,   привет! 👋"), normalize("еж привет"))
        self.assertEqual(jaccard(terms("один два"), terms("один два")), 1.0)
        self.assertLess(jaccard(terms("группа"), terms("игра")), .70)


if __name__ == "__main__":
    unittest.main()
