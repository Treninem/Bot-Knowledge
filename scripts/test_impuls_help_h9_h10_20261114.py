"""H9/H10 continuation validates all source-scoped and staged ImPULS answers."""
import hashlib
import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STAGE_PATHS = [ROOT / f"staging/ru/impuls_help_context_h{i}_20261114.json"
               for i in range(1, 11)]
SOURCE = ROOT / "packs/ru/impuls_help_qa.json"


def normalized(text):
    return " ".join(re.findall(r"[^\W_]+", text.casefold().replace("ё", "е")))


def wordset(text):
    return set(normalized(text).split())


def jaccard(a, b):
    return len(a & b) / len(a | b) if a | b else 1.0


class H9H10QA(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.stages = [json.loads(p.read_text("utf-8")) for p in STAGE_PATHS]
        cls.source = json.loads(SOURCE.read_text("utf-8"))
        cls.manifest = json.loads((ROOT / "manifest.json").read_text("utf-8"))
        cls.published = {r["id"]: r for r in cls.source["records"]}

    def test_source_and_unregistered_status(self):
        packs = {p["path"]: p["sha256"] for p in self.manifest["packs"]}
        actual = hashlib.sha256(SOURCE.read_bytes()).hexdigest()
        self.assertEqual(actual, packs["packs/ru/impuls_help_qa.json"])
        for path, stage in zip(STAGE_PATHS, self.stages):
            self.assertEqual(stage["source_pack_manifest_sha256"], actual)
            self.assertFalse(stage["consumer_registered"])
            self.assertTrue(all(stage["constraints"].values()))
            self.assertNotIn(path.relative_to(ROOT).as_posix(), packs)
            self.assertEqual(stage["checked_source_main_sha"],
                             "6c9f430da47f137d39a72bbd28c057cfb8f6be96")
            self.assertEqual(stage["checked_impuls_main_sha"],
                             "60f08d93c6f0268d63d1c06dc364287d0b18c183")
            self.assertLess(path.stat().st_size, 2 * 1024 * 1024)

    def test_progress_and_scope(self):
        expected = [45, 45, 45, 90, 50, 60, 55, 45, 45, 55]
        actual = [sum(len(e["replies"]) for e in stage["entries"])
                  for stage in self.stages]
        self.assertEqual(actual, expected)
        self.assertEqual(sum(actual), 535)
        base = {e["intent_id"] for stage in self.stages[:6]
                for e in stage["entries"]}
        h9 = {e["intent_id"] for e in self.stages[8]["entries"]}
        h10 = {e["intent_id"] for e in self.stages[9]["entries"]}
        self.assertEqual((len(base), len(h9), len(h10)), (100, 45, 55))
        self.assertFalse(h9 & h10)
        self.assertEqual(h9 | h10, base)
        self.assertEqual(self.stages[-1]["checkpoint"]["cumulative_H1_H10"], 535)
        self.assertEqual(self.stages[-1]["checkpoint"]["editorially_approved_new"], 0)
        self.assertEqual(self.stages[-1]["checkpoint"]["certified_100_sets"], 0)
        counts = {}
        for stage_i, stage in enumerate(self.stages):
            for entry in stage["entries"]:
                record = self.published[entry["intent_id"]]
                published_count = 1 + len(record["variants"])
                self.assertEqual(entry["canonical_question"], record["question"])
                self.assertEqual(entry["published_count"], published_count)
                if stage_i >= 8:
                    previous = sum(len(e["replies"])
                                   for earlier in self.stages[:stage_i]
                                   for e in earlier["entries"]
                                   if e["intent_id"] == entry["intent_id"])
                    self.assertEqual(entry["earlier_staged_candidates"], previous)
                    self.assertEqual(len(entry["replies"]), 1)
                    self.assertEqual(entry["remaining_to_target_excluding_other_prs"],
                                     100 - published_count - previous - 1)
                counts.setdefault(entry["intent_id"], published_count)
                counts[entry["intent_id"]] += len(entry["replies"])
        self.assertEqual(len(counts), 100)
        self.assertEqual(sum(100-v for v in counts.values()), 9190)
        self.assertTrue(all(v < 100 for v in counts.values()))

    def test_ids_context_and_normalized_duplicates(self):
        previous_texts = [t for rec in self.source["records"]
                          for t in [rec["answer"], *rec["variants"]]]
        seen = {normalized(t) for t in previous_texts}
        previous_words = [wordset(t) for t in previous_texts]
        reply_ids = set()
        for stage in self.stages:
            for entry in stage["entries"]:
                self.assertEqual(entry["audiences"], ["impuls"])
                for reply in entry["replies"]:
                    self.assertNotIn(reply["id"], reply_ids)
                    reply_ids.add(reply["id"])
                    self.assertTrue(reply["read_only"])
                    self.assertEqual(reply["audiences"], ["impuls"])
                    self.assertEqual(reply["response_role"], "assistant_reply")
                    self.assertIn(reply["context"],
                                  ("direct", "private", "group_addressed"))
                    self.assertGreaterEqual(len(reply["context_note"]), 25)
                    self.assertEqual(reply["editorial_status"],
                                     "candidate_pending_full_semantic_review")
                    self.assertNotIn("@", reply["text"])
                    self.assertFalse(re.search(r"https?://|\b(?:ban_user|kick_chat_member)\b",
                                               reply["text"], re.IGNORECASE))
                    candidate = normalized(reply["text"])
                    self.assertNotIn(candidate, seen, reply["id"])
                    candidate_words = wordset(reply["text"])
                    self.assertLess(max(jaccard(candidate_words, earlier)
                                        for earlier in previous_words),
                                    0.70, reply["id"])
                    seen.add(candidate)
                    previous_words.append(candidate_words)
        self.assertEqual(len(reply_ids), 535)


if __name__ == "__main__":
    unittest.main()
