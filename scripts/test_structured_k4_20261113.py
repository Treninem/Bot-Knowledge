"""K4: staged original RU contextual answers; dynamic suffix and counts."""
import json, hashlib, re, unicodedata, unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
STAGE=ROOT/"staging/ru/structured_information_20261113_delta_k4.json"
K3=ROOT/"staging/ru/structured_information_20261113_delta_k3.json"
K2=ROOT/"staging/ru/structured_information_20261113_delta_k2.json"
K=ROOT/"staging/ru/structured_information_20261111_delta_k.json"
PACK=ROOT/"packs/ru/structured_information_qa.json"
WORDS=re.compile(r"[^\W_]+",re.UNICODE)
def normal(s): return " ".join(WORDS.findall(unicodedata.normalize("NFKC",s).casefold().replace("ё","е")))
def tokens(s): return set(normal(s).split())
class K4Test(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data=json.loads(STAGE.read_text(encoding="utf-8"))
        cls.k3=json.loads(K3.read_text(encoding="utf-8"))
        cls.entries=cls.data["entries"]
        cls.answers=[r for e in cls.entries for r in e["replies"]]
    def test_registration_and_source(self):
        manifest=json.loads((ROOT/"manifest.json").read_text(encoding="utf-8"))
        registered={p["path"]:p["sha256"] for p in manifest["packs"]}
        self.assertFalse(self.data["consumer_registered"])
        self.assertNotIn(STAGE.relative_to(ROOT).as_posix(),registered)
        self.assertEqual(hashlib.sha256(PACK.read_bytes()).hexdigest(),self.data["source_pack_manifest_sha256"])
        self.assertEqual(registered[self.data["source_pack"]],self.data["source_pack_manifest_sha256"])
        self.assertLessEqual(STAGE.stat().st_size,2*1024*1024)
        self.assertTrue(all(self.data["constraints"][k] for k in ("read_only","requires_direct_address","requires_context_match","no_personal_data","no_sanctions")))
    def test_counts_and_stable_intents(self):
        cp=self.data["checkpoint"]
        self.assertEqual(len(self.entries),54)
        self.assertEqual(len(self.answers),cp["added_candidates"])
        old={e["intent_id"]:e for e in self.k3["entries"]}
        self.assertEqual(set(old),{e["intent_id"] for e in self.entries})
        for e in self.entries:
            self.assertEqual(e["canonical_question"],old[e["intent_id"]]["canonical_question"])
            self.assertEqual(e["added_candidates"],len(e["replies"]))
            self.assertEqual(e["previous_staged_count"],48)
            self.assertEqual(e["total_candidates_with_published"],3+48+len(e["replies"]))
            self.assertEqual(e["remaining"],100-e["total_candidates_with_published"])
            self.assertEqual([r["id"] for r in e["replies"]],[e["intent_id"]+"_supp_"+str(i) for i in range(58,58+len(e["replies"]))])
        self.assertEqual(cp["combined_per_intent"]+cp["remaining_per_intent"],100)
        self.assertEqual(cp["remaining_total"],54*cp["remaining_per_intent"])
    def test_unique_safe_and_cross_pack(self):
        prior=[]
        for path in (K,K2,K3):
            obj=json.loads(path.read_text(encoding="utf-8"))
            prior.extend(r["text"] for e in obj["entries"] for r in e["replies"])
        pack=json.loads(PACK.read_text(encoding="utf-8"))
        prior.extend(t for rec in pack["records"] for t in [rec["answer"],*rec["variants"]])
        norms=set(map(normal,prior));sets=list(map(tokens,prior))
        ids=set();notes=set()
        for r in self.answers:
            n=normal(r["text"]); c=normal(r["context_note"]); t=tokens(r["text"])
            self.assertNotIn(r["id"],ids)
            self.assertNotIn(n,norms,r["id"])
            self.assertNotIn(c,notes)
            ids.add(r["id"]);notes.add(c)
            self.assertGreaterEqual(len(r["text"]),55)
            self.assertGreaterEqual(len(r["context_note"]),25)
            self.assertEqual((r["language"],r["context"],r["audiences"],r["response_role"],r["read_only"]),("ru","direct",["all_ai_bots"],"assistant_reply",True))
            self.assertFalse(re.search(r"[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}",r["text"]+" "+r["context_note"]))
            for old in sets: self.assertLess(len(t & old)/len(t | old),.70,r["id"])
            norms.add(n);sets.append(t)
if __name__=="__main__": unittest.main()
