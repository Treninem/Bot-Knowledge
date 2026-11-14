"""K3: 162 RU context-scoped answers (54 intents x suffixes 55-57)."""
import hashlib, json, re, unicodedata, unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
STAGE=ROOT/"staging/ru/structured_information_20261113_delta_k3.json"
K2=ROOT/"staging/ru/structured_information_20261113_delta_k2.json"
K=ROOT/"staging/ru/structured_information_20261111_delta_k.json"
PACK=ROOT/"packs/ru/structured_information_qa.json"
WORDS=re.compile(r"[^\W_]+",re.UNICODE)
def normalize(s):
    return " ".join(WORDS.findall(unicodedata.normalize("NFKC",s).casefold().replace("ё","е")))
def tok(s): return set(normalize(s).split())
class K3StagingTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data=json.loads(STAGE.read_text(encoding="utf-8"))
        cls.k2=json.loads(K2.read_text(encoding="utf-8"))
        cls.k=json.loads(K.read_text(encoding="utf-8"))
        cls.entries=cls.data["entries"]
        cls.replies=[r for e in cls.entries for r in e["replies"]]
    def test_unregistered_and_checksum(self):
        m=json.loads((ROOT/"manifest.json").read_text(encoding="utf-8"))
        registered={p["path"]:p["sha256"] for p in m["packs"]}
        self.assertFalse(self.data["consumer_registered"])
        self.assertNotIn(STAGE.relative_to(ROOT).as_posix(),registered)
        self.assertEqual(hashlib.sha256(PACK.read_bytes()).hexdigest(),self.data["source_pack_manifest_sha256"])
        self.assertEqual(registered[self.data["source_pack"]],self.data["source_pack_manifest_sha256"])
        self.assertLessEqual(STAGE.stat().st_size,2*1024*1024)
        self.assertEqual(self.data["audiences"],["all_ai_bots"])
        self.assertTrue(all(self.data["constraints"][x] for x in
            ("read_only","requires_direct_address","requires_context_match","no_personal_data","no_sanctions")))
    def test_checkpoint_and_stable_ids(self):
        self.assertEqual((len(self.entries),len(self.replies)),(54,162))
        cp=self.data["checkpoint"]
        self.assertEqual((cp["processed_intents"],cp["added_candidates"],cp["added_per_intent"]),(54,162,3))
        self.assertEqual((cp["combined_per_intent"],cp["remaining_per_intent"],cp["remaining_total"],cp["finished_100"],cp["partial_intents"]),(51,49,2646,0,54))
        previous={e["intent_id"]:e for e in self.k2["entries"]}
        self.assertEqual(set(previous),{e["intent_id"] for e in self.entries})
        for e in self.entries:
            old=previous[e["intent_id"]]
            self.assertEqual(e["canonical_question"],old["canonical_question"])
            self.assertEqual((e["published_count"],e["previous_staged_count"],e["added_candidates"],e["total_candidates_with_published"],e["remaining"],e["target"]),(3,45,3,51,49,100))
            self.assertEqual([r["id"] for r in e["replies"]],[e["intent_id"]+"_supp_55",e["intent_id"]+"_supp_56",e["intent_id"]+"_supp_57"])
    def test_safe_unique_contexts(self):
        ids=set();texts=set();notes=set()
        for r in self.replies:
            n=normalize(r["text"]); c=normalize(r["context_note"])
            self.assertNotIn(r["id"],ids);self.assertNotIn(n,texts);self.assertNotIn(c,notes)
            ids.add(r["id"]);texts.add(n);notes.add(c)
            self.assertTrue(len(r["text"])>=55 and len(r["context_note"])>=25)
            self.assertEqual((r["language"],r["audiences"],r["context"],r["response_role"],r["read_only"]),("ru",["all_ai_bots"],"direct","assistant_reply",True))
            self.assertFalse(re.search(r"[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}",r["text"]+" "+r["context_note"]))
            self.assertFalse(any(x in n for x in ("я забаню","я удалил сообщение","я выдал мут","я сохранил твои данные")))
    def test_cross_stage_lexical_uniqueness(self):
        earlier=[r["text"] for p in (self.k,self.k2) for e in p["entries"] for r in e["replies"]]
        pack=json.loads(PACK.read_text(encoding="utf-8"))
        earlier.extend(t for record in pack["records"] for t in [record["answer"],*record["variants"]])
        norms=set(map(normalize,earlier));tokens=list(map(tok,earlier))
        for r in self.replies:
            n=normalize(r["text"]);self.assertNotIn(n,norms,r["id"])
            a=tok(r["text"])
            for b in tokens: self.assertLess(len(a&b)/len(a|b),.70,r["id"])
            norms.add(n);tokens.append(a)
if __name__=="__main__": unittest.main()
