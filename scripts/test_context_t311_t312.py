"""Exact-head source/selection regression for T311/T312."""
import shutil,tempfile,unittest
from pathlib import Path
from scripts.colloquial_t305 import ROOT
from scripts.context_t311_t312 import CONFIG,Stage,validate_both
class TestT311T312(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.a,cls.b=validate_both()
 def test_138_replies_are_explicit_only(self):
  count=0
  for model in (self.a,self.b):
   self.assertEqual(len(model.by_intent),CONFIG[model.label]["intents"])
   for intent,items in model.by_intent.items():
    for item in items:
     count+=1
     k=dict(approved_reply_ids=frozenset([item["id"]]),audience="all_ai_bots",context=item["context"],addressed=True,local_permission=True)
     self.assertEqual(model.select(intent,**k).text,item["text"])
     for change in (dict(addressed=False),dict(local_permission=False),
                    dict(audience="community_bots"),dict(context="unknown"),
                    dict(approved_reply_ids=frozenset()),dict(approved_reply_ids=[item["id"]]),
                    dict(recent_ids=(item["id"],))):
      self.assertIsNone(model.select(intent,**(k|change)))
     self.assertIsNone(model.select("unknown",**k))
  self.assertEqual(count,138)
 def test_parent_change_fails_closed(self):
  paths={"manifest.json"}
  for c in CONFIG.values():paths.update([c["source"],c["previous"],c["stage"],*c["earlier"]])
  with tempfile.TemporaryDirectory() as d:
   root=Path(d)
   for p in paths:
    dst=root/p;dst.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(ROOT/p,dst)
   self.assertEqual(len(validate_both(root)),2)
   t=root/CONFIG["T311"]["previous"];t.write_bytes(t.read_bytes()+b" ")
   with self.assertRaises(ValueError):Stage("T311",root)
   self.assertEqual(Stage("T312",root).label,"T312")
if __name__=="__main__":unittest.main()
