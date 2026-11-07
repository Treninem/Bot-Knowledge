"""T313/T314 exact-head scope and immutable parent tests."""
import unittest,shutil,tempfile
from pathlib import Path
from scripts.colloquial_t305 import ROOT
from scripts.context_t313_t314 import Stage,C,validate_both
class TestContext(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.a,cls.b=validate_both()
 def test_all_92_choices_are_opt_in(self):
  num=0
  for obj in (self.a,self.b):
   for intent,items in obj.by_intent.items():
    for x in items:
     num+=1
     opts=dict(approved_reply_ids=frozenset([x["id"]]),audience="all_ai_bots",context=x["context"],addressed=True,local_permission=True)
     self.assertEqual(obj.select(intent,**opts).text,x["text"])
     for change in (dict(addressed=False),dict(local_permission=False),dict(audience="community_bots"),
                   dict(context="unknown"),dict(approved_reply_ids=frozenset()),
                   dict(approved_reply_ids=[x["id"]]),dict(recent_ids=(x["id"],))):
      self.assertIsNone(obj.select(intent,**(opts|change)))
     self.assertIsNone(obj.select("unknown",**opts))
  self.assertEqual(num,92)
 def test_parent_mutation_denied(self):
  paths={"manifest.json"}
  for c in C.values():paths.update([c["source"],c["previous"],c["stage"],*c["earlier"]])
  with tempfile.TemporaryDirectory() as d:
   root=Path(d)
   for p in paths:
    x=root/p;x.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(ROOT/p,x)
   self.assertEqual(len(validate_both(root)),2)
   p=root/C["T313"]["previous"];p.write_bytes(p.read_bytes()+b" ")
   with self.assertRaises(ValueError):Stage("T313",root)
   self.assertEqual(Stage("T314",root).label,"T314")
if __name__=="__main__":unittest.main()
