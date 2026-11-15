#!/usr/bin/env python3
"""Offline H44-H46 QA; staged answers grant no actions or sanctions."""
import json,hashlib,re,unittest
from collections import Counter,defaultdict
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
SRC="packs/ru/impuls_help_qa.json"
def norm(s):return " ".join(re.findall(r"[^\W_]+",s.casefold().replace("ё","е"),re.UNICODE))
def jac(a,b):
    x,y=set(norm(a).split()),set(norm(b).split())
    return len(x&y)/max(1,len(x|y))
class Quality(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.faq=json.loads((ROOT/SRC).read_text(encoding="utf-8"))
        cls.index={r["id"]:r for r in cls.faq["records"]}
        cls.stages=[json.loads((ROOT/"staging"/"ru"/f"impuls_help_context_h{i}_{'20261114' if i<=30 else '20261115'}.json").read_text(encoding="utf-8")) for i in range(1,47)]
    def test_progress_and_provenance(self):
        manifest=json.loads((ROOT/"manifest.json").read_text(encoding="utf-8"))
        expected=next(p["sha256"] for p in manifest["packs"] if p["path"]==SRC)
        self.assertEqual(expected,hashlib.sha256((ROOT/SRC).read_bytes()).hexdigest())
        counts=Counter();ids=set()
        for n,stage in enumerate(self.stages,1):
            keys=set()
            for e in stage["entries"]:
                k=e["intent_id"];self.assertIn(k,self.index);self.assertNotIn(k,keys);keys.add(k)
                self.assertEqual(e["canonical_question"],self.index[k]["question"])
                if n>=44:
                    published=1+len(self.index[k]["variants"])
                    self.assertEqual(e["published_count"],published)
                    self.assertEqual(e["earlier_staged_candidates"],counts[k])
                    self.assertEqual(e[f"total_candidates_in_main_and_H{n}"],published+counts[k]+1)
                    self.assertEqual(e["remaining_to_target_excluding_other_prs"],99-published-counts[k])
                for r in e["replies"]:
                    self.assertNotIn(r["id"],ids);ids.add(r["id"]);counts[k]+=1
        self.assertEqual(len(counts),100);self.assertEqual(sum(counts.values()),1975)
        self.assertEqual(sum(99-len(self.index[k]["variants"])-cnt for k,cnt in counts.items()),7750)
        for n,stage in enumerate(self.stages[-3:],44):
            self.assertFalse(stage["consumer_registered"])
            self.assertEqual(len(stage["entries"]),20)
            self.assertEqual(stage["source_pack_manifest_sha256"],expected)
            self.assertEqual(stage["checkpoint"][f"cumulative_H1_H{n}"],1915+20*(n-43))
            for key in ("read_only","requires_direct_address","requires_context_match","no_personal_data","no_sanctions"):self.assertTrue(stage["constraints"][key])
            for e in stage["entries"]:
                r=e["replies"][0];self.assertEqual(r["response_role"],"assistant_reply")
                self.assertEqual(r["editorial_status"],"candidate_pending_full_semantic_review")
                self.assertIn(r["context"],("direct","private","group_addressed"))
                self.assertEqual(r["audiences"],["impuls"]);self.assertTrue(r["read_only"])
                self.assertGreaterEqual(len(r["text"]),75);self.assertGreaterEqual(len(r["context_note"]),55)
                self.assertIsNone(re.search(r"https?://|t\.me/|@[a-z_]|\d{10,}",r["text"]+r["context_note"],re.I))
    def test_all_prior_stages_no_new_lexical_duplicate(self):
        previous=[s for rec in self.faq["records"] for s in (rec["answer"],*rec["variants"])]
        notes=defaultdict(list)
        for n,stage in enumerate(self.stages,1):
            for e in stage["entries"]:
                for r in e["replies"]:
                    if n>=44:
                        target=norm(r["text"])
                        self.assertNotIn(target,set(map(norm,previous)),r["id"])
                        self.assertTrue(all(jac(r["text"],p)<.70 for p in previous),r["id"])
                        self.assertTrue(all(jac(r["context_note"],p)<.65 for p in notes[e["intent_id"]]),r["id"])
                    previous.append(r["text"]);notes[e["intent_id"]].append(r["context_note"])
    def test_semantic_guardrails(self):
        latest={e["intent_id"]:e for s in self.stages[-3:] for e in s["entries"]}
        self.assertIn("привет",latest["greeting"]["replies"][0]["text"].casefold())
        self.assertIn("раскладк",latest["false_positive"]["replies"][0]["text"].casefold())
        self.assertIn("Пульсы",latest["pulses_not_received"]["replies"][0]["text"])
        self.assertTrue(all(not s["consumer_registered"] for s in self.stages[-3:]))
if __name__=="__main__":unittest.main()
