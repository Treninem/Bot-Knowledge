"""T526 exact inventory: 10 stable intents, 340 total candidate mini-stories."""
from __future__ import annotations
import hashlib
import json
import subprocess
import unicodedata
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = "packs/ru/social_dialogues.json"
STAGES = [524, 525, 526]
COUNTS = {524: (12, 12, 88), 525: (12, 24, 76), 526: (10, 34, 66)}


def norm(text):
    value = unicodedata.normalize("NFKC", text).casefold().replace("ё", "е")
    return " ".join("".join(c if c.isalnum() else " " for c in value).split())


def strings(data):
    if isinstance(data, str):
        yield data
    elif isinstance(data, list):
        for item in data:
            yield from strings(item)
    elif isinstance(data, dict):
        for item in data.values():
            yield from strings(item)


class TestCreativeT526(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.stages = {n: json.loads((ROOT / f"staging/ru/creative_microstories_t{n}_context_pool.json").read_text("utf-8")) for n in STAGES}
        cls.manifest = json.loads((ROOT / "manifest.json").read_text("utf-8"))
        cls.source = json.loads((ROOT / SOURCE).read_text("utf-8"))

    def test_hash_provenance_and_non_registration(self):
        raw = (ROOT / SOURCE).read_bytes()
        actual = hashlib.sha256(raw).hexdigest()
        expected = [p["sha256"] for p in self.manifest["packs"] if p["path"] == SOURCE]
        self.assertEqual(expected, [actual])
        git_blob = subprocess.check_output(["git", "hash-object", str(ROOT / SOURCE)], cwd=ROOT, text=True).strip()
        for n in STAGES:
            stage = self.stages[n]
            self.assertEqual(stage["source_pack"], SOURCE)
            self.assertEqual(stage["source_pack_manifest_sha256"], actual)
            self.assertEqual(stage["source_pack_blob_sha"], git_blob)
            self.assertFalse(stage["consumer_registered"])
            self.assertEqual(stage["audiences"], ["all_ai_bots"])
            for flag in ("fiction_must_be_labeled", "requires_explicit_creative_request", "no_sanctions"):
                self.assertTrue(stage["constraints"][flag])
            self.assertNotIn(f"staging/ru/creative_microstories_t{n}_context_pool.json",
                             [p["path"] for p in self.manifest["packs"]])

    def test_exact_cumulative_delta_and_scope(self):
        stages = self.stages
        ids, texts, notes = set(), set(), set()
        canon = {e["intent_id"]: e["canonical_question"] for e in stages[524]["entries"]}
        self.assertEqual(len(canon), 10)
        previous = 0
        for n in STAGES:
            pack = stages[n]
            self.assertEqual(pack["checkpoint"]["added_candidates"], 10 * COUNTS[n][0])
            self.assertEqual(pack["checkpoint"]["remaining_total"], 10 * COUNTS[n][2])
            self.assertEqual(pack["checkpoint"]["processed_intents"], 10)
            self.assertEqual(pack["checkpoint"]["finished_100"], 0)
            self.assertEqual({e["intent_id"] for e in pack["entries"]}, set(canon))
            for e in pack["entries"]:
                added, cumulative, remain = COUNTS[n]
                self.assertEqual(e["canonical_question"], canon[e["intent_id"]])
                self.assertEqual(e["added_candidates"], added)
                self.assertEqual(e["total_staged"], cumulative)
                self.assertEqual(e["remaining"], remain)
                self.assertEqual(e["target"], 100)
                self.assertEqual(len(e["replies"]), added)
                if n > 524:
                    self.assertEqual(e["prior_for_stable_id"], previous)
                for reply in e["replies"]:
                    self.assertNotIn(reply["id"], ids)
                    self.assertNotIn(norm(reply["text"]), texts)
                    self.assertNotIn(norm(reply["context_note"]), notes)
                    ids.add(reply["id"])
                    texts.add(norm(reply["text"]))
                    notes.add(norm(reply["context_note"]))
                    self.assertEqual(reply["format"], "microstory")
                    self.assertEqual(reply["language"], "ru")
                    self.assertEqual(reply["audiences"], ["all_ai_bots"])
                    self.assertEqual(reply["context"], "direct")
                    self.assertTrue(reply["read_only"])
                    self.assertIn("вымышленную", reply["context_note"])
                    self.assertIn("Это вымысел", reply["avoid"])
                    self.assertTrue(50 <= len(reply["text"]) <= 480)
                    self.assertNotRegex(reply["text"], r"(?i)https?://|@\w+|(?:\+7|\b8)\d{10}\b")
            previous = COUNTS[n][1]
        self.assertEqual(len(ids), 340)
        self.assertEqual(len(texts), 340)
        self.assertEqual(len(notes), 340)
        source_strings = {norm(s) for s in strings(self.source) if len(s) > 50}
        self.assertTrue(texts.isdisjoint(source_strings))

    def test_lexical_repeats_with_prior_history(self):
        prior = []
        for n in STAGES:
            for entry in self.stages[n]["entries"]:
                for reply in entry["replies"]:
                    token_set = set(norm(reply["text"]).split())
                    self.assertGreaterEqual(len(token_set), 8)
                    for other in prior:
                        jaccard = len(token_set & other) / len(token_set | other)
                        self.assertLess(jaccard, 0.78)
                    prior.append(token_set)
        self.assertEqual(len(prior), 340)


if __name__ == "__main__":
    unittest.main()
