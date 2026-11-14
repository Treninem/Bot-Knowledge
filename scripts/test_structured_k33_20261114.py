"""K33 candidate preflight; these tests do not certify editorial or consumer behaviour."""
import hashlib,json,re,unicodedata,unittest
from pathlib import Path
R=Path(__file__).resolve().parents[1]
N=R/"staging/ru/structured_information_20261114_delta_k33.json"
P=R/"staging/ru/structured_information_20261114_delta_k32.json"
def norm(x):return " ".join(re.findall(r"[^\W_]+",unicodedata.normalize("NFKC",x).casefold().replace("ё","е")))
class K33(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.d=json.loads(N.read_text(encoding="utf-8"));cls.p=json.loads(P.read_text(encoding="utf-8"));cls.entries=cls.d["entries"]
 def test_lineage(self):
  c=self.d["checkpoint"];self.assertEqual(c["processed_intents"],44)
  self.assertEqual(c["added_candidates"],len(self.entries))
  self.assertEqual(c["remaining_total"],132-len(self.entries))
  self.assertEqual(self.d["prior_stages"][-1],P.relative_to(R).as_posix())
  old={e["intent_id"]:e for e in self.p["entries"][5:]}
  self.assertEqual(len(old),44)
  for e in self.entries:
   self.assertEqual(e["canonical_question"],old[e["intent_id"]]["canonical_question"])
   self.assertEqual((e["published_count"],e["previous_staged_count"],e["total_candidates_with_published"],e["remaining"]),(3,94,98,2))
   self.assertEqual(len(e["replies"]),1)
   self.assertEqual(e["replies"][0]["id"],e["intent_id"]+"_supp_104")
 def test_isolation(self):
  m=json.loads((R/"manifest.json").read_text(encoding="utf-8"))
  known={p["path"]:p["sha256"] for p in m["packs"]}
  self.assertFalse(self.d["consumer_registered"])
  self.assertNotIn(N.relative_to(R).as_posix(),known)
  source=R/self.d["source_pack"]
  self.assertEqual(hashlib.sha256(source.read_bytes()).hexdigest(),known[self.d["source_pack"]])
  self.assertLess(N.stat().st_size,2*1024*1024)
  self.assertEqual(self.d["audiences"],["all_ai_bots"])
  for key in ("read_only","requires_direct_address","requires_context_match","no_personal_data","no_sanctions"):self.assertTrue(self.d["constraints"][key])
 def test_unique_safe(self):
  seen_id=set();seen_text=set();seen_note=set()
  for e in self.entries:
   r=e["replies"][0]
   self.assertNotIn(r["id"],seen_id);seen_id.add(r["id"])
   self.assertNotIn(norm(r["text"]),seen_text);seen_text.add(norm(r["text"]))
   self.assertNotIn((e["intent_id"],norm(r["context_note"])),seen_note);seen_note.add((e["intent_id"],norm(r["context_note"])))
   self.assertGreaterEqual(len(r["text"]),65);self.assertGreaterEqual(len(r["context_note"]),25)
   self.assertEqual(r["language"],"ru");self.assertEqual(r["audiences"],["all_ai_bots"])
   self.assertTrue(r["read_only"]);self.assertEqual(r["context"],"direct")
   self.assertIn("не применять санкции",r["avoid"])
   self.assertNotIn("@",r["text"]+r["context_note"])
 def test_no_automatic_approval(self):
  self.assertEqual(self.d["checkpoint"]["editorial_approved_candidates"],0)
  self.assertEqual(self.d["checkpoint"]["editorial_approved_100_sets"],0)
  self.assertEqual(self.d["checkpoint"]["editorial_rejected_prior_candidates"],5)
if __name__=="__main__":unittest.main()
