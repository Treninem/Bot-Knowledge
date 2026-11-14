"""K38 staged replies: explicit replacement accounting, no automatic semantic approval."""
import hashlib
import json
import re
import unicodedata
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FILE = ROOT / "staging/ru/structured_information_20261114_delta_k38.json"

def normalize(value):
    return " ".join(re.findall(r"[^\\W_]+", unicodedata.normalize("NFKC", value).casefold().replace("ё", "е")))

def words(value):
    return set(normalize(value).split())

def grams(value):
    s = normalize(value).replace(" ", "")
    return {s[i:i + 3] for i in range(max(0, len(s) - 2))}

def jac(x, y):
    return len(x & y) / max(1, len(x | y))

class K38(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = json.loads(FILE.read_text(encoding="utf-8"))

    def test_counts_and_rejections(self):
        d = self.data
        c = d["checkpoint"]
        self.assertEqual((len(d["entries"]), c["added_candidates"], c["staged_k_series_candidate_total"]), (7, 11, 4759))
        self.assertEqual((c["first_time_raw_slots_filled"], c["replacement_candidates_for_ineligible"]), (4, 7))
        self.assertEqual((c["remaining_raw_slots"], c["raw_candidate_complete_sets"], c["partial_intents"]), (0, 54, 0))
        self.assertEqual((c["editorial_approved_candidates"], c["editorial_approved_100_sets"]), (0, 0))
        self.assertEqual(sum(len(e["replies"]) for e in d["entries"]), 11)
        self.assertEqual(sum(len(e["known_ineligible_prior_ids"]) for e in d["entries"]), 7)
        self.assertEqual(len(set(r["id"] for e in d["entries"] for r in e["replies"])), 11)
        for e in d["entries"]:
            self.assertEqual(e["published_count"], 3)
            self.assertEqual(e["total_candidates_with_published"], 3 + e["previous_staged_count"] + e["added_candidates"])
            self.assertEqual(e["eligible_numeric_count_if_all_new_pass"], 100)
            self.assertEqual(e["target"], 100)
            self.assertEqual(e["remaining_raw"], 0)

    def test_safety_and_manifest_isolation(self):
        d = self.data
        self.assertFalse(d["consumer_registered"])
        self.assertEqual(d["language"], "ru")
        self.assertEqual(d["audiences"], ["all_ai_bots"])
        for key in ("read_only", "requires_direct_address", "requires_context_match", "no_personal_data", "no_sanctions"):
            self.assertTrue(d["constraints"][key])
        manifest = json.loads((ROOT / "manifest.json").read_text(encoding="utf-8"))
        known = {x["path"]: x["sha256"] for x in manifest["packs"]}
        self.assertNotIn(FILE.relative_to(ROOT).as_posix(), known)
        self.assertEqual(d["source_pack_manifest_sha256"], known[d["source_pack"]])
        self.assertEqual(hashlib.sha256((ROOT / d["source_pack"]).read_bytes()).hexdigest(), known[d["source_pack"]])
        self.assertLess(FILE.stat().st_size, 2 * 1024 * 1024)
        for e in d["entries"]:
            self.assertEqual((e["section"], e["language"]), ("умение", "ru"))
            for v in e["replies"]:
                self.assertEqual((v["language"], v["audiences"], v["context"], v["read_only"]), ("ru", ["all_ai_bots"], "direct", True))
                self.assertEqual(v["editorial_status"], "candidate_pending_full_semantic_review")
                self.assertTrue(len(v["text"]) > 80 and len(v["context_note"]) > 35)
                self.assertIn("не применять санкции", v["avoid"])
                self.assertNotIn("@", v["text"] + v["context_note"])

    def test_cross_stage_and_known_exclusions(self):
        d = self.data
        prior = []
        excluded = set()
        for path in d["prior_stages"]:
            stage = json.loads((ROOT / path).read_text(encoding="utf-8"))
            for e in stage["entries"]:
                for r in e["replies"]:
                    prior.append((e["intent_id"], r["id"], normalize(r["text"]), words(r["text"]), grams(r.get("context_note", ""))))
                    if r.get("editorial_eligible") is False:
                        excluded.add(r["id"])
        published = json.loads((ROOT / d["source_pack"]).read_text(encoding="utf-8"))
        for e in published["records"]:
            for value in [e["answer"], *e["variants"]]:
                prior.append((e["id"], e["id"], normalize(value), words(value), set()))
        ids = {r[1] for r in prior}
        self.assertTrue(set(r for e in d["entries"] for r in e["known_ineligible_prior_ids"]).issubset(excluded))
        for e in d["entries"]:
            for v in e["replies"]:
                self.assertNotIn(v["id"], ids)
                ids.add(v["id"])
                nv, tv, cv = normalize(v["text"]), words(v["text"]), grams(v["context_note"])
                for intent, old_id, no, to, co in prior:
                    self.assertNotEqual(nv, no, (v["id"], old_id))
                    self.assertLess(jac(tv, to), 0.70, (v["id"], old_id))
                    if intent == e["intent_id"] and co:
                        self.assertLess(jac(cv, co), 0.60, (v["id"], old_id))
                prior.append((e["intent_id"], v["id"], nv, tv, cv))

if __name__ == "__main__":
    unittest.main()
