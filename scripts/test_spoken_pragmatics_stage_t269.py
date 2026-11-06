"""T269: 144 contextual RU replies, stable source SHA and fail-closed approval."""
import hashlib, json, re, unittest, unicodedata
from pathlib import Path
from scripts.staged_context_selector import StagedContextSelector
ROOT=Path(__file__).resolve().parents[1]
STAGE="staging/ru/spoken_pragmatics_t251_context_pool.json"
SOURCE="packs/ru/spoken_pragmatics_qa.json"
SECRET=re.compile(r"(?i)(ghp_[a-z0-9]{12,}|sk-[a-z0-9]{12,}|bot_token|chat_id|user_id|https://t\\.me/)")
def norm(v):
    v=unicodedata.normalize("NFKC",v).casefold().replace("ё","е")
    return " ".join("".join(" " if unicodedata.category(ch)[0] in {"P","S"} else ch for ch in v).split())
def jaccard(a,b):
    x,y=set(norm(a).split()),set(norm(b).split())
    return len(x&y)/len(x|y)
class TestT269(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.stage=json.loads((ROOT/STAGE).read_text("utf-8"))
        cls.source=json.loads((ROOT/SOURCE).read_text("utf-8"))
        cls.selector=StagedContextSelector(ROOT,STAGE)
    def test_inventory_sha_privacy_context_and_distinctness(self):
        cp=self.stage["checkpoint"]
        keys=("stage_id","updated_in","processed_intents","registered_count","prior_accepted","added_in_current","added_candidates","previous_per_intent","now_per_intent","remaining_per_intent","remaining_total","partial_intents","finished_100","rejected")
        self.assertEqual(tuple(cp[k] for k in keys),("T269","T269",24,216,1080,144,1224,54,60,40,960,24,0,0))
        self.assertIs(self.stage["consumer_registered"],False)
        registry={p["path"]:p["sha256"] for p in json.loads((ROOT/"manifest.json").read_text("utf-8"))["packs"]}
        self.assertNotIn(STAGE,registry)
        self.assertEqual(hashlib.sha256((ROOT/SOURCE).read_bytes()).hexdigest(),registry[SOURCE])
        self.assertEqual(self.stage["source_pack_manifest_sha256"],registry[SOURCE])
        origins={r["id"]:r for r in self.source["records"]}
        self.assertEqual((len(origins),len(self.stage["entries"])),(24,24))
        texts=set()
        for r in origins.values():
            for line in (r["answer"],*r["variants"]):
                key=norm(line);self.assertNotIn(key,texts);texts.add(key)
        ids=set();count=0
        for e in self.stage["entries"]:
            src=origins[e["intent_id"]]
            self.assertEqual(e["question"],src["question"])
            self.assertEqual((e["registered_reply_count"],e["staged_reply_count"],len(e["replies"])),(9,51,51))
            previous=[src["answer"],*src["variants"]];notes=set()
            for i,r in enumerate(e["replies"]):
                self.assertNotIn(r["id"],ids);ids.add(r["id"])
                key=norm(r["text"]);self.assertNotIn(key,texts);texts.add(key)
                note=norm(r["context_note"]);self.assertTrue(note);self.assertNotIn(note,notes);notes.add(note)
                self.assertEqual((r["language"],r["style"],r["audiences"],r["read_only"]),("ru","neutral",["all_ai_bots"],True))
                self.assertIn(r["context"],("direct","private","group_addressed"))
                self.assertTrue(r["avoid"].strip());self.assertIsNone(SECRET.search(r["text"]))
                if i>=45:
                    self.assertEqual(r["id"],f'{e["intent_id"]}_t269_{i-44:02d}')
                    self.assertLess(max(jaccard(r["text"],p) for p in previous),.78)
                    count+=1
                previous.append(r["text"])
        self.assertEqual((count,len(ids),len(texts)),(144,1224,1440))
    def test_explicit_approval_and_context_required(self):
        for e in self.stage["entries"]:
            for r in e["replies"][45:]:
                args=dict(approved_reply_ids=frozenset({r["id"]}),audience="all_ai_bots",context=r["context"],addressed=True,local_permission=True)
                selected=self.selector.select(e["intent_id"],**args)
                self.assertIsNotNone(selected);self.assertEqual((selected.id,selected.text),(r["id"],r["text"]))
                for denied in ({"approved_reply_ids":frozenset()},{"audience":"community_bots"},{"context":"unknown"},{"addressed":False},{"local_permission":False},{"recent_ids":(r["id"],)}):
                    self.assertIsNone(self.selector.select(e["intent_id"],**(args|denied)))
if __name__=="__main__":unittest.main()
