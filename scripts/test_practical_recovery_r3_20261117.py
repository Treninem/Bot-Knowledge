"""R3 QA for practical recovery candidates; no consumer registration or actions."""
import hashlib
import json
import unittest
from pathlib import Path
from scripts.test_practical_recovery_r1_20261114 import normalize, wordset, similarity
ROOT=Path(__file__).resolve().parents[1]
STAGE=ROOT/"staging/ru/practical_recovery_context_r3_20261117.json"
PRIOR=ROOT/"staging/ru/practical_recovery_context_r1_20261114.json"
SOURCE=ROOT/"packs/ru/practical_recovery_qa.json"
MAIN_SHA="d43134b9072c7ceff44cfcf63d5d11c0d0771d7a"
SOURCE_SHA="be8ae1408cf42816adc3f8ba818b3f004318617ba2e878e72edd85cf7eb4954e"
SOURCE_BLOB="21bf261970d1bdcf0f9fb8fb3383772b86b2dc2f"
def answer_strings(value):
    if isinstance(value,list):
        for item in value: yield from answer_strings(item)
    elif isinstance(value,dict):
        for key,item in value.items():
            if key in {"answer","text","reply"} and isinstance(item,str): yield item
            elif isinstance(item,(dict,list)): yield from answer_strings(item)
class PracticalRecoveryR3(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data=json.loads(STAGE.read_text(encoding="utf-8"))
        cls.prior=json.loads(PRIOR.read_text(encoding="utf-8"))
        cls.source_bytes=SOURCE.read_bytes()
        cls.source=json.loads(cls.source_bytes)
        cls.manifest=json.loads((ROOT/"manifest.json").read_text(encoding="utf-8"))
    def test_source_checkpoint_and_stable_intents(self):
        d=self.data
        known={p["path"]:p["sha256"] for p in self.manifest["packs"]}
        self.assertEqual(known[SOURCE.relative_to(ROOT).as_posix()],SOURCE_SHA)
        self.assertEqual(hashlib.sha256(self.source_bytes).hexdigest(),SOURCE_SHA)
        blob=b"blob "+str(len(self.source_bytes)).encode()+b"\0"+self.source_bytes
        self.assertEqual(hashlib.sha1(blob).hexdigest(),SOURCE_BLOB)
        self.assertEqual(d["checked_source_main_sha"],MAIN_SHA)
        self.assertEqual(d["current_main_reverification"]["commit_sha"],MAIN_SHA)
        self.assertFalse(d["consumer_registered"])
        self.assertNotIn(STAGE.relative_to(ROOT).as_posix(),known)
        c=d["checkpoint"]
        self.assertEqual((c["new_candidates"],c["prior_stage_candidates"],c["cumulative_candidates"],c["remaining_per_intent_if_all_pass"]),(72,120,192,83))
        self.assertEqual(len(d["entries"]),24)
        published={r["id"]:r for r in self.source["records"]}
        prior={e["intent_id"]:e for e in self.prior["entries"]}
        self.assertEqual(set(published),set(prior))
        for e in d["entries"]:
            old=published[e["intent_id"]]
            self.assertEqual(e["canonical_question"],old["question"])
            self.assertEqual((e["published_count"],e["prior_staged_candidates"],e["added_candidates"],e["total_staged"],e["eligible_numeric_if_all_accepted"],e["remaining_if_all_accepted"]),(9,5,3,8,17,83))
            self.assertEqual(len(prior[e["intent_id"]]["replies"]),5)
            self.assertEqual(len(e["replies"]),3)
    def test_ids_context_and_safety(self):
        ids,texts,notes=set(),set(),set()
        self.assertEqual(self.data["audiences"],["all_ai_bots"])
        for k in ("requires_direct_address","requires_context_match","read_only","no_personal_data","no_sanctions"): self.assertTrue(self.data["constraints"][k])
        for e in self.data["entries"]:
            for suffix,r in enumerate(e["replies"],15):
                self.assertEqual(r["id"],f'{e["intent_id"]}_ctx_{suffix:03}')
                self.assertNotIn(r["id"],ids);ids.add(r["id"])
                self.assertNotIn(normalize(r["text"]),texts);texts.add(normalize(r["text"]))
                self.assertNotIn(normalize(r["context_note"]),notes);notes.add(normalize(r["context_note"]))
                self.assertEqual((r["context"],r["language"],r["style"],r["audiences"],r["read_only"],r["editorial_status"]),("direct","ru","plain_help",["all_ai_bots"],True,"candidate_pending_full_semantic_review"))
                self.assertGreaterEqual(len(r["text"]),90);self.assertLessEqual(len(r["text"]),300);self.assertGreaterEqual(len(r["context_note"]),40)
                self.assertIn("без действий, санкций",r["avoid"])
                self.assertNotIn("@",r["text"]+r["context_note"]);self.assertNotIn("http",(r["text"]+r["context_note"]).lower())
                self.assertNotRegex(r["text"].lower(),r"\b(?:забан|замут|выдал бан|удалил сообщение)\b")
        self.assertEqual((len(ids),len(texts),len(notes)),(72,72,72))
    def test_semantic_distance_within_each_intent(self):
        published={r["id"]:r for r in self.source["records"]}
        prior={e["intent_id"]:e for e in self.prior["entries"]}
        for e in self.data["entries"]:
            old=published[e["intent_id"]]
            pool=[old["answer"],*old["variants"],*(r["text"] for r in prior[e["intent_id"]]["replies"])]
            for r in e["replies"]:
                for previous in pool: self.assertLess(similarity(r["text"],previous),0.70,(r["id"],previous))
                pool.append(r["text"])
    def test_exact_duplicates_against_registered_packs_and_main_staging(self):
        candidates=[r["text"] for e in self.data["entries"] for r in e["replies"]]
        keys={normalize(s) for s in candidates}
        checked_registered=0
        for info in self.manifest["packs"]:
            payload=json.loads((ROOT/info["path"]).read_text(encoding="utf-8"))
            for old in answer_strings(payload):
                checked_registered+=1
                self.assertNotIn(normalize(old),keys,info["path"])
        checked_staging=0
        for path in (ROOT/"staging/ru").glob("*.json"):
            if path==STAGE: continue
            payload=json.loads(path.read_text(encoding="utf-8"))
            for old in answer_strings(payload):
                checked_staging+=1
                self.assertNotIn(normalize(old),keys,path.name)
        self.assertGreater(checked_registered,0);self.assertGreater(checked_staging,0)
    def test_near_duplicates_against_related_registered_qa(self):
        related={"packs/ru/practical_recovery_qa.json","packs/ru/dialogue_help_qa.json","packs/ru/conversation_followthrough_qa.json","packs/ru/conversation_precision_qa.json","packs/ru/response_boundaries_qa.json","packs/ru/structured_information_qa.json","packs/ru/collaborative_dialogue_qa.json","packs/ru/impuls_help_qa.json","packs/ru/impuls_verified_boundaries_qa.json","packs/ru/impuls_ai_modes_help_qa.json","packs/ru/moderation_explanations_qa.json","packs/ru/moderation_dialogue_fairness_qa.json","packs/ru/context_repair_v022_qa.json","packs/ru/spoken_context_followups_qa.json","packs/ru/choice_reasoning_qa.json"}
        candidates=[r["text"] for e in self.data["entries"] for r in e["replies"]]
        words=[wordset(s) for s in candidates]
        checked=0
        for path in related:
            payload=json.loads((ROOT/path).read_text(encoding="utf-8"))
            for old in answer_strings(payload):
                old_words=wordset(old)
                if len(old_words)<4: continue
                checked+=1
                for candidate_words in words:
                    if not candidate_words or min(len(candidate_words),len(old_words))/max(len(candidate_words),len(old_words))<0.82: continue
                    score=len(candidate_words&old_words)/max(1,len(candidate_words|old_words))
                    self.assertLess(score,0.82,(path,score))
        self.assertGreater(checked,0)
if __name__=="__main__": unittest.main()
