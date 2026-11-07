"""T361/T362 tests: exact provenance, lexical uniqueness, approval and privacy."""
import json
import shutil
import tempfile
import unittest
from pathlib import Path
from scripts.colloquial_t305 import ROOT,norm
from scripts.context_t361_t362 import STAGES,Stage,validate_both

class TestT361T362(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.a,cls.b=validate_both()

    def test_approval_and_context(self):
        n=0
        for stage in (self.a,self.b):
            for ident,rows in stage.by_intent.items():
                for x in rows:
                    n+=1
                    kw=dict(approved_reply_ids=frozenset((x["id"],)),audience="all_ai_bots",
                            context=x["context"],addressed=True,local_permission=True)
                    self.assertEqual(stage.select(ident,**kw).text,x["text"])
                    for denied in (dict(addressed=False),dict(local_permission=False),dict(audience="community_bots"),
                                   dict(context="wrong"),dict(approved_reply_ids=frozenset()),
                                   dict(recent_ids=(x["id"],))):
                        self.assertIsNone(stage.select(ident,**(kw|denied)))
        self.assertEqual(n,92)

    def test_unique_and_near_duplicates(self):
        history=[]
        for cfg in STAGES.values():
            original=json.loads((ROOT/cfg["source"]).read_text("utf-8"))
            history += [r for e in original["records"] for r in [e["answer"],*e["variants"]]]
            for path in (*cfg["earlier"],cfg["previous"]):
                part=json.loads((ROOT/path).read_text("utf-8"))
                history += [reply["text"] for entry in part["entries"] for reply in entry["replies"]]
        recent=[x["text"] for s in (self.a,self.b) for rows in s.by_intent.values() for x in rows]
        old,new=[norm(x) for x in history],[norm(x) for x in recent]
        self.assertEqual(len(old),3472)
        self.assertEqual(len(set(old)),3472)
        self.assertEqual(len(new),92)
        self.assertEqual(len(set(new)),92)
        self.assertFalse(set(old)&set(new))
        prior=[set(x.split()) for x in old]
        for i,x in enumerate(new):
            tokens=set(x.split())
            for earlier in (*prior,*(set(s.split()) for s in new[:i])):
                self.assertLess(len(tokens&earlier)/len(tokens|earlier),0.78)

    def test_pins_and_independent_failure(self):
        paths={"manifest.json"}
        for cfg in STAGES.values():
            paths.update((cfg["source"],cfg["stage"],cfg["previous"],*cfg["earlier"]))
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp)
            for p in paths:
                target=root/p
                target.parent.mkdir(parents=True,exist_ok=True)
                shutil.copyfile(ROOT/p,target)
            validate_both(root)
            damaged=root/STAGES["T361"]["previous"]
            damaged.write_bytes(damaged.read_bytes()+b" ")
            with self.assertRaises(ValueError):
                Stage("T361",root)
            self.assertEqual(Stage("T362",root).label,"T362")
            shutil.copyfile(ROOT/STAGES["T361"]["previous"],damaged)
            damaged=root/STAGES["T362"]["stage"]
            payload=json.loads(damaged.read_text("utf-8"))
            payload["entries"][0]["replies"][0]["id"]="wrong_duplicated_id"
            damaged.write_text(json.dumps(payload,ensure_ascii=False),encoding="utf-8")
            with self.assertRaises(ValueError):
                Stage("T362",root)

if __name__=="__main__":
    unittest.main()
