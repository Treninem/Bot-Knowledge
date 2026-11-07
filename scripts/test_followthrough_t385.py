"""T385: source-pinned 82 intents x 2 genuinely contextual staged alternatives."""
import hashlib
import json
import shutil
import tempfile
import unittest
from pathlib import Path

from scripts.colloquial_t305 import ROOT
from scripts.staged_context_selector import StagedContextSelector, _norm

SOURCE = "packs/ru/conversation_followthrough_qa.json"
P383 = "staging/ru/followthrough_t383_context_pool.json"
P384 = "staging/ru/followthrough_t384_context_pool.json"
STAGE = "staging/ru/followthrough_t385_context_pool.json"
NEIGHBORS = ("packs/ru/dialogue_help_qa.json",
             "packs/ru/collaborative_dialogue_qa.json",
             "packs/ru/response_boundaries_qa.json",
             "packs/ru/practical_recovery_qa.json")
SOURCE_SHA = "0862daf244df650bfd85217df3bedb9f2373a6e63dbabfa8d0c831a6fb289ff7"
P383_BLOB = "6aa6b98c0a3fdb5a68ebcc0071d6c80f0967f5f3"
P384_BLOB = "86dd0b4d5c7fbd298eacf82c8d2b5df6ff6013e5"
STAGE_BLOB = "2484f31c20df35b0af67bc41d6579164da6686e5"


def blob(raw):
    return hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()


class T385Test(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = json.loads((ROOT / SOURCE).read_text("utf-8"))
        cls.first = json.loads((ROOT / P383).read_text("utf-8"))
        cls.parent = json.loads((ROOT / P384).read_text("utf-8"))
        cls.stage = json.loads((ROOT / STAGE).read_text("utf-8"))
        cls.selector = StagedContextSelector(ROOT, STAGE)

    def test_sha_ancestry_and_cumulative_progress(self):
        manifest = json.loads((ROOT / "manifest.json").read_text("utf-8"))
        manifest_sha = next(p["sha256"] for p in manifest["packs"] if p["path"] == SOURCE)
        self.assertEqual(manifest_sha, SOURCE_SHA)
        self.assertEqual(hashlib.sha256((ROOT / SOURCE).read_bytes()).hexdigest(), SOURCE_SHA)
        self.assertEqual(blob((ROOT / P383).read_bytes()), P383_BLOB)
        self.assertEqual(blob((ROOT / P384).read_bytes()), P384_BLOB)
        self.assertEqual(blob((ROOT / STAGE).read_bytes()), STAGE_BLOB)
        self.assertEqual(self.stage["previous_stage"], P384)
        self.assertEqual(self.stage["previous_stage_blob_sha"], P384_BLOB)
        self.assertEqual(self.parent["previous_stage_blob_sha"], P383_BLOB)
        self.assertEqual(self.stage["source_pack_blob_sha"], blob((ROOT / SOURCE).read_bytes()))
        self.assertEqual(self.stage["checkpoint"], {
            "stage_id": "T385", "processed_intents": 82,
            "registered_count": 246, "added_candidates": 164,
            "finished_100": 0, "partial_intents": 82,
            "remaining_total": 7790, "rejected": 0
        })
        self.assertEqual(self.stage["cumulative_checkpoint"], {
            "baseline_registered": 246, "previous_staged": 164,
            "added_candidates": 164, "total": 574,
            "partial_intents": 82, "finished_100": 0,
            "remaining_total": 7626
        })

    def test_canonical_intents_and_unique_new_replies(self):
        originals = {r["id"]: r for r in self.source["records"]}
        self.assertEqual(len(originals), 82)
        entries = self.stage["entries"]
        self.assertEqual(len(entries), 82)
        self.assertEqual({e["intent_id"] for e in entries}, set(originals))
        self.assertFalse(self.stage["consumer_registered"])
        ids = []
        notes = []
        texts = []
        for row in entries:
            self.assertEqual(row["question"], originals[row["intent_id"]]["question"])
            self.assertEqual(row["registered_reply_count"], 3)
            self.assertEqual(row["staged_reply_count"], 2)
            self.assertEqual(len(row["replies"]), 2)
            for reply in row["replies"]:
                ids.append(reply["id"])
                notes.append(_norm(reply["context_note"]))
                texts.append(_norm(reply["text"]))
                self.assertEqual(reply["audiences"], ["all_ai_bots"])
                self.assertEqual(reply["language"], "ru")
                self.assertEqual(reply["style"], "neutral")
                self.assertTrue(reply["read_only"])
                self.assertIn(reply["context"], ("direct", "private", "group_addressed"))
        self.assertEqual(len(ids), 164)
        self.assertEqual(len(set(ids)), 164)
        self.assertEqual(len(set(texts)), 164)
        self.assertEqual(len(set(notes)), 164)

    def test_cross_pack_exact_and_near_duplicate_rejection(self):
        registered = []
        for path in (SOURCE, *NEIGHBORS):
            for row in json.loads((ROOT / path).read_text("utf-8"))["records"]:
                registered.extend((row["answer"], *row.get("variants", [])))
        staged = [r["text"] for p in (self.first, self.parent)
                  for entry in p["entries"] for r in entry["replies"]]
        earlier = [_norm(t) for t in (*registered, *staged)]
        earlier_set = set(earlier)
        previous_tokens = [set(t.split()) for t in earlier]
        newer = [_norm(r["text"]) for entry in self.stage["entries"] for r in entry["replies"]]
        self.assertFalse(set(newer) & earlier_set)
        for text in newer:
            tokens = set(text.split())
            for prior in previous_tokens:
                self.assertLess(len(tokens & prior) / len(tokens | prior), 0.78)

    def test_every_reply_requires_explicit_opt_in(self):
        for entry in self.stage["entries"]:
            for r in entry["replies"]:
                opts = dict(approved_reply_ids=frozenset({r["id"]}),
                            audience="all_ai_bots", context=r["context"],
                            addressed=True, local_permission=True)
                selected = self.selector.select(entry["intent_id"], **opts)
                self.assertIsNotNone(selected)
                self.assertEqual(selected.text, r["text"])
                for negative in ({"addressed": False}, {"addressed": 1},
                                 {"local_permission": False}, {"local_permission": 1},
                                 {"approved_reply_ids": frozenset()},
                                 {"approved_reply_ids": frozenset({42})},
                                 {"context": "unknown"},
                                 {"recent_ids": (r["id"],)},
                                 {"audience": "chat_moderators"}):
                    self.assertIsNone(
                        self.selector.select(entry["intent_id"], **(opts | negative))
                    )

    def test_source_parent_and_new_stage_tampering_fails_closed(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            for name in ("manifest.json", SOURCE, P383, P384, STAGE):
                dst = root / name
                dst.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(ROOT / name, dst)
            self.assertIsInstance(StagedContextSelector(root, STAGE), StagedContextSelector)
            for name in (SOURCE, P383, P384, STAGE):
                file = root / name
                file.write_bytes(file.read_bytes() + b" ")
                with self.assertRaises(ValueError):
                    StagedContextSelector(root, STAGE)
                shutil.copyfile(ROOT / name, file)


if __name__ == "__main__":
    unittest.main()
