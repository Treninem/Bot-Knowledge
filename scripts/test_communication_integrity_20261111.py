"""Read-only stage A–J checks for RU conversation integrity, 2026-11-11."""
import hashlib
import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FILES = [
    "staging/ru/communication_integrity_20261111_context_pool.json",
    "staging/ru/communication_integrity_20261111_context_delta_b.json",
    "staging/ru/communication_integrity_20261111_context_delta_c.json",
    "staging/ru/communication_integrity_20261111_context_delta_d.json",
    "staging/ru/communication_integrity_20261111_context_delta_e.json",
    "staging/ru/communication_integrity_20261111_context_delta_f.json",
    "staging/ru/communication_integrity_20261111_context_delta_g.json",
    "staging/ru/communication_integrity_20261111_context_delta_h.json",
    "staging/ru/communication_integrity_20261111_context_delta_i.json",
    "staging/ru/communication_integrity_20261111_context_delta_j.json",
]
RELATED = [
    "greeting_exit_t544_context_pool.json",
    "conversation_contracts_t570_context_pool.json",
    "social_boundaries_t580_context_pool.json",
    "interpersonal_t590_context_pool.json",
    "group_pragmatics_t600_context_pool.json",
    "dialogue_repair_t554_context_pool.json",
    "evidence_boundaries_t560_context_pool.json",
    "practical_dialogue_t534_context_pool.json",
    "bot_help_t549_context_pool.json",
    "support_triage_20261110_context_pool.json",
]

def normalized(value):
    return " ".join(re.findall(r"[^\W_]+", value.casefold().replace("ё", "е")))

def tokens(value):
    return set(normalized(value).split())

def git_blob_sha(content):
    return hashlib.sha1(("blob " + str(len(content)) + "\0").encode() + content).hexdigest()

class CommunicationIntegrityAD(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.raw = [(ROOT / p).read_bytes() for p in FILES]
        cls.stages = [json.loads(b) for b in cls.raw]

    def test_source_manifest_and_ancestry(self):
        initial = self.stages[0]
        source = (ROOT / initial["source_pack"]).read_bytes()
        sha256 = hashlib.sha256(source).hexdigest()
        manifest = json.loads((ROOT / "manifest.json").read_text("utf-8"))
        self.assertEqual(initial["source_pack_manifest_sha256"], sha256)
        self.assertEqual(initial["source_pack_blob_sha"], git_blob_sha(source))
        self.assertIn({"path": initial["source_pack"], "sha256": sha256}, manifest["packs"])
        for index, stage in enumerate(self.stages):
            self.assertNotIn(FILES[index], [p["path"] for p in manifest["packs"]])
            self.assertIs(stage["consumer_registered"], False)
            for key in ("source_pack", "source_pack_manifest_sha256",
                        "source_pack_blob_sha", "checked_source_main_sha"):
                self.assertEqual(stage[key], initial[key])
            if index:
                self.assertEqual(stage["parent_stage"], FILES[index-1])
                self.assertEqual(stage["parent_stage_blob_sha"], git_blob_sha(self.raw[index-1]))

    def test_scope_privacy_context_and_counts(self):
        seen_ids, seen_texts, seen_notes = set(), set(), set()
        stable = None
        counts = [12, 10, 10, 12, 12, 10, 10, 8, 8, 8]
        for i, (stage, number) in enumerate(zip(self.stages, counts)):
            self.assertEqual(stage["language"], "ru")
            self.assertEqual(stage["audiences"], ["all_ai_bots"])
            self.assertEqual(stage["stage_type"], "supplemental_contextual_reply_pool")
            for key in ("read_only", "requires_direct_address", "no_personal_data",
                        "no_sanctions", "requires_context_match"):
                self.assertIs(stage["constraints"][key], True)
            cp = stage["checkpoint"]
            self.assertEqual(cp["added_candidates"], number*10)
            self.assertEqual(cp["prior_candidates"], sum(counts[:i])*10)
            self.assertEqual(cp["cumulative_candidates"], sum(counts[:i+1])*10)
            self.assertEqual(cp["processed_intents"], 10)
            self.assertEqual(cp["finished_100"], 10 if i == len(counts)-1 else 0)
            self.assertEqual(cp["partial_intents"], 0 if i == len(counts)-1 else 10)
            self.assertEqual(cp["remaining_total"], 1000-sum(counts[:i+1])*10)
            self.assertEqual(len(stage["entries"]), 10)
            stable_now = {e["intent_id"] for e in stage["entries"]}
            self.assertEqual(len(stable_now), 10)
            if stable is None:
                stable = stable_now
            self.assertEqual(stable, stable_now)
            for e in stage["entries"]:
                self.assertEqual(e["target"], 100)
                self.assertEqual(e["prior_for_stable_id"], sum(counts[:i]))
                self.assertEqual(e["added_candidates"], number)
                self.assertEqual(e["total_staged"], sum(counts[:i+1]))
                self.assertEqual(e["remaining"], 100-sum(counts[:i+1]))
                self.assertEqual(e["response_role"], "assistant_reply")
                self.assertEqual(len(e["replies"]), number)
                for idx, r in enumerate(e["replies"], sum(counts[:i])+1):
                    self.assertEqual(r["id"], f'{e["intent_id"]}_{idx:02d}')
                    self.assertEqual(r["audiences"], ["all_ai_bots"])
                    self.assertEqual(r["language"], "ru")
                    self.assertEqual(r["context"], "direct")
                    self.assertTrue(r["read_only"])
                    self.assertIn("совпадении контекста", r["avoid"])
                    self.assertGreater(len(r["context_note"]), 15)
                    self.assertNotRegex(r["text"], r"https?://|[A-Za-z0-9_.+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
                    self.assertNotRegex(r["text"], r"(?<!\w)\+?\d[\d ()-]{8,}\d(?!\w)")
                    for item, seen in ((r["id"], seen_ids),
                                       (normalized(r["text"]), seen_texts),
                                       (normalized(r["context_note"]), seen_notes)):
                        self.assertTrue(item)
                        self.assertNotIn(item, seen)
                        seen.add(item)
        self.assertEqual((len(seen_ids), len(seen_texts), len(seen_notes)), (sum(counts)*10,)*3)

    def test_all_stage_replies_against_related_pools(self):
        related = []
        for filename in RELATED:
            d = json.loads((ROOT / "staging" / "ru" / filename).read_text("utf-8"))
            related.extend(r["text"] for e in d["entries"] for r in e["replies"])
        self.assertEqual(len(related), 1920)
        candidate = [r["text"] for s in self.stages for e in s["entries"] for r in e["replies"]]
        self.assertEqual(len(candidate), 1000)
        prior = [tokens(t) for t in related]
        for idx, text in enumerate(candidate):
            a = tokens(text)
            for b in prior:
                similarity = len(a & b)/len(a | b)
                self.assertLess(similarity, 0.80, (idx, similarity, text))
            prior.append(a)

if __name__ == "__main__":
    unittest.main()
