"""v027: verify 80 new knowledge-format replies, registered digests and lossless context compaction."""
from __future__ import annotations
import hashlib
import json
import re
import unittest
from pathlib import Path
from scripts.validate_qa_v1 import validate_qa_pack, normalize_question

ROOT = Path(__file__).resolve().parents[1]
KNOWLEDGE = "packs/ru/knowledge_format.json"
CONTEXT = "packs/ru/context_cases.json"
KNOWLEDGE_SHA = "debb72afbec398996c7f91201f8694849f9f03284a25c47559862d419cd732ae"
CONTEXT_SHA = "69aa869899686a7d274b7dcb8559bc5a07b8310798c878fa88a2ee89ba0f6036"

def load(rel):
    return json.loads((ROOT / rel).read_text(encoding="utf-8"))

def token_set(value):
    return set(re.findall(r"\w+", normalize_question(value), re.UNICODE))

class KnowledgeFormatV027(unittest.TestCase):
    def test_manifest_and_size(self):
        manifest = load("manifest.json")
        entries = {entry["path"]: entry["sha256"] for entry in manifest["packs"]}
        version = tuple(int(x) for x in manifest["knowledge_version"].split("."))
        self.assertGreaterEqual(version, (2026, 11, 17, 27))
        if version == (2026, 11, 17, 27):
            self.assertEqual(entries[KNOWLEDGE], KNOWLEDGE_SHA)
        else:
            self.assertEqual(entries[KNOWLEDGE], hashlib.sha256((ROOT/KNOWLEDGE).read_bytes()).hexdigest())
        self.assertEqual(entries[CONTEXT], CONTEXT_SHA)
        for name, digest in ((CONTEXT, CONTEXT_SHA),):
            self.assertEqual(hashlib.sha256((ROOT/name).read_bytes()).hexdigest(), digest)
        total = len((ROOT/"manifest.json").read_bytes())
        total += sum(len((ROOT/entry).read_bytes()) for entry in entries)
        self.assertLessEqual(total, 8*1024*1024)
        context = load(CONTEXT)
        self.assertEqual(len(context["cases"]), 170)
        self.assertEqual(len(set(case["id"] for case in context["cases"])), 170)
        self.assertEqual(context["pack_version"], "2026.11.04.007")
        self.assertFalse(context["usage_policy"]["automatic_sanctions_allowed"])

    def test_80_replies_40_stable_intents_and_scope(self):
        data = load(KNOWLEDGE)
        self.assertEqual(validate_qa_pack(data), 40)
        self.assertEqual(data["catalog"]["id"], "knowledge_format")
        self.assertEqual(data["language"], "ru")
        self.assertEqual(data["catalog"]["audiences"], ["all_ai_bots"])
        self.assertTrue(data["catalog"]["constraints"]["read_only"])
        self.assertTrue(data["catalog"]["constraints"]["requires_direct_address"])
        rows = data["records"]
        self.assertEqual(len(rows), 40)
        self.assertEqual(len(set(row["id"] for row in rows)), 40)
        version = load("manifest.json")["knowledge_version"]
        v028 = version >= "2026.11.17.028"
        self.assertEqual(sorted(1+len(r["variants"]) for r in rows),
                         ([6]*10+[7]*30) if v028 else ([4]*10+[5]*30))
        new = set()
        for row in rows:
            self.assertTrue(row["question"].strip())
            self.assertLessEqual(len(row["variants"]), 8)
            all_answers = [row["answer"], *row["variants"]]
            normalized = [normalize_question(x) for x in all_answers]
            self.assertEqual(len(normalized), len(set(normalized)), row["id"])
            earlier = [row["answer"], *row["variants"][:(-4 if v028 else -2)]]
            for candidate in row["variants"][-4:-2] if v028 else row["variants"][-2:]:
                self.assertTrue(45 <= len(candidate) <= 280, (row["id"], candidate))
                n = normalize_question(candidate)
                self.assertNotIn(n, new)
                new.add(n)
                self.assertNotRegex(candidate, r"(?<!\w)(?:https?://\S+|@\w+|[\w.+-]+@[\w.-]+\.[A-Za-z]{2,})(?!\w)")
                a = token_set(candidate)
                for previous in earlier:
                    b = token_set(previous)
                    score = len(a & b) / len(a | b) if (a | b) else 1.0
                    self.assertLess(score, .75, (row["id"], score))
        self.assertEqual(len(new), 80)

    def test_no_cross_registered_exact_replies(self):
        manifest = load("manifest.json")
        v028 = load("manifest.json")["knowledge_version"] >= "2026.11.17.028"
        fresh = {normalize_question(x) for row in load(KNOWLEDGE)["records"]
                 for x in (row["variants"][-4:-2] if v028 else row["variants"][-2:])}
        others = set()
        for pack in manifest["packs"]:
            if pack["path"] == KNOWLEDGE:
                continue
            obj = load(pack["path"])
            if not isinstance(obj, dict):
                continue
            for record in obj.get("records", []):
                if not isinstance(record, dict):
                    continue
                for text in [record.get("answer"), *(record.get("variants") or [])]:
                    if isinstance(text, str):
                        others.add(normalize_question(text))
        self.assertFalse(fresh & others)

if __name__=="__main__":
    unittest.main()
