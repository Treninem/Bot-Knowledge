"""T590-T591: verify original synthetic contextual RU drafts without consumer activation."""
import hashlib
import json
import re
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STAGES = (
    "staging/ru/interpersonal_t590_context_pool.json",
    "staging/ru/interpersonal_t591_context_delta.json",
)
RELATED = (
    "staging/ru/social_boundaries_t580_context_pool.json",
    "staging/ru/social_boundaries_t589_context_delta.json",
    "staging/ru/greeting_exit_t544_context_pool.json",
    "staging/ru/group_turns_t501_context_pool.json",
    "staging/ru/practical_dialogue_t538_context_pool.json",
    "staging/ru/social_turns_t491_context_pool.json",
    "staging/ru/social_clarity_t498_context_pool.json",
    "staging/ru/dialogue_repair_t559_context_delta.json",
    "staging/ru/optional_humor_t523_context_pool.json",
    "staging/ru/conversation_contracts_t579_context_delta.json",
)

def normalize(value):
    value = value.casefold().replace("ё", "е")
    return " ".join(re.findall(r"[^\W_]+", value, flags=re.UNICODE))

def replies_from(doc):
    for entry in doc.get("entries", []):
        for reply in entry.get("replies", []):
            text = reply.get("text") or reply.get("reply") or reply.get("answer")
            if isinstance(text, str):
                yield text

class InterpersonalT590T591(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.docs = [json.loads((ROOT / path).read_text(encoding="utf-8"))
                    for path in STAGES]

    def test_immutable_source_and_parent_chain(self):
        base, continuation = self.docs
        manifest = json.loads((ROOT / "manifest.json").read_text(encoding="utf-8"))
        source = ROOT / base["source_pack"]
        actual_sha = hashlib.sha256(source.read_bytes()).hexdigest()
        actual_blob = subprocess.check_output(
            ["git", "hash-object", str(source)], cwd=ROOT, text=True).strip()
        self.assertEqual(actual_sha, base["source_pack_manifest_sha256"])
        self.assertIn({"path": base["source_pack"], "sha256": actual_sha}, manifest["packs"])
        self.assertEqual(actual_blob, base["source_pack_blob_sha"])
        self.assertEqual(continuation["parent_stage"], STAGES[0])
        parent_blob = subprocess.check_output(
            ["git", "hash-object", STAGES[0]], cwd=ROOT, text=True).strip()
        self.assertEqual(continuation["parent_stage_blob_sha"], parent_blob)
        for doc in self.docs:
            for key in ("source_pack", "source_pack_blob_sha",
                        "source_pack_manifest_sha256", "checked_source_main_sha"):
                self.assertEqual(doc[key], base[key])
            self.assertEqual((doc["language"], doc["audiences"],
                              doc["consumer_registered"]), ("ru", ["all_ai_bots"], False))
            self.assertIn("suggested wording", doc["scope"])
            for flag in ("read_only", "requires_direct_address",
                         "no_personal_data", "no_sanctions", "requires_context_match"):
                self.assertIs(doc["constraints"][flag], True)

    def test_counts_contexts_and_distinct_reply_ideas(self):
        original, delta = self.docs
        expected_roles = {
            "t590_specific_thanks", "t590_apologize_concretely",
            "t590_decline_gently",
        }
        intents = [e["intent_id"] for e in original["entries"]]
        self.assertEqual(len(intents), len(set(intents)))
        self.assertEqual(len(intents), 10)
        ids, texts, notes = set(), set(), set()
        vectors = []
        for stage_index, doc in enumerate(self.docs):
            c = doc["checkpoint"]
            self.assertEqual((c["prior_candidates"], c["added_candidates"],
                              c["cumulative_candidates"], c["finished_100"],
                              c["remaining_total"]),
                             (0, 120, 120, 0, 880) if stage_index == 0
                             else (120, 80, 200, 0, 800))
            self.assertEqual([e["intent_id"] for e in doc["entries"]], intents)
            for e in doc["entries"]:
                self.assertTrue(e["canonical_question"].strip())
                self.assertIn(e["section"], ("общение", "помощь", "навыки", "умение", "правила"))
                self.assertEqual(e["response_role"],
                                 "user_wording_sample" if e["intent_id"] in expected_roles
                                 else "assistant_dialogue_pattern")
                self.assertEqual((e["prior_for_stable_id"], e["added_candidates"],
                                  e["total_staged"], e["target"], e["remaining"]),
                                 (0, 12, 12, 100, 88) if stage_index == 0
                                 else (12, 8, 20, 100, 80))
                self.assertEqual(len(e["replies"]), 12 if stage_index == 0 else 8)
                for i, reply in enumerate(e["replies"], 1 if stage_index == 0 else 13):
                    self.assertEqual(reply["id"], f'{e["intent_id"]}_{i:02d}')
                    self.assertEqual((reply["language"], reply["style"],
                                      reply["audiences"], reply["context"], reply["read_only"]),
                                     ("ru", "neutral", ["all_ai_bots"], "direct", True))
                    self.assertIn("совпадении контекста", reply["avoid"])
                    self.assertFalse(re.search(
                        r"(?i)https?://|@[a-z0-9_]+|\b\+?\d[\d -]{7,}\d\b",
                        reply["text"]))
                    self.assertFalse(re.search(r"(?i)\b(забанил|заблокировал|замутил)\b",
                                              reply["text"]))
                    for val, used in ((reply["id"], ids),
                                      (normalize(reply["text"]), texts),
                                      (normalize(reply["context_note"]), notes)):
                        self.assertTrue(val)
                        self.assertNotIn(val, used)
                        used.add(val)
                    vectors.append(set(normalize(reply["text"]).split()))
        self.assertEqual((len(ids), len(texts), len(notes)), (200, 200, 200))
        for i, left in enumerate(vectors):
            for right in vectors[i+1:]:
                self.assertLess(len(left & right) / len(left | right), .8)

    def test_no_exact_or_high_lexical_overlap_in_related_pools(self):
        proposed = [set(normalize(t).split()) for doc in self.docs
                    for t in replies_from(doc)]
        normalized_proposed = {" ".join(sorted(v)) for v in proposed}
        self.assertEqual(len(normalized_proposed), 200)
        related = []
        for path in RELATED:
            data = json.loads((ROOT / path).read_text(encoding="utf-8"))
            related.extend(replies_from(data))
        self.assertGreaterEqual(len(related), 1500)
        other_set = [set(normalize(text).split()) for text in related]
        for proposed_tokens in proposed:
            for old_tokens in other_set:
                self.assertNotEqual(proposed_tokens, old_tokens)
                self.assertLess(len(proposed_tokens & old_tokens)
                                / len(proposed_tokens | old_tokens), .8)

if __name__ == "__main__":
    unittest.main()
