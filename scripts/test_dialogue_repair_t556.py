"""Read-only T556 200 new originals, pinned ancestry and global duplicate checks."""
import hashlib
import json
import subprocess
import unicodedata
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PATHS = [
    ROOT / "staging/ru/dialogue_repair_t554_context_pool.json",
    ROOT / "staging/ru/dialogue_repair_t555_context_delta.json",
    ROOT / "staging/ru/dialogue_repair_t556_context_delta.json",
]

def norm(value):
    return " ".join("".join(" " if unicodedata.category(c)[0] in {"P", "S"} else c
                    for c in unicodedata.normalize("NFKC", value).casefold().replace("ё", "е")).split())

class DialogueRepair556(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.parts = [json.loads(p.read_text(encoding="utf-8")) for p in PATHS]

    def test_lineage_manifest_and_constraints(self):
        old, prev, new = self.parts
        manifest = json.loads((ROOT / "manifest.json").read_text(encoding="utf-8"))
        raw = (ROOT / new["source_pack"]).read_bytes()
        digest = hashlib.sha256(raw).hexdigest()
        self.assertIn({"path": new["source_pack"], "sha256": digest}, manifest["packs"])
        self.assertEqual(new["source_pack_manifest_sha256"], digest)
        self.assertEqual(new["source_pack_blob_sha"],
                         subprocess.check_output(["git", "hash-object", new["source_pack"]], cwd=ROOT, text=True).strip())
        self.assertEqual(new["parent_stage"], str(PATHS[1].relative_to(ROOT)))
        self.assertEqual(new["parent_stage_blob_sha"],
                         subprocess.check_output(["git", "hash-object", str(PATHS[1])], cwd=ROOT, text=True).strip())
        for p in self.parts:
            self.assertFalse(p["consumer_registered"])
            self.assertEqual(p["audiences"], ["all_ai_bots"])
            self.assertTrue(p["constraints"]["read_only"])
            self.assertTrue(p["constraints"]["no_sanctions"])
            self.assertTrue(p["constraints"]["requires_direct_address"])
            self.assertTrue(p["constraints"]["requires_context_match"])
        self.assertEqual(new["constraints"], prev["constraints"])
        self.assertEqual(new["stage_type"], "supplemental_contextual_reply_delta")

    def test_complete_unique_440(self):
        old, prev, new = self.parts
        ids, texts, notes = set(), set(), set()
        one = {e["intent_id"]: e for e in old["entries"]}
        two = {e["intent_id"]: e for e in prev["entries"]}
        self.assertEqual(len(one), len(two))
        self.assertEqual(len(one), len(new["entries"]), 10)
        for e in new["entries"]:
            k = e["intent_id"]
            self.assertEqual(e["canonical_question"], one[k]["canonical_question"])
            self.assertEqual((e["prior_for_stable_id"], e["added_candidates"], e["total_staged"], e["target"], e["remaining"]), (24, 20, 44, 100, 56))
            self.assertEqual(len(e["replies"]), 20)
            combined = one[k]["replies"] + two[k]["replies"] + e["replies"]
            self.assertEqual(len(combined), 44)
            for i, r in enumerate(combined, 1):
                self.assertEqual(r["id"], f"{k}_{i:02d}")
                self.assertNotIn(r["id"], ids)
                ids.add(r["id"])
                for text, pool in [(r["text"], texts), (r["context_note"], notes)]:
                    n = norm(text)
                    self.assertTrue(n)
                    self.assertNotIn(n, pool)
                    pool.add(n)
                self.assertEqual(r["audiences"], ["all_ai_bots"])
                self.assertEqual(r["language"], "ru")
                self.assertEqual(r["context"], "direct")
                self.assertTrue(r["read_only"])
        self.assertEqual((len(ids), len(texts), len(notes)), (440, 440, 440))
        c = new["checkpoint"]
        self.assertEqual((c["prior_candidates"], c["added_candidates"], c["cumulative_candidates"], c["partial_intents"], c["remaining_total"]), (240, 200, 440, 10, 560))

    def test_near_duplicate_and_cross_stage(self):
        data = [r["text"] for p in self.parts for e in p["entries"] for r in e["replies"]]
        tokens = [set(norm(t).split()) for t in data]
        for i, a in enumerate(tokens):
            for b in tokens[i+1:]:
                self.assertLess(len(a & b)/len(a | b), .78)
        normalized = {norm(t) for t in data}
        for path in (ROOT/"staging/ru").glob("*.json"):
            if path in PATHS:
                continue
            other = json.loads(path.read_text(encoding="utf-8"))
            if not isinstance(other, dict):
                continue
            for item in other.get("entries", []):
                if not isinstance(item, dict):
                    continue
                for reply in item.get("replies", []):
                    value = reply.get("text") if isinstance(reply,dict) else reply
                    if isinstance(value, str):
                        self.assertNotIn(norm(value), normalized, f"cross-stage duplicate {path.name}")

if __name__ == "__main__":
    unittest.main()
