"""T411 source-anchored two-context replies: SHA, all history, scope, counts."""
import hashlib
import json
import unittest
from scripts.colloquial_t305 import ROOT
from scripts.staged_context_selector import _norm
SOURCE = "packs/ru/conversation_followthrough_qa.json"
STAGE = "staging/ru/followthrough_t411_context_pool.json"
PARENT = "staging/ru/followthrough_t410_context_pool.json"
SOURCE_SHA = "0862daf244df650bfd85217df3bedb9f2373a6e63dbabfa8d0c831a6fb289ff7"
SOURCE_BLOB = "707fcaa6440d398a730840362602d4532ab92036"
PARENT_BLOB = "95dfa757cc0cde14a88aa7aa6752baf1fb96397a"
STAGE_BLOB = "e567f8440653b9ef6ec3ee219b94f1641aafb0fe"
def blob(data):
    return hashlib.sha1(b"blob "+str(len(data)).encode()+b"\0"+data).hexdigest()
def tokens(s):
    return set(_norm(s).split())
class T411Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.read = staticmethod(lambda p:(ROOT/p).read_bytes())
        cls.manifest=json.loads(cls.read("manifest.json"))
        cls.source=json.loads(cls.read(SOURCE))
        cls.stage=json.loads(cls.read(STAGE))
    def test_sha_and_parent(self):
        self.assertEqual({p["path"]:p["sha256"] for p in self.manifest["packs"]}[SOURCE],SOURCE_SHA)
        self.assertEqual(hashlib.sha256(self.read(SOURCE)).hexdigest(),SOURCE_SHA)
        self.assertEqual(blob(self.read(SOURCE)),SOURCE_BLOB)
        self.assertEqual(blob(self.read(PARENT)),PARENT_BLOB)
        self.assertEqual(blob(self.read(STAGE)),STAGE_BLOB)
        self.assertEqual(self.stage["source_pack_manifest_sha256"],SOURCE_SHA)
        self.assertEqual(self.stage["source_pack_blob_sha"],SOURCE_BLOB)
        self.assertEqual(self.stage["previous_stage"],PARENT)
        self.assertEqual(self.stage["previous_stage_blob_sha"],PARENT_BLOB)
    def test_intents_counts_and_guards(self):
        self.assertEqual(len(self.stage["entries"]),82)
        self.assertEqual(self.stage["checkpoint"],{"stage_id":"T411","processed_intents":82,"registered_count":246,"added_candidates":164,"finished_100":0,"partial_intents":82,"remaining_total":7790,"rejected":0})
        self.assertEqual(self.stage["cumulative_checkpoint"],{"baseline_registered":246,"previous_staged":2378,"added_candidates":164,"total":2788,"partial_intents":82,"finished_100":0,"remaining_total":5412})
        self.assertIs(self.stage["consumer_registered"],False)
        self.assertEqual(self.stage["audiences"],["all_ai_bots"])
        self.assertEqual(self.stage["constraints"],{"read_only":True,"requires_direct_address":True,"no_personal_data":True})
        canon={x["id"]:x["question"] for x in self.source["records"]}
        self.assertEqual(set(canon),{e["intent_id"] for e in self.stage["entries"]})
        for e in self.stage["entries"]:
            self.assertEqual(e["question"],canon[e["intent_id"]])
            self.assertEqual(e["registered_reply_count"],3)
            self.assertEqual(e["staged_reply_count"],2)
            self.assertEqual([r["id"] for r in e["replies"]],[e["intent_id"]+"_t411_01",e["intent_id"]+"_t411_02"])
    def test_historical_dedup_scope_and_privacy(self):
        existing=[s for x in self.source["records"] for s in (x["answer"],*x["variants"])]
        for i in range(383,411):
            old=json.loads(self.read(f"staging/ru/followthrough_t{i}_context_pool.json"))
            self.assertEqual(len(old["entries"]),82)
            existing.extend(r["text"] for e in old["entries"] for r in e["replies"])
        known={_norm(s) for s in existing}
        oldtok=[tokens(s) for s in existing]
        ids,notes=set(),set()
        for e in self.stage["entries"]:
            for r in e["replies"]:
                self.assertNotIn(r["id"],ids);ids.add(r["id"])
                self.assertNotIn(_norm(r["text"]),known);known.add(_norm(r["text"]))
                self.assertNotIn(_norm(r["context_note"]),notes);notes.add(_norm(r["context_note"]))
                self.assertEqual(r["language"],"ru")
                self.assertEqual(r["audiences"],["all_ai_bots"])
                self.assertEqual(r["style"],"neutral")
                self.assertIn(r["context"],{"direct","private","group_addressed"})
                self.assertIs(r["read_only"],True)
                self.assertIn("без действий",r["avoid"])
                self.assertGreater(len(r["text"]),30)
                self.assertGreater(len(r["context_note"]),18)
                cur=tokens(r["text"])
                for t in oldtok:
                    score=len(cur & t)/len(cur | t)
                    self.assertLess(score,0.72,msg=f"similar {r['id']} score={score:.3f}")
                oldtok.append(cur)
if __name__=="__main__":unittest.main()
