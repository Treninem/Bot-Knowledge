"""T397: 82 new synthetic scoped Russian replies, with pinned source history."""
import hashlib
import json
import re
import shutil
import tempfile
import unittest
from pathlib import Path

from scripts.colloquial_t305 import ROOT
from scripts.staged_context_selector import StagedContextSelector, _norm
from scripts.followthrough_stage_catalog import FollowthroughStageCatalog

SOURCE = "packs/ru/conversation_followthrough_qa.json"
STAGE = "staging/ru/followthrough_t397_context_pool.json"
HISTORY = tuple(f"staging/ru/followthrough_t{n}_context_pool.json"
                for n in (383, 384, 385, 386, 387, 388, 389, 390, 391, 392, 393, 394, 395, 396))
SOURCE_SHA = "0862daf244df650bfd85217df3bedb9f2373a6e63dbabfa8d0c831a6fb289ff7"
SOURCE_BLOB = "707fcaa6440d398a730840362602d4532ab92036"
HISTORY_BLOBS = (
    "6aa6b98c0a3fdb5a68ebcc0071d6c80f0967f5f3",
    "86dd0b4d5c7fbd298eacf82c8d2b5df6ff6013e5",
    "2484f31c20df35b0af67bc41d6579164da6686e5",
    "ebee173a7fd4003f832bbdca87cfd10da9ee3e82",
    "b1eb2222893e832ad8b9324d03a4615a8491e7b9",
    "68cd3474b7cafcec27c7627135d11e16330f9ab2",
    "dddfc5a9612fdd889c3acf92ad6e8c1bba3d1d50",
    "41bc57dbcc429f2bfeaa68ef28ca77450748f963",
    "66157082f9e60937f513f3e6bf9c5b6c1e0f99c5",
    "e3de3c687c3ee0a4122d92f78da82d69f5467bd1",
    "2cf87aa1622684d40e50f3cfc8be837c0efdc62f",
    "70610ea757b26e45779adb6b26a2b74307529eef",
    "d5c7907dcc64e4e2e7dd68941e616d841f897c91",
    "83d5d1f66d23989d2a0a42396194feb487daac4b",
)
STAGE_BLOB = "1b15fc9a7bd48857d054a6c6634aa74597ad0567"
NEIGHBORS = (
    "packs/ru/dialogue_help_qa.json",
    "packs/ru/collaborative_dialogue_qa.json",
    "packs/ru/response_boundaries_qa.json",
    "packs/ru/practical_recovery_qa.json",
)

def blob(raw):
    return hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()

class T397Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.stage = json.loads((ROOT / STAGE).read_text("utf-8"))
        cls.source = json.loads((ROOT / SOURCE).read_text("utf-8"))
        cls.history = [json.loads((ROOT / p).read_text("utf-8")) for p in HISTORY]
        cls.selector = StagedContextSelector(ROOT, STAGE)

    def test_pinned_history_and_cumulative_progress(self):
        manifest = json.loads((ROOT / "manifest.json").read_text("utf-8"))
        registered = {p["path"]: p["sha256"] for p in manifest["packs"]}
        self.assertEqual(registered[SOURCE], SOURCE_SHA)
        self.assertEqual(hashlib.sha256((ROOT / SOURCE).read_bytes()).hexdigest(), SOURCE_SHA)
        self.assertEqual(blob((ROOT / SOURCE).read_bytes()), SOURCE_BLOB)
        self.assertEqual(tuple(blob((ROOT / p).read_bytes()) for p in HISTORY), HISTORY_BLOBS)
        self.assertEqual(blob((ROOT / STAGE).read_bytes()), STAGE_BLOB)
        self.assertEqual(self.stage["previous_stage"], HISTORY[-1])
        self.assertEqual(self.stage["previous_stage_blob_sha"], HISTORY_BLOBS[-1])
        self.assertEqual(self.stage["checkpoint"], {
            "stage_id": "T397", "processed_intents": 82, "registered_count": 246,
            "added_candidates": 82, "finished_100": 0, "partial_intents": 82,
            "remaining_total": 7872, "rejected": 0,
        })
        self.assertEqual(self.stage["cumulative_checkpoint"], {
            "baseline_registered": 246, "previous_staged": 1230,
            "added_candidates": 82, "total": 1558, "partial_intents": 82,
            "finished_100": 0, "remaining_total": 6642,
        })
        self.assertGreaterEqual(FollowthroughStageCatalog(ROOT).reply_count, 1312)

    def test_exact_unique_intents_and_context_boundaries(self):
        originals = {r["id"]: r for r in self.source["records"]}
        entries = self.stage["entries"]
        self.assertEqual(len(originals), 82)
        self.assertEqual(len(entries), 82)
        self.assertEqual({x["intent_id"] for x in entries}, set(originals))
        ids, texts, notes = [], [], []
        for entry in entries:
            ident = entry["intent_id"]
            self.assertEqual(entry["question"], originals[ident]["question"])
            self.assertEqual(entry["registered_reply_count"], 3)
            self.assertEqual(entry["staged_reply_count"], 1)
            self.assertEqual(len(entry["replies"]), 1)
            reply = entry["replies"][0]
            self.assertEqual(reply["id"], ident + "_t397_01")
            self.assertEqual(reply["audiences"], ["all_ai_bots"])
            self.assertEqual(reply["language"], "ru")
            self.assertEqual(reply["style"], "neutral")
            self.assertIs(reply["read_only"], True)
            self.assertIn(reply["context"], ("direct", "private", "group_addressed"))
            self.assertTrue(reply["avoid"].strip())
            ids.append(reply["id"])
            texts.append(_norm(reply["text"]))
            notes.append(_norm(reply["context_note"]))
        self.assertEqual(len(set(ids)), 82)
        self.assertEqual(len(set(texts)), 82)
        self.assertEqual(len(set(notes)), 82)

    def test_historical_and_neighbor_lexical_distinction(self):
        old = [r["text"] for stage in self.history
               for entry in stage["entries"] for r in entry["replies"]]
        for path in (SOURCE, *NEIGHBORS):
            old_data = json.loads((ROOT / path).read_text("utf-8"))
            for entry in old_data["records"]:
                old.extend((entry["answer"], *entry.get("variants", [])))
        old_norm = [_norm(t) for t in old]
        tokens_old = [set(x.split()) for x in old_norm]
        new = [_norm(e["replies"][0]["text"]) for e in self.stage["entries"]]
        self.assertFalse(set(new).intersection(old_norm))
        for item in new:
            tokens = set(item.split())
            for historical in tokens_old:
                self.assertLess(len(tokens & historical) / len(tokens | historical), 0.78)

    def test_all_82_selected_only_with_exact_permission(self):
        for entry in self.stage["entries"]:
            reply = entry["replies"][0]
            opts = dict(approved_reply_ids=frozenset({reply["id"]}),
                        audience="all_ai_bots", context=reply["context"],
                        addressed=True, local_permission=True)
            selected = self.selector.select(entry["intent_id"], **opts)
            self.assertIsNotNone(selected)
            self.assertEqual(selected.text, reply["text"])
            for denied in ({"addressed": False}, {"addressed": 1},
                           {"local_permission": False}, {"local_permission": 1},
                           {"approved_reply_ids": frozenset()},
                           {"approved_reply_ids": frozenset({23})},
                           {"context": "unknown"}, {"audience": "chat_moderators"},
                           {"recent_ids": (reply["id"],)}):
                self.assertIsNone(
                    self.selector.select(entry["intent_id"], **(opts | denied))
                )

    def test_tampering_source_parent_or_stage_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for rel in ("manifest.json", SOURCE, *HISTORY, STAGE):
                dst = root / rel
                dst.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(ROOT / rel, dst)
            self.assertIsInstance(StagedContextSelector(root, STAGE), StagedContextSelector)
            for rel in (SOURCE, *HISTORY, STAGE):
                path = root / rel
                path.write_bytes(path.read_bytes() + b" ")
                with self.assertRaises(ValueError):
                    StagedContextSelector(root, STAGE)
                shutil.copyfile(ROOT / rel, path)

if __name__ == '__main__':
    unittest.main()
