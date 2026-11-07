"""T400: source-pinned, immutable historical, scoped stage integrity checks."""
import hashlib
import json
import unittest
from scripts.colloquial_t305 import ROOT
from scripts.staged_context_selector import _norm

SOURCE = "packs/ru/conversation_followthrough_qa.json"
PARENT = "staging/ru/followthrough_t399_context_pool.json"
STAGE = "staging/ru/followthrough_t400_context_pool.json"
SRC_SHA256 = "0862daf244df650bfd85217df3bedb9f2373a6e63dbabfa8d0c831a6fb289ff7"
SRC_BLOB = "707fcaa6440d398a730840362602d4532ab92036"
PARENT_BLOB = "dd51f07e16a5c2fa42291ecbb1f582f74d8545b2"
STAGE_BLOB = "9c72702ef5c3c94d9f782f3ecdfc363bb2c422c5"

def blob_hash(data):
    return hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()

class T400Tests(unittest.TestCase):
    def test_stage_sha_counts_and_uniqueness(self):
        read = lambda p: (ROOT / p).read_bytes()
        manifest = json.loads(read("manifest.json"))
        self.assertEqual({x["path"]: x["sha256"] for x in manifest["packs"]}[SOURCE], SRC_SHA256)
        self.assertEqual(hashlib.sha256(read(SOURCE)).hexdigest(), SRC_SHA256)
        self.assertEqual(blob_hash(read(SOURCE)), SRC_BLOB)
        self.assertEqual(blob_hash(read(PARENT)), PARENT_BLOB)
        self.assertEqual(blob_hash(read(STAGE)), STAGE_BLOB)
        obj = json.loads(read(STAGE))
        src = json.loads(read(SOURCE))
        self.assertEqual(obj["source_pack_blob_sha"], SRC_BLOB)
        self.assertEqual(obj["previous_stage"], PARENT)
        self.assertEqual(obj["previous_stage_blob_sha"], PARENT_BLOB)
        self.assertIs(obj["consumer_registered"], False)
        self.assertEqual(obj["cumulative_checkpoint"], {
            "baseline_registered": 246, "previous_staged": 1476,
            "added_candidates": 82, "total": 1804,
            "partial_intents": 82, "finished_100": 0, "remaining_total": 6396})
        canon = {r["id"]: r["question"] for r in src["records"]}
        self.assertEqual(len(canon), 82)
        self.assertEqual(len(obj["entries"]), 82)
        self.assertEqual({e["intent_id"] for e in obj["entries"]}, set(canon))
        ids, notes = set(), set()
        seen = {_norm(t) for r in src["records"] for t in [r["answer"], *r.get("variants", [])]}
        for i in range(383, 400):
            hist = json.loads(read("staging/ru/followthrough_t%d_context_pool.json" % i))
            self.assertEqual(len(hist["entries"]), 82)
            for e in hist["entries"]:
                for r in e["replies"]:
                    seen.add(_norm(r["text"]))
        for e in obj["entries"]:
            self.assertEqual(e["question"], canon[e["intent_id"]])
            self.assertEqual(e["registered_reply_count"], 3)
            self.assertEqual(e["staged_reply_count"], 1)
            self.assertEqual(len(e["replies"]), 1)
            r = e["replies"][0]
            self.assertEqual(r["id"], e["intent_id"] + "_t400_01")
            self.assertNotIn(r["id"], ids)
            ids.add(r["id"])
            self.assertNotIn(_norm(r["text"]), seen)
            seen.add(_norm(r["text"]))
            self.assertNotIn(_norm(r["context_note"]), notes)
            notes.add(_norm(r["context_note"]))
            self.assertEqual(r["language"], "ru")
            self.assertEqual(r["audiences"], ["all_ai_bots"])
            self.assertEqual(r["style"], "neutral")
            self.assertIn(r["context"], ("direct", "private", "group_addressed"))
            self.assertIs(r["read_only"], True)
            self.assertTrue(r["avoid"].strip())

if __name__ == "__main__":
    unittest.main()
