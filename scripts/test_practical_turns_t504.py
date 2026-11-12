"""T504: independent read-only candidate extension for ten T503 stable IDs."""
import json,hashlib,re,unicodedata,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/"packs/ru/dialogue.json"
PREV=ROOT/"staging/ru/practical_turns_t503_context_pool.json"
STAGE=ROOT/"staging/ru/practical_turns_t504_context_pool.json"
def norm(t):
    return " ".join(re.findall(r"\w+",unicodedata.normalize("NFKC",t).lower().replace("ё","е")))
class StageT504Tests(unittest.TestCase):
    def test_lineage_progress_and_uniqueness(self):
        prev=json.loads(PREV.read_text("utf-8"))
        data=json.loads(STAGE.read_text("utf-8"))
        registered=json.loads((ROOT/"manifest.json").read_text("utf-8"))
        actual=hashlib.sha256(SOURCE.read_bytes()).hexdigest()
        self.assertIn({"path":"packs/ru/dialogue.json","sha256":actual},registered["packs"])
        self.assertEqual(prev["source_pack_manifest_sha256"],actual)
        self.assertEqual(data["source_pack_manifest_sha256"],actual)
        self.assertEqual(data["source_pack_blob_sha"],prev["source_pack_blob_sha"])
        self.assertEqual(data["checkpoint"]["stage_id"],"T504")
        self.assertEqual(data["checkpoint"]["previous_stage"],"T503")
        self.assertFalse(data["consumer_registered"])
        self.assertEqual(data["audiences"],["all_ai_bots"])
        self.assertTrue(data["constraints"]["read_only"])
        self.assertEqual(len(data["entries"]),10)
        self.assertEqual(sum(len(e["replies"]) for e in data["entries"]),100)
        before={e["intent_id"]:e for e in prev["entries"]}
        ids=set(); texts=set(); notes=set()
        for entry in data["entries"]:
            self.assertIn(entry["intent_id"],before)
            self.assertEqual((entry["prior_for_stable_id"],entry["added_candidates"],entry["total_staged"],entry["target"],entry["remaining"]),(10,10,20,100,80))
            self.assertEqual(len(entry["replies"]),10)
            for x in entry["replies"]:
                self.assertNotIn(x["id"],ids); ids.add(x["id"])
                self.assertEqual(x["language"],"ru")
                self.assertEqual(x["audiences"],["all_ai_bots"])
                self.assertTrue(x["read_only"])
                self.assertTrue(x["context_note"])
                self.assertNotIn(norm(x["text"]),texts);texts.add(norm(x["text"]))
                self.assertNotIn(norm(x["context_note"]),notes);notes.add(norm(x["context_note"]))
                self.assertFalse(re.search(r"(?i)(ghp_[a-z0-9]{12,}|sk-[a-z0-9]{12,}|https?://|@[a-z0-9_]+)",x["text"]))
                self.assertFalse(re.search(r"(?i)\b(забань|замуть|удали чужое сообщение)\b",x["text"]))
        self.assertEqual(len(ids),100)
if __name__=="__main__":unittest.main()
