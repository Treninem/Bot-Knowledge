"""K92–K93: validate read-only staged replies and cross-stage novelty."""
import hashlib
import json
import re
import unicodedata
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
NEW = ROOT / "staging/ru/structured_information_20261114_delta_k23.json"
OLD = [ROOT / "staging/ru/structured_information_20261111_delta_k.json"]
OLD += [ROOT / f"staging/ru/structured_information_20261113_delta_k{i}.json" for i in range(2, 14)]
OLD += [ROOT / f"staging/ru/structured_information_20261114_delta_k{i}.json" for i in range(14, 23)]
SOURCE = ROOT / "packs/ru/structured_information_qa.json"
WORD = re.compile(r"[^\W_]+", re.UNICODE)

def norm(s):
    return " ".join(WORD.findall(unicodedata.normalize("NFKC", s).casefold().replace("ё", "е")))

def toks(s):
    return set(norm(s).split())

class K23Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.new = json.loads(NEW.read_text(encoding="utf-8"))
        cls.old = [json.loads(p.read_text(encoding="utf-8")) for p in OLD]
        cls.pack = json.loads(SOURCE.read_text(encoding="utf-8"))
        cls.entries = cls.new["entries"]
        cls.replies = [r for e in cls.entries for r in e["replies"]]

    def test_counts_lineage(self):
        d, c = self.new, self.new["checkpoint"]
        self.assertEqual(d["prior_stages"], [p.relative_to(ROOT).as_posix() for p in OLD])
        self.assertEqual((len(self.entries),len(self.replies)), (54,108))
        self.assertEqual((c["published_per_intent"],c["previous_staged_per_intent"],c["added_per_intent"]), (3,82,2))
        self.assertEqual((c["added_candidates"],c["combined_per_intent"],c["remaining_per_intent"],c["remaining_total"]), (108,87,13,702))
        self.assertEqual((c["finished_100"],c["partial_intents"]), (0,54))
        previous = {e["intent_id"]:e for e in self.old[-1]["entries"]}
        self.assertEqual(set(previous), {e["intent_id"] for e in self.entries})
        for e in self.entries:
            self.assertEqual(e["canonical_question"], previous[e["intent_id"]]["canonical_question"])
            self.assertEqual((e["published_count"],e["previous_staged_count"],e["added_candidates"],e["total_candidates_with_published"],e["remaining"]), (3,82,2,87,13))
            self.assertEqual({r["id"] for r in e["replies"]}, {e["intent_id"]+"_supp_92",e["intent_id"]+"_supp_93"})

    def test_registration_and_source_integrity(self):
        d = self.new
        m = json.loads((ROOT/"manifest.json").read_text(encoding="utf-8"))
        registered = {p["path"]:p["sha256"] for p in m["packs"]}
        self.assertFalse(d["consumer_registered"])
        self.assertNotIn(NEW.relative_to(ROOT).as_posix(),registered)
        self.assertEqual(d["source_pack_manifest_sha256"],registered[d["source_pack"]])
        self.assertEqual(hashlib.sha256(SOURCE.read_bytes()).hexdigest(),registered[d["source_pack"]])
        self.assertLess(NEW.stat().st_size,2*1024*1024)
        self.assertEqual(d["audiences"],["all_ai_bots"])
        for flag in ("read_only","requires_direct_address","requires_context_match","no_personal_data","no_sanctions"):
            self.assertTrue(d["constraints"][flag])

    def test_unique_scoped_readonly(self):
        ids,texts,notes=set(),set(),set()
        for r in self.replies:
            for st,v in ((ids,r["id"]),(texts,norm(r["text"])),(notes,norm(r["context_note"]))):
                self.assertNotIn(v,st)
                st.add(v)
            self.assertGreaterEqual(len(r["text"]),65)
            self.assertGreaterEqual(len(r["context_note"]),25)
            self.assertEqual((r["language"],r["context"],r["response_role"]),("ru","direct","assistant_reply"))
            self.assertEqual(r["audiences"],["all_ai_bots"])
            self.assertTrue(r["read_only"])
            self.assertIn("не применять санкции",r["avoid"])
            self.assertNotIn("@",r["text"]+r["context_note"])

    def test_cross_stage_high_lexical_similarity(self):
        earlier=[r["text"] for d in self.old for e in d["entries"] for r in e["replies"]]
        earlier += [t for e in self.pack["records"] for t in [e["answer"],*e["variants"]]]
        norms={norm(t) for t in earlier}
        token_sets=[toks(t) for t in earlier]
        for r in self.replies:
            s,words=norm(r["text"]),toks(r["text"])
            self.assertNotIn(s,norms,r["id"])
            for old in token_sets:
                self.assertLess(len(words & old)/len(words | old),.70,r["id"])
            norms.add(s)
            token_sets.append(words)

if __name__ == "__main__":
    unittest.main()
