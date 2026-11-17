#!/usr/bin/env python3
"""H96 full staged lineage and scoped response checks; not evidence of deployment."""
import hashlib,re,unittest
from collections import Counter
from test_impuls_help_h65_20261115 import ROOT,read,normalized,similarity
PACK="packs/ru/impuls_help_qa.json"
def stage(i):
    return read(f"staging/ru/impuls_help_context_h{i}_{'20261114' if i<=30 else '20261115'}.json")
class H96FullLineage(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.records={r["id"]:r for r in read(PACK)["records"]}
        cls.all=[stage(i) for i in range(1,97)]
        cls.new=cls.all[-1]
    def test_manifest_scope(self):
        m=read("manifest.json");hashes={p["path"]:p["sha256"] for p in m["packs"]}
        raw=hashlib.sha256((ROOT/PACK).read_bytes()).hexdigest()
        self.assertEqual(raw,hashes[PACK])
        self.assertEqual(self.new["source_pack_manifest_sha256"],raw)
        self.assertEqual(self.new["checked_source_main_sha"],"6c9f430da47f137d39a72bbd28c057cfb8f6be96")
        self.assertEqual(self.new["checked_impuls_main_sha"],"54b8a3a813fec82c1f953408942ba327eb181c37")
        self.assertNotIn("staging/ru/impuls_help_context_h96_20261115.json",hashes)
        self.assertIs(self.new["consumer_registered"],False)
        self.assertEqual(self.new["audiences"],["impuls"])
        for key in ("read_only","requires_direct_address","requires_context_match","no_personal_data","no_sanctions"):
            self.assertIs(self.new["constraints"][key],True)
    def test_unique_counts_and_ids(self):
        counter=Counter();ids=set();current=set()
        for number,s in enumerate(self.all,1):
            for e in s["entries"]:
                ident=e["intent_id"];self.assertIn(ident,self.records)
                if number==96:
                    self.assertNotIn(ident,current);current.add(ident)
                    pub=1+len(self.records[ident]["variants"])
                    self.assertEqual(e["canonical_question"],self.records[ident]["question"])
                    self.assertEqual(e["published_count"],pub)
                    self.assertEqual(e["earlier_staged_candidates"],counter[ident])
                    self.assertEqual(e["added_candidates"],len(e["replies"]))
                    self.assertEqual(e["total_candidates_in_main_and_H96"],pub+counter[ident]+len(e["replies"]))
                    self.assertEqual(e["remaining_to_target_excluding_other_prs"],100-e["total_candidates_in_main_and_H96"])
                    self.assertLess(e["total_candidates_in_main_and_H96"],100)
                for r in e["replies"]:
                    self.assertNotIn(r["id"],ids);ids.add(r["id"])
                counter[ident]+=len(e["replies"])
        self.assertEqual(len(current),51)
        self.assertEqual(len(counter),100)
        self.assertEqual(sum(counter.values()),3908)
        self.assertEqual(sum(100-1-len(self.records[i]["variants"])-v for i,v in counter.items()),5817)
        cp=self.new["checkpoint"]
        self.assertEqual(cp["processed_intents"],51)
        self.assertEqual(cp["new_candidates"],51)
        self.assertEqual(cp["cumulative_H1_H96"],3908)
        self.assertEqual(cp["remaining_numeric_all_100_intents"],5817)
        self.assertEqual(cp["editorially_approved_new"],0)
        self.assertEqual(cp["certified_100_sets"],0)
    def test_text_safety_and_overlap(self):
        prev=[t for r in self.records.values() for t in [r["answer"],*r["variants"]]]
        prev += [r["text"] for s in self.all[:-1] for e in s["entries"] for r in e["replies"]]
        keys={normalized(t) for t in prev};accepted=0
        for e in self.new["entries"]:
            for r in e["replies"]:
                accepted+=1
                self.assertEqual(r["id"],f"impuls_help_{e['intent_id']}_h96_01")
                self.assertEqual(r["language"],"ru")
                self.assertEqual(r["audiences"],["impuls"])
                self.assertEqual(r["response_role"],"assistant_reply")
                self.assertEqual(r["editorial_status"],"candidate_pending_full_semantic_review")
                self.assertIs(r["read_only"],True)
                self.assertIn(r["context"],("direct","private","group_addressed"))
                self.assertGreaterEqual(len(r["text"]),75)
                self.assertGreaterEqual(len(r["context_note"]),55)
                self.assertGreaterEqual(len(r["avoid"]),70)
                joined=r["text"]+" "+r["context_note"]
                self.assertFalse(re.search(r"https?://|t\.me/|@[a-z_]|[0-9]{10,}",joined,re.I))
                self.assertFalse(re.search(r"я (?:забанил|удалил сообщение|изменил настройки|начислил)",r["text"],re.I))
                self.assertNotIn(normalized(r["text"]),keys)
                self.assertTrue(all(similarity(r["text"],t)<0.70 for t in prev),r["id"])
                keys.add(normalized(r["text"]));prev.append(r["text"])
        self.assertEqual(accepted,51)
if __name__=="__main__":unittest.main()
