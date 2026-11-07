"""T383: source-pinned, privacy-safe synthetic followthrough candidate regression."""
from __future__ import annotations

import hashlib
import json
import shutil
import tempfile
import unittest
from pathlib import Path

from scripts.colloquial_t305 import ROOT
from scripts.staged_context_selector import StagedContextSelector, _norm

STAGE = "staging/ru/followthrough_t383_context_pool.json"
SOURCE = "packs/ru/conversation_followthrough_qa.json"
RELATED = (
    SOURCE,
    "packs/ru/dialogue_help_qa.json",
    "packs/ru/collaborative_dialogue_qa.json",
    "packs/ru/response_boundaries_qa.json",
    "packs/ru/practical_recovery_qa.json",
)
PINNED_BLOB = "6aa6b98c0a3fdb5a68ebcc0071d6c80f0967f5f3"


def _blob(raw: bytes) -> str:
    return hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()


class FollowthroughT383Test(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.stage = json.loads((ROOT / STAGE).read_text("utf-8"))
        cls.registered = json.loads((ROOT / SOURCE).read_text("utf-8"))
        cls.selector = StagedContextSelector(ROOT, STAGE)

    def test_pinned_source_and_exact_checkpoint(self):
        source_bytes = (ROOT / SOURCE).read_bytes()
        stage_bytes = (ROOT / STAGE).read_bytes()
        manifest = json.loads((ROOT / "manifest.json").read_text("utf-8"))
        source_digest = next(x["sha256"] for x in manifest["packs"] if x["path"] == SOURCE)
        self.assertEqual(hashlib.sha256(source_bytes).hexdigest(), source_digest)
        self.assertEqual(self.stage["source_pack_manifest_sha256"], source_digest)
        self.assertEqual(self.stage["source_pack_blob_sha"], _blob(source_bytes))
        self.assertEqual(_blob(stage_bytes), PINNED_BLOB)
        self.assertFalse(self.stage["consumer_registered"])
        self.assertEqual(self.stage["constraints"], {
            "read_only": True, "requires_direct_address": True, "no_personal_data": True})
        canonical = {r["id"]: r for r in self.registered["records"]}
        self.assertEqual(len(canonical), 82)
        self.assertEqual(len(self.stage["entries"]), 82)
        self.assertEqual({e["intent_id"] for e in self.stage["entries"]}, set(canonical))
        self.assertEqual(self.stage["checkpoint"], {
            "stage_id": "T383", "processed_intents": 82, "registered_count": 246,
            "added_candidates": 82, "finished_100": 0, "partial_intents": 82,
            "remaining_total": 7872, "rejected": 0})
        for entry in self.stage["entries"]:
            original = canonical[entry["intent_id"]]
            self.assertEqual(entry["question"], original["question"])
            self.assertEqual(entry["registered_reply_count"], 3)
            self.assertEqual(entry["staged_reply_count"], 1)

    def test_uniqueness_cross_pack_and_lexical_similarity(self):
        existing = []
        for path in RELATED:
            rows = json.loads((ROOT / path).read_text("utf-8"))["records"]
            for row in rows:
                existing += [row["answer"], *row.get("variants", [])]
        staged = [x for e in self.stage["entries"] for x in e["replies"]]
        self.assertEqual(len(staged), 82)
        ids = [x["id"] for x in staged]
        texts = [_norm(x["text"]) for x in staged]
        notes = [_norm(x["context_note"]) for x in staged]
        self.assertEqual(len(set(ids)), 82)
        self.assertEqual(len(set(texts)), 82)
        self.assertEqual(len(set(notes)), 82)
        prior = {_norm(text) for text in existing}
        self.assertFalse(set(texts) & prior)
        prior_tokens = [set(x.split()) for x in prior]
        for answer in staged:
            self.assertTrue(answer["read_only"])
            self.assertEqual(answer["audiences"], ["all_ai_bots"])
            self.assertEqual(answer["style"], "neutral")
            self.assertIn(answer["context"], ("direct", "private", "group_addressed"))
            tokens = set(_norm(answer["text"]).split())
            for others in prior_tokens:
                self.assertLess(len(tokens & others) / len(tokens | others), 0.78)

    def test_every_reply_needs_exact_explicit_approval(self):
        for entry in self.stage["entries"]:
            item = entry["replies"][0]
            args = dict(approved_reply_ids=frozenset({item["id"]}),
                        audience="all_ai_bots", context=item["context"],
                        addressed=True, local_permission=True)
            selected = self.selector.select(entry["intent_id"], **args)
            self.assertIsNotNone(selected)
            self.assertEqual(selected.text, item["text"])
            self.assertEqual(selected.stage_path, STAGE)
            for override in (
                {"approved_reply_ids": frozenset()}, {"audience": "community_bots"},
                {"addressed": False}, {"local_permission": False},
                {"context": "private" if item["context"] != "private" else "direct"},
                {"recent_ids": (item["id"],)},
            ):
                self.assertIsNone(self.selector.select(entry["intent_id"], **(args | override)))
            self.assertIsNone(self.selector.select("unknown_intent", **args))

    def test_tampering_fails_closed_without_network(self):
        with tempfile.TemporaryDirectory() as dirname:
            tmp = Path(dirname)
            for rel in ("manifest.json", SOURCE, STAGE):
                p = tmp / rel
                p.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(ROOT / rel, p)
            self.assertIsInstance(StagedContextSelector(tmp, STAGE), StagedContextSelector)
            stage_file = tmp / STAGE
            stage_file.write_bytes(stage_file.read_bytes() + b" ")
            with self.assertRaises(ValueError):
                StagedContextSelector(tmp, STAGE)
            shutil.copyfile(ROOT / STAGE, stage_file)
            original_file = tmp / SOURCE
            original_file.write_bytes(original_file.read_bytes() + b" ")
            with self.assertRaises(ValueError):
                StagedContextSelector(tmp, STAGE)


if __name__ == "__main__":
    unittest.main()
