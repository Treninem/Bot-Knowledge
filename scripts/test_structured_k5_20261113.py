"""K5 staged contextual Russian structured QA; no consumer registration."""
import hashlib
import json
import re
import unicodedata
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STAGE = ROOT / "staging/ru/structured_information_20261113_delta_k5.json"
STAGES = [
    ROOT / "staging/ru/structured_information_20261111_delta_k.json",
    ROOT / "staging/ru/structured_information_20261113_delta_k2.json",
    ROOT / "staging/ru/structured_information_20261113_delta_k3.json",
    ROOT / "staging/ru/structured_information_20261113_delta_k4.json",
]
PACK = ROOT / "packs/ru/structured_information_qa.json"
WORDS = re.compile(r"[^\\W_]+", re.UNICODE)
MAIL = re.compile(r"[\\w.+-]+@[\\w.-]+\\.[A-Za-z]{2,}")

def norm(value):
    return " ".join(WORDS.findall(unicodedata.normalize("NFKC", value).casefold().replace("ё", "е")))

def tokens(value):
    return set(norm(value).split())

class K5StageTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = json.loads(STAGE.read_text(encoding="utf-8"))
        cls.prior = [json.loads(p.read_text(encoding="utf-8")) for p in STAGES]
        cls.pack = json.loads(PACK.read_text(encoding="utf-8"))
        cls.entries = cls.data["entries"]
        cls.replies = [r for e in cls.entries for r in e["replies"]]

    def test_unregistered_bounded_and_source_hash(self):
        manifest = json.loads((ROOT / "manifest.json").read_text(encoding="utf-8"))
        registered = {p["path"]: p["sha256"] for p in manifest["packs"]}
        self.assertFalse(self.data["consumer_registered"])
        self.assertNotIn(STAGE.relative_to(ROOT).as_posix(), registered)
        self.assertLessEqual(STAGE.stat().st_size, 2 * 1024 * 1024)
        self.assertEqual(self.data["source_pack_manifest_sha256"], registered[self.data["source_pack"]])
        self.assertEqual(hashlib.sha256(PACK.read_bytes()).hexdigest(), self.data["source_pack_manifest_sha256"])
        for flag in ("read_only", "requires_direct_address", "requires_context_match", "no_personal_data", "no_sanctions"):
            self.assertIs(self.data["constraints"][flag], True)

    def test_exact_counts_and_stable_intents(self):
        cp = self.data["checkpoint"]
        previous = {e["intent_id"]: e for e in self.prior[-1]["entries"]}
        self.assertEqual(len(self.entries), 54)
        self.assertEqual(len(self.replies), cp["added_candidates"])
        self.assertEqual(len({e["intent_id"] for e in self.entries}), 54)
        self.assertEqual(set(previous), {e["intent_id"] for e in self.entries})
        self.assertEqual(cp["combined_per_intent"] + cp["remaining_per_intent"], 100)
        self.assertEqual(cp["remaining_total"], 54 * cp["remaining_per_intent"])
        for e in self.entries:
            self.assertEqual(e["canonical_question"], previous[e["intent_id"]]["canonical_question"])
            self.assertEqual(e["previous_staged_count"], 51)
            self.assertEqual(len(e["replies"]), e["added_candidates"])
            self.assertEqual(e["total_candidates_with_published"], 3 + 51 + e["added_candidates"])
            self.assertEqual(e["remaining"], 100 - e["total_candidates_with_published"])
            self.assertEqual([r["id"] for r in e["replies"]],
                             [e["intent_id"] + "_supp_" + str(s) for s in range(61, 61 + len(e["replies"]))])

    def test_reply_shape_privacy_and_context(self):
        seen_ids, seen_notes = set(), set()
        for r in self.replies:
            self.assertNotIn(r["id"], seen_ids)
            seen_ids.add(r["id"])
            note = norm(r["context_note"])
            self.assertNotIn(note, seen_notes)
            seen_notes.add(note)
            self.assertGreaterEqual(len(r["text"]), 55)
            self.assertGreaterEqual(len(r["context_note"]), 25)
            self.assertEqual(r["language"], "ru")
            self.assertEqual(r["audiences"], ["all_ai_bots"])
            self.assertEqual(r["response_role"], "assistant_reply")
            self.assertEqual(r["context"], "direct")
            self.assertIs(r["read_only"], True)
            self.assertFalse(MAIL.search(r["text"] + " " + r["context_note"]))

    def test_exact_and_high_lexical_duplicates(self):
        prior_texts = [r["text"] for obj in self.prior for e in obj["entries"] for r in e["replies"]]
        prior_texts.extend(v for rec in self.pack["records"] for v in [rec["answer"], *rec["variants"]])
        normalized = set(map(norm, prior_texts))
        seen_tokens = list(map(tokens, prior_texts))
        for reply in self.replies:
            value = norm(reply["text"])
            self.assertNotIn(value, normalized, reply["id"])
            item_tokens = tokens(reply["text"])
            for earlier in seen_tokens:
                similarity = len(item_tokens & earlier) / len(item_tokens | earlier)
                self.assertLess(similarity, 0.70, reply["id"])
            normalized.add(value)
            seen_tokens.append(item_tokens)

if __name__ == "__main__":
    unittest.main()
