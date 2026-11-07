"""T386: approved 82-context continuation with pinned three-stage history."""
import hashlib
import json
import shutil
import tempfile
import unittest
from pathlib import Path

from scripts.colloquial_t305 import ROOT
from scripts.staged_context_selector import StagedContextSelector, _norm

SOURCE = "packs/ru/conversation_followthrough_qa.json"
PREVIOUS = (
    "staging/ru/followthrough_t383_context_pool.json",
    "staging/ru/followthrough_t384_context_pool.json",
    "staging/ru/followthrough_t385_context_pool.json",
)
STAGE = "staging/ru/followthrough_t386_context_pool.json"
SOURCE_SHA = "0862daf244df650bfd85217df3bedb9f2373a6e63dbabfa8d0c831a6fb289ff7"
SOURCE_BLOB = "707fcaa6440d398a730840362602d4532ab92036"
HISTORY_BLOBS = (
    "6aa6b98c0a3fdb5a68ebcc0071d6c80f0967f5f3",
    "86dd0b4d5c7fbd298eacf82c8d2b5df6ff6013e5",
    "2484f31c20df35b0af67bc41d6579164da6686e5",
)
STAGE_BLOB = "ebee173a7fd4003f832bbdca87cfd10da9ee3e82"
NEIGHBORS = (
    "packs/ru/dialogue_help_qa.json",
    "packs/ru/collaborative_dialogue_qa.json",
    "packs/ru/response_boundaries_qa.json",
    "packs/ru/practical_recovery_qa.json",
)


def blob(raw):
    return hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()


class T386Test(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.stage = json.loads((ROOT / STAGE).read_text("utf-8"))
        cls.source = json.loads((ROOT / SOURCE).read_text("utf-8"))
        cls.history = [json.loads((ROOT / path).read_text("utf-8")) for path in PREVIOUS]
        cls.selector = StagedContextSelector(ROOT, STAGE)

    def test_actual_sha_chain_and_progress(self):
        manifest = json.loads((ROOT / "manifest.json").read_text("utf-8"))
        source_hash = next(row["sha256"] for row in manifest["packs"] if row["path"] == SOURCE)
        self.assertEqual(source_hash, SOURCE_SHA)
        self.assertEqual(hashlib.sha256((ROOT / SOURCE).read_bytes()).hexdigest(), SOURCE_SHA)
        self.assertEqual(blob((ROOT / SOURCE).read_bytes()), SOURCE_BLOB)
        self.assertEqual(tuple(blob((ROOT / path).read_bytes()) for path in PREVIOUS), HISTORY_BLOBS)
        self.assertEqual(blob((ROOT / STAGE).read_bytes()), STAGE_BLOB)
        self.assertEqual(self.stage["previous_stage"], PREVIOUS[-1])
        self.assertEqual(self.stage["previous_stage_blob_sha"], HISTORY_BLOBS[-1])
        self.assertEqual(self.stage["checkpoint"], {
            "stage_id": "T386", "processed_intents": 82, "registered_count": 246,
            "added_candidates": 82, "finished_100": 0, "partial_intents": 82,
            "remaining_total": 7872, "rejected": 0,
        })
        self.assertEqual(self.stage["cumulative_checkpoint"], {
            "baseline_registered": 246, "previous_staged": 328, "added_candidates": 82,
            "total": 656, "partial_intents": 82, "finished_100": 0,
            "remaining_total": 7544,
        })

    def test_82_existing_intents_and_one_distinct_new_reply_each(self):
        originals = {r["id"]: r for r in self.source["records"]}
        entries = self.stage["entries"]
        self.assertEqual(len(originals), 82)
        self.assertEqual(len(entries), 82)
        self.assertEqual({x["intent_id"] for x in entries}, set(originals))
        new_ids = []
        new_texts = []
        notes = []
        for entry in entries:
            self.assertEqual(entry["question"], originals[entry["intent_id"]]["question"])
            self.assertEqual(entry["registered_reply_count"], 3)
            self.assertEqual(entry["staged_reply_count"], 1)
            self.assertEqual(len(entry["replies"]), 1)
            row = entry["replies"][0]
            self.assertEqual(row["audiences"], ["all_ai_bots"])
            self.assertTrue(row["read_only"])
            self.assertEqual(row["language"], "ru")
            self.assertEqual(row["style"], "neutral")
            self.assertIn(row["context"], ("direct", "private", "group_addressed"))
            new_ids.append(row["id"])
            new_texts.append(_norm(row["text"]))
            notes.append(_norm(row["context_note"]))
        for values in (new_ids, new_texts, notes):
            self.assertEqual(len(set(values)), 82)

    def test_cross_history_and_registered_lexical_distinction(self):
        old = [r["text"] for stage in self.history
               for entry in stage["entries"] for r in entry["replies"]]
        for path in (SOURCE, *NEIGHBORS):
            for entry in json.loads((ROOT / path).read_text("utf-8"))["records"]:
                old.extend((entry["answer"], *entry.get("variants", [])))
        earlier = [_norm(t) for t in old]
        historical_tokens = [set(t.split()) for t in earlier]
        current = [_norm(row["replies"][0]["text"]) for row in self.stage["entries"]]
        self.assertFalse(set(current) & set(earlier))
        for text in current:
            tokens = set(text.split())
            for old_tokens in historical_tokens:
                self.assertLess(len(tokens & old_tokens) / len(tokens | old_tokens), 0.78)

    def test_authorization_required_for_every_candidate(self):
        for entry in self.stage["entries"]:
            reply = entry["replies"][0]
            opts = dict(approved_reply_ids=frozenset({reply["id"]}),
                        audience="all_ai_bots", context=reply["context"],
                        addressed=True, local_permission=True)
            selected = self.selector.select(entry["intent_id"], **opts)
            self.assertIsNotNone(selected)
            self.assertEqual(selected.text, reply["text"])
            for negative in ({"addressed": False}, {"addressed": 1},
                             {"local_permission": False}, {"local_permission": 1},
                             {"approved_reply_ids": frozenset()},
                             {"approved_reply_ids": frozenset({23})},
                             {"approved_reply_ids": frozenset({"not-this-id"})},
                             {"context": "wrong"}, {"audience": "chat_moderators"},
                             {"recent_ids": (reply["id"],)}):
                self.assertIsNone(
                    self.selector.select(entry["intent_id"], **(opts | negative))
                )

    def test_history_or_stage_tampering_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for rel in ("manifest.json", SOURCE, *PREVIOUS, STAGE):
                dst = root / rel
                dst.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(ROOT / rel, dst)
            self.assertIsInstance(StagedContextSelector(root, STAGE), StagedContextSelector)
            for rel in (SOURCE, *PREVIOUS, STAGE):
                dst = root / rel
                dst.write_bytes(dst.read_bytes() + b" ")
                with self.assertRaises(ValueError):
                    StagedContextSelector(root, STAGE)
                shutil.copyfile(ROOT / rel, dst)


if __name__ == "__main__":
    unittest.main()
