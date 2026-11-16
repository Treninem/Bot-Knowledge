#!/usr/bin/env python3
"""Prove six schema-compatible new humor intents and preserve staged overflow."""
import hashlib
import json
import pathlib
import re
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
FILE = ROOT / "packs/ru/situational_microhumor_qa.json"
STAGE = ROOT / "staging/ru/situational_microhumor_unregistered_48_20261116.json"
PACK_SHA = "1d4299e4d56622e4a2ab7a411638b792096742280549ca16b26d9a14508a8888"
STAGE_SHA = "8905b9a9bfe8601adf53aba1ae280e27b542746bbb392c2e87c4bb687f65d3cc"
BASELINE_SHA = "f5c236fff6afdd40cc4dde6e42dfde5d5fe86bec859280d9f3936f2573a584a3"
VERSION = "2026.11.16.008"
NEW_IDS = ["humor_scene_music","humor_scene_laundry","humor_scene_boardgames","humor_scene_camping","humor_scene_museums","humor_scene_languages"]

def norm(value):
    return " ".join(re.findall(r"[^\W_]+", value.casefold().replace("ё", "е")))

class HumorSecondWave(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = json.loads(FILE.read_text("utf-8"))
        cls.rows = cls.data["records"]

    def test_registered_invariants(self):
        self.assertEqual(hashlib.sha256(FILE.read_bytes()).hexdigest(), PACK_SHA)
        manifest = json.loads((ROOT / "manifest.json").read_text("utf-8"))
        self.assertEqual(manifest["knowledge_version"], VERSION)
        self.assertEqual(self.data["pack_version"], VERSION)
        self.assertEqual(len([p for p in manifest["packs"] if p["path"] == "packs/ru/situational_microhumor_qa.json" and p["sha256"] == PACK_SHA]), 1)
        self.assertEqual(len(self.rows), 18)
        self.assertEqual([r["id"] for r in self.rows[12:]], NEW_IDS)
        self.assertTrue(all(len(r["variants"]) == 8 for r in self.rows))
        self.assertLessEqual(sum((ROOT / p["path"]).stat().st_size for p in manifest["packs"]), 8 * 1024 * 1024)

    def test_first_108_exactly_preserved(self):
        previous = [text for r in self.rows[:12] for text in [r["answer"], *r["variants"]]]
        self.assertEqual(len(previous), 108)
        blob = json.dumps(previous, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
        self.assertEqual(hashlib.sha256(blob).hexdigest(), BASELINE_SHA)

    def test_54_new_scoped_and_unique(self):
        phrases = [text for r in self.rows for text in [r["answer"], *r["variants"]]]
        self.assertEqual(len(phrases), 162)
        self.assertEqual(len(set(map(norm, phrases))), 162)
        for row in self.rows:
            self.assertEqual(row["audiences"], ["all_ai_bots"])
            self.assertEqual(row["language"], "ru")
            self.assertEqual(row["constraints"], {"read_only": True, "requires_direct_address": True, "no_personal_data": True})
            self.assertTrue(row["question"].lower().startswith(("пошути", "придумай", "расскажи", "дай")))
            self.assertFalse(set(row) & {"action", "execute", "sanction", "mute", "ban", "auto_apply"})
        self.assertFalse(any(re.search(r"https?://|t\.me/|@[A-Za-z0-9_]|[0-9]{10,}", x, re.I) for x in phrases))

    def test_48_overflow_candidates_are_unregistered(self):
        self.assertEqual(hashlib.sha256(STAGE.read_bytes()).hexdigest(), STAGE_SHA)
        stage = json.loads(STAGE.read_text("utf-8"))
        self.assertFalse(stage["consumer_registered"])
        self.assertEqual(stage["checkpoint"]["staged_new_candidates"], 48)
        self.assertEqual(len(stage["records"]), 12)
        candidates = [x for r in stage["records"] for x in r["additional_replies"]]
        self.assertEqual(len(candidates), 48)
        self.assertEqual(len(set(map(norm, candidates))), 48)
        existing = set(map(norm, [x for r in self.rows for x in [r["answer"], *r["variants"]]]))
        self.assertFalse(set(map(norm, candidates)) & existing)

if __name__ == "__main__":
    unittest.main()
