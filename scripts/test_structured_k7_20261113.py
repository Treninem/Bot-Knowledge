"""K7 synthetic contextual RU answers: no consumer registration, permissions or sanctions."""
import hashlib
import json
import re
import unicodedata
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STAGE = ROOT / "staging/ru/structured_information_20261113_delta_k7.json"
STAGES = [
    ROOT / "staging/ru/structured_information_20261111_delta_k.json",
    ROOT / "staging/ru/structured_information_20261113_delta_k2.json",
    ROOT / "staging/ru/structured_information_20261113_delta_k3.json",
    ROOT / "staging/ru/structured_information_20261113_delta_k4.json",
    ROOT / "staging/ru/structured_information_20261113_delta_k5.json",
    ROOT / "staging/ru/structured_information_20261113_delta_k6.json",
]
PACK = ROOT / "packs/ru/structured_information_qa.json"
WORDS = re.compile(r"[^\W_]+", re.UNICODE)
EMAIL = re.compile(r"[\w.+-]+@[\w.-]+\.[a-zA-Z]{2,}")

def norm(value):
    return " ".join(WORDS.findall(unicodedata.normalize("NFKC", value).casefold().replace("ё", "е")))

def tokens(value):
    return set(norm(value).split())

class K7StageTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = json.loads(STAGE.read_text(encoding="utf-8"))
        cls.prior = [json.loads(p.read_text(encoding="utf-8")) for p in STAGES]
        cls.pack = json.loads(PACK.read_text(encoding="utf-8"))
        cls.entries = cls.data["entries"]
        cls.replies = [r for e in cls.entries for r in e["replies"]]

    def test_registered_pack_unchanged_and_stage_unregistered(self):
        manifest = json.loads((ROOT / "manifest.json").read_text(encoding="utf-8"))
        known = {p["path"]: p["sha256"] for p in manifest["packs"]}
        self.assertFalse(self.data["consumer_registered"])
        self.assertNotIn(STAGE.relative_to(ROOT).as_posix(), known)
        self.assertLessEqual(STAGE.stat().st_size, 2 * 1024 * 1024)
        self.assertEqual(self.data["source_pack_manifest_sha256"], known[self.data["source_pack"]])
        self.assertEqual(hashlib.sha256(PACK.read_bytes()).hexdigest(), known[self.data["source_pack"]])
        self.assertEqual(self.data["checked_source_main_sha"], self.data["checkpoint"]["source_main"])
        for flag in ("read_only", "requires_direct_address", "requires_context_match", "no_personal_data", "no_sanctions"):
            self.assertIs(self.data["constraints"][flag], True)

    def test_stable_54_intents_and_exact_count_delta(self):
        cp = self.data["checkpoint"]
        previous = {e["intent_id"]: e for e in self.prior[-1]["entries"]}
        self.assertEqual(len(self.entries), 54)
        self.assertEqual(len(self.replies), 54)
        self.assertEqual(len(self.replies), cp["added_candidates"])
        self.assertEqual(len(previous), 54)
        self.assertEqual({e["intent_id"] for e in self.entries}, set(previous))
        self.assertEqual(cp["combined_per_intent"], 60)
        self.assertEqual(cp["remaining_per_intent"], 40)
        self.assertEqual(cp["remaining_total"], 54 * 40)
        self.assertEqual(cp["partial_intents"], 54)
        self.assertEqual(cp["finished_100"], 0)
        for e in self.entries:
            self.assertEqual(e["canonical_question"], previous[e["intent_id"]]["canonical_question"])
            self.assertEqual(e["previous_staged_count"], 56)
            self.assertEqual(e["published_count"], 3)
            self.assertEqual(e["added_candidates"], 1)
            self.assertEqual(e["total_candidates_with_published"], 60)
            self.assertEqual(e["remaining"], 40)
            self.assertEqual([r["id"] for r in e["replies"]],
                             [e["intent_id"] + "_supp_66"])

    def test_ids_context_privacy_and_readonly(self):
        ids, replies, notes = set(), set(), set()
        for r in self.replies:
            self.assertNotIn(r["id"], ids)
            ids.add(r["id"])
            self.assertGreaterEqual(len(r["text"]), 55)
            self.assertGreaterEqual(len(r["context_note"]), 25)
            self.assertEqual(r["language"], "ru")
            self.assertEqual(r["audiences"], ["all_ai_bots"])
            self.assertEqual(r["response_role"], "assistant_reply")
            self.assertEqual(r["context"], "direct")
            self.assertIs(r["read_only"], True)
            self.assertIn("не применять санкции", r["avoid"])
            self.assertIsNone(EMAIL.search(r["text"] + " " + r["context_note"]))
            k, note = norm(r["text"]), norm(r["context_note"])
            self.assertNotIn(k, replies)
            self.assertNotIn(note, notes)
            replies.add(k)
            notes.add(note)

    def test_normalized_and_high_lexical_duplicates_against_K_and_published(self):
        all_text = [r["text"] for stage in self.prior for e in stage["entries"] for r in e["replies"]]
        all_text += [s for rec in self.pack["records"] for s in [rec["answer"], *rec["variants"]]]
        earlier_normal = {norm(s) for s in all_text}
        earlier_tokens = [tokens(s) for s in all_text]
        for r in self.replies:
            value = norm(r["text"])
            self.assertNotIn(value, earlier_normal, r["id"])
            t = tokens(r["text"])
            for old in earlier_tokens:
                self.assertLess(len(t & old) / len(t | old), 0.70, r["id"])
            earlier_normal.add(value)
            earlier_tokens.append(t)

    def test_context_notes_are_not_copies_of_answers(self):
        for r in self.replies:
            self.assertNotEqual(norm(r["text"]), norm(r["context_note"]))
            self.assertGreater(len(tokens(r["text"]) - tokens(r["context_note"])), 4)

if __name__ == "__main__":
    unittest.main()
