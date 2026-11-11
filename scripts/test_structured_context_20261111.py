"""Read-only validation for independent structured-information contextual supplement."""
from __future__ import annotations

import hashlib
import json
import re
import unicodedata
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
POOL = ROOT / "staging/ru/structured_information_20261111_delta_a.json"
TOKEN = re.compile(r"[^\W_]+", re.UNICODE)


def normalized(s: str) -> str:
    return " ".join(TOKEN.findall(unicodedata.normalize("NFKC", s).casefold().replace("ё", "е")))


def git_blob_sha(raw: bytes) -> str:
    return hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()


class StructuredContextSupplementTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pool = json.loads(POOL.read_text(encoding="utf-8"))
        cls.source = json.loads((ROOT / cls.pool["source_pack"]).read_text(encoding="utf-8"))
        cls.entries = cls.pool["entries"]
        cls.replies = [reply for entry in cls.entries for reply in entry["replies"]]

    def test_registered_source_sha_and_staging_only(self):
        manifest = json.loads((ROOT / "manifest.json").read_text(encoding="utf-8"))
        known = {p["path"]: p["sha256"] for p in manifest["packs"]}
        self.assertNotIn(POOL.relative_to(ROOT).as_posix(), known)
        raw = (ROOT / self.pool["source_pack"]).read_bytes()
        expected = known[self.pool["source_pack"]]
        self.assertEqual(hashlib.sha256(raw).hexdigest(), expected)
        self.assertEqual(self.pool["source_pack_manifest_sha256"], expected)
        self.assertEqual(self.pool["source_pack_blob_sha"], git_blob_sha(raw))
        self.assertIs(self.pool["consumer_registered"], False)
        self.assertEqual(self.pool["audiences"], ["all_ai_bots"])
        for flag in ("read_only", "requires_direct_address", "requires_context_match",
                     "no_personal_data", "no_sanctions"):
            self.assertIs(self.pool["constraints"][flag], True)

    def test_30_existing_stable_intents_and_150_new_replies(self):
        source_entries = {rec["id"]: rec for rec in self.source["records"]}
        self.assertEqual(len(self.entries), 30)
        self.assertEqual(len(self.replies), 150)
        self.assertEqual(self.pool["checkpoint"]["added_candidates"], 150)
        self.assertEqual(self.pool["checkpoint"]["finished_100"], 0)
        self.assertEqual(self.pool["checkpoint"]["partial_intents"], 30)
        self.assertEqual(self.pool["external_draft_source"]["pr"], 229)
        seen = set()
        for entry in self.entries:
            intent = entry["intent_id"]
            self.assertNotIn(intent, seen)
            seen.add(intent)
            self.assertIn(intent, source_entries)
            src = source_entries[intent]
            self.assertEqual(src["question"], entry["canonical_question"])
            self.assertEqual(1 + len(src["variants"]), entry["published_count"])
            self.assertEqual(entry["unmerged_pr_229_count"], 9)
            self.assertEqual(entry["added_candidates"], 5)
            self.assertEqual(entry["potential_if_both_prs_merged"], 14)
            self.assertEqual(entry["remaining_if_both_merged"], 86)
            self.assertEqual(len(entry["replies"]), 5)
            for suffix, reply in enumerate(entry["replies"], start=10):
                self.assertEqual(reply["id"], f"{intent}_supp_{suffix:02d}")
                self.assertEqual(reply["language"], "ru")
                self.assertEqual(reply["audiences"], ["all_ai_bots"])
                self.assertEqual(reply["context"], "direct")
                self.assertEqual(reply["style"], "helpful_precision")
                self.assertIs(reply["read_only"], True)
                self.assertGreaterEqual(len(reply["text"]), 45)
                self.assertGreaterEqual(len(reply["context_note"]), 30)

    def test_distinct_text_context_and_no_claimed_actions(self):
        for field in ("id", "text", "context_note"):
            normalized_values = [
                reply[field] if field == "id" else normalized(reply[field])
                for reply in self.replies
            ]
            self.assertEqual(len(normalized_values), len(set(normalized_values)), field)
        for reply in self.replies:
            text = reply["text"]
            self.assertNotRegex(text, r"(?i)(?:ghp_|github_pat_|\bt\.me/|\btelegram\.me/)")
            self.assertNotRegex(text, r"(?i)[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,}")
            self.assertNotRegex(normalized(text), r"\bя (?:забанил|замутил|выдал роль|раскрыл данные)\b")
            self.assertIn("не применять санкции", reply["avoid"])

    def test_no_exact_duplicates_with_registered_qa(self):
        manifest = json.loads((ROOT / "manifest.json").read_text(encoding="utf-8"))
        registered_answers = set()
        def walk(obj):
            if isinstance(obj, dict):
                for key, val in obj.items():
                    if key in ("answer", "response", "text") and isinstance(val, str):
                        registered_answers.add(normalized(val))
                    elif isinstance(val, (dict, list)):
                        walk(val)
            elif isinstance(obj, list):
                for val in obj:
                    walk(val)
        for p in manifest["packs"]:
            walk(json.loads((ROOT / p["path"]).read_text(encoding="utf-8")))
        self.assertTrue(registered_answers)
        self.assertFalse(registered_answers.intersection(normalized(r["text"]) for r in self.replies))

    def test_lexical_overlap_under_review_threshold(self):
        all_source = [rec["answer"] for rec in self.source["records"]]
        all_source += [v for rec in self.source["records"] for v in rec["variants"]]
        all_text = [r["text"] for r in self.replies] + all_source
        sets = [set(normalized(t).split()) for t in all_text]
        n = len(self.replies)
        for i, left in enumerate(sets[:n]):
            for j in range(i + 1, len(sets)):
                right = sets[j]
                similarity = len(left & right) / len(left | right)
                self.assertLess(similarity, 0.68, (self.replies[i]["id"], j))


class StructuredContextContinuationBTest(unittest.TestCase):
    """Review the second independent stage without counting unmerged #229 as main."""
    @classmethod
    def setUpClass(cls):
        cls.a = json.loads((ROOT / "staging/ru/structured_information_20261111_delta_a.json").read_text(encoding="utf-8"))
        cls.b = json.loads((ROOT / "staging/ru/structured_information_20261111_delta_b.json").read_text(encoding="utf-8"))
        cls.source = json.loads((ROOT / cls.b["source_pack"]).read_text(encoding="utf-8"))
        cls.a_replies = [reply for entry in cls.a["entries"] for reply in entry["replies"]]
        cls.b_replies = [reply for entry in cls.b["entries"] for reply in entry["replies"]]
        cls.all_replies = cls.a_replies + cls.b_replies

    def test_b_counts_and_source_checks(self):
        self.assertEqual(len(self.a_replies), 150)
        self.assertEqual(len(self.b_replies), 150)
        self.assertEqual(len(self.all_replies), 300)
        self.assertEqual(len(self.b["entries"]), 30)
        self.assertEqual(self.b["checkpoint"]["added_candidates"], 150)
        self.assertEqual(self.b["checkpoint"]["cumulative_new_in_independent_pr"], 300)
        self.assertEqual(self.b["checkpoint"]["prior_independent_stage"], 150)
        self.assertEqual(self.b["checkpoint"]["finished_100"], 0)
        self.assertEqual(self.b["checkpoint"]["partial_intents"], 30)
        self.assertFalse(self.b["consumer_registered"])
        manifest = json.loads((ROOT / "manifest.json").read_text(encoding="utf-8"))
        registry = {p["path"]: p["sha256"] for p in manifest["packs"]}
        self.assertNotIn("staging/ru/structured_information_20261111_delta_b.json", registry)
        raw = (ROOT / self.b["source_pack"]).read_bytes()
        self.assertEqual(hashlib.sha256(raw).hexdigest(), registry[self.b["source_pack"]])
        self.assertEqual(self.b["source_pack_manifest_sha256"], registry[self.b["source_pack"]])
        self.assertEqual(self.b["source_pack_blob_sha"], git_blob_sha(raw))
        self.assertEqual(self.b["external_draft_source"]["pr"], 229)
        for flag in ("read_only", "requires_direct_address", "requires_context_match",
                     "no_personal_data", "no_sanctions"):
            self.assertIs(self.b["constraints"][flag], True)

    def test_stable_ids_and_contexts_across_both_stages(self):
        source = {record["id"]: record for record in self.source["records"]}
        ids = [entry["intent_id"] for stage in (self.a, self.b) for entry in stage["entries"]]
        self.assertEqual(len(ids), len(set(ids)))
        self.assertEqual(len(ids), 60)
        for entry in self.b["entries"]:
            self.assertIn(entry["intent_id"], source)
            original = source[entry["intent_id"]]
            self.assertEqual(entry["canonical_question"], original["question"])
            self.assertEqual(entry["published_count"], 1 + len(original["variants"]))
            self.assertEqual(entry["published_count"], 3)
            self.assertEqual(entry["unmerged_pr_229_count"], 9)
            self.assertEqual(entry["added_candidates"], 5)
            self.assertEqual(entry["potential_if_both_prs_merged"], 14)
            self.assertEqual(entry["remaining_if_both_merged"], 86)
            self.assertEqual(len(entry["replies"]), 5)
            for idx, reply in enumerate(entry["replies"], 10):
                self.assertEqual(reply["id"], f'{entry["intent_id"]}_supp_{idx:02d}')
                self.assertIs(reply["read_only"], True)
                self.assertEqual(reply["language"], "ru")
                self.assertEqual(reply["context"], "direct")
                self.assertEqual(reply["audiences"], ["all_ai_bots"])
                self.assertGreaterEqual(len(reply["text"]), 45)
                self.assertGreaterEqual(len(reply["context_note"]), 30)
                self.assertIn("не применять санкции", reply["avoid"])
        for field in ("id", "text", "context_note"):
            keys = [r[field] if field == "id" else normalized(r[field]) for r in self.all_replies]
            self.assertEqual(len(keys), len(set(keys)), field)
        for reply in self.all_replies:
            self.assertNotRegex(reply["text"], r"(?i)(?:ghp_|github_pat_|\\bt\\.me/|\\btelegram\\.me/)")
            self.assertNotRegex(reply["text"], r"(?i)[a-z0-9._%+-]+@[a-z0-9.-]+\\.[a-z]{2,}")

    def test_all_staged_replies_lexically_distinct_from_registered(self):
        prior = [v for record in self.source["records"] for v in [record["answer"], *record["variants"]]]
        refs = [set(normalized(text).split()) for text in prior]
        new = [set(normalized(reply["text"]).split()) for reply in self.all_replies]
        for idx, words in enumerate(new):
            for other in refs:
                self.assertLess(len(words & other) / len(words | other), 0.68, idx)
            for other in new[:idx]:
                self.assertLess(len(words & other) / len(words | other), 0.68, idx)

if __name__ == "__main__":
    unittest.main()
