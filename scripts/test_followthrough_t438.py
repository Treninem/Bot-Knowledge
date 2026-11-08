"""T438: 82 independent situated Russian replies, source-pinned and history checked."""
import hashlib
import json
import unittest

from scripts.colloquial_t305 import ROOT
from scripts.staged_context_selector import _norm

SOURCE = "packs/ru/conversation_followthrough_qa.json"
PARENT = "staging/ru/followthrough_t436_context_pool.json"
STAGE = "staging/ru/followthrough_t438_context_pool.json"
SOURCE_SHA = "0862daf244df650bfd85217df3bedb9f2373a6e63dbabfa8d0c831a6fb289ff7"
SOURCE_BLOB = "707fcaa6440d398a730840362602d4532ab92036"
PARENT_BLOB = "915d487e6234f1288f66f925136832812dd9fb2d"
STAGE_BLOB = "722e8cc02e416756d5a155958fa1b13a99dc2a9f"
STAGES = (*range(383, 423), 424, 425, *range(427, 435), 436)

def raw(path):
    return (ROOT / path).read_bytes()

def load(path):
    return json.loads(raw(path))

def git_blob(payload):
    return hashlib.sha1(b"blob " + str(len(payload)).encode() + b"\0" + payload).hexdigest()

def terms(text):
    return set(_norm(text).split())

class T438Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = load(SOURCE)
        cls.stage = load(STAGE)
        cls.manifest = load("manifest.json")

    def test_source_and_ancestry(self):
        source_digest = {p["path"]: p["sha256"] for p in self.manifest["packs"]}[SOURCE]
        self.assertEqual(source_digest, SOURCE_SHA)
        self.assertEqual(hashlib.sha256(raw(SOURCE)).hexdigest(), SOURCE_SHA)
        self.assertEqual(git_blob(raw(SOURCE)), SOURCE_BLOB)
        self.assertEqual(git_blob(raw(PARENT)), PARENT_BLOB)
        self.assertEqual(git_blob(raw(STAGE)), STAGE_BLOB)
        stage = self.stage
        self.assertEqual((stage["source_pack_manifest_sha256"], stage["source_pack_blob_sha"]), (SOURCE_SHA, SOURCE_BLOB))
        self.assertEqual((stage["previous_stage"], stage["previous_stage_blob_sha"]), (PARENT, PARENT_BLOB))

    def test_counts_and_safe_application(self):
        s = self.stage
        self.assertEqual((s["schema_version"], s["stage_type"], s["consumer_registered"]), (1, "supplemental_contextual_reply_pool", False))
        self.assertEqual((s["language"], s["audiences"]), ("ru", ["all_ai_bots"]))
        self.assertEqual(s["constraints"], {"read_only": True, "requires_direct_address": True, "no_personal_data": True})
        self.assertEqual(s["checkpoint"], {"stage_id":"T438","processed_intents":82,"registered_count":246,"added_candidates":82,"finished_100":0,"partial_intents":82,"remaining_total":7872,"rejected":0})
        self.assertEqual(s["cumulative_checkpoint"], {"baseline_registered":246,"previous_staged":4346,"added_candidates":82,"total":4674,"partial_intents":82,"finished_100":0,"remaining_total":3526})
        questions = {r["id"]: r["question"] for r in self.source["records"]}
        self.assertEqual(len(questions), 82)
        self.assertEqual(len(s["entries"]), 82)
        self.assertEqual({x["intent_id"] for x in s["entries"]}, set(questions))
        seen_ids, seen_notes = set(), set()
        for entry in s["entries"]:
            self.assertEqual(entry["question"], questions[entry["intent_id"]])
            self.assertEqual((entry["registered_reply_count"], entry["staged_reply_count"]), (3, 1))
            self.assertEqual(len(entry["replies"]), 1)
            reply = entry["replies"][0]
            self.assertEqual(reply["id"], entry["intent_id"]+"_t438_01")
            self.assertNotIn(reply["id"], seen_ids)
            seen_ids.add(reply["id"])
            self.assertEqual((reply["language"], reply["style"], reply["audiences"]), ("ru", "neutral", ["all_ai_bots"]))
            self.assertIn(reply["context"], ("direct", "private", "group_addressed"))
            self.assertIs(reply["read_only"], True)
            self.assertIn("без действий", reply["avoid"])
            self.assertGreater(len(reply["text"]), 50)
            self.assertGreater(len(reply["context_note"]), 20)
            note = _norm(reply["context_note"])
            self.assertNotIn(note, seen_notes)
            seen_notes.add(note)

    def test_all_previous_stages_and_near_duplicates(self):
        earlier = [t for row in self.source["records"] for t in (row["answer"], *row["variants"])]
        for n in STAGES:
            part = load(f"staging/ru/followthrough_t{n}_context_pool.json")
            self.assertEqual(len(part["entries"]), 82)
            earlier.extend(reply["text"] for entry in part["entries"] for reply in entry["replies"])
        self.assertEqual(len(earlier), 4592)
        seen = {_norm(x) for x in earlier}
        earlier_tokens = [terms(x) for x in earlier]
        for entry in self.stage["entries"]:
            reply = entry["replies"][0]
            normalized = _norm(reply["text"])
            self.assertNotIn(normalized, seen, msg=reply["id"])
            current = terms(reply["text"])
            for previous in earlier_tokens:
                shared = len(current & previous)
                ratio = shared / (len(current)+len(previous)-shared) if current or previous else 0
                self.assertLess(ratio, .72, msg=reply["id"])
            seen.add(normalized)
            earlier_tokens.append(current)

if __name__ == "__main__":
    unittest.main()
