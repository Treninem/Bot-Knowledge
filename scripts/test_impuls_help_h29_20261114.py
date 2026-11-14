#!/usr/bin/env python3
"""Staging H29: read-only FAQ continuation, no consumer registration."""
import json, re, unittest
from collections import Counter
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def norm(s):
    return " ".join(re.findall(r"[\w]+",s.lower().replace("ё","е")))
def jac(a,b):
    a,b=set(norm(a).split()),set(norm(b).split())
    return len(a & b)/max(len(a | b),1)
class H29QA(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.faq=json.loads((ROOT/"packs/ru/impuls_help_qa.json").read_text(encoding="utf-8"))
        cls.stages=[json.loads((ROOT/f"staging/ru/impuls_help_context_h{i}_20261114.json").read_text(encoding="utf-8")) for i in range(1,30)]
    def test_stage_and_counts(self):
        h=self.stages[-1]
        self.assertFalse(h["consumer_registered"])
        self.assertTrue(h["constraints"]["read_only"])
        self.assertEqual(len(h["entries"]),50)
        self.assertEqual(len({e["intent_id"] for e in h["entries"]}),50)
        c=Counter()
        ids=set()
        for st in self.stages:
            for e in st["entries"]:
                c[e["intent_id"]]+=len(e["replies"])
                for r in e["replies"]:
                    self.assertNotIn(r["id"],ids)
                    ids.add(r["id"])
        self.assertEqual(sum(c.values()),1485)
        self.assertEqual(len(c),100)
        faq={e["id"]:e for e in self.faq["records"]}
        self.assertTrue(all(i in faq for i in c))
        self.assertEqual(sum(100-(1+len(faq[k]["variants"])+v) for k,v in c.items()),8240)
    def test_unique_contextual_replies(self):
        earlier=[r["text"] for st in self.stages[:-1] for e in st["entries"] for r in e["replies"]]
        earlier += [v for e in self.faq["records"] for v in [e["answer"],*e["variants"]]]
        per_intent={}
        for st in self.stages[:-1]:
            for e in st["entries"]:
                per_intent.setdefault(e["intent_id"],[]).extend(r["context_note"] for r in e["replies"])
        normalized={norm(v) for v in earlier}
        for e in self.stages[-1]["entries"]:
            r=e["replies"][0]
            self.assertTrue(r["read_only"])
            self.assertEqual(r["response_role"],"assistant_reply")
            self.assertEqual(r["editorial_status"],"candidate_pending_full_semantic_review")
            self.assertEqual(r["audiences"],["impuls"])
            self.assertIn(r["context"],["direct","private","group_addressed"])
            self.assertGreater(len(r["text"]),54)
            self.assertGreater(len(r["context_note"]),39)
            self.assertNotIn(norm(r["text"]),normalized)
            self.assertTrue(all(jac(r["text"],q)<.70 for q in earlier),r["id"])
            self.assertTrue(all(jac(r["context_note"],q)<.58 for q in per_intent.get(e["intent_id"],[])),r["id"])
            self.assertFalse(any(x in r["text"] for x in ("https://","http://","t.me/","@")))
            self.assertEqual(e["remaining_to_target_excluding_other_prs"],100-e["total_candidates_in_main_and_H29"])
            earlier.append(r["text"])
            normalized.add(norm(r["text"]))
if __name__=="__main__":
    unittest.main()
