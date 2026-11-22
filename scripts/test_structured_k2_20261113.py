"""K52-K54 staged Russian context replies: checkpoint, safety and cross-pack QA."""
import hashlib
import json
import re
import unicodedata
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STAGE = ROOT / "staging/ru/structured_information_20261113_delta_k2.json"
PREV = ROOT / "staging/ru/structured_information_20261111_delta_k.json"
SOURCE = ROOT / "packs/ru/structured_information_qa.json"
SOURCE_SHA256 = "55b3f6126d36cd92687d005b7fedf5a11df9ee61cf453103accdf1f13c8498f0"
EXPECTED_SUFFIXES = (52, 53, 54)
WORDS = re.compile(r"[^\W_]+", re.UNICODE)

def normalize(s):
    return " ".join(WORDS.findall(unicodedata.normalize("NFKC", s).casefold().replace("ё", "е")))

def tokenize(s):
    return set(normalize(s).split())

class K2StageTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = json.loads(STAGE.read_text(encoding="utf-8"))
        cls.previous = json.loads(PREV.read_text(encoding="utf-8"))
        cls.entries = cls.data["entries"]
        cls.new = [r for e in cls.entries for r in e["replies"]]

    def test_source_and_unregistered_status(self):
        manifest = json.loads((ROOT / "manifest.json").read_text(encoding="utf-8"))
        registered = {x["path"]: x["sha256"] for x in manifest["packs"]}
        self.assertEqual(registered["packs/ru/structured_information_qa.json"], SOURCE_SHA256)
        self.assertEqual(hashlib.sha256(SOURCE.read_bytes()).hexdigest(), SOURCE_SHA256)
        self.assertNotIn(STAGE.relative_to(ROOT).as_posix(), registered)
        self.assertFalse(self.data["consumer_registered"])
        self.assertEqual(self.data["audiences"], ["all_ai_bots"])
        self.assertTrue(all(self.data["constraints"][flag] for flag in
            ("read_only", "requires_direct_address", "requires_context_match",
             "no_personal_data", "no_sanctions")))
        self.assertLessEqual(STAGE.stat().st_size, 2 * 1024 * 1024)

    def test_exact_checkpoint(self):
        cp = self.data["checkpoint"]
        self.assertEqual((len(self.entries), len(self.new)), (54, 162))
        self.assertEqual((cp["processed_intents"], cp["added_candidates"], cp["added_per_intent"]), (54, 162, 3))
        self.assertEqual((cp["combined_per_intent"], cp["remaining_per_intent"], cp["remaining_total"]), (48, 52, 2808))
        self.assertEqual((cp["finished_100"], cp["partial_intents"]), (0, 54))
        before = {e["intent_id"]: e for e in self.previous["entries"]}
        self.assertEqual(set(before), {e["intent_id"] for e in self.entries})
        for e in self.entries:
            self.assertEqual(e["canonical_question"], before[e["intent_id"]]["canonical_question"])
            self.assertEqual((e["published_count"], e["previous_staged_count"], e["added_candidates"],
                              e["total_candidates_with_published"], e["remaining"], e["target"]),
                             (3, 42, 3, 48, 52, 100))
            self.assertEqual([r["id"] for r in e["replies"]],
                             [f"{e['intent_id']}_supp_{s}" for s in EXPECTED_SUFFIXES])

    def test_unique_safe_usable_replies(self):
        ids = set()
        texts = set()
        notes = set()
        for r in self.new:
            self.assertNotIn(r["id"], ids)
            self.assertNotIn(normalize(r["text"]), texts)
            self.assertNotIn(normalize(r["context_note"]), notes)
            ids.add(r["id"])
            texts.add(normalize(r["text"]))
            notes.add(normalize(r["context_note"]))
            self.assertEqual(r["language"], "ru")
            self.assertEqual(r["audiences"], ["all_ai_bots"])
            self.assertEqual(r["response_role"], "assistant_reply")
            self.assertEqual(r["context"], "direct")
            self.assertTrue(r["read_only"])
            self.assertTrue(len(r["text"]) >= 55)
            self.assertTrue(len(r["context_note"]) >= 25)
            self.assertTrue(len(r["avoid"]) >= 20)
            self.assertIsNone(re.search(r"[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}", r["text"] + r["context_note"]))
            self.assertFalse(any(x in normalize(r["text"]) for x in
                ("я забаню", "я удалил сообщение", "я выдал мут", "я сохранил твои данные")))

    def test_no_exact_or_near_lexical_repetition(self):
        older_texts = []
        for path in sorted((ROOT / "staging/ru").glob("structured_information_20261111_delta_*.json")):
            old = json.loads(path.read_text(encoding="utf-8"))
            older_texts.extend(r["text"] for e in old["entries"] for r in e["replies"])
        source = json.loads(SOURCE.read_text(encoding="utf-8"))
        older_texts.extend(t for r in source["records"] for t in [r["answer"], *r["variants"]])
        checked = set()
        known = []
        for s in older_texts:
            n = normalize(s)
            checked.add(n)
            known.append(tokenize(s))
        for r in self.new:
            n = normalize(r["text"])
            self.assertNotIn(n, checked, r["id"])
            a = tokenize(r["text"])
            for b in known:
                self.assertLess(len(a & b) / len(a | b), .70, r["id"])
            known.append(a)
            checked.add(n)

if __name__ == "__main__":
    unittest.main()
