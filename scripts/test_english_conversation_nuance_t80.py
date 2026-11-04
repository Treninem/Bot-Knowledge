"""T80 English conversational nuance regression."""
import json, hashlib, re, unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
PACK=ROOT/"packs/ru/english_conversation_nuance_qa.json"
def norm(s): return re.sub(r"[^\w]+"," ",s.casefold()).strip()
class EnglishNuanceT80(unittest.TestCase):
    def test_integrity_and_scope(self):
        payload=PACK.read_bytes(); data=json.loads(payload); manifest=json.loads((ROOT/"manifest.json").read_text(encoding="utf-8"))
        expected=next(p["sha256"] for p in manifest["packs"] if p["path"]=="packs/ru/english_conversation_nuance_qa.json")
        self.assertEqual(hashlib.sha256(payload).hexdigest(),expected); self.assertLess(len(payload),1024*1024)
        rows=data["records"]; self.assertEqual(len(rows),32); self.assertEqual(len({r["id"] for r in rows}),32)
        qs=set(); answers=set()
        for r in rows:
            self.assertEqual((len(r["aliases"]),len(r["variants"])),(2,2))
            self.assertEqual(r["language"],"en"); self.assertEqual(r["audiences"],["all_ai_bots"])
            self.assertTrue(all(r["constraints"].values()))
            for q in [r["question"],*r["aliases"]]: self.assertNotIn(norm(q),qs); qs.add(norm(q))
            for answer in [r["answer"],*r["variants"]]: self.assertNotIn(norm(answer),answers); answers.add(norm(answer))
        self.assertEqual((len(qs),len(answers)),(96,96))
    def test_cross_pack_queries(self):
        data=json.loads(PACK.read_text(encoding="utf-8")); qs={norm(q) for r in data["records"] for q in [r["question"],*r["aliases"]]}
        for f in ["english_pragmatics_qa.json","collaborative_dialogue_qa.json","dialogue_help_qa.json","conversation_precision_qa.json","impuls_help_qa.json"]:
            p=json.loads((ROOT/"packs/ru"/f).read_text(encoding="utf-8"))
            for r in p["records"]:
                for q in [r["question"],*r.get("aliases",[])]: self.assertNotIn(norm(q),qs)
if __name__=="__main__": unittest.main()
