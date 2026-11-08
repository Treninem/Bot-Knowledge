"""T409 source-anchored context quality, lineage, privacy and count checks."""
import hashlib
import json
import unittest
from scripts.colloquial_t305 import ROOT
from scripts.staged_context_selector import _norm

SOURCE = "packs/ru/conversation_followthrough_qa.json"
STAGE = "staging/ru/followthrough_t409_context_pool.json"
PARENT = "staging/ru/followthrough_t408_context_pool.json"
SOURCE_SHA = "0862daf244df650bfd85217df3bedb9f2373a6e63dbabfa8d0c831a6fb289ff7"
SOURCE_BLOB = "707fcaa6440d398a730840362602d4532ab92036"
PARENT_BLOB = "d270253f07299d773afbb591ed0fb88477712eba"
STAGE_BLOB = "0384f8ea5277b2ce46a6d38e101528a92c905ae4"


def blob_hash(data):
    return hashlib.sha1(b"blob " + str(len(data)).encode() + bytes([0]) + data).hexdigest()


def tokens(s):
    return set(_norm(s).split())


class T409Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.read = staticmethod(lambda p: (ROOT / p).read_bytes())
        cls.manifest = json.loads(cls.read("manifest.json"))
        cls.source = json.loads(cls.read(SOURCE))
        cls.stage = json.loads(cls.read(STAGE))

    def test_pinned_manifest_source_and_git_blobs(self):
        self.assertEqual({p["path"]: p["sha256"] for p in self.manifest["packs"]}[SOURCE], SOURCE_SHA)
        self.assertEqual(hashlib.sha256(self.read(SOURCE)).hexdigest(), SOURCE_SHA)
        self.assertEqual(blob_hash(self.read(SOURCE)), SOURCE_BLOB)
        self.assertEqual(blob_hash(self.read(PARENT)), PARENT_BLOB)
        self.assertEqual(blob_hash(self.read(STAGE)), STAGE_BLOB)
        self.assertEqual(self.stage["source_pack_manifest_sha256"], SOURCE_SHA)
        self.assertEqual(self.stage["source_pack_blob_sha"], SOURCE_BLOB)
        self.assertEqual(self.stage["previous_stage"], PARENT)
        self.assertEqual(self.stage["previous_stage_blob_sha"], PARENT_BLOB)

    def test_exact_counts_and_canonical_questions(self):
        self.assertEqual(len(self.source["records"]), 82)
        self.assertEqual(len(self.stage["entries"]), 82)
        self.assertEqual(self.stage["checkpoint"], {
            "stage_id": "T409", "processed_intents": 82, "registered_count": 246,
            "added_candidates": 82, "finished_100": 0, "partial_intents": 82,
            "remaining_total": 7872, "rejected": 0
        })
        self.assertEqual(self.stage["cumulative_checkpoint"], {
            "baseline_registered": 246, "previous_staged": 2214,
            "added_candidates": 82, "total": 2542,
            "partial_intents": 82, "finished_100": 0, "remaining_total": 5658
        })
        canon = {r["id"]: r["question"] for r in self.source["records"]}
        self.assertEqual(set(canon), {e["intent_id"] for e in self.stage["entries"]})
        for e in self.stage["entries"]:
            self.assertEqual(e["question"], canon[e["intent_id"]])
            self.assertEqual(e["registered_reply_count"], 3)
            self.assertEqual(e["staged_reply_count"], 1)
            self.assertEqual(len(e["replies"]), 1)
            self.assertEqual(e["replies"][0]["id"], e["intent_id"] + "_t409_01")

    def test_context_permissions_and_no_repetitions(self):
        self.assertIs(self.stage["consumer_registered"], False)
        self.assertEqual(self.stage["language"], "ru")
        self.assertEqual(self.stage["audiences"], ["all_ai_bots"])
        self.assertEqual(self.stage["constraints"], {
            "read_only": True, "requires_direct_address": True,
            "no_personal_data": True
        })
        existing = [s for record in self.source["records"]
                    for s in (record["answer"], *record.get("variants", []))]
        for i in range(383, 409):
            old = json.loads(self.read(f"staging/ru/followthrough_t{i}_context_pool.json"))
            self.assertEqual(len(old["entries"]), 82)
            existing.extend(r["text"] for e in old["entries"] for r in e["replies"])
        known = {_norm(s) for s in existing}
        known_tokens = [tokens(s) for s in existing]
        notes, ids = set(), set()
        for e in self.stage["entries"]:
            r = e["replies"][0]
            self.assertNotIn(r["id"], ids)
            ids.add(r["id"])
            self.assertNotIn(_norm(r["text"]), known)
            known.add(_norm(r["text"]))
            self.assertNotIn(_norm(r["context_note"]), notes)
            notes.add(_norm(r["context_note"]))
            self.assertEqual(r["language"], "ru")
            self.assertEqual(r["audiences"], ["all_ai_bots"])
            self.assertEqual(r["style"], "neutral")
            self.assertIn(r["context"], {"direct", "private", "group_addressed"})
            self.assertIs(r["read_only"], True)
            self.assertIn("без действий", r["avoid"])
            self.assertGreater(len(r["text"]), 30)
            self.assertGreater(len(r["context_note"]), 18)
            wt = tokens(r["text"])
            for old in known_tokens:
                common = len(wt & old)
                score = common / len(wt | old)
                self.assertLess(score, 0.72,
                                msg=f"Near lexical duplicate in {r['id']}: {score:.3f}")
            known_tokens.append(wt)


if __name__ == "__main__":
    unittest.main()
