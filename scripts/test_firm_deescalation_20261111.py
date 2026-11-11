"""Read-only QA for original contextual RU de-escalation stages A and B."""
from __future__ import annotations
import hashlib
import json
import re
import unicodedata
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STAGES = [
    ROOT / "staging/ru/firm_deescalation_20261111_context_pool.json",
    ROOT / "staging/ru/firm_deescalation_20261111_b.json",
]
TOKENS = re.compile(r"[^\W_]+", re.UNICODE)
INTENTS = {
    "direct_insult", "mockery_instead_of_argument", "unfounded_accusation",
    "rushed_answer", "sanction_bait", "private_data_pressure",
    "bully_third_party", "end_repetitive_argument", "group_tone_boundary",
    "criticism_of_assistant",
}

def norm(s: str) -> str:
    return " ".join(TOKENS.findall(unicodedata.normalize("NFKC", s).casefold().replace("ё", "е")))

def blobsha(data: bytes) -> str:
    return hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()

class FirmDialogueTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.stages = [json.loads(path.read_text("utf-8")) for path in STAGES]
        cls.replies = [r for stage in cls.stages for e in stage["entries"] for r in e["replies"]]

    def test_source_hash_and_unregistered_context(self):
        manifest = json.loads((ROOT / "manifest.json").read_text("utf-8"))
        registered = {p["path"]: p["sha256"] for p in manifest["packs"]}
        for path, stage in zip(STAGES, self.stages):
            self.assertNotIn(path.relative_to(ROOT).as_posix(), registered)
            src = (ROOT / stage["source_pack"]).read_bytes()
            self.assertEqual(hashlib.sha256(src).hexdigest(), registered[stage["source_pack"]])
            self.assertEqual(hashlib.sha256(src).hexdigest(), stage["source_pack_manifest_sha256"])
            self.assertEqual(blobsha(src), stage["source_pack_blob_sha"])
            self.assertIs(stage["consumer_registered"], False)
            self.assertEqual(stage["audiences"], ["all_ai_bots"])
            for fld in ("read_only", "requires_direct_address", "requires_context_match", "no_sanctions", "no_personal_data"):
                self.assertIs(stage["constraints"][fld], True)

    def test_stable_id_sequence_and_checkpoint(self):
        self.assertEqual(len(self.replies), 200)
        names = [e["intent_id"] for e in self.stages[0]["entries"]]
        self.assertEqual({n.removeprefix("firm20261111_") for n in names}, INTENTS)
        for n, stage in enumerate(self.stages):
            cp = stage["checkpoint"]
            self.assertEqual((cp["prior_candidates"], cp["added_candidates"], cp["cumulative_candidates"]), (n*100,100,(n+1)*100))
            self.assertEqual(cp["remaining_total"], 900 - n*100)
            self.assertEqual(cp["partial_intents"], 10)
            self.assertEqual(cp["finished_100"], 0)
            self.assertEqual([e["intent_id"] for e in stage["entries"]], names)
            for e in stage["entries"]:
                self.assertEqual((e["prior_for_stable_id"],e["added_candidates"],e["total_staged"],e["target"],e["remaining"]), (n*10,10,(n+1)*10,100,90-n*10))
                self.assertEqual(len(e["replies"]), 10)
                for i,r in enumerate(e["replies"],1+n*10):
                    self.assertEqual(r["id"], f'{e["intent_id"]}_{i:02}')
                    self.assertEqual(r["language"], "ru")
                    self.assertEqual(r["style"], "firm_calm")
                    self.assertEqual(r["context"], "direct")
                    self.assertEqual(r["audiences"], ["all_ai_bots"])
                    self.assertIs(r["read_only"], True)
                    self.assertIn("не выдавать санкции", r["avoid"])
                    self.assertGreaterEqual(len(r["text"]), 60)
                    self.assertGreaterEqual(len(r["context_note"]), 30)

    def test_duplicates_and_privacy(self):
        for key in ("id", "text", "context_note"):
            vals = [r[key] if key == "id" else norm(r[key]) for r in self.replies]
            self.assertEqual(len(vals), len(set(vals)),key)
        sets = [set(norm(r["text"]).split()) for r in self.replies]
        for i, s in enumerate(sets):
            for t in sets[i+1:]:
                self.assertLess(len(s & t) / len(s | t), .8)
        for r in self.replies:
            self.assertNotRegex(r["text"], r"(?i)[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,}")
            self.assertNotRegex(r["text"], r"(?i)(?:ghp_|github_pat_|(?:telegram|t)\.me/)")
            self.assertNotRegex(norm(r["text"]), r"\bя (?:забанил|замутил|удалил сообщение|раскрыл данные)\b")

    def test_not_exact_repeats_of_registered_answers(self):
        manifest = json.loads((ROOT / "manifest.json").read_text("utf-8"))
        known = set()
        def walk(node):
            if isinstance(node, dict):
                for k,v in node.items():
                    if k in ("answer", "response", "text") and isinstance(v,str):
                        known.add(norm(v))
                    elif isinstance(v, (dict,list)):
                        walk(v)
            elif isinstance(node,list):
                for v in node:
                    walk(v)
        for item in manifest["packs"]:
            walk(json.loads((ROOT / item["path"]).read_text("utf-8")))
        self.assertFalse(known.intersection(norm(r["text"]) for r in self.replies))

    def test_no_close_lexical_overlap_with_six_related_staging_packs(self):
        related = [
            "staging/ru/group_pragmatics_t600_context_pool.json",
            "staging/ru/interpersonal_t590_context_pool.json",
            "staging/ru/communication_integrity_20261111_context_pool.json",
            "staging/ru/dialogue_repair_t554_context_pool.json",
            "staging/ru/optional_humor_t518_context_pool.json",
            "staging/ru/group_pragmatics_t611_alternatives_review_only.json",
        ]
        other = []
        def walk(node):
            if isinstance(node, dict):
                if isinstance(node.get("text"), str) and (
                    "id" in node or "context_note" in node or "context" in node
                ):
                    other.append(norm(node["text"]))
                for k,v in node.items():
                    if k != "text":
                        walk(v)
            elif isinstance(node,list):
                for item in node:
                    walk(item)
        for path in related:
            walk(json.loads((ROOT / path).read_text("utf-8")))
        self.assertGreaterEqual(len(other), 1000)
        refs = [set(t.split()) for t in other]
        for reply in self.replies:
            txt = norm(reply["text"])
            self.assertNotIn(txt,other, reply["id"])
            words = set(txt.split())
            for outside in refs:
                self.assertLess(len(words & outside) / len(words | outside), .55, reply["id"])

if __name__ == "__main__":
    unittest.main()
