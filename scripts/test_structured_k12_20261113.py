"""K12 read-only structured RU candidate verification. No consumer or action access."""
import hashlib
import json
import re
import unicodedata
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STAGE = ROOT / "staging/ru/structured_information_20261113_delta_k12.json"
PRIOR = [
    "staging/ru/structured_information_20261111_delta_k.json",
    *[f"staging/ru/structured_information_20261113_delta_k{n}.json" for n in range(2, 12)]
]
PACK = ROOT / "packs/ru/structured_information_qa.json"
WORDS = re.compile(r"[^\W_]+", re.UNICODE)
EMAIL = re.compile(r"[\w.+-]+@[\w.-]+\.[a-zA-Z]{2,}")

def norm(s):
    return " ".join(WORDS.findall(unicodedata.normalize("NFKC", s).casefold().replace("ё", "е")))

def tokens(s):
    return set(norm(s).split())

class K12StageTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = json.loads(STAGE.read_text(encoding="utf-8"))
        cls.prior = [json.loads((ROOT / p).read_text(encoding="utf-8")) for p in PRIOR]
        cls.pack = json.loads(PACK.read_text(encoding="utf-8"))
        cls.entries = cls.data["entries"]
        cls.replies = [r for e in cls.entries for r in e["replies"]]

    def test_readonly_unregistered_source_and_sha(self):
        d = self.data
        manifest = json.loads((ROOT / "manifest.json").read_text(encoding="utf-8"))
        registered = {e["path"]: e["sha256"] for e in manifest["packs"]}
        self.assertFalse(d["consumer_registered"])
        self.assertNotIn(STAGE.relative_to(ROOT).as_posix(), registered)
        self.assertEqual(d["source_pack_manifest_sha256"], registered[d["source_pack"]])
        self.assertEqual(hashlib.sha256(PACK.read_bytes()).hexdigest(), registered[d["source_pack"]])
        self.assertEqual(d["checked_source_main_sha"], d["checkpoint"]["source_main"])
        self.assertLess(STAGE.stat().st_size, 2 * 1024 * 1024)
        self.assertEqual(d["audiences"], ["all_ai_bots"])
        for flag in ("read_only", "requires_direct_address", "requires_context_match", "no_personal_data", "no_sanctions"):
            self.assertIs(d["constraints"][flag], True)

    def test_exact_progress_and_stable_intents(self):
        cp = self.data["checkpoint"]
        old = {e["intent_id"]: e for e in self.prior[-1]["entries"]}
        self.assertEqual(len(self.entries), 54)
        self.assertEqual(len(self.replies), 54)
        self.assertEqual(set(e["intent_id"] for e in self.entries), set(old))
        for key, expected in {
            "previous_staged_per_intent": 65, "added_per_intent": 1,
            "added_candidates": 54, "combined_per_intent": 69,
            "remaining_per_intent": 31, "remaining_total": 1674,
            "partial_intents": 54, "finished_100": 0,
        }.items():
            self.assertEqual(cp[key], expected, key)
        self.assertEqual(self.data["prior_stages"], PRIOR)
        for e in self.entries:
            self.assertEqual(e["canonical_question"], old[e["intent_id"]]["canonical_question"])
            self.assertEqual((e["published_count"], e["previous_staged_count"],
                              e["added_candidates"], e["total_candidates_with_published"], e["remaining"]),
                             (3, 65, 1, 69, 31))
            self.assertEqual([r["id"] for r in e["replies"]],
                             [e["intent_id"] + "_supp_75"])

    def test_privacy_context_and_local_uniqueness(self):
        ids, responses, contexts = set(), set(), set()
        for r in self.replies:
            self.assertNotIn(r["id"], ids)
            self.assertGreaterEqual(len(r["text"]), 55, r["id"])
            self.assertGreaterEqual(len(r["context_note"]), 25, r["id"])
            self.assertEqual(r["language"], "ru")
            self.assertEqual(r["audiences"], ["all_ai_bots"])
            self.assertEqual(r["context"], "direct")
            self.assertEqual(r["response_role"], "assistant_reply")
            self.assertIs(r["read_only"], True)
            self.assertIn("не применять санкции", r["avoid"])
            self.assertIsNone(EMAIL.search(r["text"] + " " + r["context_note"]))
            self.assertNotIn(norm(r["text"]), responses)
            self.assertNotIn(norm(r["context_note"]), contexts)
            ids.add(r["id"])
            responses.add(norm(r["text"]))
            contexts.add(norm(r["context_note"]))

    def test_normalized_and_high_lexical_duplicates_all_stages_and_pack(self):
        prior = [r["text"] for stage in self.prior for e in stage["entries"] for r in e["replies"]]
        prior += [text for item in self.pack["records"] for text in [item["answer"], *item["variants"]]]
        existing_norm = {norm(s) for s in prior}
        existing_tokens = [tokens(s) for s in prior]
        for r in self.replies:
            n, t = norm(r["text"]), tokens(r["text"])
            self.assertNotIn(n, existing_norm, r["id"])
            for old in existing_tokens:
                self.assertLess(len(t & old) / len(t | old), 0.70, r["id"])
            existing_norm.add(n)
            existing_tokens.append(t)

    def test_context_notes_distinct_from_responses(self):
        for r in self.replies:
            self.assertNotEqual(norm(r["text"]), norm(r["context_note"]))
            self.assertGreater(len(tokens(r["text"]) - tokens(r["context_note"])), 4)

if __name__ == "__main__":
    unittest.main()
