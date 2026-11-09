"""T507 staged RU replies: pinned source, contextual privacy and dedup."""
import hashlib, json, re, unicodedata, unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "packs/ru/dialogue.json"
STAGE = ROOT / "staging/ru/precision_t507_context_pool.json"
COUNTS = {"missing_subject_reference": 15, "quoted_text_boundary": 15,
          "attachment_incomplete": 15, "unverified_external_status": 15,
          "privacy_before_troubleshooting": 15, "mixed_request_decomposition": 15,
          "format_contract_following": 10}

def norm(value):
    return " ".join(re.findall(r"\w+", unicodedata.normalize("NFKC", value).lower().replace("ё", "е")))

class T507Tests(unittest.TestCase):
    def test_qa_and_integrity(self):
        obj = json.loads(STAGE.read_text("utf-8"))
        raw = SOURCE.read_bytes()
        sha = hashlib.sha256(raw).hexdigest()
        blob = hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()
        manifest = json.loads((ROOT / "manifest.json").read_text("utf-8"))
        self.assertIn({"path": "packs/ru/dialogue.json", "sha256": sha}, manifest["packs"])
        self.assertEqual(obj["source_pack_manifest_sha256"], sha)
        self.assertEqual(obj["source_pack_blob_sha"], blob)
        self.assertFalse(obj["consumer_registered"])
        self.assertEqual(obj["language"], "ru")
        self.assertEqual(obj["audiences"], ["all_ai_bots"])
        self.assertTrue(all(obj["constraints"].values()))
        self.assertEqual(obj["checkpoint"]["stage_id"], "T507")
        self.assertEqual(obj["checkpoint"]["base_commit"], "788a125410ef5bf2f5bcdad4c3b3310e2dfc56fd")
        self.assertEqual({e["intent_id"]: len(e["replies"]) for e in obj["entries"]}, COUNTS)
        self.assertEqual(len({e["canonical_question"] for e in obj["entries"]}), 7)
        ids, texts, notes = set(), set(), set()
        for entry in obj["entries"]:
            self.assertEqual(entry["target"], 100)
            self.assertEqual(entry["prior_for_stable_id"], 0)
            self.assertEqual(entry["total_staged"], len(entry["replies"]))
            self.assertEqual(entry["remaining"], 100 - len(entry["replies"]))
            prior_words = []
            for r in entry["replies"]:
                answer, note = norm(r["text"]), norm(r["context_note"])
                self.assertNotIn(r["id"], ids)
                self.assertNotIn(answer, texts)
                self.assertNotIn(note, notes)
                ids.add(r["id"]); texts.add(answer); notes.add(note)
                self.assertGreater(len(answer), 35)
                self.assertGreater(len(note), 20)
                self.assertEqual(r["language"], "ru")
                self.assertEqual(r["audiences"], ["all_ai_bots"])
                self.assertEqual(r["context"], "direct")
                self.assertTrue(r["read_only"])
                self.assertTrue(r["avoid"])
                self.assertFalse(re.search(r"(?i)(ghp_[a-z0-9]{12,}|sk-[a-z0-9]{12,}|https?://|@[a-z0-9_]+)", r["text"]))
                self.assertFalse(re.search(r"(?i)\b(забань|замуть|удали чужое сообщение)\b", r["text"]))
                words = set(answer.split())
                for old in prior_words:
                    self.assertLess(len(words & old) / len(words | old), 0.78)
                prior_words.append(words)
        self.assertEqual(len(ids), 100)
        c = obj["checkpoint"]
        self.assertEqual(c["added_candidates"], 100)
        self.assertEqual(c["processed_intents"], 7)
        self.assertEqual(c["partial_intents"], 7)
        self.assertEqual(c["finished_100"], 0)
        self.assertEqual(c["remaining_total"], 600)

    def test_no_cross_stage_exact_duplicate(self):
        cur = json.loads(STAGE.read_text("utf-8"))
        intents = {e["intent_id"] for e in cur["entries"]}
        texts = {norm(r["text"]) for e in cur["entries"] for r in e["replies"]}
        for sid in ("t503", "t504", "t505", "t506"):
            p = ROOT / f"staging/ru/practical_turns_{sid}_context_pool.json"
            if not p.exists():
                continue
            for entry in json.loads(p.read_text("utf-8"))["entries"]:
                self.assertNotIn(entry["intent_id"], intents)
                for r in entry["replies"]:
                    self.assertNotIn(norm(r["text"]), texts)

if __name__ == "__main__":
    unittest.main()
