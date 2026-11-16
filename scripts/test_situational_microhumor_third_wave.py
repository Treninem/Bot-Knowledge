#!/usr/bin/env python3
"""Third-wave situational humor: 72 synthetic replies, 8 distinct intents, preserved 162."""
import hashlib
import json
import pathlib
import re
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
FILE = ROOT / "packs/ru/situational_microhumor_qa.json"
STAGE = ROOT / "staging/ru/situational_microhumor_unregistered_48_20261116.json"
PACK_SHA = "fc82d4122364a4be8961a98f4af57f1f0d059b99fd7721049d88fbfac3779bb1"
PREFIX_SHA = "bfd5683423ff72e0ff3d0bbdbcb2decd27d42a8c6be653425efec2c9a68ebade"
NEW_IDS = ["humor_scene_alarms","humor_scene_video_calls","humor_scene_groceries","humor_scene_coffee_tea","humor_scene_needlework","humor_scene_office_supplies","humor_scene_home_network","humor_scene_cinema"]

def norm(text):
    return " ".join(re.findall(r"[^\\W_]+", text.casefold().replace("ё", "е")))

class ThirdWave(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pack = json.loads(FILE.read_text("utf-8"))
        cls.rows = cls.pack["records"]

    def test_counts_and_exact_prior_replies(self):
        self.assertEqual(hashlib.sha256(FILE.read_bytes()).hexdigest(), PACK_SHA)
        self.assertEqual(len(self.rows), 26)
        self.assertEqual([r["id"] for r in self.rows[18:]], NEW_IDS)
        prior = [v for r in self.rows[:18] for v in [r["answer"], *r["variants"]]]
        self.assertEqual(len(prior), 162)
        self.assertEqual(hashlib.sha256(json.dumps(prior, ensure_ascii=False, separators=(",", ":")).encode()).hexdigest(), PREFIX_SHA)
        self.assertEqual([len(r["variants"]) for r in self.rows], [8] * 26)

    def test_new_replies_unique_private_and_staging_isolated(self):
        registered = [v for r in self.rows for v in [r["answer"], *r["variants"]]]
        stage = json.loads(STAGE.read_text("utf-8"))
        staged = [v for r in stage["records"] for v in r["additional_replies"]]
        self.assertEqual(len(registered), 234)
        self.assertEqual(len(staged), 48)
        self.assertEqual(len(set(map(norm, registered))), 234)
        self.assertFalse(set(map(norm, registered)) & set(map(norm, staged)))
        for row in self.rows[18:]:
            self.assertEqual(row["audiences"], ["all_ai_bots"])
            self.assertEqual(row["language"], "ru")
            self.assertEqual(row["contexts"], ["direct", "private", "group_addressed"])
            self.assertEqual(row["constraints"], {"read_only": True, "requires_direct_address": True, "no_personal_data": True})
            self.assertFalse(set(row) & {"action", "sanction", "mute", "ban", "execute"})
            for sentence in [row["answer"], *row["variants"]]:
                self.assertFalse(re.search(r"https?://|t\\.me/|@[A-Za-z0-9_]|[0-9]{10,}", sentence, re.I))

if __name__ == "__main__":
    unittest.main()
