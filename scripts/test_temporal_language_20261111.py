"""Read-only tests for the temporal language contextual staging candidate (2026-11-11)."""
import hashlib
import json
import re
import unicodedata
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STAGE = ROOT / "staging/ru/temporal_language_20261111_context_pool.json"
AUX = {"all_ai_bots"}

def norm(value):
    text = unicodedata.normalize("NFKC", value).casefold().replace("ё", "е")
    return " ".join(re.findall(r"[^\\W_]+", text, flags=re.UNICODE))

def blob_sha(raw):
    return hashlib.sha1(b"blob " + str(len(raw)).encode("ascii") + b"\\x00" + raw).hexdigest()

class TemporalLanguageStagingTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.payload = json.loads(STAGE.read_text("utf-8"))
        cls.entries = cls.payload["entries"]
        cls.replies = [r for entry in cls.entries for r in entry["replies"]]

    def test_integrity_and_manifest_source(self):
        stage = self.payload
        source = stage["source_pack"]
        raw = (ROOT / source).read_bytes()
        manifest = json.loads((ROOT / "manifest.json").read_text("utf-8"))
        expected_sha = hashlib.sha256(raw).hexdigest()
        self.assertEqual(expected_sha, stage["source_pack_manifest_sha256"])
        self.assertEqual(blob_sha(raw), stage["source_pack_blob_sha"])
        self.assertIn({"path": source, "sha256": expected_sha}, manifest["packs"])
        self.assertFalse(stage["consumer_registered"])
        self.assertNotIn({"path": str(STAGE.relative_to(ROOT))}, manifest["packs"])

    def test_metadata_and_stable_progress(self):
        s = self.payload
        self.assertEqual(s["stage_type"], "supplemental_contextual_reply_pool")
        self.assertEqual(s["audiences"], ["all_ai_bots"])
        self.assertEqual(s["language"], "ru")
        for key in ("read_only", "requires_direct_address", "no_personal_data", "no_sanctions", "requires_context_match"):
            self.assertIs(s["constraints"][key], True)
        cp = s["checkpoint"]
        self.assertEqual((cp["prior_candidates"], cp["added_candidates"], cp["cumulative_candidates"]), (0, 100, 100))
        self.assertEqual((cp["processed_intents"], cp["finished_100"], cp["partial_intents"], cp["remaining_total"]), (10, 0, 10, 900))
        self.assertEqual(len(self.entries), 10)
        self.assertEqual(len({e["intent_id"] for e in self.entries}), 10)
        for e in self.entries:
            self.assertEqual((e["prior_for_stable_id"], e["added_candidates"], e["total_staged"], e["target"], e["remaining"]), (0, 10, 10, 100, 90))
            self.assertEqual(e["audiences"], ["all_ai_bots"])
            self.assertEqual(e["language"], "ru")
            self.assertTrue(e["canonical_question"])
            self.assertEqual(len(e["replies"]), 10)
            for i, r in enumerate(e["replies"], 1):
                self.assertEqual(r["id"], f"{e['intent_id']}_{i:02d}")
                self.assertEqual(r["language"], "ru")
                self.assertEqual(r["audiences"], ["all_ai_bots"])
                self.assertEqual(r["context"], "direct")
                self.assertTrue(r["read_only"])
                self.assertIn("не применять санкции", r["avoid"])
                self.assertGreater(len(r["text"].strip()), 29)
                self.assertGreater(len(r["context_note"].strip()), 12)

    def test_uniqueness_and_lexical_near_repeats(self):
        ids = [r["id"] for r in self.replies]
        texts = [norm(r["text"]) for r in self.replies]
        contexts = [norm(r["context_note"]) for r in self.replies]
        self.assertEqual((len(set(ids)), len(set(texts)), len(set(contexts))), (100, 100, 100))
        bags = [set(v.split()) for v in texts]
        for i, left in enumerate(bags):
            for right in bags[i+1:]:
                self.assertLess(len(left & right) / len(left | right), 0.8)

    def test_privacy_no_sanctions_or_false_access(self):
        for r in self.replies:
            text = r["text"]
            self.assertNotRegex(text, r"(?i)[A-Z0-9._%+-]+@[A-Z0-9.-]+\\.[A-Z]{2,}")
            self.assertNotRegex(text, r"(?:\\+?\\d[ \\-]?){11,}")
            self.assertNotRegex(text, r"(?i)(?:бот|я) (?:забанил|замутил|уже отправил|изменил настройки)")
            self.assertNotIn("token", text.casefold())

if __name__ == "__main__":
    unittest.main()
