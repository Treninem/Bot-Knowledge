"""T570 B/C continuation: pinned source, 300 contextual replies, privacy and dedup."""
import hashlib
import json
import re
import subprocess
import unicodedata
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
POOL = "staging/ru/conversation_contracts_t570_context_pool.json"
B = "staging/ru/conversation_contracts_t570_context_delta_b.json"
C = "staging/ru/conversation_contracts_t570_context_delta_c.json"
D = "staging/ru/conversation_contracts_t570_context_delta_d.json"
E = "staging/ru/conversation_contracts_t570_context_delta_e.json"
SOURCE = "packs/ru/response_boundaries_qa.json"
RELATED = (
    "packs/ru/dialogue_help_qa.json",
    "packs/ru/collaborative_dialogue_qa.json",
    "packs/ru/conversation_followthrough_qa.json",
    "packs/ru/practical_recovery_qa.json",
    "packs/ru/social_dialogues.json",
    "staging/ru/conversation_t539_context_pool.json",
    "staging/ru/followthrough_t485_context_pool.json",
    "staging/ru/interpersonal_t599_context_delta.json",
    "staging/ru/group_pragmatics_t609_context_delta.json",
    "staging/ru/support_triage_20261110_context_delta_g.json",
    "staging/ru/firm_deescalation_20261111_j.json",
    "staging/ru/communication_integrity_20261111_context_delta_j.json",
)
EXPECTED_SOURCE_SHA256 = "e0d704a2a03d5aabb3db479eb47f07c2ba229ca76955a3cfc0f89dd5386538d9"
EXPECTED_SOURCE_BLOB = "f15104dbf08d3691b198abb7f0bd52d81383b5a0"
EXPECTED_POOL_BLOB = "7b3fd3e231223818a8baa1e54622b8f5776ccf83"
EXPECTED_B_BLOB = "fe641a3015d288f18eed2e320b8c9ccd42aa867f"
EXPECTED_C_BLOB = "0da53da620ec554b6852e676ac9627ac33e8962d"
EXPECTED_D_BLOB = "172cbea5af0cb09131ad5f0db75340c0a4dd3ace"
EXPECTED_POOL_MAIN = "9a41aae633d3266e4c600d93e9c6e2b08e0638f0"
EXPECTED_MAIN = "4e2cd1a48694c5727a1a84ce40cdc1a96a68e89d"

def norm(value):
    value = unicodedata.normalize("NFKC", value).casefold().replace("ё", "е")
    return " ".join(re.findall(r"[^\W_]+", value, flags=re.UNICODE))

def tokens(value):
    return set(norm(value).split())

def jaccard(left, right):
    a, b = tokens(left), tokens(right)
    return len(a & b) / len(a | b) if a or b else 1.0

def git_blob(path):
    return subprocess.check_output(
        ["git", "hash-object", str(ROOT / path)], cwd=ROOT, text=True
    ).strip()

def candidate_texts(obj):
    if isinstance(obj, dict):
        for key in ("text", "answer", "reply", "response"):
            if isinstance(obj.get(key), str):
                yield obj[key]
        for value in obj.values():
            if isinstance(value, (dict, list)):
                yield from candidate_texts(value)
    elif isinstance(obj, list):
        for item in obj:
            yield from candidate_texts(item)

class TestT570ContinuationBC(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pool = json.loads((ROOT / POOL).read_text(encoding="utf-8"))
        cls.b = json.loads((ROOT / B).read_text(encoding="utf-8"))
        cls.c = json.loads((ROOT / C).read_text(encoding="utf-8"))
        cls.d = json.loads((ROOT / D).read_text(encoding="utf-8"))
        cls.e = json.loads((ROOT / E).read_text(encoding="utf-8"))
        cls.stages = (cls.pool, cls.b, cls.c, cls.d, cls.e)
        cls.base_replies = [r for e in cls.pool["entries"] for r in e["replies"]]
        cls.b_replies = [r for e in cls.b["entries"] for r in e["replies"]]
        cls.c_replies = [r for e in cls.c["entries"] for r in e["replies"]]
        cls.d_replies = [r for e in cls.d["entries"] for r in e["replies"]]
        cls.e_replies = [r for e in cls.e["entries"] for r in e["replies"]]
        cls.all_replies = cls.base_replies + cls.b_replies + cls.c_replies + cls.d_replies + cls.e_replies

    def test_source_and_parent_blob_chain(self):
        manifest = json.loads((ROOT / "manifest.json").read_text(encoding="utf-8"))
        source = ROOT / SOURCE
        digest = hashlib.sha256(source.read_bytes()).hexdigest()
        self.assertEqual(digest, EXPECTED_SOURCE_SHA256)
        self.assertEqual(git_blob(SOURCE), EXPECTED_SOURCE_BLOB)
        self.assertIn({"path": SOURCE, "sha256": digest}, manifest["packs"])
        for stage in self.stages:
            self.assertEqual(stage["source_pack_manifest_sha256"], digest)
            self.assertEqual(stage["source_pack_blob_sha"], EXPECTED_SOURCE_BLOB)
            self.assertEqual(stage["source_pack"], SOURCE)
            self.assertFalse(stage["consumer_registered"])
        self.assertEqual(self.pool["checked_source_main_sha"], EXPECTED_POOL_MAIN)
        self.assertEqual(self.b["checked_source_main_sha"], EXPECTED_MAIN)
        self.assertEqual(self.c["checked_source_main_sha"], EXPECTED_MAIN)
        self.assertEqual(self.d["checked_source_main_sha"], EXPECTED_MAIN)
        self.assertEqual(self.e["checked_source_main_sha"], EXPECTED_MAIN)
        self.assertEqual(self.b["parent_stage"], POOL)
        self.assertEqual(self.b["parent_stage_blob_sha"], EXPECTED_POOL_BLOB)
        self.assertEqual(git_blob(POOL), EXPECTED_POOL_BLOB)
        self.assertEqual(self.c["parent_stage"], B)
        self.assertEqual(self.c["parent_stage_blob_sha"], EXPECTED_B_BLOB)
        self.assertEqual(git_blob(B), EXPECTED_B_BLOB)
        self.assertEqual(self.d["parent_stage"], C)
        self.assertEqual(self.d["parent_stage_blob_sha"], EXPECTED_C_BLOB)
        self.assertEqual(git_blob(C), EXPECTED_C_BLOB)
        self.assertEqual(self.e["parent_stage"], D)
        self.assertEqual(self.e["parent_stage_blob_sha"], EXPECTED_D_BLOB)
        self.assertEqual(git_blob(D), EXPECTED_D_BLOB)
        self.assertIsNone(self.pool["parent_stage"])
        registered_paths = {item["path"] for item in manifest["packs"]}
        for path in (POOL, B, C, D, E):
            self.assertNotIn(path, registered_paths)

    def test_exact_counts_ids_context_and_safety(self):
        expected = ((100, 100, 100, 0, 10, 900),
                    (100, 100, 200, 0, 10, 800),
                    (200, 100, 300, 0, 10, 700),
                    (300, 100, 400, 0, 10, 600),
                    (400, 100, 500, 0, 10, 500))
        for stage, values in zip(self.stages, expected):
            cp = stage["checkpoint"]
            actual = (cp["prior_candidates"], cp["added_candidates"],
                      cp["cumulative_candidates"], cp["finished_100"],
                      cp["partial_intents"], cp["remaining_total"])
            self.assertEqual(actual, values)
            self.assertEqual(cp["processed_intents"], 10)
            self.assertEqual(len(stage["entries"]), 10)
            self.assertEqual(stage["language"], "ru")
            self.assertEqual(stage["audiences"], ["all_ai_bots"])
            for key in ("read_only", "requires_direct_address", "no_personal_data",
                        "no_sanctions", "requires_context_match"):
                self.assertIs(stage["constraints"][key], True)

        ids, texts, notes = set(), set(), set()
        by_intent = {}
        for stage_index, stage in enumerate(self.stages):
            start = (1, 11, 21, 31, 41)[stage_index]
            expected_total = (10, 20, 30, 40, 50)[stage_index]
            for entry in stage["entries"]:
                by_intent.setdefault(entry["intent_id"], []).extend(entry["replies"])
                self.assertEqual(entry["target"], 100)
                self.assertEqual(entry["prior_for_stable_id"], (0, 10, 20, 30, 40)[stage_index])
                self.assertEqual(entry["added_candidates"], 10)
                self.assertEqual(entry["total_staged"], expected_total)
                self.assertEqual(entry["remaining"], 100 - expected_total)
                self.assertEqual(len(entry["replies"]), 10)
                for offset, reply in enumerate(entry["replies"]):
                    suffix = start + offset
                    self.assertEqual(reply["id"], f'{entry["intent_id"]}_{suffix:02d}')
                    for value, target in ((reply["id"], ids),
                                          (norm(reply["text"]), texts),
                                          (norm(reply["context_note"]), notes)):
                        self.assertTrue(value)
                        self.assertNotIn(value, target)
                        target.add(value)
                    self.assertEqual((reply["language"], reply["style"],
                                      reply["audiences"], reply["context"],
                                      reply["read_only"]),
                                     ("ru", "neutral", ["all_ai_bots"], "direct", True))
                    self.assertTrue(reply["avoid"])
                    self.assertNotRegex(reply["text"], r"https?://|[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}")
                    self.assertNotRegex(reply["text"], r"(?<!\w)\+?\d[\d ()-]{8,}\d(?!\w)")
                    self.assertNotRegex(reply["text"].casefold(),
                                        r"\b(забаню|замучу|выдам санкцию|удалю участника)\b")
        self.assertEqual((len(ids), len(texts), len(notes)), (500, 500, 500))
        self.assertEqual(len(by_intent), 10)
        self.assertTrue(all(len(rows) == 50 for rows in by_intent.values()))

    def test_near_duplicates_inside_series_and_related_sample(self):
        texts = [r["text"] for r in self.all_replies]
        maximum = max(jaccard(texts[i], texts[j])
                      for i in range(len(texts)) for j in range(i + 1, len(texts)))
        self.assertLess(maximum, 0.78)
        related = []
        for path in RELATED:
            obj = json.loads((ROOT / path).read_text(encoding="utf-8"))
            related.extend(candidate_texts(obj))
        self.assertGreater(len(related), 100)
        for answer in self.b_replies + self.c_replies + self.d_replies + self.e_replies:
            self.assertFalse(any(norm(answer["text"]) == norm(x) for x in related))
            self.assertLess(max((jaccard(answer["text"], x) for x in related), default=0), 0.78)

    def test_no_exact_duplicate_in_registered_packs_or_other_staging(self):
        manifest = json.loads((ROOT / "manifest.json").read_text(encoding="utf-8"))
        fresh = {norm(r["text"]) for r in self.b_replies + self.c_replies + self.d_replies + self.e_replies}
        for pack in manifest["packs"]:
            obj = json.loads((ROOT / pack["path"]).read_text(encoding="utf-8"))
            for value in candidate_texts(obj):
                self.assertNotIn(norm(value), fresh, f"Registered duplicate in {pack['path']}")
        excluded = {POOL, B, C, D, E}
        for path in (ROOT / "staging/ru").glob("*.json"):
            rel = path.relative_to(ROOT).as_posix()
            if rel in excluded:
                continue
            try:
                obj = json.loads(path.read_text(encoding="utf-8"))
            except (UnicodeError, json.JSONDecodeError) as exc:
                self.fail(f"Invalid staging JSON in {rel}: {exc}")
            for value in candidate_texts(obj):
                self.assertNotIn(norm(value), fresh, f"Staging duplicate in {rel}")

if __name__ == "__main__":
    unittest.main()
