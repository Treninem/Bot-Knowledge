"""Validate synthetic K79-K80 with original registered pack and all previous K stages."""
import json, re, hashlib, unittest, unicodedata
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
STAGE=ROOT/"staging/ru/structured_information_20261114_delta_k15.json"
PRIOR=["staging/ru/structured_information_20261111_delta_k.json"]+[f"staging/ru/structured_information_20261113_delta_k{i}.json" for i in range(2,14)]+["staging/ru/structured_information_20261114_delta_k14.json"]
PACK=ROOT/"packs/ru/structured_information_qa.json"
WORDS=re.compile(r"[^\W_]+",re.UNICODE)
def norm(x): return " ".join(WORDS.findall(unicodedata.normalize("NFKC",x).casefold().replace("ё","е")))
def tok(x): return set(norm(x).split())
class K15Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.d=json.loads(STAGE.read_text(encoding="utf-8"))
        cls.old=[json.loads((ROOT/p).read_text(encoding="utf-8")) for p in PRIOR]
        cls.pack=json.loads(PACK.read_text(encoding="utf-8"))
        cls.r=[r for e in cls.d["entries"] for r in e["replies"]]
    def test_counts_ids_lineage(self):
        d=self.d;c=d["checkpoint"]
        self.assertEqual(d["prior_stages"],PRIOR)
        self.assertEqual(len(d["entries"]),54);self.assertEqual(len(self.r),108)
        for field,n in {"processed_intents":54,"published_per_intent":3,"previous_staged_per_intent":69,"added_per_intent":2,"added_candidates":108,"combined_per_intent":74,"remaining_per_intent":26,"remaining_total":1404,"finished_100":0,"partial_intents":54}.items(): self.assertEqual(c[field],n)
        old={e["intent_id"]:e for e in self.old[-1]["entries"]}
        self.assertEqual(set(old),{e["intent_id"] for e in d["entries"]})
        for e in d["entries"]:
            self.assertEqual(e["canonical_question"],old[e["intent_id"]]["canonical_question"])
            self.assertEqual((e["published_count"],e["previous_staged_count"],e["added_candidates"],e["total_candidates_with_published"],e["remaining"]),(3,69,2,74,26))
            self.assertEqual({r["id"] for r in e["replies"]},{e["intent_id"]+"_supp_79",e["intent_id"]+"_supp_80"})
    def test_safety_source_hash(self):
        d=self.d;m=json.loads((ROOT/"manifest.json").read_text(encoding="utf-8"))
        registered={p["path"]:p["sha256"] for p in m["packs"]}
        self.assertFalse(d["consumer_registered"])
        self.assertNotIn(STAGE.relative_to(ROOT).as_posix(),registered)
        self.assertEqual(d["source_pack_manifest_sha256"],registered[d["source_pack"]])
        self.assertEqual(hashlib.sha256(PACK.read_bytes()).hexdigest(),registered[d["source_pack"]])
        self.assertLess(STAGE.stat().st_size,2*1024*1024)
        self.assertEqual(d["audiences"],["all_ai_bots"])
        for field in ("read_only","requires_direct_address","requires_context_match","no_personal_data","no_sanctions"):self.assertTrue(d["constraints"][field])
    def test_unique_context_privacy(self):
        ids=set();texts=set();notes=set()
        for r in self.r:
            self.assertNotIn(r["id"],ids);ids.add(r["id"])
            self.assertNotIn(norm(r["text"]),texts);texts.add(norm(r["text"]))
            self.assertNotIn(norm(r["context_note"]),notes);notes.add(norm(r["context_note"]))
            self.assertGreaterEqual(len(r["text"]),65);self.assertGreaterEqual(len(r["context_note"]),25)
            self.assertEqual(r["language"],"ru");self.assertEqual(r["context"],"direct")
            self.assertEqual(r["audiences"],["all_ai_bots"]);self.assertEqual(r["response_role"],"assistant_reply")
            self.assertTrue(r["read_only"]);self.assertIn("не применять санкции",r["avoid"])
            self.assertNotIn("@",r["text"]+r["context_note"])
    def test_no_repeats(self):
        prev=[r["text"] for s in self.old for e in s["entries"] for r in e["replies"]]
        prev += [x for e in self.pack["records"] for x in [e["answer"],*e["variants"]]]
        norms={norm(x) for x in prev};tokens=[tok(x) for x in prev]
        for r in self.r:
            n=norm(r["text"]);t=tok(r["text"])
            self.assertNotIn(n,norms,r["id"])
            for u in tokens:self.assertLess(len(t&u)/len(t|u),0.70,r["id"])
            norms.add(n);tokens.append(t)
if __name__=="__main__":unittest.main()
