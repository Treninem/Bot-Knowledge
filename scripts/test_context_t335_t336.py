"""T335/T336 integration, parent binding, duplicate and approval checks."""
import json
import shutil
import tempfile
import unittest
from pathlib import Path
from scripts.colloquial_t305 import ROOT, norm
from scripts.context_t335_t336 import STAGES, Stage, validate_both

class TestT335T336(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.a,cls.b=validate_both()

    def test_every_reply_requires_explicit_approval_and_scope(self):
        count=0
        for stage in (self.a,self.b):
            for ident, items in stage.by_intent.items():
                for x in items:
                    count+=1
                    kw=dict(approved_reply_ids=frozenset([x["id"]]),audience="all_ai_bots",context=x["context"],addressed=True,local_permission=True)
                    self.assertEqual(stage.select(ident,**kw).text,x["text"])
                    for changed in (dict(addressed=False),dict(local_permission=False),dict(audience="community_bots"),dict(context="unknown"),dict(recent_ids=(x["id"],)),dict(approved_reply_ids=frozenset())):
                        self.assertIsNone(stage.select(ident,**(kw|changed)))
        self.assertEqual(count,92)

    def test_no_lexical_near_duplication_against_history(self):
        older=[]
        for cfg in STAGES.values():
            source=json.loads((ROOT/cfg["source"]).read_text("utf-8"))
            older += [t for row in source["records"] for t in [row["answer"],*row["variants"]]]
            for path in (*cfg["earlier"],cfg["previous"]):
                stage=json.loads((ROOT/path).read_text("utf-8"))
                older += [x["text"] for row in stage["entries"] for x in row["replies"]]
        fresh=[x["text"] for stage in (self.a,self.b) for rows in stage.by_intent.values() for x in rows]
        prior=[norm(x) for x in older]
        new=[norm(x) for x in fresh]
        self.assertEqual(len(prior),2184)
        self.assertEqual(len(new),92)
        self.assertEqual(len(set(prior)),2184)
        self.assertEqual(len(set(new)),92)
        self.assertFalse(set(prior)&set(new))
        def similarity(a,b):
            x,y=set(a.split()),set(b.split())
            return len(x&y)/len(x|y)
        for i,x in enumerate(new):
            for y in (*prior,*new[:i]):
                self.assertLess(similarity(x,y),0.78)

    def test_source_and_parent_integrity(self):
        paths={"manifest.json"}
        for c in STAGES.values():
            paths.update((c["source"],c["stage"],c["previous"],*c["earlier"]))
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp)
            for p in paths:
                dest=root/p
                dest.parent.mkdir(parents=True,exist_ok=True)
                shutil.copyfile(ROOT/p,dest)
            self.assertEqual(len(validate_both(root)),2)
            parent=root/STAGES["T335"]["previous"]
            parent.write_bytes(parent.read_bytes()+b" ")
            with self.assertRaises(ValueError):
                Stage("T335",root)
            self.assertEqual(Stage("T336",root).label,"T336")
            shutil.copyfile(ROOT/STAGES["T335"]["previous"],parent)
            src=root/STAGES["T336"]["source"]
            src.write_bytes(src.read_bytes()+b" ")
            with self.assertRaises(ValueError):
                Stage("T336",root)

if __name__=="__main__":
    unittest.main()
