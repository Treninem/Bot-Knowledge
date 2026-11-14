#!/usr/bin/env python3
"""Check H25/H26 independently of the prior H23/H24 tests (no consumer side effects)."""
import hashlib
import json
import re
import unittest
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PACK = ROOT / "packs/ru/impuls_help_qa.json"
PACK_SHA = "50edd41dc0c6a868577433944e0ff0b2a36c2c9ebe53d587e5cbb4692185bbc9"
MAIN_SHA = "6c9f430da47f137d39a72bbd28c057cfb8f6be96"


def normalize(text):
    return " ".join(re.findall(r"[\w]+", text.lower().replace("ё", "е"), flags=re.UNICODE))


def jac(a, b):
    x, y = set(normalize(a).split()), set(normalize(b).split())
    return len(x & y) / max(len(x | y), 1)


class H25H26(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.stage = [
            json.loads((ROOT / f"staging/ru/impuls_help_context_h{i}_20261114.json").read_text("utf-8"))
            for i in range(1, 27)
        ]
        cls.faq = json.loads(PACK.read_text("utf-8"))
        cls.by_id = {x["id"]: x for x in cls.faq["records"]}

    def test_source_manifest_and_no_registration(self):
        self.assertEqual(hashlib.sha256(PACK.read_bytes()).hexdigest(), PACK_SHA)
        manifest = json.loads((ROOT / "manifest.json").read_text("utf-8"))
        self.assertEqual(next(x["sha256"] for x in manifest["packs"]
                              if x["path"] == "packs/ru/impuls_help_qa.json"), PACK_SHA)
        for s in self.stage[-2:]:
            self.assertEqual(s["checked_source_main_sha"], MAIN_SHA)
            self.assertEqual(s["source_pack_manifest_sha256"], PACK_SHA)
            self.assertEqual(s["audiences"], ["impuls"])
            self.assertFalse(s["consumer_registered"])
            self.assertTrue(s["constraints"]["no_sanctions"])

    def test_counters_and_raw_remaining(self):
        counts = Counter()
        ids = set()
        for s in self.stage:
            for e in s["entries"]:
                self.assertIn(e["intent_id"], self.by_id)
                counts[e["intent_id"]] += len(e["replies"])
                for r in e["replies"]:
                    self.assertNotIn(r["id"], ids)
                    ids.add(r["id"])
        self.assertEqual(len(counts), 100)
        self.assertEqual(sum(counts.values()), 1335)
        sizes = Counter(1 + len(self.by_id[k]["variants"]) + n for k, n in counts.items())
        self.assertEqual(sizes, Counter({14: 6, 15: 49, 17: 19, 18: 26}))
        self.assertEqual(sum((100 - x) * n for x, n in sizes.items()), 8390)

    def test_new_stage_metadata(self):
        first, second = self.stage[-2:]
        self.assertEqual(len(first["entries"]), 50)
        self.assertEqual(len(second["entries"]), 50)
        self.assertFalse({e["intent_id"] for e in first["entries"]} &
                         {e["intent_id"] for e in second["entries"]})
        for num, total, remain, s in [(25, 1285, 8440, first), (26, 1335, 8390, second)]:
            cp = s["checkpoint"]
            self.assertEqual(cp["new_candidates"], 50)
            self.assertEqual(cp["processed_intents"], 50)
            self.assertEqual(cp[f"cumulative_H1_H{num}"], total)
            self.assertEqual(cp["remaining_numeric_all_100_intents"], remain)
            self.assertEqual(cp["editorially_approved_new"], 0)
            self.assertEqual(cp["certified_100_sets"], 0)
            for e in s["entries"]:
                self.assertEqual(e["canonical_question"], self.by_id[e["intent_id"]]["question"])
                self.assertEqual(e["published_count"], 1 + len(self.by_id[e["intent_id"]]["variants"]))
                self.assertEqual(e["added_candidates"], 1)
                self.assertEqual(e["target"], 100)
                self.assertEqual(e["remaining_to_target_excluding_other_prs"],
                                 100 - e[f"total_candidates_in_main_and_H{num}"])
                self.assertEqual(len(e["replies"]), 1)
                r = e["replies"][0]
                self.assertEqual(r["id"], f"impuls_help_{e['intent_id']}_h{num}_01")
                self.assertEqual(r["audiences"], ["impuls"])
                self.assertEqual(r["language"], "ru")
                self.assertEqual(r["response_role"], "assistant_reply")
                self.assertTrue(r["read_only"])
                self.assertEqual(r["editorial_status"], "candidate_pending_full_semantic_review")
                self.assertIn(r["context"], ["private", "direct", "group_addressed"])
                self.assertGreater(len(r["text"]), 45)
                self.assertGreater(len(r["context_note"]), 25)
                for bad in ("action", "execute", "ban", "mute"):
                    self.assertNotIn(bad, r)
                for leak in ("t.me/", "http://", "https://", "@"):
                    self.assertNotIn(leak, r["text"])

    def test_new_text_and_scenario_dedup(self):
        corpus = [x for e in self.faq["records"] for x in (e["answer"], *e["variants"])]
        contexts = {}
        for s in self.stage[:-2]:
            for e in s["entries"]:
                contexts.setdefault(e["intent_id"], [])
                for r in e["replies"]:
                    corpus.append(r["text"])
                    contexts[e["intent_id"]].append(r["context_note"])
        normals = {normalize(s) for s in corpus}
        for s in self.stage[-2:]:
            for e in s["entries"]:
                for r in e["replies"]:
                    self.assertNotIn(normalize(r["text"]), normals, r["id"])
                    self.assertTrue(all(jac(r["text"], old) < .70 for old in corpus), r["id"])
                    self.assertTrue(all(jac(r["context_note"], old) < .58
                                        for old in contexts[e["intent_id"]]), r["id"])
                    corpus.append(r["text"])
                    normals.add(normalize(r["text"]))
                    contexts[e["intent_id"]].append(r["context_note"])

    def test_negation_not_collapsed(self):
        self.assertEqual(normalize("Ёж!"), normalize("еж"))
        self.assertNotEqual(normalize("не выключай"), normalize("выключай"))


if __name__ == "__main__":
    unittest.main()
