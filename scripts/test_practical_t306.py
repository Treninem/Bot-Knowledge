"""T306: verified recovery of exact older T159 contributions without overwrite."""
import json
import unittest
from pathlib import Path
from scripts.practical_t306 import PracticalT306, STAGE, SOURCE, ROOT, norm, blob_sha

class TestPracticalT306(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.selector = PracticalT306(ROOT)
        cls.stage = json.loads((ROOT / STAGE).read_text("utf-8"))
        cls.parent = json.loads((ROOT / SOURCE).read_text("utf-8"))

    def test_original_parent_pinned_and_unregistered(self):
        self.assertEqual(self.stage["source_pack_blob_sha"], blob_sha((ROOT / SOURCE).read_bytes()))
        self.assertEqual(self.stage["provenance_pr"], 241)
        self.assertFalse(self.stage["consumer_registered"])
        manifest = json.loads((ROOT / "manifest.json").read_text("utf-8"))
        registered = {x["path"]: x["sha256"] for x in manifest["packs"]}
        self.assertNotIn(STAGE, registered)
        self.assertEqual(self.stage["source_pack_manifest_sha256"], registered[SOURCE])
        self.assertEqual(len(self.selector.cache_identity), 3)

    def test_96_salvaged_unique_replies_and_denials(self):
        seen_id, seen_text, seen_note = set(), set(), set()
        source = {norm(a) for row in self.parent["records"] for a in [row["answer"], *row["variants"]]}
        self.assertEqual(len(source), 216)
        self.assertEqual(len(self.stage["entries"]), 24)
        for entry in self.stage["entries"]:
            self.assertEqual(entry["baseline_registered"] + len(entry["replies"]), 13)
            for reply in entry["replies"]:
                self.assertNotIn(reply["id"], seen_id)
                self.assertNotIn(norm(reply["text"]), seen_text | source)
                self.assertNotIn(norm(reply["context_note"]), seen_note)
                seen_id.add(reply["id"])
                seen_text.add(norm(reply["text"]))
                seen_note.add(norm(reply["context_note"]))
                kwargs = dict(approved_reply_ids=frozenset({reply["id"]}),
                              audience="all_ai_bots", context=reply["context"],
                              addressed=True, local_permission=True)
                actual = self.selector.select(entry["intent_id"], **kwargs)
                self.assertIsNotNone(actual)
                self.assertEqual(actual.text, reply["text"])
                for denial in (
                    {"approved_reply_ids": frozenset()},
                    {"approved_reply_ids": [reply["id"]]},
                    {"audience": "community_bots"},
                    {"context": "unknown"},
                    {"addressed": False},
                    {"local_permission": False},
                    {"recent_ids": (reply["id"],)},
                    {"recent_ids": [reply["id"]]},
                ):
                    self.assertIsNone(self.selector.select(entry["intent_id"], **(kwargs | denial)))
        self.assertEqual(len(seen_id), 96)
        self.assertEqual(len(seen_text), 96)
        self.assertEqual(len(seen_note), 96)

    def test_malformed_stage_or_missing_intent_rejected(self):
        with self.assertRaises(ValueError):
            PracticalT306(ROOT, "staging/ru/unchecked.json")
        self.assertIsNone(self.selector.select("nonexistent", approved_reply_ids=frozenset({"fake"}),
            audience="all_ai_bots", context="direct", addressed=True, local_permission=True))

if __name__ == "__main__":
    unittest.main()
