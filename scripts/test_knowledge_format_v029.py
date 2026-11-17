"""v029: exact 90 new synthetic replies, pinned v028 prefix and snapshot boundary."""
from __future__ import annotations
import copy
import hashlib
import json
import re
import unittest
from pathlib import Path

from scripts.validate_qa_v1 import normalize_question, validate_qa_pack

ROOT = Path(__file__).resolve().parents[1]
KNOWLEDGE = "packs/ru/knowledge_format.json"
ENGLISH = "packs/ru/english_conversation_nuance_qa.json"
OLD_SHA = "7ee49105c38ef02ef48de3a2a7cb8f6861bd7799a8ffe202ab025ed7d98d19ae"
NEW_SHA = "45dd314dc1eb82f1ce83ca8e63ee2c1e21d8101edc4798e0dc96fb8cbb32b3ca"
EN_SHA = "21835e41338ce92fdd0db17211561fc8e6e74dbdd3ddbe2281dd368bfbc94bab"

def read(rel):
    return json.loads((ROOT / rel).read_text(encoding="utf-8"))

def lexical(a, b):
    u = set(re.findall(r"\w+", normalize_question(a), re.UNICODE))
    v = set(re.findall(r"\w+", normalize_question(b), re.UNICODE))
    return len(u & v) / len(u | v) if u | v else 1.0

class KnowledgeFormatV029(unittest.TestCase):
    def test_manifest_and_exact_budget(self):
        manifest = read("manifest.json")
        version = tuple(int(part) for part in manifest["knowledge_version"].split("."))
        self.assertGreaterEqual(version, (2026, 11, 17, 29))
        entries = {p["path"]: p["sha256"] for p in manifest["packs"]}
        self.assertEqual(len(entries), len(manifest["packs"]))
        self.assertEqual(len(entries), 54)
        self.assertEqual(entries[KNOWLEDGE], NEW_SHA)
        self.assertEqual(entries[ENGLISH], EN_SHA)
        size = (ROOT / "manifest.json").stat().st_size
        for name, expected in entries.items():
            payload = (ROOT / name).read_bytes()
            self.assertEqual(hashlib.sha256(payload).hexdigest(), expected, name)
            size += len(payload)
        self.assertLessEqual(size, 8 * 1024 * 1024)
        if version == (2026, 11, 17, 29):
            self.assertEqual(size, 8384593)  # exact historical v029 snapshot
        self.assertEqual(len(read(ENGLISH)["records"]), 87)

    def test_90_new_and_previous_270_preserved(self):
        data = read(KNOWLEDGE)
        self.assertEqual(validate_qa_pack(data), 40)
        self.assertEqual(data["catalog"]["id"], "knowledge_format")
        self.assertEqual(data["catalog"]["audiences"], ["all_ai_bots"])
        self.assertTrue(data["catalog"]["constraints"]["read_only"])
        self.assertTrue(data["catalog"]["constraints"]["requires_direct_address"])
        self.assertEqual(len({r["id"] for r in data["records"]}), 40)
        self.assertEqual(len(data["records"]), 40)
        older = copy.deepcopy(data)
        all_seen, new_seen = set(), set()
        old_total, new_total = 0, 0
        for i, (current, previous) in enumerate(zip(data["records"], older["records"])):
            count_new = 3 if i < 10 else 2
            variants = current["variants"]
            self.assertEqual(len(variants), 8)
            previous["variants"] = variants[:-count_new]
            old = [current["answer"], *previous["variants"]]
            old_total += len(old)
            for answer in [current["answer"], *variants]:
                key = normalize_question(answer)
                self.assertNotIn(key, all_seen, current["id"])
                all_seen.add(key)
            for answer in variants[-count_new:]:
                new_total += 1
                key = normalize_question(answer)
                self.assertTrue(60 <= len(answer) <= 350, current["id"])
                self.assertNotIn(key, new_seen)
                new_seen.add(key)
                self.assertNotRegex(answer, r"(?<!\w)(?:https?://\S+|@\w+|[\w.+-]+@[\w.-]+\.[A-Za-z]{2,})(?!\w)")
                self.assertLess(max(lexical(answer, earlier) for earlier in old), 0.48, current["id"])
                old.append(answer)
        serialized = json.dumps(older, ensure_ascii=False, separators=(",", ":")) + "\n"
        self.assertEqual(hashlib.sha256(serialized.encode("utf-8")).hexdigest(), OLD_SHA)
        self.assertEqual(old_total, 270)
        self.assertEqual(new_total, 90)
        self.assertEqual(len(new_seen), 90)
        self.assertEqual(len(all_seen), 360)

if __name__ == "__main__":
    unittest.main()
