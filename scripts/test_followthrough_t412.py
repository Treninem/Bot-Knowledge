"""T412: independently situated RU followthrough answers, exact ancestry and scope."""
import hashlib
import json
import re
import unittest
from scripts.colloquial_t305 import ROOT
from scripts.staged_context_selector import _norm

SOURCE = "packs/ru/conversation_followthrough_qa.json"
PARENT = "staging/ru/followthrough_t411_context_pool.json"
STAGE = "staging/ru/followthrough_t412_context_pool.json"
SOURCE_SHA = "0862daf244df650bfd85217df3bedb9f2373a6e63dbabfa8d0c831a6fb289ff7"
SOURCE_BLOB = "707fcaa6440d398a730840362602d4532ab92036"
PARENT_BLOB = "836deea92279a4d03971c4b490e69c50deef2c71"
STAGE_BLOB = "01e3db997548b2e3f96353a7c03e1cd3a4ce9f18"

def read_bytes(path):
    return (ROOT / path).read_bytes()

def blob(data):
    return hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()

def token_set(value):
    return set(_norm(value).split())

class T412Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = json.loads(read_bytes(SOURCE))
        cls.stage = json.loads(read_bytes(STAGE))
        cls.manifest = json.loads(read_bytes("manifest.json"))

    def test_exact_source_and_parent(self):
        manifest_sha = {item["path"]: item["sha256"] for item in self.manifest["packs"]}[SOURCE]
        self.assertEqual(manifest_sha, SOURCE_SHA)
        self.assertEqual(hashlib.sha256(read_bytes(SOURCE)).hexdigest(), SOURCE_SHA)
        self.assertEqual(blob(read_bytes(SOURCE)), SOURCE_BLOB)
        self.assertEqual(blob(read_bytes(PARENT)), PARENT_BLOB)
        self.assertEqual(blob(read_bytes(STAGE)), STAGE_BLOB)
        self.assertEqual(self.stage["source_pack_manifest_sha256"], SOURCE_SHA)
        self.assertEqual(self.stage["source_pack_blob_sha"], SOURCE_BLOB)
        self.assertEqual(self.stage["previous_stage"], PARENT)
        self.assertEqual(self.stage["previous_stage_blob_sha"], PARENT_BLOB)

    def test_checkpoint_intent_map_and_safety(self):
        self.assertEqual(self.stage["schema_version"], 1)
        self.assertEqual(self.stage["stage_type"], "supplemental_contextual_reply_pool")
        self.assertIs(self.stage["consumer_registered"], False)
        self.assertEqual(self.stage["language"], "ru")
        self.assertEqual(self.stage["audiences"], ["all_ai_bots"])
        self.assertEqual(self.stage["constraints"], {"read_only": True, "requires_direct_address": True, "no_personal_data": True})
        self.assertEqual(self.stage["checkpoint"], {"stage_id":"T412","processed_intents":82,"registered_count":246,"added_candidates":82,"finished_100":0,"partial_intents":82,"remaining_total":7872,"rejected":0})
        self.assertEqual(self.stage["cumulative_checkpoint"], {"baseline_registered":246,"previous_staged":2542,"added_candidates":82,"total":2870,"partial_intents":82,"finished_100":0,"remaining_total":5330})
        canon = {r["id"]: r["question"] for r in self.source["records"]}
        self.assertEqual(len(canon), 82)
        self.assertEqual(len(self.stage["entries"]), 82)
        self.assertEqual(set(canon), {x["intent_id"] for x in self.stage["entries"]})
        for entry in self.stage["entries"]:
            self.assertEqual(entry["question"], canon[entry["intent_id"]])
            self.assertEqual(entry["registered_reply_count"], 3)
            self.assertEqual(entry["staged_reply_count"], 1)
            self.assertEqual(len(entry["replies"]), 1)
            reply = entry["replies"][0]
            self.assertEqual(reply["id"], entry["intent_id"]+"_t412_01")
            self.assertEqual(reply["audiences"], ["all_ai_bots"])
            self.assertEqual(reply["language"], "ru")
            self.assertEqual(reply["style"], "neutral")
            self.assertIn(reply["context"], ("direct", "private", "group_addressed"))
            self.assertIs(reply["read_only"], True)
            self.assertIn("без действий", reply["avoid"])
            self.assertGreater(len(reply["text"]), 35)
            self.assertRegex(reply["text"], "[А-Яа-яЁё]")
            self.assertGreater(len(reply["context_note"]), 20)

    def test_full_history_dedup_and_scope(self):
        older = [x for row in self.source["records"] for x in [row["answer"], *row["variants"]]]
        for i in range(383, 412):
            history = json.loads(read_bytes(f"staging/ru/followthrough_t{i}_context_pool.json"))
            self.assertEqual(len(history["entries"]), 82)
            older.extend(reply["text"] for e in history["entries"] for reply in e["replies"])
        known = {_norm(x) for x in older}
        token_history = [token_set(x) for x in older]
        ids, contexts = set(), set()
        for entry in self.stage["entries"]:
            for r in entry["replies"]:
                self.assertNotIn(r["id"], ids)
                ids.add(r["id"])
                value = _norm(r["text"])
                self.assertNotIn(value, known, msg=r["id"])
                known.add(value)
                note = _norm(r["context_note"])
                self.assertNotIn(note, contexts, msg=r["id"])
                contexts.add(note)
                new_tokens = token_set(r["text"])
                for old_tokens in token_history:
                    overlap = len(new_tokens & old_tokens)
                    jaccard = overlap / len(new_tokens | old_tokens) if new_tokens | old_tokens else 0
                    self.assertLess(jaccard, 0.72, msg=f"near-duplicate {r['id']}: {jaccard:.3f}")
                token_history.append(new_tokens)

if __name__ == "__main__":
    unittest.main()
