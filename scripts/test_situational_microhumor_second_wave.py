#!/usr/bin/env python3
"""Second-wave humor: protect original 108 texts and test 48 safe additions."""
import hashlib
import json
import pathlib
import re
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
FILE = ROOT / "packs/ru/situational_microhumor_qa.json"
PACK_SHA = "469ff1f0f05a4ef14cae1881af4c72632f31c9d5d70e7f5c694a13e69544e4d5"
BASELINE_SHA = "f5c236fff6afdd40cc4dde6e42dfde5d5fe86bec859280d9f3936f2573a584a3"
VERSION = "2026.11.16.008"

def normalize(value):
    return " ".join(re.findall(r"[^\W_]+", value.casefold().replace("ё", "е"), re.UNICODE))

class HumorSecondWave(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pack = json.loads(FILE.read_text(encoding="utf-8"))
        cls.records = cls.pack["records"]

    def test_hash_scope_and_counts(self):
        raw = FILE.read_bytes()
        self.assertEqual(hashlib.sha256(raw).hexdigest(), PACK_SHA)
        self.assertEqual(self.pack["pack_version"], VERSION)
        manifest = json.loads((ROOT / "manifest.json").read_text(encoding="utf-8"))
        self.assertEqual(manifest["knowledge_version"], VERSION)
        entry = [p for p in manifest["packs"] if p["path"] == "packs/ru/situational_microhumor_qa.json"]
        self.assertEqual(len(entry), 1)
        self.assertEqual(entry[0]["sha256"], PACK_SHA)
        self.assertEqual(len(self.records), 12)
        self.assertLessEqual(sum((ROOT / p["path"]).stat().st_size for p in manifest["packs"]), 8 * 1024 * 1024)
        self.assertLessEqual(len(raw), 2 * 1024 * 1024)

    def test_original_108_preserved_in_place(self):
        original = [s for r in self.records for s in [r["answer"], *r["variants"][:8]]]
        raw = json.dumps(original, ensure_ascii=False, separators=(",", ":"))
        self.assertEqual(len(original), 108)
        self.assertEqual(hashlib.sha256(raw.encode("utf-8")).hexdigest(), BASELINE_SHA)

    def test_new_48_unique_private_safe_and_opt_in(self):
        phrases = []
        for row in self.records:
            self.assertEqual(len(row["variants"]), 12)
            self.assertEqual(row["audiences"], ["all_ai_bots"])
            self.assertEqual(row["constraints"], {"read_only": True, "requires_direct_address": True, "no_personal_data": True})
            self.assertEqual(row["language"], "ru")
            self.assertTrue(row["question"].lower().startswith(("пошути", "придумай", "расскажи", "дай")))
            self.assertFalse(set(row) & {"action", "execute", "sanction", "mute", "ban", "auto_apply"})
            phrases.extend([row["answer"], *row["variants"]])
        self.assertEqual(len(phrases), 156)
        self.assertEqual(len(set(map(normalize, phrases))), 156)
        self.assertTrue(all(not re.search(r"https?://|t\.me/|@[A-Za-z0-9_]|[0-9]{10,}", p, re.I) for p in phrases))


    def test_optional_humor_neighbor_lexical_gate(self):
        # Limited cross-pack check, not a semantic certification.
        neighbor = json.loads((ROOT / "packs/ru/optional_humor_qa.json").read_text(encoding="utf-8"))
        previous = [set(normalize(s).split()) for r in neighbor["records"]
                    for s in [r["answer"], *r.get("variants", [])]]
        for row in self.records:
            for response in row["variants"][-4:]:
                current = set(normalize(response).split())
                for old in previous:
                    union = len(current | old)
                    score = len(current & old) / union if union else 0
                    self.assertLess(score, 0.35, row["id"])

if __name__ == "__main__":
    unittest.main()
