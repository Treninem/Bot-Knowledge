"""T430: source-pinned distinct contextual replies, exact history and scope."""
import hashlib
import json
import unittest
from scripts.colloquial_t305 import ROOT
from scripts.staged_context_selector import _norm

SOURCE = "packs/ru/conversation_followthrough_qa.json"
PARENT = "staging/ru/followthrough_t429_context_pool.json"
STAGE = "staging/ru/followthrough_t430_context_pool.json"
SOURCE_SHA = "0862daf244df650bfd85217df3bedb9f2373a6e63dbabfa8d0c831a6fb289ff7"
SOURCE_BLOB = "707fcaa6440d398a730840362602d4532ab92036"
PARENT_BLOB = "cf0ad83036e0fafea4fa1a0d7c207bf0183e7528"
STAGE_BLOB = "6004d03017463aee1545021cc2bcde5a6bfa48e8"

def read(path):
    return (ROOT / path).read_bytes()

def blob(data):
    return hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()

def tokens(value):
    return set(_norm(value).split())

class T430Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = json.loads(read(SOURCE))
        cls.stage = json.loads(read(STAGE))
        cls.manifest = json.loads(read("manifest.json"))

    def test_pinned_origin_and_exact_byte_content(self):
        registered = {x["path"]:x["sha256"] for x in self.manifest["packs"]}[SOURCE]
        self.assertEqual(registered,SOURCE_SHA)
        self.assertEqual(hashlib.sha256(read(SOURCE)).hexdigest(),SOURCE_SHA)
        self.assertEqual(blob(read(SOURCE)),SOURCE_BLOB)
        self.assertEqual(blob(read(PARENT)),PARENT_BLOB)
        self.assertEqual(blob(read(STAGE)),STAGE_BLOB)
        self.assertEqual(self.stage["source_pack_manifest_sha256"],SOURCE_SHA)
        self.assertEqual(self.stage["source_pack_blob_sha"],SOURCE_BLOB)
        self.assertEqual((self.stage["previous_stage"],self.stage["previous_stage_blob_sha"]),(PARENT,PARENT_BLOB))

    def test_scope_inventory_counts_and_safety(self):
        d=self.stage
        self.assertEqual((d["schema_version"],d["stage_type"]),(1,"supplemental_contextual_reply_pool"))
        self.assertIs(d["consumer_registered"],False)
        self.assertEqual((d["language"],d["audiences"]),( "ru",["all_ai_bots"]))
        self.assertEqual(d["constraints"],{"read_only":True,"requires_direct_address":True,"no_personal_data":True})
        self.assertEqual(d["checkpoint"],{"stage_id":"T430","processed_intents":82,"registered_count":246,"added_candidates":82,"finished_100":0,"partial_intents":82,"remaining_total":7872,"rejected":0})
        self.assertEqual(d["cumulative_checkpoint"],{"baseline_registered":246,"previous_staged":3854,"added_candidates":82,"total":4182,"partial_intents":82,"finished_100":0,"remaining_total":4018})
        canon={x["id"]:x["question"] for x in self.source["records"]}
        self.assertEqual(len(canon),82)
        self.assertEqual(len(d["entries"]),82)
        self.assertEqual({x["intent_id"] for x in d["entries"]},set(canon))
        for e in d["entries"]:
            self.assertEqual(e["question"],canon[e["intent_id"]])
            self.assertEqual((e["registered_reply_count"],e["staged_reply_count"]),(3,1))
            self.assertEqual(len(e["replies"]),1)
            r=e["replies"][0]
            self.assertEqual(r["id"],e["intent_id"]+"_t430_01")
            self.assertEqual((r["language"],r["style"],r["audiences"]),( "ru","neutral",["all_ai_bots"]))
            self.assertIn(r["context"],("direct","private","group_addressed"))
            self.assertIs(r["read_only"],True)
            self.assertIn("без действий",r["avoid"])
            self.assertGreater(len(r["text"]),35)
            self.assertGreater(len(r["context_note"]),20)

    def test_all_history_normalized_and_near_dedup(self):
        previous=[a for row in self.source["records"] for a in [row["answer"],*row["variants"]]]
        for i in [*range(383,423),424,425,427,428,429]:
            stage=json.loads(read(f"staging/ru/followthrough_t{i}_context_pool.json"))
            self.assertEqual(len(stage["entries"]),82)
            previous.extend(r["text"] for e in stage["entries"] for r in e["replies"])
        known={_norm(x) for x in previous}
        history=[tokens(x) for x in previous]
        ids,notes=set(),set()
        for e in self.stage["entries"]:
            for r in e["replies"]:
                self.assertNotIn(r["id"],ids)
                ids.add(r["id"])
                v=_norm(r["text"])
                self.assertNotIn(v,known,msg=r["id"])
                known.add(v)
                n=_norm(r["context_note"])
                self.assertNotIn(n,notes)
                notes.add(n)
                cur=tokens(r["text"])
                for old in history:
                    union=cur|old
                    j=len(cur&old)/len(union) if union else 0
                    self.assertLess(j,0.72,msg=f"near duplicate {r['id']}: {j:.3f}")
                history.append(cur)

if __name__=="__main__":
    unittest.main()
