"""Regression guards for synthetic context-specific conversation answers."""
import json, re, unicodedata, unittest
from pathlib import Path
R=Path(__file__).resolve().parents[1]
P=R/"staging/ru/conversation_nuance_20261112.json"
BASE=["packs/ru/response_boundaries_qa.json","packs/ru/practical_recovery_qa.json","packs/ru/conversation_followthrough_qa.json","packs/ru/optional_humor_qa.json"]
def norm(s):
 s=unicodedata.normalize("NFKC",s).casefold().replace("ё","е")
 return " ".join(re.findall(r"[^\\W_]+",s,re.UNICODE))
class TestContextualConversation(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.data=json.loads(P.read_text("utf-8"))
  cls.entries=cls.data["entries"]
  cls.replies=[r for e in cls.entries for r in e["replies"]]
 def test_guardrails(self):
  d=self.data
  self.assertFalse(d["consumer_registered"])
  self.assertEqual(d["audiences"],["all_ai_bots"])
  self.assertTrue(all(d["constraints"].values()))
  self.assertEqual((len(self.entries),len(self.replies)),(20,100))
  self.assertEqual(d["checkpoint"]["remaining_total"],1900)
  for e in self.entries:
   self.assertEqual(e["remaining"],95)
   self.assertEqual(e["accepted_staged"],5)
   self.assertEqual(e["target"],100)
  for r in self.replies:
   self.assertTrue(r["read_only"])
   self.assertTrue(r["selection_conditions"]["requires_context_match"])
   self.assertTrue(r["selection_conditions"]["no_sanctions"])
   self.assertGreater(len(r["context_note"]),25)
   self.assertGreater(len(r["text"]),36)
 def test_normalized_uniqueness(self):
  self.assertEqual(len(set(r["id"] for r in self.replies)),len(self.replies))
  for field in ("text","context_note"):
   self.assertEqual(len(set(norm(r[field]) for r in self.replies)),len(self.replies))
  historical=[]
  for file in BASE:
   pkg=json.loads((R/file).read_text("utf-8"))
   for rec in pkg["records"]:
    historical.extend([rec["answer"],*rec.get("variants",[])])
  historic=set(map(norm,historical))
  self.assertTrue(all(norm(r["text"]) not in historic for r in self.replies))
 def test_protection(self):
  mail=re.compile(r"[\\w.+-]+@[\\w.-]+\\.[A-Za-z]{2,}")
  self.assertTrue(all(mail.search(r["text"]+" "+r["context_note"]) is None for r in self.replies))
  for e in self.entries:
   for r in e["replies"]:
    self.assertTrue(r["selection_conditions"]["humor_opt_in"] if e["intent_id"].endswith(("light_joke","kind_tease","safe_sarcasm")) else not r["selection_conditions"]["humor_opt_in"])
if __name__=="__main__":unittest.main()
