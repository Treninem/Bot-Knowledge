#!/usr/bin/env python3
"""H95 exact-lineage, scope and candidate checks; does not certify a consumer rollout."""
import hashlib, re, unittest
from collections import Counter
from test_impuls_help_h65_20261115 import ROOT, read, normalized, similarity
PACK = "packs/ru/impuls_help_qa.json"
EXPECTED_NEW = 50
EXPECTED_INTENTS = 49
EXPECTED_STAGED = 3857
EXPECTED_GAPS = 5868
def stage(i):
    return read(f"staging/ru/impuls_help_context_h{i}_{'20261114' if i <= 30 else '20261115'}.json")
class H95FullLineage(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.records = {r["id"]: r for r in read(PACK)["records"]}
        cls.all = [stage(i) for i in range(1,96)]
        cls.new = cls.all[-1]
    def test_source_and_privacy_scope(self):
        sheet = self.new; manifest = read("manifest.json")
        hashes = {x["path"]:x["sha256"] for x in manifest["packs"]}
        raw = hashlib.sha256((ROOT / PACK).read_bytes()).hexdigest()
        self.assertEqual(raw,hashes[PACK])
        self.assertEqual(raw,sheet["source_pack_manifest_sha256"])
        self.assertNotIn("staging/ru/impuls_help_context_h95_20261115.json",hashes)
        self.assertEqual(sheet["checked_source_main_sha"],"6c9f430da47f137d39a72bbd28c057cfb8f6be96")
        self.assertEqual(sheet["checked_impuls_main_sha"],"54b8a3a813fec82c1f953408942ba327eb181c37")
        self.assertIs(sheet["consumer_registered"],False)
        self.assertEqual(sheet["audiences"],["impuls"])
        for key in ("read_only","requires_direct_address","requires_context_match","no_personal_data","no_sanctions"):
            self.assertIs(sheet["constraints"][key],True)
    def test_lineage_ids_and_coverage(self):
        staged=Counter();ids=set();seen=set()
        for num,sheet in enumerate(self.all,1):
            for e in sheet["entries"]:
                ident=e["intent_id"];self.assertIn(ident,self.records)
                if num==95:
                    self.assertNotIn(ident,seen);seen.add(ident)
                    pub=1+len(self.records[ident]["variants"])
                    self.assertEqual(e["canonical_question"],self.records[ident]["question"])
                    self.assertEqual(e["published_count"],pub)
                    self.assertEqual(e["earlier_staged_candidates"],staged[ident])
                    self.assertEqual(e["added_candidates"],len(e["replies"]))
                    self.assertEqual(e["total_candidates_in_main_and_H95"],pub+staged[ident]+len(e["replies"]))
                    self.assertEqual(e["remaining_to_target_excluding_other_prs"],100-e["total_candidates_in_main_and_H95"])
                    self.assertLess(e["total_candidates_in_main_and_H95"],100)
                for reply in e["replies"]:
                    self.assertNotIn(reply["id"],ids);ids.add(reply["id"])
                staged[ident]+=len(e["replies"])
        self.assertEqual(len(seen),EXPECTED_INTENTS)
        self.assertEqual(len(staged),100)
        self.assertEqual(sum(staged.values()),EXPECTED_STAGED)
        self.assertEqual(sum(100-1-len(self.records[i]["variants"])-v for i,v in staged.items()),EXPECTED_GAPS)
        cp=self.new["checkpoint"]
        self.assertEqual(cp["processed_intents"],EXPECTED_INTENTS)
        self.assertEqual(cp["new_candidates"],EXPECTED_NEW)
        self.assertEqual(cp["cumulative_H1_H95"],EXPECTED_STAGED)
        self.assertEqual(cp["remaining_numeric_all_100_intents"],EXPECTED_GAPS)
        self.assertEqual(cp["editorially_approved_new"],0)
        self.assertEqual(cp["certified_100_sets"],0)
    def test_new_nonrepetitive_and_safe(self):
        older=[t for r in self.records.values() for t in [r["answer"],*r["variants"]]]
        older += [v["text"] for s in self.all[:-1] for e in s["entries"] for v in e["replies"]]
        used={normalized(t) for t in older}; accepted=0
        for e in self.new["entries"]:
            for index,reply in enumerate(e["replies"],1):
                accepted+=1
                self.assertEqual(reply["id"],f"impuls_help_{e['intent_id']}_h95_{index:02d}")
                self.assertEqual(reply["language"],"ru")
                self.assertEqual(reply["audiences"],["impuls"])
                self.assertEqual(reply["response_role"],"assistant_reply")
                self.assertEqual(reply["editorial_status"],"candidate_pending_full_semantic_review")
                self.assertIs(reply["read_only"],True)
                self.assertIn(reply["context"],("private","direct","group_addressed"))
                self.assertGreaterEqual(len(reply["text"]),75)
                self.assertGreaterEqual(len(reply["context_note"]),55)
                self.assertGreaterEqual(len(reply["avoid"]),70)
                self.assertFalse(re.search(r"https?://|t\.me/|@[a-z_]|[0-9]{10,}",reply["text"]+" "+reply["context_note"],re.I))
                self.assertFalse(re.search(r"я (?:забанил|удалил сообщение|изменил настройки|начислил)",reply["text"],re.I))
                self.assertNotIn(normalized(reply["text"]),used)
                self.assertTrue(all(similarity(reply["text"],other)<0.70 for other in older),reply["id"])
                older.append(reply["text"]);used.add(normalized(reply["text"]))
        self.assertEqual(accepted,EXPECTED_NEW)
if __name__=="__main__":unittest.main()
