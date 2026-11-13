"""Read-only staging N81–N84 regression; no candidate is consumer-registered."""
from __future__ import annotations

import hashlib
import json
import re
import unicodedata
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "packs/ru/structured_information_qa.json"
MANIFEST = ROOT / "manifest.json"
L = ROOT / "staging/ru/structured_information_20261111_delta_l.json"
M = ROOT / "staging/ru/structured_information_20261112_delta_m.json"
N = ROOT / "staging/ru/structured_information_20261113_delta_n.json"
OLDER = [
    ROOT / f"staging/ru/structured_information_20261111_delta_{letter}.json"
    for letter in "abcdefghij"
]
SOURCE_SHA = "55b3f6126d36cd92687d005b7fedf5a11df9ee61cf453103accdf1f13c8498f0"
SOURCE_GIT_BLOB = "8b3d596b5b50d3d319ebf450c96d5623fc99d26a"
WORDS = re.compile(r"[^\W_]+", re.UNICODE)
EMAIL = re.compile(r"[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}")
# Some strings are naturally similar, so this lexical screen is not a semantic certificate.
JACCARD_LIMIT = 0.70

def normalize(value: str) -> str:
    return " ".join(WORDS.findall(unicodedata.normalize("NFKC", value).casefold().replace("ё", "е")))

def replies(data: dict) -> list[dict]:
    return [r for entry in data["entries"] for r in entry["replies"]]

class StructuredNContinuation(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.n = json.loads(N.read_text(encoding="utf-8"))
        cls.m = json.loads(M.read_text(encoding="utf-8"))
        cls.l = json.loads(L.read_text(encoding="utf-8"))
        cls.source = json.loads(SOURCE.read_text(encoding="utf-8"))
        cls.older = []
        for path in OLDER:
            cls.older.extend(replies(json.loads(path.read_text(encoding="utf-8"))))
        cls.n_replies = replies(cls.n)
        cls.previous = cls.older + replies(cls.l) + replies(cls.m)

    def test_published_pack_sha_and_no_registration(self):
        raw = SOURCE.read_bytes()
        self.assertEqual(hashlib.sha256(raw).hexdigest(), SOURCE_SHA)
        self.assertEqual(hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest(), SOURCE_GIT_BLOB)
        manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
        registered = {item["path"]: item["sha256"] for item in manifest["packs"]}
        self.assertEqual(registered["packs/ru/structured_information_qa.json"], SOURCE_SHA)
        self.assertNotIn("staging/ru/structured_information_20261113_delta_n.json", registered)

    def test_structure_and_exact_checkpoint(self):
        self.assertLessEqual(N.stat().st_size, 2 * 1024 * 1024)
        self.assertEqual(self.n["schema_version"], 1)
        self.assertFalse(self.n["consumer_registered"])
        self.assertEqual(self.n["audiences"], ["all_ai_bots"])
        self.assertEqual(self.n["language"], "ru")
        self.assertTrue(all(self.n["constraints"][k] for k in (
            "read_only", "requires_direct_address", "requires_context_match",
            "no_personal_data", "no_sanctions"
        )))
        self.assertEqual(len(self.n["entries"]), 60)
        self.assertEqual(len(self.n_replies), 240)
        self.assertEqual(len(replies(self.l)), 1860)
        self.assertEqual(len(replies(self.m)), 1740)
        c = self.n["checkpoint"]
        self.assertEqual(c["processed_intents"], 60)
        self.assertEqual(c["new_replies"], len(self.n_replies))
        self.assertEqual(c["prior_L_replies"], 1860)
        self.assertEqual(c["prior_M_replies"], 1740)
        self.assertEqual(c["combined_L_M_N_replies"], 3840)
        self.assertEqual(c["total_per_intent"], 78)
        self.assertEqual(c["remaining_per_intent"], 22)
        self.assertEqual(c["remaining_total"], 1320)
        self.assertEqual(c["partial_intents"], 60)
        self.assertEqual(c["finished_100"], 0)
        self.assertEqual(c["next_suffix"], 85)
        for l_entry, m_entry, n_entry in zip(self.l["entries"], self.m["entries"], self.n["entries"]):
            self.assertEqual(l_entry["intent_id"], m_entry["intent_id"])
            self.assertEqual(l_entry["intent_id"], n_entry["intent_id"])
            self.assertEqual(
                (n_entry["published_count"], n_entry["previous_staged_count"], n_entry["prior_L_count"], n_entry["prior_M_count"]),
                (3, 11, 31, 29),
            )
            self.assertEqual((n_entry["added_candidates"], n_entry["total_candidates_with_published"], n_entry["remaining"], n_entry["target"]),
                             (4, 78, 22, 100))
            self.assertEqual([r["id"] for r in n_entry["replies"]],
                             [f"{n_entry['intent_id']}_supp_{suffix}" for suffix in range(81, 85)])

    def test_lexical_distance_and_safety(self):
        previous = [v for record in self.source["records"] for v in (record["answer"], *record["variants"])]
        previous.extend(r["text"] for r in self.previous)
        normalized = set(map(normalize, previous))
        token_sets = [set(x.split()) for x in normalized if x]
        ids = {r["id"] for r in self.previous}
        notes = {normalize(r["context_note"]) for r in self.previous}
        for r in self.n_replies:
            answer, note = normalize(r["text"]), normalize(r["context_note"])
            self.assertNotIn(r["id"], ids, r["id"])
            self.assertNotIn(answer, normalized, r["id"])
            self.assertNotIn(note, notes, r["id"])
            self.assertGreaterEqual(len(r["text"]), 45, r["id"])
            self.assertGreaterEqual(len(r["context_note"]), 35, r["id"])
            self.assertEqual(r["language"], "ru")
            self.assertEqual(r["audiences"], ["all_ai_bots"])
            self.assertEqual(r["context"], "direct")
            self.assertEqual(r["response_role"], "assistant_reply")
            self.assertTrue(r["read_only"])
            self.assertIsNone(EMAIL.search(r["text"] + " " + r["context_note"]))
            tokens = set(answer.split())
            for old in token_sets:
                self.assertLess(len(tokens & old) / len(tokens | old), JACCARD_LIMIT, r["id"])
            ids.add(r["id"])
            normalized.add(answer)
            notes.add(note)
            token_sets.append(tokens)

    def test_distinct_selection_notes_within_each_intent(self):
        for entry in self.n["entries"]:
            notes = [set(normalize(r["context_note"]).split()) for r in entry["replies"]]
            for i, left in enumerate(notes):
                for right in notes[i + 1:]:
                    self.assertLess(len(left & right) / len(left | right), JACCARD_LIMIT, entry["intent_id"])

if __name__ == "__main__":
    unittest.main()
