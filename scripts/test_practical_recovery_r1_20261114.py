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
                          c["new_candidates"]), (24, 24, 24, 72))
        self.assertEqual((c["editorial_approved_candidates"], c["editorial_approved_100_sets"]),
                         (0, 0))
        seen = set()
        for e in d["entries"]:
            self.assertIn(e["intent_id"], published)
            old = published[e["intent_id"]]
            self.assertEqual(e["canonical_question"], old["question"])
            self.assertEqual(len(old["variants"]), 8)
            self.assertEqual((e["published_count"], e["added_candidates"],
                              e["eligible_numeric_if_all_accepted"], e["target"]),
                             (9, 3, 12, 100))
            self.assertEqual(len(e["replies"]), 3)
            self.assertEqual((e["section"], e["language"]), ("помощь", "ru"))
            for i, r in enumerate(e["replies"], 10):
                self.assertEqual(r["id"], f'{e["intent_id"]}_ctx_{i:03}')
                self.assertNotIn(r["id"], seen)
                seen.add(r["id"])
        self.assertEqual(len(seen), 72)

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
        self.assertEqual((len(texts), len(contexts), len(ids)), (72, 72, 72))

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


if __name__ == "__main__":
    unittest.main()
