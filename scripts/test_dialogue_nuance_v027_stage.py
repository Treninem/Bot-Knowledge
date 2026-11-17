"""Exact-source, distinct-context and privacy checks for staged dialogue v027."""
from __future__ import annotations
import hashlib
import json
import re
import unittest
from pathlib import Path
from scripts.validate_qa_v1 import normalize_question, validate_qa_pack

ROOT = Path(__file__).resolve().parents[1]
PACK = "packs/ru/dialogue_nuance_v024_qa.json"
STAGE = "staging/ru/dialogue_nuance_v027_context_overflow_20261117.json"
PRIOR = "staging/ru/dialogue_nuance_v025_overflow_20261117.json"
PINNED_SHA256 = "721ebd555f86a2106ccd3cd1d4dc721fc0ffd7030d20f6df96a7709f1a08c8d0"

def read(path):
    return json.loads((ROOT / path).read_text("utf-8"))

def tokens(s):
    return set(re.findall(r"\w+", normalize_question(s), re.UNICODE))

class DialogueStageV027(unittest.TestCase):
    def test_new_delta_and_source(self):
        manifest = read("manifest.json")
        entries = {p["path"]: p["sha256"] for p in manifest["packs"]}
        self.assertEqual(entries[PACK], PINNED_SHA256)
        self.assertEqual(hashlib.sha256((ROOT / PACK).read_bytes()).hexdigest(), PINNED_SHA256)
        source, prior, stage = read(PACK), read(PRIOR), read(STAGE)
        self.assertEqual(validate_qa_pack(source), 15)
        self.assertEqual(stage["source_pack_sha256"], PINNED_SHA256)
        self.assertEqual(stage["source_manifest_version"], "2026.11.17.026")
        self.assertEqual(stage["consumer_registered"], False)
        self.assertEqual(stage["read_only"], True)
        self.assertEqual(stage["audiences"], ["all_ai_bots"])
        self.assertEqual(stage["previous_stage"], PRIOR)
        self.assertEqual(stage["target_pack"], PACK)
        self.assertEqual(len(stage["records"]), 15)
        base = {r["id"]: r for r in source["records"]}
        prev = {r["intent_id"]: r for r in prior["records"]}
        self.assertEqual(set(base), set(prev))
        seen_ids, new_texts = set(), set()
        for item in stage["records"]:
            ident = item["intent_id"]
            self.assertIn(ident, base)
            self.assertNotIn(ident, seen_ids)
            seen_ids.add(ident)
            original = [base[ident]["answer"], *base[ident]["variants"]]
            old_staged = prev[ident]["variants"]
            self.assertEqual(len(original), 9)
            self.assertEqual(len(old_staged), 2)
            self.assertEqual(item["base_registered_count"], 9)
            self.assertEqual(item["prior_unregistered_count"], 2)
            self.assertEqual(len(item["variants"]), 3)
            existing = [normalize_question(x) for x in original + old_staged]
            self.assertEqual(len(existing), len(set(existing)))
            context_notes = set()
            for i, reply in enumerate(item["variants"], 12):
                self.assertEqual(reply["id"], f"{ident}_v{i}")
                self.assertIn(reply["contexts"][0], ("direct", "private", "group_addressed"))
                self.assertTrue(set(reply["contexts"]).issubset({"direct", "private", "group_addressed"}))
                self.assertGreater(len(reply["when"]), 24)
                self.assertGreater(len(reply["avoid"]), 20)
                text = reply["text"]
                self.assertGreater(len(text), 45)
                self.assertLess(len(text), 250)
                norm = normalize_question(text)
                self.assertTrue(norm)
                self.assertNotIn(norm, existing)
                self.assertNotIn(norm, new_texts)
                self.assertNotIn(reply["when"], context_notes)
                context_notes.add(reply["when"])
                terms = tokens(text)
                for prior_text in original + old_staged:
                    similar = tokens(prior_text)
                    jac = len(terms & similar) / len(terms | similar) if (terms | similar) else 1
                    self.assertLess(jac, 0.75, (ident, text, prior_text))
                existing.append(norm)
                original.append(text)
                new_texts.add(norm)
                self.assertNotRegex(text, r"(?<!\w)(?:https?://\S+|@\w+|[\w.+-]+@[\w.-]+\.[A-Za-z]{2,})(?!\w)")
        self.assertEqual(len(seen_ids), 15)
        self.assertEqual(len(new_texts), 45)

    def test_no_registered_text_collision(self):
        stage = read(STAGE)
        texts = {normalize_question(v["text"]) for r in stage["records"] for v in r["variants"]}
        registered = set()
        for item in read("manifest.json")["packs"]:
            data = read(item["path"])
            if not isinstance(data, dict):
                continue
            for r in data.get("records", []):
                if not isinstance(r, dict):
                    continue
                for v in [r.get("answer"), *(r.get("variants") or [])]:
                    if isinstance(v, str):
                        registered.add(normalize_question(v))
        self.assertFalse(texts & registered)

if __name__ == "__main__":
    unittest.main()
