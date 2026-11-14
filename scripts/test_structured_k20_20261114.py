"""Check K89 synthetic replies against all earlier K stages and registered source."""
import hashlib
import json
import re
import unicodedata
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STAGE = ROOT / "staging/ru/structured_information_20261114_delta_k20.json"
PRIOR = ["staging/ru/structured_information_20261111_delta_k.json"] + [
    f"staging/ru/structured_information_20261113_delta_k{i}.json"
    for i in range(2, 14)
] + [
    f"staging/ru/structured_information_20261114_delta_k{i}.json"
    for i in range(14, 20)
]
PACK = ROOT / "packs/ru/structured_information_qa.json"
WORD = re.compile(r"[^\W_]+", re.UNICODE)


def norm(s):
    return " ".join(WORD.findall(unicodedata.normalize("NFKC", s).casefold().replace("ё", "е")))


def words(s):
    return set(norm(s).split())


class K20Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = json.loads(STAGE.read_text(encoding="utf-8"))
        cls.old = [json.loads((ROOT / p).read_text(encoding="utf-8")) for p in PRIOR]
        cls.pack = json.loads(PACK.read_text(encoding="utf-8"))
        cls.replies = [r for e in cls.data["entries"] for r in e["replies"]]

    def test_lineage_and_counts(self):
        d, c = self.data, self.data["checkpoint"]
        self.assertEqual(d["prior_stages"], PRIOR)
        self.assertEqual(len(d["entries"]), 54)
        self.assertEqual(len(self.replies), 54)
        expected = {
            "processed_intents": 54, "published_per_intent": 3,
            "previous_staged_per_intent": 79, "added_per_intent": 1,
            "added_candidates": 54, "combined_per_intent": 83,
            "remaining_per_intent": 17, "remaining_total": 918,
            "finished_100": 0, "partial_intents": 54, "duplicate_rejections": 0
        }
        for key, value in expected.items():
            self.assertEqual(c[key], value, key)
        previous = {e["intent_id"]: e for e in self.old[-1]["entries"]}
        self.assertEqual(set(previous), {e["intent_id"] for e in d["entries"]})
        for e in d["entries"]:
            self.assertEqual(e["canonical_question"], previous[e["intent_id"]]["canonical_question"])
            self.assertEqual(
                (e["published_count"], e["previous_staged_count"], e["added_candidates"],
                 e["total_candidates_with_published"], e["remaining"]),
                (3, 79, 1, 83, 17)
            )
            self.assertEqual(
                {r["id"] for r in e["replies"]},
                {e["intent_id"] + "_supp_89"}
            )

    def test_source_hash_and_scope(self):
        d = self.data
        m = json.loads((ROOT / "manifest.json").read_text(encoding="utf-8"))
        registered = {p["path"]: p["sha256"] for p in m["packs"]}
        self.assertFalse(d["consumer_registered"])
        self.assertNotIn(STAGE.relative_to(ROOT).as_posix(), registered)
        self.assertEqual(d["source_pack_manifest_sha256"], registered[d["source_pack"]])
        self.assertEqual(hashlib.sha256(PACK.read_bytes()).hexdigest(), registered[d["source_pack"]])
        self.assertLess(STAGE.stat().st_size, 2 * 1024 * 1024)
        self.assertEqual(d["audiences"], ["all_ai_bots"])
        for flag in ("read_only", "requires_direct_address", "requires_context_match",
                     "no_personal_data", "no_sanctions"):
            self.assertTrue(d["constraints"][flag], flag)

    def test_unique_context_safety(self):
        ids, texts, notes = set(), set(), set()
        for r in self.replies:
            for store, value in ((ids, r["id"]), (texts, norm(r["text"])),
                                 (notes, norm(r["context_note"]))):
                self.assertNotIn(value, store, r["id"])
                store.add(value)
            self.assertGreaterEqual(len(r["text"]), 65)
            self.assertGreaterEqual(len(r["context_note"]), 25)
            self.assertEqual(r["language"], "ru")
            self.assertEqual(r["context"], "direct")
            self.assertEqual(r["audiences"], ["all_ai_bots"])
            self.assertEqual(r["response_role"], "assistant_reply")
            self.assertTrue(r["read_only"])
            self.assertIn("не применять санкции", r["avoid"])
            self.assertNotIn("@", r["text"] + r["context_note"])

    def test_no_lexical_duplicates(self):
        previous = [r["text"] for d in self.old for e in d["entries"] for r in e["replies"]]
        previous += [text for e in self.pack["records"] for text in [e["answer"], *e["variants"]]]
        norms = {norm(x) for x in previous}
        token_sets = [words(x) for x in previous]
        for r in self.replies:
            normalized, t = norm(r["text"]), words(r["text"])
            self.assertNotIn(normalized, norms, r["id"])
            for u in token_sets:
                self.assertLess(len(t & u) / len(t | u), 0.70, r["id"])
            norms.add(normalized)
            token_sets.append(t)


if __name__ == "__main__":
    unittest.main()
