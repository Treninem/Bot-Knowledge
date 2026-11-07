"""T384: cumulative ancestry + read-only scoped 82-reply followthrough delta."""
import hashlib
import json
import shutil
import tempfile
import unittest
from pathlib import Path

from scripts.colloquial_t305 import ROOT
from scripts.staged_context_selector import StagedContextSelector, _norm

STAGE = "staging/ru/followthrough_t384_context_pool.json"
PARENT = "staging/ru/followthrough_t383_context_pool.json"
SOURCE = "packs/ru/conversation_followthrough_qa.json"
SOURCE_SHA = "0862daf244df650bfd85217df3bedb9f2373a6e63dbabfa8d0c831a6fb289ff7"
PARENT_BLOB = "6aa6b98c0a3fdb5a68ebcc0071d6c80f0967f5f3"
STAGE_BLOB = "86dd0b4d5c7fbd298eacf82c8d2b5df6ff6013e5"
NEIGHBORS = ("packs/ru/dialogue_help_qa.json", "packs/ru/collaborative_dialogue_qa.json",
             "packs/ru/response_boundaries_qa.json", "packs/ru/practical_recovery_qa.json")


def blob(raw):
    return hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()


class T384Test(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.parent = json.loads((ROOT / PARENT).read_text("utf-8"))
        cls.stage = json.loads((ROOT / STAGE).read_text("utf-8"))
        cls.source = json.loads((ROOT / SOURCE).read_text("utf-8"))
        cls.selector = StagedContextSelector(ROOT, STAGE)

    def test_pinned_hashes_counts_and_provenance(self):
        raw_source = (ROOT / SOURCE).read_bytes()
        raw_parent = (ROOT / PARENT).read_bytes()
        raw_stage = (ROOT / STAGE).read_bytes()
        manifest = json.loads((ROOT / "manifest.json").read_text("utf-8"))
        self.assertEqual(next(p["sha256"] for p in manifest["packs"]
                              if p["path"] == SOURCE), SOURCE_SHA)
        self.assertEqual(hashlib.sha256(raw_source).hexdigest(), SOURCE_SHA)
        self.assertEqual(blob(raw_parent), PARENT_BLOB)
        self.assertEqual(blob(raw_stage), STAGE_BLOB)
        self.assertEqual(self.stage["previous_stage"], PARENT)
        self.assertEqual(self.stage["previous_stage_blob_sha"], PARENT_BLOB)
        self.assertEqual(self.stage["source_pack_blob_sha"], blob(raw_source))
        self.assertEqual(self.stage["checkpoint"], {
            "stage_id":"T384","processed_intents":82,"registered_count":246,
            "added_candidates":82,"finished_100":0,"partial_intents":82,
            "remaining_total":7872,"rejected":0,
        })
        self.assertEqual(self.stage["cumulative_checkpoint"], {
            "baseline_registered":246,"previous_staged":82,"added_candidates":82,
            "total":410,"partial_intents":82,"finished_100":0,"remaining_total":7790,
        })
        ids = {row["id"]:row for row in self.source["records"]}
        self.assertEqual(len(ids), 82)
        self.assertEqual({x["intent_id"] for x in self.stage["entries"]}, set(ids))
        self.assertFalse(self.stage["consumer_registered"])
        for item in self.stage["entries"]:
            self.assertEqual(item["question"], ids[item["intent_id"]]["question"])
            self.assertEqual(item["registered_reply_count"],3)
            self.assertEqual(item["staged_reply_count"],1)

    def test_originality_isolation_and_lexical_review(self):
        registered = []
        for path in (SOURCE, *NEIGHBORS):
            for row in json.loads((ROOT / path).read_text("utf-8"))["records"]:
                registered.extend((row["answer"], *row.get("variants", [])))
        earlier = [r["text"] for item in self.parent["entries"] for r in item["replies"]]
        current = [r for item in self.stage["entries"] for r in item["replies"]]
        self.assertEqual(len(current),82)
        ids = [x["id"] for x in current]
        notes = [_norm(x["context_note"]) for x in current]
        texts = [_norm(x["text"]) for x in current]
        self.assertEqual(len(set(ids)),82)
        self.assertEqual(len(set(notes)),82)
        self.assertEqual(len(set(texts)),82)
        previous_texts = [_norm(t) for t in (*registered, *earlier)]
        self.assertFalse(set(texts) & set(previous_texts))
        priors = [set(t.split()) for t in previous_texts]
        for row in current:
            self.assertTrue(row["read_only"])
            self.assertEqual(row["audiences"],["all_ai_bots"])
            self.assertEqual(row["style"],"neutral")
            self.assertIn(row["context"],("direct","private","group_addressed"))
            tokens = set(_norm(row["text"]).split())
            for earlier_tokens in priors:
                self.assertLess(len(tokens & earlier_tokens)/len(tokens | earlier_tokens),0.78)

    def test_all_answers_gated(self):
        for entry in self.stage["entries"]:
            r = entry["replies"][0]
            args = dict(approved_reply_ids=frozenset({r["id"]}),
                        audience="all_ai_bots",context=r["context"],
                        addressed=True,local_permission=True)
            selected = self.selector.select(entry["intent_id"],**args)
            self.assertIsNotNone(selected)
            self.assertEqual(selected.text,r["text"])
            for change in ({"addressed":False},{"local_permission":False},
                           {"audience":"community_bots"},{"approved_reply_ids":frozenset()},
                           {"context":"wrong"},{"recent_ids":(r["id"],)}):
                self.assertIsNone(self.selector.select(entry["intent_id"],**(args|change)))

    def test_parent_and_stage_tamper_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            for rel in ("manifest.json",SOURCE,PARENT,STAGE):
                target = root / rel
                target.parent.mkdir(parents=True,exist_ok=True)
                shutil.copyfile(ROOT / rel,target)
            self.assertIsInstance(StagedContextSelector(root,STAGE),StagedContextSelector)
            for path in (PARENT, STAGE, SOURCE):
                file = root / path
                file.write_bytes(file.read_bytes() + b" ")
                with self.assertRaises(ValueError):
                    StagedContextSelector(root,STAGE)
                shutil.copyfile(ROOT / path,file)


if __name__ == "__main__":
    unittest.main()
