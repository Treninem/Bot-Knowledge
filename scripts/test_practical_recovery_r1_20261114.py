"""QA for unregistered, context-gated practical recovery candidates R1."""
import hashlib
import json
import re
import unicodedata
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STAGE_PATH = "staging/ru/practical_recovery_context_r1_20261114.json"
SOURCE_PATH = "packs/ru/practical_recovery_qa.json"


def normalize(s):
    s = unicodedata.normalize("NFKC", s).casefold().replace("ё", "е")
    return " ".join(re.findall(r"[^\W_]+", s))


def wordset(s):
    return {x for x in normalize(s).split() if len(x) > 2}


def similarity(a, b):
    x, y = wordset(a), wordset(b)
    return len(x & y) / max(1, len(x | y))


def select_scoped_reply(entry, *, addressed=False, context_note=None):
    """Reference fail-closed selector, NOT a verified production consumer."""
    if not addressed or not context_note:
        return None
    matches = [r for r in entry["replies"]
               if r["context"] == "direct"
               and normalize(r["context_note"]) == normalize(context_note)]
    return matches[0]["text"] if len(matches) == 1 else None


class PracticalRecoveryR1(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = json.loads((ROOT / STAGE_PATH).read_text(encoding="utf-8"))
        cls.source_bytes = (ROOT / SOURCE_PATH).read_bytes()
        cls.source = json.loads(cls.source_bytes)
        cls.manifest = json.loads((ROOT / "manifest.json").read_text(encoding="utf-8"))

    def test_source_integrity_and_isolation(self):
        d = self.data
        known = {p["path"]: p["sha256"] for p in self.manifest["packs"]}
        self.assertEqual(d["source_pack"], SOURCE_PATH)
        self.assertEqual(known[SOURCE_PATH], d["source_pack_manifest_sha256"])
        self.assertEqual(hashlib.sha256(self.source_bytes).hexdigest(),
                         d["source_pack_manifest_sha256"])
        blob = b"blob " + str(len(self.source_bytes)).encode() + b"\0" + self.source_bytes
        self.assertEqual(hashlib.sha1(blob).hexdigest(), d["source_pack_blob_sha"])
        self.assertNotIn(STAGE_PATH, known)
        self.assertFalse(d["consumer_registered"])
        self.assertLess((ROOT / STAGE_PATH).stat().st_size, 2 * 1024 * 1024)

    def test_exact_coverage_and_ids(self):
        d = self.data
        c = d["checkpoint"]
        published = {r["id"]: r for r in self.source["records"]}
        self.assertEqual((len(published), len(d["entries"]), c["processed_intents"],
                          c["new_candidates"]), (24, 24, 24, 120))
        self.assertEqual((c["editorial_approved_candidates"], c["editorial_approved_100_sets"]),
                         (0, 0))
        self.assertEqual(d["current_main_reverification"], {
            "commit_sha": "d43134b9072c7ceff44cfcf63d5d11c0d0771d7a",
            "manifest_version": "2026.11.17.030",
            "source_pack_manifest_sha256": "be8ae1408cf42816adc3f8ba818b3f004318617ba2e878e72edd85cf7eb4954e",
            "source_pack_blob_sha": "21bf261970d1bdcf0f9fb8fb3383772b86b2dc2f",
        })
        seen = set()
        for e in d["entries"]:
            self.assertIn(e["intent_id"], published)
            old = published[e["intent_id"]]
            self.assertEqual(e["canonical_question"], old["question"])
            self.assertEqual(len(old["variants"]), 8)
            self.assertEqual((e["published_count"], e["added_candidates"],
                              e["eligible_numeric_if_all_accepted"], e["target"]),
                             (9, 5, 14, 100))
            self.assertEqual(len(e["replies"]), 5)
            self.assertEqual((e["section"], e["language"]), ("помощь", "ru"))
            for i, r in enumerate(e["replies"], 10):
                self.assertEqual(r["id"], f'{e["intent_id"]}_ctx_{i:03}')
                self.assertNotIn(r["id"], seen)
                seen.add(r["id"])
        self.assertEqual(len(seen), 120)

    def test_safety_and_direct_context(self):
        d = self.data
        self.assertEqual(d["audiences"], ["all_ai_bots"])
        for field in ("read_only", "requires_direct_address", "requires_context_match",
                      "no_personal_data", "no_sanctions"):
            self.assertTrue(d["constraints"][field])
        for e in d["entries"]:
            for r in e["replies"]:
                self.assertEqual((r["context"], r["language"], r["audiences"],
                                  r["read_only"], r["editorial_status"]),
                                 ("direct", "ru", ["all_ai_bots"], True,
                                  "candidate_pending_full_semantic_review"))
                self.assertGreaterEqual(len(r["text"]), 90)
                self.assertLessEqual(len(r["text"]), 300)
                self.assertGreaterEqual(len(r["context_note"]), 40)
                self.assertIn("без действий, санкций", r["avoid"])
                self.assertNotIn("@", r["text"] + r["context_note"])
                self.assertNotIn("http", (r["text"] + r["context_note"]).lower())

    def test_exact_and_high_lexical_duplicates(self):
        texts, contexts, ids = set(), set(), set()
        published = {r["id"]: r for r in self.source["records"]}
        for e in self.data["entries"]:
            old = published[e["intent_id"]]
            pool = [old["answer"], *old["variants"]]
            for r in e["replies"]:
                key = normalize(r["text"])
                context = normalize(r["context_note"])
                self.assertNotIn(key, texts)
                self.assertNotIn(context, contexts)
                self.assertNotIn(r["id"], ids)
                texts.add(key)
                contexts.add(context)
                ids.add(r["id"])
                for text in pool:
                    self.assertNotEqual(key, normalize(text))
                    self.assertLess(similarity(r["text"], text), 0.70,
                                    (r["id"], "near existing text"))
                pool.append(r["text"])
        self.assertEqual((len(texts), len(contexts), len(ids)), (120, 120, 120))

    def test_fail_closed_reference_selector(self):
        for e in self.data["entries"]:
            for r in e["replies"]:
                self.assertIsNone(select_scoped_reply(e, context_note=r["context_note"]))
                self.assertIsNone(select_scoped_reply(e, addressed=True))
                self.assertIsNone(select_scoped_reply(e, addressed=True,
                                                       context_note="unrelated situation"))
                self.assertEqual(select_scoped_reply(e, addressed=True,
                                                     context_note=r["context_note"]),
                                 r["text"])


    def test_registered_pack_exact_and_near_duplicates(self):
        def answer_strings(value):
            if isinstance(value, list):
                for item in value:
                    if isinstance(item, str):
                        yield item
                    else:
                        yield from answer_strings(item)
            elif isinstance(value, dict):
                for key, item in value.items():
                    if key in {"answer", "text", "reply"} and isinstance(item, str):
                        yield item
                    elif key in {"variants", "replies", "responses", "records", "entries",
                                 "catalog", "reactions", "items", "examples"}:
                        yield from answer_strings(item)
                    elif isinstance(item, (dict, list)):
                        yield from answer_strings(item)

        related_paths = {
            "packs/ru/practical_recovery_qa.json",
            "packs/ru/dialogue_help_qa.json",
            "packs/ru/conversation_followthrough_qa.json",
            "packs/ru/conversation_precision_qa.json",
            "packs/ru/response_boundaries_qa.json",
            "packs/ru/structured_information_qa.json",
            "packs/ru/collaborative_dialogue_qa.json",
            "packs/ru/impuls_help_qa.json",
            "packs/ru/impuls_verified_boundaries_qa.json",
            "packs/ru/impuls_ai_modes_help_qa.json",
            "packs/ru/moderation_explanations_qa.json",
            "packs/ru/moderation_dialogue_fairness_qa.json",
            "packs/ru/context_repair_v022_qa.json",
            "packs/ru/spoken_context_followups_qa.json",
            "packs/ru/choice_reasoning_qa.json",
        }
        candidates = [r["text"] for e in self.data["entries"] for r in e["replies"]]
        candidate_keys = {normalize(s) for s in candidates}
        candidate_words = [wordset(s) for s in candidates]
        suspicious = []
        checked = 0
        near_checked = 0
        for info in self.manifest["packs"]:
            payload = json.loads((ROOT / info["path"]).read_text(encoding="utf-8"))
            for old in answer_strings(payload):
                checked += 1
                self.assertNotIn(normalize(old), candidate_keys, info["path"])
                if info["path"] not in related_paths:
                    continue
                old_words = wordset(old)
                if len(old_words) < 4:
                    continue
                near_checked += 1
                for candidate, words in zip(candidates, candidate_words):
                    if not words:
                        continue
                    if min(len(words), len(old_words)) / max(len(words), len(old_words)) < 0.82:
                        continue
                    union = words | old_words
                    score = len(words & old_words) / max(1, len(union))
                    if score >= 0.82:
                        suspicious.append((info["path"], candidate, old, score))
        self.assertFalse(suspicious, suspicious[:5])
        self.assertGreater(checked, 0)
        self.assertGreater(near_checked, 0)


if __name__ == "__main__":
    unittest.main()
