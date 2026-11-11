"""Exact source-anchored, read-only QA of independent C/D contextual stages."""
from __future__ import annotations

import hashlib
import json
import re
import unittest
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PATHS = [
    ROOT / ("staging/ru/structured_information_20261111_delta_" + suffix + ".json")
    for suffix in "abcd"
]
SOURCE = ROOT / "packs/ru/structured_information_qa.json"
SHA256 = "55b3f6126d36cd92687d005b7fedf5a11df9ee61cf453103accdf1f13c8498f0"
SOURCE_BLOB = "8b3d596b5b50d3d319ebf450c96d5623fc99d26a"


def normalized(text: str) -> str:
    value = unicodedata.normalize("NFKC", text).casefold().replace("ё", "е")
    return " ".join(re.findall(r"[^\W_]+", value, flags=re.UNICODE))


def words(text: str) -> set[str]:
    return set(normalized(text).split())


def jaccard(a: set[str], b: set[str]) -> float:
    return len(a & b) / len(a | b) if (a | b) else 1.0


def all_strings(value):
    if isinstance(value, dict):
        for key, item in value.items():
            if key in ("answer", "response", "text") and isinstance(item, str):
                yield item
            if isinstance(item, (dict, list)):
                yield from all_strings(item)
    elif isinstance(value, list):
        for item in value:
            yield from all_strings(item)


class StructuredRemainderTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.stages = [json.loads(p.read_text(encoding="utf-8")) for p in PATHS]
        cls.source = json.loads(SOURCE.read_text(encoding="utf-8"))
        cls.records = {rec["id"]: rec for rec in cls.source["records"]}
        cls.entries = [entry for s in cls.stages for entry in s["entries"]]
        cls.all_replies = [reply for entry in cls.entries for reply in entry["replies"]]
        cls.new_replies = [
            reply for stage in cls.stages[2:]
            for entry in stage["entries"] for reply in entry["replies"]
        ]

    def test_source_hash_and_registry_scope(self):
        raw = SOURCE.read_bytes()
        self.assertEqual(hashlib.sha256(raw).hexdigest(), SHA256)
        git_blob = hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()
        self.assertEqual(git_blob, SOURCE_BLOB)
        manifest = json.loads((ROOT / "manifest.json").read_text(encoding="utf-8"))
        packs = {p["path"]: p["sha256"] for p in manifest["packs"]}
        self.assertEqual(packs["packs/ru/structured_information_qa.json"], SHA256)
        self.assertEqual(manifest["knowledge_version"], "2026.11.09.003")
        for path, stage in zip(PATHS, self.stages):
            self.assertNotIn(path.relative_to(ROOT).as_posix(), packs)
            self.assertFalse(stage["consumer_registered"])
            self.assertEqual(stage["source_pack_manifest_sha256"], SHA256)
            self.assertEqual(stage["source_pack_blob_sha"], SOURCE_BLOB)
            self.assertEqual(stage["audiences"], ["all_ai_bots"])
            for flag in ("read_only", "requires_direct_address", "requires_context_match",
                         "no_personal_data", "no_sanctions"):
                self.assertIs(stage["constraints"][flag], True)

    def test_exact_stage_inventory_and_coverage(self):
        self.assertEqual([len(s["entries"]) for s in self.stages], [30, 30, 25, 29])
        self.assertEqual([sum(len(e["replies"]) for e in s["entries"]) for s in self.stages],
                         [150, 150, 75, 87])
        self.assertEqual(len(self.new_replies), 162)
        self.assertEqual(len(self.all_replies), 462)
        self.assertEqual(len(self.entries), 114)
        self.assertEqual(len(self.records), 114)
        ids = [e["intent_id"] for e in self.entries]
        self.assertEqual(len(ids), len(set(ids)))
        self.assertEqual(set(ids), set(self.records))
        for stage in self.stages[2:]:
            self.assertEqual(stage["checkpoint"]["added_candidates"],
                             sum(len(e["replies"]) for e in stage["entries"]))
            self.assertEqual(stage["checkpoint"]["finished_100"], 0)
        for e in self.entries:
            src = self.records[e["intent_id"]]
            self.assertEqual(e["canonical_question"], src["question"])
            self.assertEqual(e["published_count"], 1 + len(src["variants"]))
            self.assertEqual(e["published_count"], 3)
            self.assertEqual(e["unmerged_pr_229_count"], 9)
            self.assertEqual(e["added_candidates"], len(e["replies"]))
            self.assertEqual(e["target"], 100)
            for reply in e["replies"]:
                self.assertTrue(reply["id"].startswith(e["intent_id"] + "_supp_"))
                self.assertEqual(reply["language"], "ru")
                self.assertEqual(reply["style"], "helpful_precision")
                self.assertEqual(reply["audiences"], ["all_ai_bots"])
                self.assertEqual(reply["context"], "direct")
                self.assertIs(reply["read_only"], True)
                self.assertGreaterEqual(len(reply["context_note"]), 25)
                self.assertGreaterEqual(len(reply["text"]), 40)

    def test_unique_text_ids_and_context_and_no_private_data_or_sanction(self):
        for key in ("id", "text", "context_note"):
            values = [r[key] if key == "id" else normalized(r[key])
                      for r in self.all_replies]
            self.assertEqual(len(values), len(set(values)), key)
        for r in self.all_replies:
            self.assertNotRegex(r["text"], r"(?i)(ghp_|github_pat_|\bt\.me/|@\w+)")
            self.assertNotRegex(r["text"], r"(?i)[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,}")
            self.assertNotRegex(normalized(r["text"]),
                                r"\bя (?:забанил|замутил|выдал роль|раскрыл данные)\b")
            self.assertIn("без санкций", r["avoid"].lower()) if r in self.new_replies else self.assertIn("не применять санкции", r["avoid"])

    def test_no_registered_pack_exact_duplicates_and_low_token_overlap(self):
        manifest = json.loads((ROOT / "manifest.json").read_text(encoding="utf-8"))
        registered = set()
        for item in manifest["packs"]:
            package = json.loads((ROOT / item["path"]).read_text(encoding="utf-8"))
            registered.update(normalized(t) for t in all_strings(package))
        self.assertFalse(registered.intersection(normalized(r["text"]) for r in self.all_replies))
        prior = [r["answer"] for r in self.source["records"]]
        prior += [v for r in self.source["records"] for v in r["variants"]]
        token_prior = [words(v) for v in prior + [r["text"] for r in self.all_replies[:300]]]
        token_new = [words(r["text"]) for r in self.new_replies]
        for i, left in enumerate(token_new):
            for right in token_prior + token_new[:i]:
                self.assertLess(jaccard(left, right), 0.68, (i, left, right))


if __name__ == "__main__":
    unittest.main()
