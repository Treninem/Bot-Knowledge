"""T428 source-pinned 82 genuinely situated replies; all-history validation."""
import hashlib
import json
import unittest
from scripts.colloquial_t305 import ROOT
from scripts.staged_context_selector import _norm

SOURCE = "packs/ru/conversation_followthrough_qa.json"
PARENT = "staging/ru/followthrough_t427_context_pool.json"
STAGE = "staging/ru/followthrough_t428_context_pool.json"
SOURCE_SHA = "0862daf244df650bfd85217df3bedb9f2373a6e63dbabfa8d0c831a6fb289ff7"
SOURCE_BLOB = "707fcaa6440d398a730840362602d4532ab92036"
PARENT_BLOB = "4bad4fa90347dbd8123f49be0e732f88a5e096f3"
STAGE_BLOB = "9947f434ebf95511d0f9ce00466a420aad0fd743"

def read(path):
    return (ROOT / path).read_bytes()

def blob(data):
    return hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()

def tokens(value):
    return set(_norm(value).split())

class T428Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = json.loads(read(SOURCE))
        cls.stage = json.loads(read(STAGE))
        cls.manifest = json.loads(read("manifest.json"))

    def test_immutable_origin(self):
        recorded = {x["path"]: x["sha256"] for x in self.manifest["packs"]}[SOURCE]
        self.assertEqual(recorded, SOURCE_SHA)
        self.assertEqual(hashlib.sha256(read(SOURCE)).hexdigest(), SOURCE_SHA)
        self.assertEqual(blob(read(SOURCE)), SOURCE_BLOB)
        self.assertEqual(blob(read(PARENT)), PARENT_BLOB)
        self.assertEqual(blob(read(STAGE)), STAGE_BLOB)
        self.assertEqual(self.stage["source_pack_manifest_sha256"], SOURCE_SHA)
        self.assertEqual(self.stage["source_pack_blob_sha"], SOURCE_BLOB)
        self.assertEqual(self.stage["previous_stage"], PARENT)
        self.assertEqual(self.stage["previous_stage_blob_sha"], PARENT_BLOB)

    def test_exact_inventory_and_permissions(self):
        data = self.stage
        self.assertEqual(data["schema_version"],1)
        self.assertEqual(data["stage_type"],"supplemental_contextual_reply_pool")
        self.assertIs(data["consumer_registered"],False)
        self.assertEqual(data["language"],"ru")
        self.assertEqual(data["audiences"],["all_ai_bots"])
        self.assertEqual(data["constraints"],{"read_only":True,"requires_direct_address":True,"no_personal_data":True})
        self.assertEqual(data["checkpoint"],{"stage_id":"T428","processed_intents":82,"registered_count":246,"added_candidates":82,"finished_100":0,"partial_intents":82,"remaining_total":7872,"rejected":0})
        self.assertEqual(data["cumulative_checkpoint"],{"baseline_registered":246,"previous_staged":3690,"added_candidates":82,"total":4018,"partial_intents":82,"finished_100":0,"remaining_total":4182})
        canon={x["id"]:x["question"] for x in self.source["records"]}
        self.assertEqual(len(canon),82)
        self.assertEqual(len(data["entries"]),82)
        self.assertEqual(set(canon),{e["intent_id"] for e in data["entries"]})
        for entry in data["entries"]:
            self.assertEqual(entry["question"],canon[entry["intent_id"]])
            self.assertEqual((entry["registered_reply_count"],entry["staged_reply_count"]),(3,1))
            self.assertEqual(len(entry["replies"]),1)
            reply=entry["replies"][0]
            self.assertEqual(reply["id"],entry["intent_id"]+"_t428_01")
            self.assertEqual(reply["audiences"],["all_ai_bots"])
            self.assertEqual(reply["language"],"ru")
            self.assertEqual(reply["style"],"neutral")
            self.assertIn(reply["context"],("direct","private","group_addressed"))
            self.assertIs(reply["read_only"],True)
            self.assertIn("без действий",reply["avoid"])
            self.assertGreater(len(reply["text"]),35)
            self.assertGreater(len(reply["context_note"]),20)

    def test_complete_history_uniqueness_and_near_duplicates(self):
        previous=[x for row in self.source["records"] for x in [row["answer"],*row["variants"]]]
        for i in [*range(383,423),424,425,427]:
            history=json.loads(read(f"staging/ru/followthrough_t{i}_context_pool.json"))
            self.assertEqual(len(history["entries"]),82)
            previous.extend(r["text"] for e in history["entries"] for r in e["replies"])
        known={_norm(x) for x in previous}
        token_history=[tokens(x) for x in previous]
        seen_ids,seen_notes=set(),set()
        for e in self.stage["entries"]:
            for r in e["replies"]:
                self.assertNotIn(r["id"],seen_ids)
                seen_ids.add(r["id"])
                v=_norm(r["text"])
                self.assertNotIn(v,known,msg=r["id"])
                known.add(v)
                n=_norm(r["context_note"])
                self.assertNotIn(n,seen_notes,msg=r["id"])
                seen_notes.add(n)
                cur=tokens(r["text"])
                for old in token_history:
                    j=len(cur & old)/len(cur | old) if cur | old else 0
                    self.assertLess(j,0.72,msg=f"near duplicate {r['id']}: {j:.3f}")
                token_history.append(cur)

if __name__ == "__main__":
    unittest.main()
