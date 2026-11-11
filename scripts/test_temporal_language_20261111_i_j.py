"""Read-only, consumer-unregistered temporal language completion checks (I/J)."""
import hashlib
import json
import re
import unicodedata
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PREFIX = ROOT / "staging/ru"
SUFFIXES = ("context_pool",) + tuple(f"context_delta_{c}" for c in "bcdefghij")
PATHS = [PREFIX / f"temporal_language_20261111_{s}.json" for s in SUFFIXES]
NORMAL_RE = re.compile(r"[^\\W_]+", re.UNICODE)

def normalized(value):
    return " ".join(NORMAL_RE.findall(unicodedata.normalize("NFKC", value).casefold().replace("ё", "е")))

def git_blob(raw):
    return hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()

class TemporalCompletion(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.stages = [json.loads(p.read_text("utf-8")) for p in PATHS]
        cls.rows = [r for s in cls.stages for e in s["entries"] for r in e["replies"]]

    def test_manifest_and_source(self):
        source = self.stages[0]["source_pack"]
        raw = (ROOT / source).read_bytes()
        expected = hashlib.sha256(raw).hexdigest()
        manifest = json.loads((ROOT / "manifest.json").read_text("utf-8"))
        self.assertEqual(expected, "0cfedc133354a69522fecc3cda6bc21533c66005f0dc207050075f787dc977a8")
        self.assertEqual(git_blob(raw), self.stages[0]["source_pack_blob_sha"])
        self.assertIn({"path": source, "sha256": expected}, manifest["packs"])
        self.assertTrue(all(str(p.relative_to(ROOT)) not in [x["path"] for x in manifest["packs"]] for p in PATHS))

    def test_ancestry_and_progress(self):
        names = {e["intent_id"] for e in self.stages[0]["entries"]}
        self.assertEqual(len(names), 10)
        for i, (stage, path) in enumerate(zip(self.stages, PATHS)):
            count = 100 * (i + 1)
            self.assertEqual(stage["stage_type"], "supplemental_contextual_reply_pool")
            self.assertFalse(stage["consumer_registered"])
            self.assertEqual(stage["language"], "ru")
            self.assertEqual(stage["audiences"], ["all_ai_bots"])
            self.assertTrue(all(stage["constraints"][k] is True for k in
                                ("read_only", "requires_direct_address", "no_personal_data", "no_sanctions", "requires_context_match")))
            self.assertEqual(stage["source_pack_manifest_sha256"], self.stages[0]["source_pack_manifest_sha256"])
            self.assertEqual(stage["source_pack_blob_sha"], self.stages[0]["source_pack_blob_sha"])
            if i:
                self.assertEqual(stage["parent_stage"], str(PATHS[i - 1].relative_to(ROOT)))
                self.assertEqual(stage["parent_stage_blob_sha"], git_blob(PATHS[i - 1].read_bytes()))
            cp = stage["checkpoint"]
            self.assertEqual((cp["prior_candidates"], cp["added_candidates"], cp["cumulative_candidates"]), (count-100, 100, count))
            self.assertEqual((cp["processed_intents"], cp["finished_100"], cp["partial_intents"], cp["remaining_total"]),
                             (10, 10 if i == 9 else 0, 0 if i == 9 else 10, 1000 - count))
            self.assertEqual({e["intent_id"] for e in stage["entries"]}, names)
            for entry in stage["entries"]:
                self.assertEqual((entry["prior_for_stable_id"], entry["added_candidates"], entry["total_staged"],
                                  entry["target"], entry["remaining"]), (count // 10-10, 10, count // 10, 100, 100-count // 10))
                self.assertEqual(len(entry["replies"]), 10)
                self.assertEqual(entry["audiences"], ["all_ai_bots"])
                for offset, reply in enumerate(entry["replies"], count // 10-9):
                    self.assertEqual(reply["id"], f'{entry["intent_id"]}_{offset:02d}')
                    self.assertEqual(reply["language"], "ru")
                    self.assertEqual(reply["audiences"], ["all_ai_bots"])
                    self.assertTrue(reply["read_only"])
                    self.assertEqual(reply["context"], "direct")
                    self.assertIn("не применять санкции", reply["avoid"])
                    self.assertGreater(len(reply["context_note"].strip()), 12)
                    self.assertGreater(len(reply["text"].strip()), 30)

    def test_unique_and_contextual(self):
        self.assertEqual(len(self.rows), 1000)
        ids = [r["id"] for r in self.rows]
        texts = [normalized(r["text"]) for r in self.rows]
        notes = [normalized(r["context_note"]) for r in self.rows]
        self.assertEqual((len(set(ids)), len(set(texts)), len(set(notes))), (1000, 1000, 1000))
        bags = [set(t.split()) for t in texts]
        for i, bag in enumerate(bags):
            for second in bags[i+1:]:
                self.assertLess(len(bag & second) / len(bag | second), 0.8)

    def test_privacy_actions(self):
        for reply in self.rows:
            text = reply["text"]
            self.assertNotRegex(text, r"(?i)[a-z0-9._%+-]+@[a-z0-9.-]+\\.[a-z]{2,}")
            self.assertNotRegex(text, r"(?:\\+?\\d[ \\-]?){11,}")
            self.assertNotRegex(text, r"(?i)(?:бот|я) (?:забанил|замутил|уже отправил|изменил настройки)")
            self.assertNotIn("token", text.casefold())

if __name__ == "__main__":
    unittest.main()
