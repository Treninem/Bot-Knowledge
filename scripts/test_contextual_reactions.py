"""Opt-in social response catalogue regression tests."""
import hashlib, json, tempfile, unittest
from pathlib import Path
from scripts.contextual_reactions import ContextualReactions, ROOT, PACK, norm
class SocialResponseTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.obj=ContextualReactions();cls.payload=(ROOT/PACK).read_bytes()
        cls.source=json.loads(cls.payload)
        cls.manifest=json.loads((ROOT/"manifest.json").read_text(encoding="utf-8"))
    def query(self,txt,*,intent="thanks",**kw):
        args={"addressed":True,"local_permission":True};args.update(kw)
        return self.obj.reply(txt,intent=intent,**args)
    def test_registered_SHA_legacy_counts_and_uniqueness(self):
        paths=[x for x in self.manifest["packs"] if x["path"]==PACK]
        self.assertEqual(len(paths),1)
        self.assertEqual(paths[0]["sha256"],hashlib.sha256(self.payload).hexdigest())
        self.assertEqual(len(self.source["reactions"]["greeting"]),100)
        self.assertEqual(self.source["reactions"]["thanks"],["Пожалуйста.","Рад, что пригодилось."])
        self.assertEqual(self.source["reactions"]["farewell"],["До встречи.","Хорошо, до связи."])
        values=[v for intent in self.source["contextual_reactions"]["intents"].values() for g in intent["contexts"].values() for v in g]
        self.assertEqual(len(values),136);self.assertEqual(len(set(map(norm,values))),136)
        for intent,group in self.source["contextual_reactions"]["intents"].items():
            self.assertEqual(len(group["contexts"]),17)
            self.assertEqual(set(group["context_conditions"]),set(group["contexts"]))
            self.assertEqual(sum(map(len,group["contexts"].values()))+len(self.source["reactions"][intent]),70)
    def test_scopes_and_negative_inputs(self):
        self.assertEqual(self.query("спасибо")["status"],"ok")
        self.assertEqual(self.query("до встречи",intent="farewell")["status"],"ok")
        for phrase in ("спасибо?", "не спасибо", "«спасибо»", "он сказал спасибо",
                       "спасибо, а как настроить?", "спасибо https://example.org", "спасибо @bot"):
            self.assertEqual(self.query(phrase)["status"],"no_match")
        self.assertEqual(self.query("спасибо",intent="farewell")["status"],"no_match")
        for args,status in (({"addressed":False},"not_addressed"),({"local_permission":False},"not_authorized"),
                             ({"sensitive":True},"suppressed"),({"silence_requested":True},"suppressed"),
                             ({"language":"en"},"wrong_language")):
            self.assertEqual(self.query("спасибо",**args)["status"],status)
    def test_context_reachability_and_local_repeat(self):
        for intent,entry in self.source["contextual_reactions"]["intents"].items():
            phrase=entry["accepted_inputs"][0]
            for context,replies in entry["contexts"].items():
                for i,expected in enumerate(replies):
                    self.assertEqual(self.query(phrase,intent=intent,context=context,recent=replies[:i])["text"],expected)
                self.assertEqual(self.query(phrase,intent=intent,context=context,recent=replies)["status"],"repeat_suppressed")
        self.assertEqual(self.query("спасибо")["context"],"neutral")
    def test_rejected_parameters_and_sha_change(self):
        for opts in ({"intent":"other"},{"context":"not_a_group"},{"audience":"chat_moderators"},
                     {"addressed":"yes"},{"recent":"a string"},{"recent":["x"]*129}):
            with self.assertRaises(ValueError): self.query("спасибо",**opts)
        with tempfile.TemporaryDirectory() as d:
            folder=Path(d);(folder/"packs/ru").mkdir(parents=True)
            (folder/PACK).write_bytes(self.payload+b" ")
            (folder/"manifest.json").write_text(json.dumps(self.manifest),encoding="utf-8")
            with self.assertRaises(ValueError): ContextualReactions(folder)
            (folder/PACK).write_bytes(self.payload)
            other=ContextualReactions(folder)
            self.assertEqual(other.snapshot_key,self.obj.snapshot_key)
if __name__=="__main__": unittest.main()
