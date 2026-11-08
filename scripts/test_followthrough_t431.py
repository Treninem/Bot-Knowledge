"""T431: 82 new synthetic contextual replies, pinned origin and full-history de-dup."""
import hashlib
import json
import unittest
from scripts.colloquial_t305 import ROOT
from scripts.staged_context_selector import _norm

SOURCE = "packs/ru/conversation_followthrough_qa.json"
PARENT = "staging/ru/followthrough_t430_context_pool.json"
STAGE = "staging/ru/followthrough_t431_context_pool.json"
SOURCE_SHA = "0862daf244df650bfd85217df3bedb9f2373a6e63dbabfa8d0c831a6fb289ff7"
SOURCE_BLOB = "707fcaa6440d398a730840362602d4532ab92036"
PARENT_BLOB = "6004d03017463aee1545021cc2bcde5a6bfa48e8"
STAGE_BLOB = "0b259f09db1d58004c48d6b298c573197e3ad191"
STAGES = (*range(383, 423), 424, 425, 427, 428, 429, 430)

def read(path):
    return (ROOT / path).read_bytes()

def git_blob(data):
    return hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()

def toks(s):
    return set(_norm(s).split())

class T431Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.manifest = json.loads(read("manifest.json"))
        cls.source = json.loads(read(SOURCE))
        cls.parent = json.loads(read(PARENT))
        cls.stage = json.loads(read(STAGE))

    def test_exact_bytes_and_pins(self):
        registered = {x["path"]: x["sha256"] for x in self.manifest["packs"]}[SOURCE]
        self.assertEqual(registered, SOURCE_SHA)
        self.assertEqual(hashlib.sha256(read(SOURCE)).hexdigest(), SOURCE_SHA)
        self.assertEqual(git_blob(read(SOURCE)), SOURCE_BLOB)
        self.assertEqual(git_blob(read(PARENT)), PARENT_BLOB)
        self.assertEqual(git_blob(read(STAGE)), STAGE_BLOB)
        self.assertEqual(self.stage["source_pack_manifest_sha256"], SOURCE_SHA)
        self.assertEqual(self.stage["source_pack_blob_sha"], SOURCE_BLOB)
        self.assertEqual((self.stage["previous_stage"], self.stage["previous_stage_blob_sha"]), (PARENT, PARENT_BLOB))

    def test_scope_counts_and_context(self):
        stage = self.stage
        self.assertEqual((stage["schema_version"], stage["stage_type"]), (1, "supplemental_contextual_reply_pool"))
        self.assertIs(stage["consumer_registered"], False)
        self.assertEqual((stage["language"], stage["audiences"]), ("ru", ["all_ai_bots"]))
        self.assertEqual(stage["constraints"], {"read_only": True, "requires_direct_address": True, "no_personal_data": True})
        self.assertEqual(stage["checkpoint"], {"stage_id":"T431", "processed_intents":82, "registered_count":246, "added_candidates":82, "finished_100":0, "partial_intents":82, "remaining_total":7872, "rejected":0})
        self.assertEqual(stage["cumulative_checkpoint"], {"baseline_registered":246, "previous_staged":3936, "added_candidates":82, "total":4264, "partial_intents":82, "finished_100":0, "remaining_total":3936})
        questions = {x["id"]: x["question"] for x in self.source["records"]}
        self.assertEqual(len(questions), 82)
        self.assertEqual(len(stage["entries"]), 82)
        self.assertEqual({e["intent_id"] for e in stage["entries"]}, set(questions))
        ids, notes = set(), set()
        for e in stage["entries"]:
            self.assertEqual(e["question"], questions[e["intent_id"]])
            self.assertEqual((e["registered_reply_count"], e["staged_reply_count"]), (3, 1))
            self.assertEqual(len(e["replies"]), 1)
            x = e["replies"][0]
            self.assertEqual(x["id"], e["intent_id"] + "_t431_01")
            self.assertNotIn(x["id"], ids)
            ids.add(x["id"])
            self.assertEqual((x["language"], x["style"], x["audiences"]), ("ru", "neutral", ["all_ai_bots"]))
            self.assertIn(x["context"], ("direct", "private", "group_addressed"))
            self.assertTrue(x["read_only"])
            self.assertIn("без действий", x["avoid"])
            self.assertGreater(len(x["text"]), 50)
            self.assertGreater(len(x["context_note"]), 20)
            self.assertNotIn(_norm(x["context_note"]), notes)
            notes.add(_norm(x["context_note"]))

    def test_all_previous_stages_normalized_and_near_duplicates(self):
        previous = [y for record in self.source["records"] for y in (record["answer"], *record["variants"])]
        for n in STAGES:
            path = f"staging/ru/followthrough_t{n}_context_pool.json"
            part = json.loads(read(path))
            self.assertEqual(len(part["entries"]), 82)
            previous.extend(x["text"] for e in part["entries"] for x in e["replies"])
        self.assertEqual(len(previous), 4182)
        known = {_norm(x) for x in previous}
        tokens = [toks(x) for x in previous]
        for e in self.stage["entries"]:
            x = e["replies"][0]
            normed = _norm(x["text"])
            self.assertNotIn(normed, known, msg=x["id"])
            known.add(normed)
            cur = toks(x["text"])
            for old in tokens:
                overlap = len(cur & old)
                similarity = overlap / (len(cur) + len(old) - overlap) if cur or old else 0
                self.assertLess(similarity, .72, msg=x["id"])
            tokens.append(cur)

if __name__ == "__main__":
    unittest.main()
