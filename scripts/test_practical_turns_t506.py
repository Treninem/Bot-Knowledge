"""T506: 400 original contextual replies; registered source immutable; opt-in only."""
import hashlib
import json
import re
import unicodedata
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = "staging/ru/practical_turns_{}_context_pool.json"
PARENT_STAGES = ("t503", "t504", "t505")
STAGE = ROOT / BASE.format("t506")
SOURCE = ROOT / "packs/ru/dialogue.json"

def norm(text):
    return " ".join(re.findall(r"\w+", unicodedata.normalize("NFKC", text).lower().replace("ё", "е")))

class T506StageTests(unittest.TestCase):
    def test_pinned_source_and_cumulative_intents(self):
        stage = json.loads(STAGE.read_text("utf-8"))
        history = [json.loads((ROOT / BASE.format(s)).read_text("utf-8")) for s in PARENT_STAGES]
        sha = hashlib.sha256(SOURCE.read_bytes()).hexdigest()
        manifest = json.loads((ROOT / "manifest.json").read_text("utf-8"))
        self.assertIn({"path": "packs/ru/dialogue.json", "sha256": sha}, manifest["packs"])
        self.assertEqual(stage["source_pack_manifest_sha256"], sha)
        self.assertEqual(stage["source_pack_blob_sha"], history[-1]["source_pack_blob_sha"])
        self.assertEqual(stage["checkpoint"]["previous_stage"], "T505")
        self.assertEqual(stage["checkpoint"]["stage_id"], "T506")
        self.assertEqual(stage["checkpoint"]["base_commit"], "788a125410ef5bf2f5bcdad4c3b3310e2dfc56fd")
        self.assertFalse(stage["consumer_registered"])
        self.assertEqual(stage["audiences"], ["all_ai_bots"])
        self.assertTrue(stage["constraints"]["read_only"])
        self.assertTrue(stage["constraints"]["no_sanctions"])
        self.assertEqual(stage["language"], "ru")
        self.assertEqual(len(stage["entries"]), 8)

        by_intent = {}
        for old in history:
            for entry in old["entries"]:
                by_intent.setdefault(entry["intent_id"], []).extend(entry["replies"])
        global_ids = set()
        global_texts = set()
        global_notes = set()
        additions = 0
        for entry in stage["entries"]:
            intent = entry["intent_id"]
            self.assertIn(intent, by_intent)
            count = 50
            self.assertEqual(entry["prior_for_stable_id"], 50)
            self.assertEqual(entry["added_candidates"], count)
            self.assertEqual(entry["target"], 100)
            self.assertEqual(entry["total_staged"], 50 + count)
            self.assertEqual(entry["remaining"], 50 - count)
            self.assertEqual(len(entry["replies"]), count)
            parents = {norm(x["text"]) for x in by_intent[intent]}
            prior_notes = {norm(x["context_note"]) for x in by_intent[intent]}
            parent_word_sets = [set(x.split()) for x in parents]
            for r in entry["replies"]:
                additions += 1
                self.assertNotIn(r["id"], global_ids)
                global_ids.add(r["id"])
                answer = norm(r["text"])
                note = norm(r["context_note"])
                self.assertNotIn(answer, parents)
                self.assertNotIn(note, prior_notes)
                self.assertNotIn(answer, global_texts)
                self.assertNotIn(note, global_notes)
                global_texts.add(answer)
                global_notes.add(note)
                self.assertEqual(r["language"], "ru")
                self.assertEqual(r["audiences"], ["all_ai_bots"])
                self.assertEqual(r["context"], "direct")
                self.assertTrue(r["read_only"])
                self.assertTrue(r["avoid"])
                self.assertGreater(len(answer), 35)
                self.assertFalse(re.search(r"(?i)(ghp_[a-z0-9]{12,}|sk-[a-z0-9]{12,}|https?://|@[a-z0-9_]+)", r["text"]))
                self.assertFalse(re.search(r"(?i)\b(забань|замуть|удали чужое сообщение)\b", r["text"]))
                words = set(answer.split())
                for oldwords in parent_word_sets:
                    self.assertLess(len(words & oldwords) / len(words | oldwords), 0.78, r["id"])
                parent_word_sets.append(words)
        self.assertEqual(additions, 400)
        self.assertEqual(len(global_ids), 400)
        self.assertEqual(stage["checkpoint"]["added_candidates"], 400)
        self.assertEqual(stage["checkpoint"]["finished_100"], 10)
        self.assertEqual(stage["checkpoint"]["partial_intents"], 0)
        self.assertEqual(stage["checkpoint"]["remaining_total"], 0)

if __name__ == "__main__":
    unittest.main()
