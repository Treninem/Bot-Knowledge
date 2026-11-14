#!/usr/bin/env python3
"""Staging H30 continuation: normalized uniqueness and context safety; no bot operations."""
import json, re, unittest
from pathlib import Path
from collections import Counter
ROOT=Path(__file__).resolve().parents[1]
def norm(s):
    return " ".join(re.findall(r"[\w]+",s.lower().replace("ё","е")))
def jac(a,b):
    a,b=set(norm(a).split()),set(norm(b).split())
    return len(a & b)/max(len(a | b),1)
class H30QA(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.faq=json.loads((ROOT/"packs/ru/impuls_help_qa.json").read_text(encoding="utf-8"))
        cls.stages=[json.loads((ROOT/f"staging/ru/impuls_help_context_h{i}_20261114.json").read_text(encoding="utf-8")) for i in range(1,31)]
    def test_counts_source_and_roles(self):
        f={e["id"]:e for e in self.faq["records"]}
        ids=set()
        c=Counter()
        for stage in self.stages:
            self.assertFalse(stage["consumer_registered"])
            self.assertTrue(stage["constraints"]["no_sanctions"])
            for e in stage["entries"]:
                self.assertIn(e["intent_id"],f)
                c[e["intent_id"]]+=len(e["replies"])
                for r in e["replies"]:
                    self.assertNotIn(r["id"],ids)
                    ids.add(r["id"])
        self.assertEqual(len(c),100)
        self.assertEqual(sum(c.values()),1535)
        self.assertEqual(sum(100-(1+len(f[k]["variants"])+n) for k,n in c.items()),8190)
        self.assertEqual(Counter(1+len(f[k]["variants"])+n for k,n in c.items()),Counter({16:6,17:49,19:19,20:26}))
    def test_new_replies_match_context_without_duplicates(self):
        h=self.stages[-1]
        self.assertEqual(len(h["entries"]),50)
        seen=[r["text"] for st in self.stages[:-1] for e in st["entries"] for r in e["replies"]]
        seen += [v for e in self.faq["records"] for v in [e["answer"],*e["variants"]]]
        notes={}
        for st in self.stages[:-1]:
            for e in st["entries"]:
                notes.setdefault(e["intent_id"],[]).extend(r["context_note"] for r in e["replies"])
        normalized={norm(s) for s in seen}
        for e in h["entries"]:
            r=e["replies"][0]
            self.assertEqual(r["response_role"],"assistant_reply")
            self.assertEqual(r["editorial_status"],"candidate_pending_full_semantic_review")
            self.assertEqual(r["audiences"],["impuls"])
            self.assertTrue(r["read_only"])
            self.assertIn(r["context"],["direct","private","group_addressed"])
            self.assertGreater(len(r["text"]),54)
            self.assertGreater(len(r["context_note"]),39)
            self.assertNotIn(norm(r["text"]),normalized)
            self.assertTrue(all(jac(r["text"],v)<.70 for v in seen),r["id"])
            self.assertTrue(all(jac(r["context_note"],v)<.58 for v in notes.get(e["intent_id"],[])),r["id"])
            self.assertFalse(any(x in r["text"] for x in ("https://","http://","t.me/","@")))
            self.assertEqual(e["remaining_to_target_excluding_other_prs"],100-e["total_candidates_in_main_and_H30"])
            normalized.add(norm(r["text"]))
            seen.append(r["text"])
if __name__=="__main__":
    unittest.main()
