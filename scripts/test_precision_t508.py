"""T508 synthetic Russian contextual candidate integrity and continuity (read-only)."""
import hashlib
import json
import re
import unicodedata
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
NEW = ROOT / "staging/ru/precision_t508_context_pool.json"
PRIOR = ROOT / "staging/ru/precision_t507_context_pool.json"
SOURCE = ROOT / "packs/ru/dialogue.json"
COUNTS_PRIOR = {
    "missing_subject_reference": 15,
    "quoted_text_boundary": 15,
    "attachment_incomplete": 15,
    "unverified_external_status": 15,
    "privacy_before_troubleshooting": 15,
    "mixed_request_decomposition": 15,
    "format_contract_following": 10,
}

def norm(value):
    value = unicodedata.normalize("NFKC", value).lower().replace("ё", "е")
    return " ".join(re.findall(r"\w+", value))

def jaccard(a, b):
    a, b = set(a.split()), set(b.split())
    return len(a & b) / len(a | b) if (a or b) else 1.0

class T508Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.stage = json.loads(NEW.read_text(encoding="utf-8"))
        cls.previous = json.loads(PRIOR.read_text(encoding="utf-8"))

    def test_source_and_read_only_scope(self):
        stage = self.stage
        raw = SOURCE.read_bytes()
        manifest = json.loads((ROOT / "manifest.json").read_text(encoding="utf-8"))
        real = hashlib.sha256(raw).hexdigest()
        blob = hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()
        self.assertIn({"path": "packs/ru/dialogue.json", "sha256": real}, manifest["packs"])
        self.assertEqual(stage["source_pack"], "packs/ru/dialogue.json")
        self.assertEqual(stage["source_pack_manifest_sha256"], real)
        self.assertEqual(stage["source_pack_blob_sha"], blob)
        self.assertEqual(stage["language"], "ru")
        self.assertEqual(stage["audiences"], ["all_ai_bots"])
        self.assertFalse(stage["consumer_registered"])
        self.assertEqual(stage["stage_type"], "supplemental_contextual_reply_pool")
        self.assertTrue(all(stage["constraints"].values()))
        self.assertEqual(stage["checkpoint"]["previous_stage"], "T507")
        self.assertEqual(stage["checkpoint"]["base_commit"], "1bca731fbe0d610dd792998494b609216578eef2")

    def test_incremental_counts_and_duplicates(self):
        stage = self.stage
        parent = self.previous
        old = {e["intent_id"]: e for e in parent["entries"]}
        self.assertEqual(set(old), set(COUNTS_PRIOR))
        self.assertEqual({k: len(v["replies"]) for k,v in old.items()}, COUNTS_PRIOR)
        self.assertEqual({e["intent_id"] for e in stage["entries"]}, set(old))
        self.assertEqual(stage["checkpoint"]["processed_intents"], 7)
        self.assertEqual(stage["checkpoint"]["added_candidates"], 140)
        self.assertEqual(stage["checkpoint"]["finished_100"], 0)
        self.assertEqual(stage["checkpoint"]["partial_intents"], 7)
        self.assertEqual(stage["checkpoint"]["remaining_total"], 460)
        seen_ids, seen_texts, seen_notes = set(), set(), set()
        for entry in old.values():
            for reply in entry["replies"]:
                seen_ids.add(reply["id"])
                seen_texts.add(norm(reply["text"]))
                seen_notes.add(norm(reply["context_note"]))
        accepted = 0
        for entry in stage["entries"]:
            previous = old[entry["intent_id"]]
            self.assertEqual(entry["canonical_question"], previous["canonical_question"])
            self.assertEqual(entry["prior_for_stable_id"], previous["total_staged"])
            self.assertEqual(entry["added_candidates"], 20)
            self.assertEqual(len(entry["replies"]), 20)
            self.assertEqual(entry["total_staged"], previous["total_staged"] + 20)
            self.assertEqual(entry["remaining"], 100 - entry["total_staged"])
            self.assertEqual(entry["target"], 100)
            other = [norm(p["text"]) for p in previous["replies"]]
            for reply in entry["replies"]:
                txt, note = norm(reply["text"]), norm(reply["context_note"])
                self.assertNotIn(reply["id"], seen_ids)
                self.assertNotIn(txt, seen_texts)
                self.assertNotIn(note, seen_notes)
                self.assertGreater(len(txt), 35)
                self.assertGreater(len(note), 20)
                self.assertLess(max((jaccard(txt,x) for x in other), default=0), 0.78)
                self.assertEqual(reply["language"], "ru")
                self.assertEqual(reply["audiences"], ["all_ai_bots"])
                self.assertEqual(reply["context"], "direct")
                self.assertTrue(reply["read_only"])
                self.assertTrue(reply["avoid"])
                self.assertFalse(re.search(r"(?i)(ghp_[a-z0-9]{12,}|sk-[a-z0-9]{12,}|https?://|@[a-z0-9_]+)", reply["text"]))
                self.assertFalse(re.search(r"(?i)\b(забань|замуть|удали чужое сообщение)\b", reply["text"]))
                seen_ids.add(reply["id"]); seen_texts.add(txt); seen_notes.add(note)
                other.append(txt)
                accepted += 1
        self.assertEqual(accepted, 140)
        self.assertEqual(sum(e["total_staged"] for e in stage["entries"]), 240)
        self.assertEqual(sum(e["remaining"] for e in stage["entries"]), 460)

    def test_no_identical_reply_in_related_stages(self):
        current = {norm(reply["text"]) for entry in self.stage["entries"] for reply in entry["replies"]}
        for sid in ("t503", "t504", "t505", "t506"):
            file = ROOT / f"staging/ru/practical_turns_{sid}_context_pool.json"
            if file.exists():
                previous = json.loads(file.read_text(encoding="utf-8"))
                for entry in previous["entries"]:
                    for reply in entry["replies"]:
                        self.assertNotIn(norm(reply["text"]), current)

if __name__ == "__main__":
    unittest.main()
