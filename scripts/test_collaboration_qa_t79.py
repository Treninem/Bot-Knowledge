"""T79 collaboration pack regression tests."""
from pathlib import Path
import hashlib, json, re, unittest
ROOT=Path(__file__).resolve().parents[1]
PACK=ROOT/"packs/ru/collaborative_dialogue_qa.json"
def n(s): return re.sub(r"[^\w]+"," ",s.casefold().replace("ё","е")).strip()
class CollaborationT79Tests(unittest.TestCase):
    def test_sha_and_unique_contextual_responses(self):
        payload=PACK.read_bytes(); data=json.loads(payload); manifest=json.loads((ROOT/"manifest.json").read_text(encoding="utf-8"))
        expected=next(x["sha256"] for x in manifest["packs"] if x["path"]=="packs/ru/collaborative_dialogue_qa.json")
        self.assertEqual(hashlib.sha256(payload).hexdigest(),expected)
        self.assertLess(len(payload),1024*1024)
        rows=data["records"][:37]; self.assertGreaterEqual(len(data["records"]),37)
        self.assertEqual(len(set(x["id"] for x in rows)),37)
        questions=set(); answers=set()
        for r in rows:
            self.assertEqual(len(r["aliases"]),2); self.assertEqual(len(r["variants"]),4)
            self.assertEqual(r["audiences"],["all_ai_bots"])
            self.assertEqual(r["constraints"],{"read_only":True,"requires_direct_address":True,"no_personal_data":True})
            for q in [r["question"],*r["aliases"]]: self.assertNotIn(n(q),questions); questions.add(n(q))
            for a in [r["answer"],*r["variants"]]: self.assertNotIn(n(a),answers); answers.add(n(a))
        self.assertEqual(len(answers),185); self.assertEqual(len(questions),111)
    def test_no_existing_qa_key_collisions(self):
        new=json.loads(PACK.read_text(encoding="utf-8"))
        keys={n(q) for r in new["records"] for q in [r["question"],*r["aliases"]]}
        for name in ["dialogue_help_qa","conversation_precision_qa","impuls_help_qa","english_pragmatics_qa"]:
            old=json.loads((ROOT/f"packs/ru/{name}.json").read_text(encoding="utf-8"))
            for r in old["records"]:
                for q in [r["question"],*r.get("aliases",[])]: self.assertNotIn(n(q),keys)
if __name__=="__main__": unittest.main()
