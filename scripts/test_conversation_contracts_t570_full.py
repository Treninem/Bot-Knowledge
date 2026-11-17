"""Full T570 lineage and contextual QA through checkpoint J (1000/1000)."""
import hashlib
import json
import re
import subprocess
import unicodedata
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
POOL = "staging/ru/conversation_contracts_t570_context_pool.json"
STAGES = tuple(
    f"staging/ru/conversation_contracts_t570_context_delta_{letter}.json"
    for letter in "bcdefghij"
)
SOURCE = "packs/ru/response_boundaries_qa.json"
EXPECTED_SOURCE_SHA256 = "e0d704a2a03d5aabb3db479eb47f07c2ba229ca76955a3cfc0f89dd5386538d9"
EXPECTED_SOURCE_BLOB = "f15104dbf08d3691b198abb7f0bd52d81383b5a0"
EXPECTED_POOL_BLOB = "7b3fd3e231223818a8baa1e54622b8f5776ccf83"
EXPECTED_BLOBS = {
    STAGES[0]: "fe641a3015d288f18eed2e320b8c9ccd42aa867f",
    STAGES[1]: "0da53da620ec554b6852e676ac9627ac33e8962d",
    STAGES[2]: "172cbea5af0cb09131ad5f0db75340c0a4dd3ace",
    STAGES[3]: "16052c0e42d016e9fbd0255e0ab7af30f798b0db",
    STAGES[4]: "97f1fbe4f5c0f232e1575d92fed422f887380dc7",
    STAGES[5]: "899aa17c07581e834be10597b02f37d9a28ab297",
    STAGES[6]: "769fdb84b8bf38b0ab3be354a8b916a977b16016",
    STAGES[7]: "68924dd1e5b5689c66121786282fc44f2ac79390",
    STAGES[8]: "edb3217f51ee25805ca68eb651de75daa2908ad0",
}
EXPECTED_POOL_MAIN = "9a41aae633d3266e4c600d93e9c6e2b08e0638f0"
EXPECTED_PREVIOUS_MAIN = "4e2cd1a48694c5727a1a84ce40cdc1a96a68e89d"
EXPECTED_CURRENT_MAIN = "16bcdd62b379b8759fb15c798fbf1ac5174147d7"
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

class TestT570FullLineageJ(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pool = json.loads((ROOT / POOL).read_text(encoding="utf-8"))
        cls.stages = [json.loads((ROOT / p).read_text(encoding="utf-8")) for p in STAGES]
        cls.all_stages = [cls.pool] + cls.stages
        cls.replies_by_stage = [
            [r for entry in stage["entries"] for r in entry["replies"]]
            for stage in cls.all_stages
        ]
        cls.all_replies = [r for rows in cls.replies_by_stage for r in rows]

    def test_source_and_parent_blob_chain(self):
        manifest = json.loads((ROOT / "manifest.json").read_text(encoding="utf-8"))
        source = ROOT / SOURCE
        digest = hashlib.sha256(source.read_bytes()).hexdigest()
        self.assertEqual(digest, EXPECTED_SOURCE_SHA256)
        self.assertEqual(git_blob(SOURCE), EXPECTED_SOURCE_BLOB)
        self.assertIn({"path": SOURCE, "sha256": digest}, manifest["packs"])
        self.assertEqual(self.pool["checked_source_main_sha"], EXPECTED_POOL_MAIN)
        self.assertIsNone(self.pool["parent_stage"])
        self.assertEqual(git_blob(POOL), EXPECTED_POOL_BLOB)
        parent_path, parent_blob = POOL, EXPECTED_POOL_BLOB
        for index, (path, stage) in enumerate(zip(STAGES, self.stages)):
            self.assertEqual(git_blob(path), EXPECTED_BLOBS[path])
            self.assertEqual(stage["parent_stage"], parent_path)
            self.assertEqual(stage["parent_stage_blob_sha"], parent_blob)
            self.assertEqual(stage["checked_source_main_sha"],
                             EXPECTED_CURRENT_MAIN if index >= 5 else EXPECTED_PREVIOUS_MAIN)
            parent_path, parent_blob = path, EXPECTED_BLOBS[path]
        registered = {item["path"] for item in manifest["packs"]}
        for path in (POOL,) + STAGES:
            self.assertNotIn(path, registered)
        for stage in self.all_stages:
            self.assertEqual(stage["source_pack"], SOURCE)
            self.assertEqual(stage["source_pack_manifest_sha256"], digest)
            self.assertEqual(stage["source_pack_blob_sha"], EXPECTED_SOURCE_BLOB)
            self.assertFalse(stage["consumer_registered"])

    def test_counts_context_ids_and_safety(self):
        checkpoints = (
            (0, 100, 100, 0, 10, 900),
            (100, 100, 200, 0, 10, 800),
            (200, 100, 300, 0, 10, 700),
            (300, 100, 400, 0, 10, 600),
            (400, 100, 500, 0, 10, 500),
            (500, 100, 600, 0, 10, 400),
            (600, 100, 700, 0, 10, 300),
            (700, 100, 800, 0, 10, 200),
            (800, 100, 900, 0, 10, 100),
            (900, 100, 1000, 10, 0, 0),
        )
        ids, texts, notes, by_intent = set(), set(), set(), {}
        starts, totals = (1, 11, 21, 31, 41, 51, 61, 71, 81, 91), (10, 20, 30, 40, 50, 60, 70, 80, 90, 100)
        for index, (stage, expected) in enumerate(zip(self.all_stages, checkpoints)):
            cp = stage["checkpoint"]
            actual = (cp["prior_candidates"], cp["added_candidates"],
                      cp["cumulative_candidates"], cp["finished_100"],
                      cp["partial_intents"], cp["remaining_total"])
            self.assertEqual(actual, expected)
            self.assertEqual(cp["processed_intents"], 10)
            self.assertEqual(len(stage["entries"]), 10)
            self.assertEqual(stage["language"], "ru")
            self.assertEqual(stage["audiences"], ["all_ai_bots"])
            for key in ("read_only", "requires_direct_address", "no_personal_data",
                        "no_sanctions", "requires_context_match"):
                self.assertIs(stage["constraints"][key], True)
            start, total = starts[index], totals[index]
            for entry in stage["entries"]:
                by_intent.setdefault(entry["intent_id"], []).extend(entry["replies"])
                self.assertEqual(entry["target"], 100)
                self.assertEqual(entry["prior_for_stable_id"], start - 1)
                self.assertEqual(entry["added_candidates"], 10)
                self.assertEqual(entry["total_staged"], total)
                self.assertEqual(entry["remaining"], 100 - total)
                self.assertEqual(len(entry["replies"]), 10)
                for offset, reply in enumerate(entry["replies"]):
                    self.assertEqual(reply["id"], f'{entry["intent_id"]}_{start + offset:02d}')
                    for value, target in ((reply["id"], ids),
                                          (norm(reply["text"]), texts),
                                          (norm(reply["context_note"]), notes)):
                        self.assertTrue(value)
                        self.assertNotIn(value, target)
                        target.add(value)
                    self.assertEqual((reply["language"], reply["style"], reply["audiences"],
                                      reply["context"], reply["read_only"]),
                                     ("ru", "neutral", ["all_ai_bots"], "direct", True))
                    self.assertTrue(reply["avoid"])
                    self.assertNotRegex(reply["text"], r"https?://|[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}")
                    self.assertNotRegex(reply["text"], r"(?<!\w)\+?\d[\d ()-]{8,}\d(?!\w)")
                    self.assertNotRegex(reply["text"].casefold(),
                                        r"\b(забаню|замучу|выдам санкцию|удалю участника)\b")
        self.assertEqual((len(ids), len(texts), len(notes)), (1000, 1000, 1000))
        self.assertEqual(len(by_intent), 10)
        self.assertTrue(all(len(rows) == 100 for rows in by_intent.values()))

    def test_near_duplicates_and_related_contexts(self):
        values = [r["text"] for r in self.all_replies]
        maximum = max(jaccard(values[i], values[j])
                      for i in range(len(values)) for j in range(i + 1, len(values)))
        self.assertLess(maximum, 0.78)
        related = []
        for path in RELATED:
            obj = json.loads((ROOT / path).read_text(encoding="utf-8"))
            related.extend(candidate_texts(obj))
        self.assertGreater(len(related), 100)
        for answer in sum(self.replies_by_stage[-4:], []):
            self.assertFalse(any(norm(answer["text"]) == norm(x) for x in related))
            self.assertLess(max((jaccard(answer["text"], x) for x in related), default=0), 0.78)

    def test_no_exact_duplicates_in_registered_packs_or_other_staging(self):
        manifest = json.loads((ROOT / "manifest.json").read_text(encoding="utf-8"))
        fresh = {norm(r["text"]) for rows in self.replies_by_stage[-4:] for r in rows}
        for pack in manifest["packs"]:
            obj = json.loads((ROOT / pack["path"]).read_text(encoding="utf-8"))
            for value in candidate_texts(obj):
                self.assertNotIn(norm(value), fresh, f"Registered duplicate in {pack['path']}")
        excluded = {POOL, *STAGES}
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
