"""Checks for generic support triage continuation C/D/E/F/G; staging data only."""
import hashlib
import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FILES = [
    "staging/ru/support_triage_20261110_context_pool.json",
    "staging/ru/support_triage_20261110_context_delta_b.json",
    "staging/ru/support_triage_20261110_context_delta_c.json",
    "staging/ru/support_triage_20261110_context_delta_d.json",
    "staging/ru/support_triage_20261110_context_delta_e.json",
    "staging/ru/support_triage_20261110_context_delta_f.json",
    "staging/ru/support_triage_20261110_context_delta_g.json",
]
RELATED = [
    "staging/ru/evidence_boundaries_t560_context_pool.json",
    "staging/ru/social_boundaries_t580_context_pool.json",
    "staging/ru/interpersonal_t590_context_pool.json",
    "staging/ru/group_pragmatics_t600_context_pool.json",
    "staging/ru/dialogue_repair_t554_context_pool.json",
    "staging/ru/practical_dialogue_t534_context_pool.json",
]

def normalized(s):
    return " ".join(re.findall(r"[^\W_]+", s.casefold().replace("ё", "е")))

def blob_sha(raw):
    prefix = ("blob " + str(len(raw)) + "\0").encode()
    return hashlib.sha1(prefix + raw).hexdigest()

def tokens(s):
    return set(normalized(s).split())

class TestSupportTriageContinuation(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.raws = [(ROOT / p).read_bytes() for p in FILES]
        cls.stages = [json.loads(b) for b in cls.raws]

    def test_source_manifest_lineage(self):
        first = self.stages[0]
        source_bytes = (ROOT / first["source_pack"]).read_bytes()
        sha = hashlib.sha256(source_bytes).hexdigest()
        manifest = json.loads((ROOT / "manifest.json").read_text("utf-8"))
        self.assertEqual(first["source_pack_manifest_sha256"], sha)
        self.assertEqual(first["source_pack_blob_sha"], blob_sha(source_bytes))
        self.assertIn({"path": first["source_pack"], "sha256": sha}, manifest["packs"])
        for path in FILES:
            self.assertNotIn(path, [p["path"] for p in manifest["packs"]])
        for i, stage in enumerate(self.stages):
            self.assertEqual(stage["source_pack"], first["source_pack"])
            for key in ("source_pack_manifest_sha256", "source_pack_blob_sha", "checked_source_main_sha"):
                self.assertEqual(stage[key], first[key])
            if i:
                self.assertEqual(stage["parent_stage"], FILES[i-1])
                self.assertEqual(stage["parent_stage_blob_sha"], blob_sha(self.raws[i-1]))

    def test_scope_counts_ids_and_private_data(self):
        seen_ids, seen_texts, seen_notes = set(), set(), set()
        counts = [10, 10, 20, 10, 10, 20, 20]
        names = None
        for i, (stage, count) in enumerate(zip(self.stages, counts)):
            self.assertEqual(stage["stage_type"], "supplemental_contextual_reply_pool")
            self.assertIs(stage["consumer_registered"], False)
            self.assertEqual(stage["audiences"], ["all_ai_bots"])
            self.assertEqual(stage["language"], "ru")
            for key in ("read_only", "requires_direct_address", "no_personal_data", "no_sanctions", "requires_context_match"):
                self.assertIs(stage["constraints"][key], True)
            cp = stage["checkpoint"]
            self.assertEqual(cp["added_candidates"], count * 10)
            self.assertEqual(cp["prior_candidates"], sum(counts[:i]) * 10)
            self.assertEqual(cp["cumulative_candidates"], sum(counts[:i+1]) * 10)
            self.assertEqual(cp["processed_intents"], 10)
            self.assertEqual(cp["finished_100"], 10 if i == len(counts) - 1 else 0)
            self.assertEqual(cp["partial_intents"], 0 if i == len(counts) - 1 else 10)
            self.assertEqual(cp["remaining_total"], 1000 - sum(counts[:i+1]) * 10)
            self.assertEqual(len(stage["entries"]), 10)
            names_now = {e["intent_id"] for e in stage["entries"]}
            if names is None:
                names = names_now
            self.assertEqual(names_now, names)
            for entry in stage["entries"]:
                self.assertEqual(entry["target"], 100)
                self.assertEqual(entry["added_candidates"], count)
                self.assertEqual(entry["prior_for_stable_id"], sum(counts[:i]))
                self.assertEqual(entry["total_staged"], sum(counts[:i+1]))
                self.assertEqual(entry["remaining"], 100 - sum(counts[:i+1]))
                self.assertEqual(entry["response_role"], "assistant_reply")
                self.assertEqual(len(entry["replies"]), count)
                for idx, r in enumerate(entry["replies"], sum(counts[:i]) + 1):
                    self.assertEqual(r["id"], f'{entry["intent_id"]}_{idx:02d}')
                    self.assertEqual(r["audiences"], ["all_ai_bots"])
                    self.assertEqual(r["language"], "ru")
                    self.assertEqual(r["context"], "direct")
                    self.assertIs(r["read_only"], True)
                    self.assertIn("совпадении условия", r["avoid"])
                    for value, seen in ((r["id"], seen_ids), (normalized(r["text"]), seen_texts),
                                        (normalized(r["context_note"]), seen_notes)):
                        self.assertTrue(value)
                        self.assertNotIn(value, seen)
                        seen.add(value)
                    self.assertNotRegex(r["text"], r"https?://|[A-Za-z0-9_.+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
                    self.assertNotRegex(r["text"], r"(?<!\w)\+?\d[\d ()-]{8,}\d(?!\w)")
        self.assertEqual((len(seen_ids), len(seen_texts), len(seen_notes)), (1000, 1000, 1000))

    def test_lexical_near_duplicates_against_prior_stages_and_related(self):
        prior = [r["text"] for s in self.stages[:2] for e in s["entries"] for r in e["replies"]]
        incoming = [r["text"] for s in self.stages[2:] for e in s["entries"] for r in e["replies"]]
        self.assertEqual(len(incoming), 800)
        related = []
        for filename in RELATED:
            data = json.loads((ROOT / filename).read_text("utf-8"))
            for entry in data.get("entries", []):
                related.extend(r["text"] for r in entry.get("replies", []))
        old = [tokens(t) for t in prior + related]
        exact = {normalized(t) for t in prior + related}
        highest = 0.0
        for t in incoming:
            n = normalized(t)
            self.assertNotIn(n, exact)
            exact.add(n)
            a = tokens(t)
            for b in old:
                shared = len(a & b)
                similarity = shared / len(a | b) if a or b else 1
                highest = max(highest, similarity)
                self.assertLess(similarity, .80, (t, similarity))
            old.append(a)
        self.assertLess(highest, .80)
        print("C+D+E+F+G cross-pool token Jaccard max:", round(highest, 4),
              "compared against", len(prior) + len(related), "prior/related replies")

if __name__ == "__main__":
    unittest.main()
