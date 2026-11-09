"""T525: test exactly 120 new creative replies against the T524 baseline."""
from __future__ import annotations

import hashlib
import json
import re
import subprocess
import unicodedata
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "packs/ru/social_dialogues.json"
T524 = ROOT / "staging/ru/creative_microstories_t524_context_pool.json"
T525 = ROOT / "staging/ru/creative_microstories_t525_context_pool.json"


def norm(value):
    value = unicodedata.normalize("NFKC", value).casefold().replace("ё", "е")
    return " ".join("".join(c if c.isalnum() else " " for c in value).split())


def every_string(node):
    if isinstance(node, str):
        yield node
    elif isinstance(node, dict):
        for value in node.values():
            yield from every_string(value)
    elif isinstance(node, list):
        for value in node:
            yield from every_string(value)


class T525Quality(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.old = json.loads(T524.read_text("utf-8"))
        cls.new = json.loads(T525.read_text("utf-8"))
        cls.manifest = json.loads((ROOT / "manifest.json").read_text("utf-8"))

    def test_source_hash_and_isolation(self):
        digest = hashlib.sha256(SOURCE.read_bytes()).hexdigest()
        self.assertEqual(self.new["source_pack_manifest_sha256"], digest)
        self.assertEqual(self.old["source_pack_manifest_sha256"], digest)
        self.assertIn({"path": "packs/ru/social_dialogues.json", "sha256": digest},
                      self.manifest["packs"])
        blob = subprocess.check_output(
            ["git", "hash-object", str(SOURCE)], cwd=ROOT, text=True).strip()
        self.assertEqual(self.new["source_pack_blob_sha"], blob)
        self.assertFalse(self.new["consumer_registered"])
        self.assertFalse(self.old["consumer_registered"])
        self.assertNotIn("staging/ru/creative_microstories_t525_context_pool.json",
                         [p["path"] for p in self.manifest["packs"]])
        for flag in ("no_sanctions", "fiction_must_be_labeled",
                     "requires_explicit_creative_request"):
            self.assertTrue(self.new["constraints"][flag])

    def test_stable_intents_and_checkpoint(self):
        old = {e["intent_id"]: e for e in self.old["entries"]}
        new = {e["intent_id"]: e for e in self.new["entries"]}
        self.assertEqual(len(old), len(new))
        self.assertEqual(len(new), 10)
        self.assertEqual(set(old), set(new))
        cp = self.new["checkpoint"]
        self.assertEqual(cp["stage_id"], "T525")
        self.assertEqual(cp["base_commit"],
                         "639722e000ed84648a78c579d301f1d36cb6c959")
        self.assertEqual(cp["added_candidates"], 120)
        self.assertEqual(cp["remaining_total"], 760)
        self.assertEqual(cp["finished_100"], 0)
        for ident, entry in new.items():
            previous = old[ident]
            self.assertEqual(entry["canonical_question"], previous["canonical_question"])
            self.assertEqual(entry["baseline_registered"], 0)
            self.assertEqual(entry["prior_for_stable_id"], 12)
            self.assertEqual(entry["total_staged"], 24)
            self.assertEqual(entry["added_candidates"], 12)
            self.assertEqual(entry["target"], 100)
            self.assertEqual(entry["remaining"], 76)
            self.assertEqual(len(entry["replies"]), 12)

    def test_originality_scope_and_context(self):
        a = [r for e in self.old["entries"] for r in e["replies"]]
        b = [r for e in self.new["entries"] for r in e["replies"]]
        self.assertEqual(len(a), 120)
        self.assertEqual(len(b), 120)
        all_replies = a + b
        ids = [r["id"] for r in all_replies]
        texts = [norm(r["text"]) for r in all_replies]
        notes = [norm(r["context_note"]) for r in all_replies]
        self.assertEqual(len(ids), len(set(ids)))
        self.assertEqual(len(texts), len(set(texts)))
        self.assertEqual(len(notes), len(set(notes)))
        baseline = {norm(s) for s in every_string(json.loads(SOURCE.read_text("utf-8")))
                    if len(s) > 50}
        self.assertTrue(set(texts).isdisjoint(baseline))
        for r in b:
            self.assertEqual(r["language"], "ru")
            self.assertEqual(r["format"], "microstory")
            self.assertEqual(r["context"], "direct")
            self.assertEqual(r["audiences"], ["all_ai_bots"])
            self.assertTrue(r["read_only"])
            self.assertIn("вымышленную", r["context_note"])
            self.assertIn("Это вымысел", r["avoid"])
            self.assertIn("прямому запросу", r["avoid"])
            self.assertTrue(65 <= len(r["text"]) <= 480)
            self.assertNotRegex(r["text"], r"(?i)https?://|@\\w+|(?:\\+7|\\b8)\\d{10}\\b")
        prev = [set(norm(r["text"]).split()) for r in a]
        for r in b:
            t = set(norm(r["text"]).split())
            for p in prev:
                self.assertLess(len(t & p) / len(t | p), 0.78)
            prev.append(t)


if __name__ == "__main__":
    unittest.main()
