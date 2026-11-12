"""T517: read-only qa.v1 humor integrity, exact SHA and mandatory opt-in."""
from __future__ import annotations

import hashlib
import json
import re
import unicodedata
import unittest
from pathlib import Path

from scripts.search_knowledge import KnowledgeSearch
from scripts.validate_qa_v1 import validate_qa_pack
from scripts.validate_pack import evaluate_snapshot_budget

ROOT = Path(__file__).resolve().parents[1]
PACK = "packs/ru/optional_humor_qa.json"
LIMIT = 8 * 1024 * 1024


def norm(value: str) -> str:
    value = unicodedata.normalize("NFKC", value).casefold().replace("ё", "е")
    return " ".join("".join(x if x.isalnum() else " " for x in value).split())


def texts(value):
    if isinstance(value, str) and 20 <= len(value) < 2000:
        yield value
    elif isinstance(value, list):
        for item in value:
            yield from texts(item)
    elif isinstance(value, dict):
        for item in value.values():
            yield from texts(item)


class OriginalHumorT517(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.manifest = json.loads((ROOT / "manifest.json").read_text("utf-8"))
        cls.payload = (ROOT / PACK).read_bytes()
        cls.data = json.loads(cls.payload)
        cls.index = KnowledgeSearch(ROOT)

    def test_schema_exact_sha_and_snapshot_budget(self):
        self.assertEqual(validate_qa_pack(self.data), 10)
        found = [x for x in self.manifest["packs"] if x["path"] == PACK]
        self.assertEqual(len(found), 1)
        self.assertEqual(hashlib.sha256(self.payload).hexdigest(), found[0]["sha256"])
        lengths = [(ROOT / x["path"]).stat().st_size for x in self.manifest["packs"]]
        total, remaining = evaluate_snapshot_budget((ROOT / "manifest.json").stat().st_size, lengths)
        self.assertGreater(remaining, 0, total)
        # The pack keeps its exact SHA, while unrelated vetted additions
        # may advance the manifest beyond the version at test creation.
        version = self.manifest["knowledge_version"]
        self.assertRegex(version, r"^\d{4}\.\d{2}\.\d{2}\.\d{3}$")
        self.assertGreaterEqual(tuple(map(int, version.split("."))), (2026, 11, 9, 3))

    def test_exactly_ninety_unique_original_responses(self):
        rows = self.data["records"]
        self.assertEqual(len(rows), 10)
        responses = [text for row in rows for text in (row["answer"], *row["variants"])]
        self.assertEqual(len(responses), 90)
        self.assertEqual(len(set(map(norm, responses))), 90)
        self.assertEqual(len({x["id"] for x in rows}), 10)
        self.assertTrue(all(len(row["variants"]) == 8 for row in rows))
        self.assertIn("Только по явному запросу", self.data["catalog"]["description"])
        self.assertTrue(all(row["constraints"] == self.data["catalog"]["constraints"] for row in rows))

    def test_no_reused_registered_phrase(self):
        current = {norm(t) for r in self.data["records"] for t in (r["answer"], *r["variants"])}
        earlier = set()
        for pack in self.manifest["packs"]:
            if pack["path"] == PACK:
                continue
            for text in texts(json.loads((ROOT / pack["path"]).read_text("utf-8"))):
                earlier.add(norm(text))
        self.assertFalse(current & earlier)

    def test_opt_in_is_required_for_exact_query_and_loose_search(self):
        query = self.data["records"][0]["question"]
        absent = self.index.search(query, context="direct")
        self.assertFalse(any(result[1] == PACK for result in absent))
        present = self.index.search(query, context="direct", humor_opt_in=True)
        self.assertTrue(any(result[0] == "humor_t517_daily" and result[1] == PACK for result in present))
        self.assertFalse(any(result[1] == PACK for result in self.index.search(
            "поделись повседневными делами", context="direct")))
        with self.assertRaises(ValueError):
            self.index.search(query, humor_opt_in="yes")

    def test_context_and_sensitive_humor_boundaries(self):
        for key in ("friendly", "darkfiction"):
            query = next(x["question"] for x in self.data["records"] if x["id"] == "humor_t517_" + key)
            hits = self.index.search(query, context="group_addressed", humor_opt_in=True, limit=20)
            self.assertFalse(any(hit[0] == "humor_t517_" + key for hit in hits))
            hits = self.index.search(query, context="private", humor_opt_in=True, limit=20)
            self.assertTrue(any(hit[0] == "humor_t517_" + key for hit in hits))


if __name__ == "__main__":
    unittest.main()
