"""T436: distinct situational followthrough candidates; read-only full-history verification."""
import hashlib
import json
import unittest
from scripts.colloquial_t305 import ROOT
from scripts.staged_context_selector import _norm

SOURCE = "packs/ru/conversation_followthrough_qa.json"
STAGE = "staging/ru/followthrough_t436_context_pool.json"
PARENT = "staging/ru/followthrough_t434_context_pool.json"
SOURCE_SHA = "0862daf244df650bfd85217df3bedb9f2373a6e63dbabfa8d0c831a6fb289ff7"
SOURCE_BLOB = "707fcaa6440d398a730840362602d4532ab92036"
PARENT_BLOB = "0c6d96d7ee06bd7a166e0e0535fce35bd937cfdb"
STAGE_BLOB = "915d487e6234f1288f66f925136832812dd9fb2d"
STAGES = (*range(383, 423), 424, 425, *range(427, 435))

def raw(path):
    return (ROOT / path).read_bytes()

def load(path):
    return json.loads(raw(path))

def git_blob(content):
    return hashlib.sha1(b"blob " + str(len(content)).encode() + b"\0" + content).hexdigest()

def terms(value):
    return set(_norm(value).split())

class T436Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = load(SOURCE)
        cls.stage = load(STAGE)
        cls.manifest = load("manifest.json")

    def test_immutable_source_and_parent(self):
        manifest_sha = {p["path"]: p["sha256"] for p in self.manifest["packs"]}[SOURCE]
        self.assertEqual(manifest_sha, SOURCE_SHA)
        self.assertEqual(hashlib.sha256(raw(SOURCE)).hexdigest(), SOURCE_SHA)
        self.assertEqual(git_blob(raw(SOURCE)), SOURCE_BLOB)
        self.assertEqual(git_blob(raw(PARENT)), PARENT_BLOB)
        self.assertEqual(git_blob(raw(STAGE)), STAGE_BLOB)
        s = self.stage
        self.assertEqual(s["source_pack_manifest_sha256"], SOURCE_SHA)
        self.assertEqual(s["source_pack_blob_sha"], SOURCE_BLOB)
        self.assertEqual((s["previous_stage"], s["previous_stage_blob_sha"]), (PARENT, PARENT_BLOB))

    def test_exact_progress_and_permissions(self):
        s = self.stage
        self.assertEqual((s["schema_version"], s["stage_type"]), (1, "supplemental_contextual_reply_pool"))
        self.assertIs(s["consumer_registered"], False)
        self.assertEqual((s["language"], s["audiences"]), ("ru", ["all_ai_bots"]))
        self.assertEqual(s["constraints"], {"read_only": True, "requires_direct_address": True, "no_personal_data": True})
        self.assertEqual(s["checkpoint"], {"stage_id": "T436", "processed_intents": 82, "registered_count": 246, "added_candidates": 82, "finished_100": 0, "partial_intents": 82, "remaining_total": 7872, "rejected": 0})
        self.assertEqual(s["cumulative_checkpoint"], {"baseline_registered": 246, "previous_staged": 4264, "added_candidates": 82, "total": 4592, "partial_intents": 82, "finished_100": 0, "remaining_total": 3608})
        expected = {r["id"]: r["question"] for r in self.source["records"]}
        self.assertEqual(len(expected), 82)
        self.assertEqual(len(s["entries"]), 82)
        self.assertEqual({e["intent_id"] for e in s["entries"]}, set(expected))
        ids = set()
        notes = set()
        for e in s["entries"]:
            self.assertEqual(e["question"], expected[e["intent_id"]])
            self.assertEqual((e["registered_reply_count"], e["staged_reply_count"]), (3, 1))
            self.assertEqual(len(e["replies"]), 1)
            x = e["replies"][0]
            self.assertEqual(x["id"], e["intent_id"] + "_t436_01")
            self.assertNotIn(x["id"], ids)
            ids.add(x["id"])
            self.assertEqual((x["language"], x["style"], x["audiences"]), ("ru", "neutral", ["all_ai_bots"]))
            self.assertIn(x["context"], ("direct", "private", "group_addressed"))
            self.assertIs(x["read_only"], True)
            self.assertIn("без действий", x["avoid"])
            self.assertNotIn("actions", x)
            self.assertGreater(len(x["text"]), 50)
            self.assertGreater(len(x["context_note"]), 20)
            note = _norm(x["context_note"])
            self.assertNotIn(note, notes)
            notes.add(note)

    def test_not_rewordings_of_previous_history(self):
        previous = [s for r in self.source["records"] for s in (r["answer"], *r["variants"])]
        self.assertEqual(len(previous), 246)
        for n in STAGES:
            stage = load(f"staging/ru/followthrough_t{n}_context_pool.json")
            self.assertEqual(len(stage["entries"]), 82)
            previous.extend(x["text"] for e in stage["entries"] for x in e["replies"])
        self.assertEqual(len(previous), 4510)
        existing = {_norm(s) for s in previous}
        prior = [terms(s) for s in previous]
        for e in self.stage["entries"]:
            x = e["replies"][0]
            normalized = _norm(x["text"])
            self.assertNotIn(normalized, existing, msg=x["id"])
            current = terms(x["text"])
            for old in prior:
                overlap = len(current & old)
                denominator = len(current) + len(old) - overlap
                ratio = overlap / denominator if denominator else 0
                self.assertLess(ratio, .72, msg=x["id"])
            existing.add(normalized)
            prior.append(current)

if __name__ == "__main__":
    unittest.main()
