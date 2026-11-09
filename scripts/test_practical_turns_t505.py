"""T505: independently authored practical RU continuation, opt-in only."""
import hashlib, json, re, unicodedata, unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/"packs/ru/dialogue.json"
STAGE=ROOT/"staging/ru/practical_turns_t505_context_pool.json"
PREVIOUS=[ROOT/"staging/ru/practical_turns_t503_context_pool.json", ROOT/"staging/ru/practical_turns_t504_context_pool.json"]
def norm(t):
    return " ".join(re.findall(r"\w+",unicodedata.normalize("NFKC",t).lower().replace("ё","е")))
class T505(unittest.TestCase):
    def test_integrity_lineage_and_audience(self):
        d=json.loads(STAGE.read_text("utf-8"))
        old=[json.loads(p.read_text("utf-8")) for p in PREVIOUS]
        actual=hashlib.sha256(SOURCE.read_bytes()).hexdigest()
        manifest=json.loads((ROOT/"manifest.json").read_text("utf-8"))
        self.assertIn({"path":"packs/ru/dialogue.json","sha256":actual},manifest["packs"])
        self.assertEqual(d["source_pack_manifest_sha256"],actual)
        self.assertEqual(d["source_pack_blob_sha"],old[1]["source_pack_blob_sha"])
        self.assertEqual(d["checkpoint"]["previous_stage"],"T504")
        self.assertEqual(d["checkpoint"]["stage_id"],"T505")
        self.assertFalse(d["consumer_registered"])
        self.assertEqual(d["audiences"],["all_ai_bots"])
        self.assertTrue(d["constraints"]["read_only"])
        self.assertTrue(d["constraints"]["no_sanctions"])
        self.assertEqual(len(d["entries"]),10)
        self.assertEqual(sum(len(e["replies"]) for e in d["entries"]),400)
        previous={}
        for p in old:
            for e in p["entries"]:previous.setdefault(e["intent_id"],[]).extend(e["replies"])
        ids=set(); answers=set();notes=set()
        for e in d["entries"]:
            self.assertIn(e["intent_id"],previous)
            self.assertEqual((e["prior_for_stable_id"],e["added_candidates"],e["target"],e["total_staged"],e["remaining"]),(20,80,100,100,0) if e["intent_id"] in {"verify_numeric_context","interpret_relative_time"} else (20,30,100,50,50))
            self.assertEqual(len(e["replies"]),80 if e["intent_id"] in {"verify_numeric_context","interpret_relative_time"} else 30)
            parents={norm(x["text"]) for x in previous[e["intent_id"]]}
            context_parents={norm(x["context_note"]) for x in previous[e["intent_id"]]}
            for x in e["replies"]:
                self.assertNotIn(x["id"],ids);ids.add(x["id"])
                n=norm(x["text"]); q=norm(x["context_note"])
                self.assertNotIn(n,answers);answers.add(n)
                self.assertNotIn(q,notes);notes.add(q)
                self.assertNotIn(n,parents)
                self.assertNotIn(q,context_parents)
                self.assertEqual(x["language"],"ru")
                self.assertEqual(x["audiences"],["all_ai_bots"])
                self.assertTrue(x["read_only"])
                self.assertEqual(x["context"],"direct")
                self.assertTrue(x["avoid"])
                self.assertFalse(re.search(r"(?i)(ghp_[a-z0-9]{12,}|sk-[a-z0-9]{12,}|https?://|@[a-z0-9_]+)",x["text"]))
                self.assertFalse(re.search(r"(?i)\b(забань|замуть|удали чужое сообщение)\b",x["text"]))
                a=set(n.split())
                for p in parents:
                    b=set(p.split())
                    self.assertLess(len(a&b)/len(a|b),.78,x["id"])
        self.assertEqual(len(ids),400)
if __name__=="__main__":unittest.main()
