"""Read-only acceptance checks for ten generic RU help intents; no product claims."""
import hashlib
import json
import re
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STAGE = ROOT / "staging/ru/support_triage_20261110_context_pool.json"
STAGE_B = ROOT / "staging/ru/support_triage_20261110_context_delta_b.json"
RELATED = [
    "staging/ru/evidence_boundaries_t560_context_pool.json",
    "staging/ru/evidence_boundaries_t569_context_delta.json",
    "staging/ru/social_boundaries_t580_context_pool.json",
    "staging/ru/social_boundaries_t589_context_delta.json",
    "staging/ru/interpersonal_t590_context_pool.json",
    "staging/ru/interpersonal_t599_context_delta.json",
    "staging/ru/group_pragmatics_t600_context_pool.json",
    "staging/ru/group_pragmatics_t603_context_delta.json",
    "staging/ru/dialogue_repair_t554_context_pool.json",
    "staging/ru/dialogue_repair_t559_context_delta.json",
    "staging/ru/practical_dialogue_t534_context_pool.json",
    "staging/ru/practical_dialogue_t538_context_pool.json",
]

def normalized(s):
    return " ".join(re.findall(r"[^\W_]+", s.casefold().replace("ё", "е")))

def text_tokens(s):
    return set(normalized(s).split())

def git_blob(path):
    return subprocess.check_output(
        ["git", "hash-object", str(path)], cwd=ROOT, text=True
    ).strip()

class TestSupportTriage20261110(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.stage = json.loads(STAGE.read_text(encoding="utf-8"))
        cls.stage_b = json.loads(STAGE_B.read_text(encoding="utf-8"))

    def test_source_pack_and_scope(self):
        stage = self.stage
        self.assertEqual(stage["schema_version"], 1)
        self.assertEqual(stage["stage_type"], "supplemental_contextual_reply_pool")
        self.assertIs(stage["consumer_registered"], False)
        self.assertEqual(stage["audiences"], ["all_ai_bots"])
        self.assertEqual(stage["language"], "ru")
        for key in ("read_only", "requires_direct_address", "no_personal_data",
                    "no_sanctions", "requires_context_match"):
            self.assertIs(stage["constraints"][key], True)
        source = ROOT / stage["source_pack"]
        digest = hashlib.sha256(source.read_bytes()).hexdigest()
        self.assertEqual(digest, stage["source_pack_manifest_sha256"])
        self.assertEqual(git_blob(source), stage["source_pack_blob_sha"])
        manifest = json.loads((ROOT / "manifest.json").read_text(encoding="utf-8"))
        self.assertIn({"path": stage["source_pack"], "sha256": digest}, manifest["packs"])
        self.assertNotIn({"path": STAGE.relative_to(ROOT).as_posix()}, manifest["packs"])

    def test_counts_context_and_privacy(self):
        stage = self.stage
        checkpoint = stage["checkpoint"]
        self.assertEqual(checkpoint["processed_intents"], 10)
        self.assertEqual(checkpoint["prior_candidates"], 0)
        self.assertEqual(checkpoint["added_candidates"], 100)
        self.assertEqual(checkpoint["cumulative_candidates"], 100)
        self.assertEqual(checkpoint["remaining_total"], 900)
        self.assertEqual((checkpoint["finished_100"], checkpoint["partial_intents"]), (0, 10))
        self.assertEqual(len(stage["entries"]), 10)
        ids, texts, notes = set(), set(), set()
        self.assertEqual(len({e["intent_id"] for e in stage["entries"]}), 10)
        for entry in stage["entries"]:
            self.assertEqual(entry["target"], 100)
            self.assertEqual((entry["prior_for_stable_id"], entry["added_candidates"],
                              entry["total_staged"], entry["remaining"]), (0, 10, 10, 90))
            self.assertEqual(entry["audiences"], ["all_ai_bots"])
            self.assertEqual(entry["response_role"], "assistant_reply")
            self.assertEqual(len(entry["replies"]), 10)
            for seq, reply in enumerate(entry["replies"], 1):
                self.assertEqual(reply["id"], f'{entry["intent_id"]}_{seq:02d}')
                self.assertEqual(reply["language"], "ru")
                self.assertEqual(reply["audiences"], ["all_ai_bots"])
                self.assertEqual(reply["context"], "direct")
                self.assertIs(reply["read_only"], True)
                self.assertIn("совпадении условия", reply["avoid"])
                for value, dest in ((reply["id"], ids), (normalized(reply["text"]), texts),
                                    (normalized(reply["context_note"]), notes)):
                    self.assertTrue(value)
                    self.assertNotIn(value, dest)
                    dest.add(value)
                self.assertNotRegex(reply["text"], r"https?://|[A-Za-z0-9_.+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
                self.assertNotRegex(reply["text"], r"(?<!\w)\+?\d[\d ()-]{8,}\d(?!\w)")
        self.assertEqual((len(ids), len(texts), len(notes)), (100, 100, 100))

    def test_delta_lineage_and_second_hundred(self):
        other = self.stage_b
        self.assertEqual(other["parent_stage"], STAGE.relative_to(ROOT).as_posix())
        self.assertEqual(other["parent_stage_blob_sha"], git_blob(STAGE))
        for key in ("source_pack", "source_pack_manifest_sha256",
                    "source_pack_blob_sha", "checked_source_main_sha"):
            self.assertEqual(other[key], self.stage[key])
        self.assertIs(other["consumer_registered"], False)
        self.assertEqual(other["audiences"], ["all_ai_bots"])
        for key in ("read_only", "requires_direct_address", "no_personal_data",
                    "no_sanctions", "requires_context_match"):
            self.assertIs(other["constraints"][key], True)
        checkpoint = other["checkpoint"]
        self.assertEqual((checkpoint["prior_candidates"], checkpoint["added_candidates"],
                          checkpoint["cumulative_candidates"], checkpoint["remaining_total"]),
                         (100, 100, 200, 800))
        self.assertEqual((checkpoint["processed_intents"], checkpoint["partial_intents"],
                          checkpoint["finished_100"]), (10, 10, 0))
        existing_text = {normalized(r["text"]) for e in self.stage["entries"]
                         for r in e["replies"]}
        existing_notes = {normalized(r["context_note"]) for e in self.stage["entries"]
                          for r in e["replies"]}
        new_ids, new_text, new_notes = set(), set(), set()
        self.assertEqual(len(other["entries"]), 10)
        for entry in other["entries"]:
            self.assertIn(entry["intent_id"], {e["intent_id"] for e in self.stage["entries"]})
            self.assertEqual((entry["target"], entry["prior_for_stable_id"],
                              entry["added_candidates"], entry["total_staged"], entry["remaining"]),
                             (100, 10, 10, 20, 80))
            self.assertEqual(len(entry["replies"]), 10)
            for i, reply in enumerate(entry["replies"], 11):
                self.assertEqual(reply["id"], f'{entry["intent_id"]}_{i:02d}')
                self.assertEqual(reply["language"], "ru")
                self.assertEqual(reply["audiences"], ["all_ai_bots"])
                self.assertEqual(reply["context"], "direct")
                self.assertIs(reply["read_only"], True)
                self.assertIn("совпадении условия", reply["avoid"])
                self.assertNotRegex(reply["text"], r"https?://|[A-Za-z0-9_.+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
                self.assertNotRegex(reply["text"], r"(?<!\w)\+?\d[\d ()-]{8,}\d(?!\w)")
                self.assertNotIn(normalized(reply["text"]), existing_text)
                self.assertNotIn(normalized(reply["context_note"]), existing_notes)
                self.assertNotIn(reply["id"], new_ids)
                self.assertNotIn(normalized(reply["text"]), new_text)
                self.assertNotIn(normalized(reply["context_note"]), new_notes)
                new_ids.add(reply["id"])
                new_text.add(normalized(reply["text"]))
                new_notes.add(normalized(reply["context_note"]))
        self.assertEqual((len(new_ids), len(new_text), len(new_notes)), (100, 100, 100))

    def test_no_near_duplicates_with_related_staged_replies(self):
        current = [r["text"] for document in (self.stage, self.stage_b)
                   for e in document["entries"] for r in e["replies"]]
        previous = []
        for path in RELATED:
            obj = json.loads((ROOT / path).read_text(encoding="utf-8"))
            self.assertIs(obj["consumer_registered"], False)
            previous.extend(r["text"] for e in obj["entries"] for r in e["replies"])
        self.assertGreaterEqual(len(previous), 1000)
        existing = set(map(normalized, previous))
        candidates = list(map(text_tokens, current))
        for i, value in enumerate(current):
            self.assertNotIn(normalized(value), existing)
            for other in candidates[i + 1:]:
                self.assertLess(len(candidates[i] & other) / len(candidates[i] | other), 0.80)
        reference = list(map(text_tokens, previous))
        for candidate in candidates:
            for other in reference:
                self.assertLess(len(candidate & other) / len(candidate | other), 0.80)

if __name__ == "__main__":
    unittest.main()
