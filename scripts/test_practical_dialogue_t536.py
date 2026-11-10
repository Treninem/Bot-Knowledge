"""T536: three-stage practical dialogue cumulative quality and source boundary."""
import hashlib
import json
import subprocess
import unicodedata
import unittest
from pathlib import Path
R = Path(__file__).resolve().parents[1]
def norm(t):
    return " ".join("".join(c if c.isalnum() else " " for c in unicodedata.normalize("NFKC", t).casefold().replace("ё", "е")).split())
class TestT536(unittest.TestCase):
    def test_all_three_stages(self):
        pools = [json.loads((R / f"staging/ru/practical_dialogue_t{n}_context_pool.json").read_text("utf-8")) for n in (534, 535, 536)]
        sha = hashlib.sha256((R / "packs/ru/dialogue.json").read_bytes()).hexdigest()
        blob = subprocess.check_output(["git", "hash-object", "packs/ru/dialogue.json"], cwd=R, text=True).strip()
        manifest = json.loads((R / "manifest.json").read_text("utf-8"))
        self.assertIn({"path":"packs/ru/dialogue.json", "sha256":sha}, manifest["packs"])
        ids=set(); texts=set(); notes=set(); bags=[]
        for n,pool in zip((534,535,536), pools):
            self.assertFalse(pool["consumer_registered"])
            self.assertEqual((pool["source_pack_manifest_sha256"],pool["source_pack_blob_sha"]),(sha,blob))
            self.assertEqual(pool["audiences"],["all_ai_bots"])
            for flag in ("read_only", "requires_direct_address", "no_personal_data", "no_sanctions", "requires_context_match"):
                self.assertTrue(pool["constraints"][flag])
            self.assertEqual(len(pool["entries"]),8)
            for e in pool["entries"]:
                self.assertEqual((e["prior_for_stable_id"],e["added_candidates"],e["total_staged"],e["remaining"],e["target"]),((n-534)*20,20,(n-533)*20,100-(n-533)*20,100))
                self.assertEqual(len(e["replies"]),20)
                for z in e["replies"]:
                    self.assertNotIn(z["id"],ids);ids.add(z["id"])
                    self.assertNotIn(norm(z["text"]),texts);texts.add(norm(z["text"]))
                    self.assertNotIn(norm(z["context_note"]),notes);notes.add(norm(z["context_note"]))
                    self.assertEqual(z["language"],"ru")
                    self.assertEqual(z["audiences"],["all_ai_bots"])
                    self.assertTrue(z["read_only"])
                    self.assertGreaterEqual(len(z["text"]),40)
                    bag=set(norm(z["text"]).split())
                    for before in bags:
                        self.assertLess(len(bag & before)/len(bag | before),.78)
                    bags.append(bag)
        self.assertEqual((len(ids),len(texts),len(notes)),(480,480,480))
        self.assertEqual((pools[-1]["checkpoint"]["added_candidates"],pools[-1]["checkpoint"]["remaining_total"]),(160,320))
        self.assertFalse(any(p["path"].startswith("staging/ru/practical_dialogue_t") for p in manifest["packs"]))
if __name__=="__main__":
    unittest.main()
