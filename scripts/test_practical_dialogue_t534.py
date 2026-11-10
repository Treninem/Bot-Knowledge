"""T534: scoped practical dialogue responses, immutable source pin and diversity."""
import hashlib, json, re, subprocess, unicodedata, unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
STAGE=ROOT/"staging/ru/practical_dialogue_t534_context_pool.json"
SOURCE=ROOT/"packs/ru/dialogue.json"
def norm(s):
    s=unicodedata.normalize("NFKC",s).casefold().replace("ё","е")
    return " ".join("".join(x if x.isalnum() else " " for x in s).split())
class TestT534(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pool=json.loads(STAGE.read_text(encoding="utf-8"))
        cls.manifest=json.loads((ROOT/"manifest.json").read_text("utf-8"))
    def test_manifest_pinning_and_isolation(self):
        sha=hashlib.sha256(SOURCE.read_bytes()).hexdigest()
        blob=subprocess.check_output(["git","hash-object",str(SOURCE)],cwd=ROOT,text=True).strip()
        self.assertEqual(sha,self.pool["source_pack_manifest_sha256"])
        self.assertEqual(blob,self.pool["source_pack_blob_sha"])
        self.assertIn({"path":"packs/ru/dialogue.json","sha256":sha},self.manifest["packs"])
        self.assertFalse(self.pool["consumer_registered"])
        self.assertNotIn({"path":"staging/ru/practical_dialogue_t534_context_pool.json","sha256":sha},self.manifest["packs"])
        for flag in ("read_only","requires_direct_address","no_personal_data","no_sanctions","requires_context_match"):
            self.assertTrue(self.pool["constraints"][flag])
    def test_counter_and_unique_contexts(self):
        entries=self.pool["entries"]
        self.assertEqual(len(entries),8)
        ids=set();texts=set();notes=set();tokens=[]
        self.assertEqual(self.pool["checkpoint"]["added_candidates"],80)
        self.assertEqual(self.pool["checkpoint"]["remaining_total"],720)
        for entry in entries:
            self.assertEqual(len(entry["replies"]),10)
            self.assertEqual(entry["prior_for_stable_id"],0)
            self.assertEqual(entry["added_candidates"],10)
            self.assertEqual(entry["total_staged"],10)
            self.assertEqual(entry["remaining"],90)
            self.assertEqual(entry["target"],100)
            for row in entry["replies"]:
                self.assertNotIn(row["id"],ids);ids.add(row["id"])
                self.assertNotIn(norm(row["text"]),texts);texts.add(norm(row["text"]))
                self.assertNotIn(norm(row["context_note"]),notes);notes.add(norm(row["context_note"]))
                self.assertEqual(row["language"],"ru")
                self.assertEqual(row["audiences"],["all_ai_bots"])
                self.assertTrue(row["read_only"])
                self.assertGreaterEqual(len(row["text"]),40)
                self.assertNotRegex(row["text"],r"(?i)https?://|@\\w+")
                words=set(norm(row["text"]).split())
                for other in tokens:
                    self.assertLess(len(words & other)/len(words | other),0.78)
                tokens.append(words)
        self.assertEqual(len(ids),80)
        self.assertEqual(len(texts),80)
        self.assertEqual(len(notes),80)
if __name__=="__main__": unittest.main()
