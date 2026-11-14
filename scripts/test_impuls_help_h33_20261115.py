#!/usr/bin/env python3
"""H33 staging QA: 39 original addressed, read-only RU replies with prior-state audit."""
import json
import re
import unittest
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
def n(s): return " ".join(re.findall(r"\w+", s.casefold().replace("ё","е")))
def j(a,b):
    aa,bb=set(n(a).split()),set(n(b).split())
    return len(aa&bb)/max(1,len(aa|bb))

class H33QA(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.faq=json.loads((ROOT/"packs/ru/impuls_help_qa.json").read_text(encoding="utf-8"))
        cls.f={r["id"]:r for r in cls.faq["records"]}
        cls.stages=[json.loads((ROOT/f"staging/ru/impuls_help_context_h{i}_{'20261115' if i>=31 else '20261114'}.json").read_text(encoding="utf-8")) for i in range(1,34)]
    def test_unique_ids_and_exact_counts(self):
        counter=Counter(); seen=set()
        for st in self.stages:
            self.assertFalse(st["consumer_registered"])
            self.assertTrue(st["constraints"]["no_sanctions"])
            for ent in st["entries"]:
                self.assertIn(ent["intent_id"],self.f)
                counter[ent["intent_id"]]+=len(ent["replies"])
                for r in ent["replies"]:
                    self.assertNotIn(r["id"],seen)
                    seen.add(r["id"])
        self.assertEqual(len(counter),100)
        self.assertEqual(sum(counter.values()),1635)
        self.assertEqual(sum(100-(1+len(self.f[k]["variants"])+v) for k,v in counter.items()),8090)
        self.assertEqual(self.stages[-1]["checkpoint"]["cumulative_H1_H33"],1635)
        self.assertEqual(self.stages[-1]["checkpoint"]["remaining_numeric_all_100_intents"],8090)
    def test_h33_is_read_only_and_distinct_from_previous(self):
        old=[r["text"] for st in self.stages[:-1] for e in st["entries"] for r in e["replies"]]
        old += [s for e in self.faq["records"] for s in [e["answer"],*e["variants"]]]
        notes=defaultdict(list)
        for st in self.stages[:-1]:
            for e in st["entries"]:
                notes[e["intent_id"]].extend(r["context_note"] for r in e["replies"])
        h=self.stages[-1]
        self.assertEqual(len(h["entries"]),39)
        self.assertEqual(len({e["intent_id"] for e in h["entries"]}),39)
        for e in h["entries"]:
            self.assertEqual(e["canonical_question"],self.f[e["intent_id"]]["question"])
            self.assertEqual(e["added_candidates"],1)
            self.assertEqual(len(e["replies"]),1)
            r=e["replies"][0]
            self.assertEqual(r["id"],f"impuls_help_{e['intent_id']}_h33_01")
            self.assertEqual(r["response_role"],"assistant_reply")
            self.assertEqual(r["editorial_status"],"candidate_pending_full_semantic_review")
            self.assertTrue(r["read_only"])
            self.assertIn(r["context"],{"direct","private","group_addressed"})
            self.assertGreater(len(r["text"]),54)
            self.assertGreater(len(r["context_note"]),39)
            self.assertNotEqual(n(r["text"]),n(r["context_note"]))
            self.assertTrue(all(j(r["text"],x)<.70 for x in old),r["id"])
            self.assertTrue(all(j(r["context_note"],x)<.58 for x in notes[e["intent_id"]]),r["id"])
            self.assertFalse(re.search(r"https?://|t\.me/|@[A-Za-z_]|[0-9]{10,}",r["text"]+r["context_note"]))
            self.assertEqual(e["remaining_to_target_excluding_other_prs"],100-e["total_candidates_in_main_and_H33"])
            old.append(r["text"]); notes[e["intent_id"]].append(r["context_note"])
    def test_role_semantics_anchors(self):
        d={e["intent_id"]:e["replies"][0]["text"] for e in self.stages[-1]["entries"]}
        for key,words in {
            "greeting":("приветств","правил"),
            "purpose":("бот","верс"),
            "old_rule_timing":("правил","момент"),
            "request_vs_question":("просьб","подтвержд"),
            "private_vs_group":("личк","групп"),
        }.items():
            text=n(d[key])
            for word in words:self.assertIn(word,text)
if __name__=="__main__":unittest.main()
