"""V028: 80 new context-relevant RU replies, immutable v027 lineage, 8 MiB budget."""
import copy
import hashlib
import json
import re
import unittest
from pathlib import Path

from scripts.validate_qa_v1 import validate_qa_pack, normalize_question

ROOT = Path(__file__).resolve().parents[1]
PACK = "packs/ru/knowledge_format.json"
COMPACT = "packs/ru/pragmatic_contrasts.json"
PREVIOUS_PACK_SHA = "debb72afbec398996c7f91201f8694849f9f03284a25c47559862d419cd732ae"
PACK_SHA = "7ee49105c38ef02ef48de3a2a7cb8f6861bd7799a8ffe202ab025ed7d98d19ae"
COMPACT_SHA = "ded710d7e40ebbb8cef03f12fa27823a97a1768083a8f92df7a9df09c3b3478d"


def load(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def normalize(text):
    return normalize_question(text)


def lexical_similarity(x, y):
    a = set(re.findall(r"\w+", normalize(x), flags=re.UNICODE))
    b = set(re.findall(r"\w+", normalize(y), flags=re.UNICODE))
    return len(a & b) / len(a | b) if a | b else 1.0


class KnowledgeFormatV028(unittest.TestCase):
    def test_manifest_real_sha_and_snapshot(self):
        m = load("manifest.json")
        self.assertGreaterEqual(
            tuple(map(int, m["knowledge_version"].split("."))), (2026, 11, 17, 28))
        files = {item["path"]: item["sha256"] for item in m["packs"]}
        self.assertEqual(len(files), len(m["packs"]))
        if m["knowledge_version"] == "2026.11.17.028":
            self.assertEqual(files[PACK], PACK_SHA)
        else:
            self.assertEqual(files[PACK], hashlib.sha256((ROOT / PACK).read_bytes()).hexdigest())
        self.assertEqual(files[COMPACT], COMPACT_SHA)
        size = (ROOT / "manifest.json").stat().st_size
        for path, expected in files.items():
            content = (ROOT / path).read_bytes()
            self.assertEqual(hashlib.sha256(content).hexdigest(), expected, path)
            size += len(content)
        self.assertLessEqual(size, 8 * 1024 * 1024)
        self.assertEqual(len(load(COMPACT)["pairs"]), 48)
        self.assertEqual(len(load(COMPACT)["categories"]), 12)
        self.assertTrue(load(COMPACT)["usage_policy"]["no_automatic_sanctions"])
        self.assertTrue(load(COMPACT)["usage_policy"]["no_privileged_actions"])
        print("V028_SNAPSHOT_OK bytes=", size)

    def test_80_new_and_190_preserved(self):
        pack = load(PACK)
        self.assertEqual(validate_qa_pack(pack), 40)
        self.assertEqual(pack["catalog"]["audiences"], ["all_ai_bots"])
        self.assertTrue(pack["catalog"]["constraints"]["read_only"])
        self.assertTrue(pack["catalog"]["constraints"]["requires_direct_address"])
        self.assertEqual(len(pack["records"]), 40)
        self.assertEqual(len({r["id"] for r in pack["records"]}), 40)
        extended = load("manifest.json")["knowledge_version"] >= "2026.11.17.029"
        self.assertEqual(sorted(1 + len(r["variants"]) for r in pack["records"]),
                         [9] * 40 if extended else [6] * 10 + [7] * 30)
        prev = copy.deepcopy(pack)
        v028 = copy.deepcopy(pack)
        answers, seen, new = 0, set(), []
        for index, (row, past) in enumerate(zip(pack["records"], prev["records"])):
            count_v028 = 5 if index < 10 else 6
            self.assertEqual(len(row["variants"]), 8 if extended else count_v028)
            v028["records"][index]["variants"] = row["variants"][:count_v028]
            past["variants"] = row["variants"][:count_v028-2]
            answers += 1 + len(past["variants"])
            earlier = [row["answer"], *past["variants"]]
            for answer in [row["answer"], *row["variants"]]:
                key = normalize(answer)
                self.assertNotIn(key, seen, row["id"])
                seen.add(key)
            for answer in row["variants"][count_v028-2:count_v028]:
                self.assertTrue(80 <= len(answer) <= 350, (row["id"], answer))
                self.assertNotRegex(answer, r"(?<!\w)(?:https?://\S+|@\w+|[\w.+-]+@[\w.-]+\.[A-Za-z]{2,})(?!\w)")
                self.assertNotRegex(answer.lower(), r"\b(?:забаню|заблокировал участника|выдал мут)\b")
                self.assertLess(max(lexical_similarity(answer, old) for old in earlier), .48, row["id"])
                new.append(answer)
        original = json.dumps(prev, ensure_ascii=False, separators=(",", ":")) + "\n"
        self.assertEqual(hashlib.sha256(original.encode("utf-8")).hexdigest(), PREVIOUS_PACK_SHA)
        v028_serialized = json.dumps(v028, ensure_ascii=False, separators=(",", ":")) + "\n"
        self.assertEqual(hashlib.sha256(v028_serialized.encode("utf-8")).hexdigest(), PACK_SHA)
        self.assertEqual(answers, 190)
        self.assertEqual(len(new), 80)
        self.assertEqual(len({normalize(x) for x in new}), 80)
        print("V028_INCREMENTS_OK previous=190 new=80 total=270")


if __name__ == "__main__":
    unittest.main()
