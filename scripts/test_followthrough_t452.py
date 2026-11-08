"""T452: 82 newly authored situation-specific replies; source, full lineage, scope and dedup."""
import hashlib
import json
import re
import unittest

from scripts.colloquial_t305 import ROOT
from scripts.staged_context_selector import _norm

SOURCE = "packs/ru/conversation_followthrough_qa.json"
STAGE = "staging/ru/followthrough_t452_context_pool.json"
PARENT = "staging/ru/followthrough_t451_context_pool.json"
SOURCE_SHA = "0862daf244df650bfd85217df3bedb9f2373a6e63dbabfa8d0c831a6fb289ff7"
SOURCE_BLOB = "707fcaa6440d398a730840362602d4532ab92036"
PARENT_BLOB = "1fe127da7259b2389812c76097047d9155e0f19f"
STAGE_BLOB = "962307b5753f7364d5eb75dc03451f99a76bf639"
STAGES = (*range(383, 423), 424, 425, *range(427, 435), 436, 438, 439, 440, 441, 442, 444, 445, 446, 448, 449, 450, 451)
SECRET = re.compile(r"(?i)(ghp_[a-z0-9]{12,}|sk-[a-z0-9]{12,}|bot_token|chat_id|user_id|https://t\.me/|[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,})")

def raw(path):
    return (ROOT / path).read_bytes()

def load(path):
    return json.loads(raw(path))

def git_blob(content):
    return hashlib.sha1(b"blob " + str(len(content)).encode() + b"\0" + content).hexdigest()

def terms(text):
    return set(_norm(text).split())

class T452Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = load(SOURCE)
        cls.stage = load(STAGE)
        cls.manifest = load("manifest.json")

    def test_exact_source_parent_and_stage_blob(self):
        s = self.stage
        listed = {x["path"]: x["sha256"] for x in self.manifest["packs"]}[SOURCE]
        self.assertEqual(listed, SOURCE_SHA)
        self.assertEqual(hashlib.sha256(raw(SOURCE)).hexdigest(), SOURCE_SHA)
        self.assertEqual(git_blob(raw(SOURCE)), SOURCE_BLOB)
        self.assertEqual(git_blob(raw(PARENT)), PARENT_BLOB)
        self.assertEqual(git_blob(raw(STAGE)), STAGE_BLOB)
        self.assertEqual((s["source_pack"], s["source_pack_manifest_sha256"], s["source_pack_blob_sha"]), (SOURCE, SOURCE_SHA, SOURCE_BLOB))
        self.assertEqual((s["previous_stage"], s["previous_stage_blob_sha"]), (PARENT, PARENT_BLOB))

    def test_entry_integrity_privacy_and_checkpoint(self):
        s = self.stage
        self.assertEqual(s["stage_type"], "supplemental_contextual_reply_pool")
        self.assertEqual(s["schema_version"], 1)
        self.assertFalse(s["consumer_registered"])
        self.assertEqual(s["audiences"], ["all_ai_bots"])
        self.assertEqual(s["constraints"], {"read_only": True, "requires_direct_address": True, "no_personal_data": True})
        self.assertEqual(s["checkpoint"], {"stage_id": "T452", "processed_intents": 82, "registered_count": 246, "added_candidates": 82, "finished_100": 0, "partial_intents": 82, "remaining_total": 7872, "rejected": 0})
        self.assertEqual(s["cumulative_checkpoint"], {"baseline_registered": 246, "previous_staged": 5330, "added_candidates": 82, "total": 5658, "partial_intents": 82, "finished_100": 0, "remaining_total": 2542})
        source = {x["id"]: x["question"] for x in self.source["records"]}
        self.assertEqual(len(source), 82)
        self.assertEqual(len(s["entries"]), 82)
        self.assertEqual({x["intent_id"] for x in s["entries"]}, set(source))
        ids, notes = set(), set()
        for row in s["entries"]:
            self.assertEqual(row["question"], source[row["intent_id"]])
            self.assertEqual((row["registered_reply_count"], row["staged_reply_count"]), (3, 1))
            self.assertEqual(len(row["replies"]), 1)
            x = row["replies"][0]
            self.assertEqual(x["id"], row["intent_id"] + "_t452_01")
            self.assertNotIn(x["id"], ids)
            ids.add(x["id"])
            self.assertEqual((x["language"], x["style"], x["audiences"]), ("ru", "neutral", ["all_ai_bots"]))
            self.assertIn(x["context"], ("direct", "private", "group_addressed"))
            self.assertIs(x["read_only"], True)
            self.assertIn("без действий", x["avoid"])
            self.assertNotIn("actions", x)
            self.assertGreater(len(x["text"]), 55)
            self.assertGreater(len(x["context_note"]), 35)
            self.assertIsNone(SECRET.search(x["text"]))
            self.assertIsNone(SECRET.search(x["context_note"]))
            note = _norm(x["context_note"])
            self.assertNotIn(note, notes)
            notes.add(note)

    def test_full_previous_history_and_normalized_near_duplicates(self):
        prior = [v for record in self.source["records"] for v in (record["answer"], *record["variants"])]
        self.assertEqual(len(prior), 246)
        for n in STAGES:
            stage = load(f"staging/ru/followthrough_t{n}_context_pool.json")
            self.assertEqual(len(stage["entries"]), 82)
            prior.extend(r["text"] for entry in stage["entries"] for r in entry["replies"])
        self.assertEqual(len(prior), 5576)
        normalized = {_norm(v) for v in prior}
        terms_prior = [terms(v) for v in prior]
        for entry in self.stage["entries"]:
            reply = entry["replies"][0]
            current_norm = _norm(reply["text"])
            self.assertNotIn(current_norm, normalized, msg=reply["id"])
            current = terms(reply["text"])
            for earlier in terms_prior:
                common = len(current & earlier)
                denom = len(current) + len(earlier) - common
                self.assertLess(common / denom if denom else 0, .72, msg=reply["id"])
            normalized.add(current_norm)
            terms_prior.append(current)

if __name__ == "__main__":
    unittest.main()
