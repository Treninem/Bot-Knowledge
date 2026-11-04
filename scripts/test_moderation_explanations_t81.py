"""T81 moderation language only, no sanctions or cross-audience leak."""
import hashlib,json,re,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; PACK=ROOT/"packs/ru/moderation_explanations_qa.json"
def norm(s):return re.sub(r"[^\w]+"," ",s.casefold().replace("ё","е")).strip()
class ModerateT81(unittest.TestCase):
    def test_integrity_scope_and_variants(self):
        p=PACK.read_bytes();d=json.loads(p); m=json.loads((ROOT/"manifest.json").read_text(encoding="utf-8"))
        self.assertEqual(hashlib.sha256(p).hexdigest(),next(x["sha256"] for x in m["packs"] if x["path"]=="packs/ru/moderation_explanations_qa.json"))
        self.assertLess(len(p),1024*1024);self.assertEqual(len(d["records"]),30)
        self.assertEqual(d["catalog"]["audiences"],["chat_moderators","community_bots"])
        qs=set();ans=set();ids=set()
        for r in d["records"]:
            self.assertNotIn(r["id"],ids);ids.add(r["id"])
            self.assertEqual(r["audiences"],["chat_moderators","community_bots"])
            self.assertNotIn("all_ai_bots",r["audiences"])
            self.assertTrue(all(r["constraints"].values()))
            self.assertFalse(set(r)&{"action","ban","mute","sanction","execute"})
            self.assertEqual((len(r["aliases"]),len(r["variants"])),(2,2))
            for q in [r["question"],*r["aliases"]]:self.assertNotIn(norm(q),qs);qs.add(norm(q))
            for a in [r["answer"],*r["variants"]]:self.assertNotIn(norm(a),ans);ans.add(norm(a))
        self.assertEqual((len(qs),len(ans)),(90,90))
    def test_no_existing_qa_keys(self):
        new=json.loads(PACK.read_text(encoding="utf-8")); keys={norm(q) for r in new["records"] for q in [r["question"],*r["aliases"]]}
        for name in ("dialogue_help_qa","impuls_help_qa","conversation_precision_qa","collaborative_dialogue_qa","english_pragmatics_qa","english_conversation_nuance_qa"):
            old=json.loads((ROOT/"packs/ru"/(name+".json")).read_text(encoding="utf-8"))
            for r in old["records"]:
                for q in [r["question"],*r.get("aliases",[])]:self.assertNotIn(norm(q),keys)
if __name__=="__main__":unittest.main()
