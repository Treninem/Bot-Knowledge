"""T537: additive eight-intent dialogue coverage and immutable source."""
import hashlib
import json
import subprocess
import unicodedata
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def norm(s):
    s=unicodedata.normalize("NFKC",s).casefold().replace("ё","е")
    return " ".join("".join(ch if ch.isalnum() else " " for ch in s).split())
class TestT537(unittest.TestCase):
    def test_four_stages(self):
        stages=[json.loads((ROOT/f"staging/ru/practical_dialogue_t{n}_context_pool.json").read_text("utf-8")) for n in range(534,538)]
        source=ROOT/"packs/ru/dialogue.json"
        sha=hashlib.sha256(source.read_bytes()).hexdigest()
        blob=subprocess.check_output(["git","hash-object",str(source)],cwd=ROOT,text=True).strip()
        manifest=json.loads((ROOT/"manifest.json").read_text("utf-8"))
        self.assertIn({"path":"packs/ru/dialogue.json","sha256":sha},manifest["packs"])
        ids=set();answers=set();notes=set();wordbags=[]
        baseids={e["intent_id"] for e in stages[0]["entries"]}
        self.assertEqual(len(baseids),8)
        for idx,st in enumerate(stages):
            self.assertFalse(st["consumer_registered"])
            self.assertEqual(st["audiences"],["all_ai_bots"])
            self.assertEqual((st["source_pack_manifest_sha256"],st["source_pack_blob_sha"]),(sha,blob))
            self.assertEqual({e["intent_id"] for e in st["entries"]},baseids)
            for k in ("read_only","no_sanctions","no_personal_data","requires_context_match","requires_direct_address"):
                self.assertTrue(st["constraints"][k])
            for e in st["entries"]:
                self.assertEqual((e["prior_for_stable_id"],e["added_candidates"],e["total_staged"],e["remaining"],e["target"]),(idx*20,20,(idx+1)*20,100-(idx+1)*20,100))
                self.assertEqual(len(e["replies"]),20)
                for row in e["replies"]:
                    self.assertNotIn(row["id"],ids);ids.add(row["id"])
                    self.assertNotIn(norm(row["text"]),answers);answers.add(norm(row["text"]))
                    self.assertNotIn(norm(row["context_note"]),notes);notes.add(norm(row["context_note"]))
                    self.assertEqual(row["language"],"ru")
                    self.assertEqual(row["audiences"],["all_ai_bots"])
                    self.assertTrue(row["read_only"])
                    self.assertGreaterEqual(len(row["text"]),40)
                    bag=set(norm(row["text"]).split())
                    for seen in wordbags:
                        self.assertLess(len(seen & bag)/len(seen | bag),.78)
                    wordbags.append(bag)
        self.assertEqual(len(ids),640)
        self.assertEqual(len(answers),640)
        self.assertEqual(len(notes),640)
        self.assertEqual(stages[-1]["checkpoint"]["remaining_total"],160)
        self.assertFalse(any(x["path"].startswith("staging/ru/practical_dialogue_") for x in manifest["packs"]))
if __name__=="__main__":
    unittest.main()
