"""Read-only tests for the temporal language contextual staging candidate (2026-11-11)."""
import hashlib
import json
import re
import unicodedata
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STAGE = ROOT / "staging/ru/temporal_language_20261111_context_pool.json"
STAGE_B = ROOT / "staging/ru/temporal_language_20261111_context_delta_b.json"
STAGE_C = ROOT / "staging/ru/temporal_language_20261111_context_delta_c.json"
STAGE_D = ROOT / "staging/ru/temporal_language_20261111_context_delta_d.json"
STAGE_E = ROOT / "staging/ru/temporal_language_20261111_context_delta_e.json"
STAGE_F = ROOT / "staging/ru/temporal_language_20261111_context_delta_f.json"
AUX = {"all_ai_bots"}

def norm(value):
    text = unicodedata.normalize("NFKC", value).casefold().replace("ё", "е")
    return " ".join(re.findall(r"[^\W_]+", text, flags=re.UNICODE))

def blob_sha(raw):
    return hashlib.sha1(b"blob " + str(len(raw)).encode("ascii") + b"\x00" + raw).hexdigest()

class TemporalLanguageStagingTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.payload = json.loads(STAGE.read_text("utf-8"))
        cls.entries = cls.payload["entries"]
        cls.delta = json.loads(STAGE_B.read_text("utf-8"))
        cls.stage_c = json.loads(STAGE_C.read_text("utf-8"))
        cls.stage_d = json.loads(STAGE_D.read_text("utf-8"))
        cls.stage_e = json.loads(STAGE_E.read_text("utf-8"))
        cls.stage_f = json.loads(STAGE_F.read_text("utf-8"))
        cls.replies = [r for stage in (cls.payload, cls.delta, cls.stage_c, cls.stage_d, cls.stage_e, cls.stage_f) for entry in stage["entries"] for r in entry["replies"]]

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
        self.assertEqual((len(set(ids)), len(set(texts)), len(set(contexts))), (600, 600, 600))
        bags = [set(v.split()) for v in texts]
        for i, left in enumerate(bags):
            for right in bags[i+1:]:
                self.assertLess(len(left & right) / len(left | right), 0.8)

    def test_stage_b_parent_and_progress(self):
        b = self.delta
        self.assertEqual(b["parent_stage"], str(STAGE.relative_to(ROOT)))
        self.assertEqual(b["parent_stage_blob_sha"], blob_sha(STAGE.read_bytes()))
        self.assertEqual(b["source_pack_manifest_sha256"], self.payload["source_pack_manifest_sha256"])
        self.assertEqual(b["source_pack_blob_sha"], self.payload["source_pack_blob_sha"])
        self.assertFalse(b["consumer_registered"])
        cp = b["checkpoint"]
        self.assertEqual((cp["prior_candidates"], cp["added_candidates"], cp["cumulative_candidates"]), (100, 100, 200))
        self.assertEqual((cp["processed_intents"], cp["finished_100"], cp["partial_intents"], cp["remaining_total"]), (10, 0, 10, 800))
        self.assertEqual({e["intent_id"] for e in b["entries"]}, {e["intent_id"] for e in self.entries})
        for e in b["entries"]:
            self.assertEqual((e["prior_for_stable_id"], e["total_staged"], e["target"], e["remaining"]), (10, 20, 100, 80))
            self.assertEqual(len(e["replies"]), 10)
            for i, r in enumerate(e["replies"], 11):
                self.assertEqual(r["id"], f"{e['intent_id']}_{i:02d}")
                self.assertTrue(r["read_only"])
                self.assertEqual(r["context"], "direct")
                self.assertEqual(r["language"], "ru")
                self.assertEqual(r["audiences"], ["all_ai_bots"])
                self.assertIn("не применять санкции", r["avoid"])
                self.assertGreater(len(r["context_note"]), 12)

    def test_stage_c_through_f_ancestry_progress_and_applicability(self):
        previous = self.delta
        paths = (STAGE_C, STAGE_D, STAGE_E, STAGE_F)
        expected_totals = (300, 400, 500, 600)
        prior = (200, 300, 400, 500)
        for stage_path, cumulative, previous_count in zip(paths, expected_totals, prior):
            stage = json.loads(stage_path.read_text("utf-8"))
            parent_path = {300: STAGE_B, 400: STAGE_C, 500: STAGE_D, 600: STAGE_E}[cumulative]
            self.assertEqual(stage["parent_stage"], str(parent_path.relative_to(ROOT)))
            self.assertEqual(stage["parent_stage_blob_sha"], blob_sha(parent_path.read_bytes()))
            self.assertEqual(stage["source_pack_manifest_sha256"], self.payload["source_pack_manifest_sha256"])
            self.assertEqual(stage["source_pack_blob_sha"], self.payload["source_pack_blob_sha"])
            self.assertFalse(stage["consumer_registered"])
            self.assertEqual(stage["audiences"], ["all_ai_bots"])
            self.assertEqual(stage["constraints"], self.payload["constraints"])
            self.assertEqual((stage["checkpoint"]["prior_candidates"], stage["checkpoint"]["added_candidates"],
                              stage["checkpoint"]["cumulative_candidates"]), (previous_count, 100, cumulative))
            self.assertEqual((stage["checkpoint"]["processed_intents"], stage["checkpoint"]["finished_100"],
                              stage["checkpoint"]["partial_intents"], stage["checkpoint"]["remaining_total"]),
                             (10, 0, 10, 1000 - cumulative))
            self.assertEqual({e["intent_id"] for e in stage["entries"]},
                             {e["intent_id"] for e in self.entries})
            start = previous_count // 10 + 1
            for entry in stage["entries"]:
                self.assertEqual((entry["prior_for_stable_id"], entry["added_candidates"],
                                  entry["total_staged"], entry["target"], entry["remaining"]),
                                 (start - 1, 10, cumulative // 10, 100, 100 - cumulative // 10))
                self.assertEqual(len(entry["replies"]), 10)
                self.assertEqual(entry["language"], "ru")
                self.assertEqual(entry["audiences"], ["all_ai_bots"])
                for index, reply in enumerate(entry["replies"], start):
                    self.assertEqual(reply["id"], f'{entry["intent_id"]}_{index:02d}')
                    self.assertEqual(reply["audiences"], ["all_ai_bots"])
                    self.assertEqual(reply["context"], "direct")
                    self.assertEqual(reply["language"], "ru")
                    self.assertIs(reply["read_only"], True)
                    self.assertIn("не применять санкции", reply["avoid"])
                    self.assertGreater(len(reply["text"].strip()), 29)
                    self.assertGreater(len(reply["context_note"].strip()), 12)
            previous = stage

    def test_privacy_no_sanctions_or_false_access(self):
        for r in self.replies:
            text = r["text"]
            self.assertNotRegex(text, r"(?i)[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}")
            self.assertNotRegex(text, r"(?:\+?\d[ \-]?){11,}")
            self.assertNotRegex(text, r"(?i)(?:бот|я) (?:забанил|замутил|уже отправил|изменил настройки)")
            self.assertNotIn("token", text.casefold())

if __name__ == "__main__":
    unittest.main()
