#!/usr/bin/env python3
"""Read-only checks for the H23/H24 contextual candidate continuation."""
import hashlib
import json
import re
import unittest
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MAIN_SHA = "6c9f430da47f137d39a72bbd28c057cfb8f6be96"
PACK_SHA = "50edd41dc0c6a868577433944e0ff0b2a36c2c9ebe53d587e5cbb4692185bbc9"
STAGES = [
    ROOT / "staging" / "ru" / f"impuls_help_context_h{i}_20261114.json"
    for i in range(1, 25)
]
PACK = ROOT / "packs" / "ru" / "impuls_help_qa.json"
MANIFEST = ROOT / "manifest.json"


def norm(text: str) -> str:
    return " ".join(re.findall(r"[\w]+", text.casefold().replace("ё", "е"), re.UNICODE))


def overlap(a: str, b: str) -> float:
    left, right = set(norm(a).split()), set(norm(b).split())
    return len(left & right) / max(len(left | right), 1)


class H23H24(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pack = json.loads(PACK.read_text(encoding="utf-8"))
        cls.manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
        cls.stages = [json.loads(p.read_text(encoding="utf-8")) for p in STAGES]
        cls.published = {r["id"]: r for r in cls.pack["records"]}

    def test_manifest_source_and_isolation(self):
        self.assertEqual(hashlib.sha256(PACK.read_bytes()).hexdigest(), PACK_SHA)
        registered = {x["path"]: x["sha256"] for x in self.manifest["packs"]}
        self.assertEqual(registered["packs/ru/impuls_help_qa.json"], PACK_SHA)
        for stage in self.stages[-2:]:
            self.assertEqual(stage["checked_source_main_sha"], MAIN_SHA)
            self.assertEqual(stage["source_pack_manifest_sha256"], PACK_SHA)
            self.assertFalse(stage["consumer_registered"])
            self.assertEqual(stage["audiences"], ["impuls"])
            self.assertEqual(stage["language"], "ru")
            self.assertTrue(stage["constraints"]["read_only"])
            self.assertTrue(stage["constraints"]["no_sanctions"])

    def test_counts_and_stable_intents(self):
        counts = Counter()
        ids = set()
        for stage in self.stages:
            for record in stage["entries"]:
                self.assertIn(record["intent_id"], self.published)
                counts[record["intent_id"]] += len(record["replies"])
                for response in record["replies"]:
                    self.assertNotIn(response["id"], ids)
                    ids.add(response["id"])
        self.assertEqual(len(counts), 100)
        self.assertEqual(sum(counts.values()), 1235)
        totals = Counter(1 + len(self.published[key]["variants"]) + added for key, added in counts.items())
        self.assertEqual(totals, Counter({13: 6, 14: 49, 16: 19, 17: 26}))
        self.assertEqual(sum(100 - size for size in totals.elements()), 8490)

    def test_current_checkpoint_delta(self):
        for n, total, remaining in [(23, 1185, 8540), (24, 1235, 8490)]:
            stage = self.stages[n - 1]
            checkpoint = stage["checkpoint"]
            self.assertEqual(checkpoint["new_candidates"], 50)
            self.assertEqual(checkpoint["processed_intents"], 50)
            self.assertEqual(checkpoint[f"cumulative_H1_H{n}"], total)
            self.assertEqual(checkpoint["remaining_numeric_all_100_intents"], remaining)
            self.assertEqual(checkpoint["editorially_approved_new"], 0)
            self.assertEqual(checkpoint["certified_100_sets"], 0)
            self.assertEqual(len(stage["entries"]), 50)
            for e in stage["entries"]:
                self.assertEqual(e["canonical_question"], self.published[e["intent_id"]]["question"])
                self.assertEqual(e["added_candidates"], 1)
                self.assertEqual(e["target"], 100)
                self.assertEqual(e["remaining_to_target_excluding_other_prs"],
                                 100 - e[f"total_candidates_in_main_and_H{n}"])
                self.assertEqual(e["published_count"],
                                 1 + len(self.published[e["intent_id"]]["variants"]))

    def test_language_scope_and_no_actions(self):
        new = self.stages[-2:]
        self.assertFalse({e["intent_id"] for e in new[0]["entries"]} &
                         {e["intent_id"] for e in new[1]["entries"]})
        for n, stage in [(23, new[0]), (24, new[1])]:
            for e in stage["entries"]:
                self.assertEqual(len(e["replies"]), 1)
                reply = e["replies"][0]
                self.assertEqual(reply["id"], f"impuls_help_{e['intent_id']}_h{n}_01")
                self.assertEqual(reply["language"], "ru")
                self.assertEqual(reply["audiences"], ["impuls"])
                self.assertEqual(reply["response_role"], "assistant_reply")
                self.assertEqual(reply["editorial_status"], "candidate_pending_full_semantic_review")
                self.assertIn(reply["context"], ["private", "direct", "group_addressed"])
                self.assertTrue(reply["read_only"])
                self.assertGreater(len(reply["context_note"]), 25)
                self.assertGreater(len(reply["text"]), 45)
                self.assertGreater(len(reply["avoid"]), 40)
                for forbidden_key in ["ban", "mute", "action", "execute"]:
                    self.assertNotIn(forbidden_key, reply)
                for private_marker in ["t.me/", "http://", "https://", "@"]:
                    self.assertNotIn(private_marker, reply["text"])

    def test_new_replies_not_cosmetic_duplicates(self):
        corpus = [v for e in self.published.values() for v in [e["answer"], *e["variants"]]]
        existing = {norm(x) for x in corpus}
        contextual = {}
        for stage in self.stages[:-2]:
            for e in stage["entries"]:
                contextual.setdefault(e["intent_id"], [])
                for reply in e["replies"]:
                    corpus.append(reply["text"])
                    existing.add(norm(reply["text"]))
                    contextual[e["intent_id"]].append(reply["context_note"])
        for stage in self.stages[-2:]:
            for e in stage["entries"]:
                for reply in e["replies"]:
                    self.assertNotIn(norm(reply["text"]), existing, reply["id"])
                    self.assertTrue(all(overlap(reply["text"], x) < .70 for x in corpus),
                                    reply["id"])
                    self.assertTrue(all(overlap(reply["context_note"], x) < .58
                                        for x in contextual.get(e["intent_id"], [])),
                                    reply["id"])
                    corpus.append(reply["text"])
                    existing.add(norm(reply["text"]))
                    contextual.setdefault(e["intent_id"], []).append(reply["context_note"])

    def test_negation_preserved(self):
        self.assertEqual(norm("Ёлка, свет!"), norm("елка свет"))
        self.assertNotEqual(norm("не отключать"), norm("отключать"))


if __name__ == "__main__":
    unittest.main()
