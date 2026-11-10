"""T544: RU direct/group greetings, returns, farewells and honest scope — staging only."""
import hashlib
import json
import re
import subprocess
import unicodedata
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
POOL = ROOT / "staging/ru/greeting_exit_t544_context_pool.json"
SOURCE = "packs/ru/social_dialogues.json"

def norm(s):
    s = unicodedata.normalize("NFKC", s).casefold().replace("ё", "е")
    return " ".join("".join(" " if unicodedata.category(c)[0] in {"P", "S"} else c for c in s).split())

class T544(unittest.TestCase):
    def test_source_scope_duplicates(self):
        j = json.loads(POOL.read_text(encoding="utf-8"))
        mf = json.loads((ROOT / "manifest.json").read_text(encoding="utf-8"))
        digest = hashlib.sha256((ROOT / SOURCE).read_bytes()).hexdigest()
        blob = subprocess.check_output(["git", "hash-object", str(ROOT / SOURCE)], cwd=ROOT, text=True).strip()
        self.assertIn({"path": SOURCE, "sha256": digest}, mf["packs"])
        self.assertEqual((j["source_pack"], j["source_pack_manifest_sha256"], j["source_pack_blob_sha"]), (SOURCE, digest, blob))
        self.assertEqual((j["stage_type"], j["consumer_registered"], j["audiences"]), ("supplemental_contextual_reply_pool", False, ["all_ai_bots"]))
        for k in ("read_only", "requires_direct_address", "no_personal_data", "no_sanctions", "requires_context_match"):
            self.assertTrue(j["constraints"][k])
        self.assertEqual(len(j["entries"]), 5)
        ids, texts, notes, bags = set(), set(), set(), []
        for e in j["entries"]:
            self.assertTrue(e["intent_id"].startswith("t544_"))
            self.assertEqual((e["prior_for_stable_id"], e["added_candidates"], e["total_staged"], e["remaining"]), (50, 25, 75, 25))
            self.assertEqual(len(e["replies"]), 75)
            for i, r in enumerate(e["replies"], 1):
                self.assertEqual(r["id"], e["intent_id"] + "_%02d" % i)
                self.assertNotIn(r["id"], ids); ids.add(r["id"])
                for value, seen in ((r["text"], texts), (r["context_note"], notes)):
                    key = norm(value); self.assertTrue(key); self.assertNotIn(key, seen); seen.add(key)
                self.assertTrue(r["read_only"])
                self.assertEqual(r["audiences"], ["all_ai_bots"])
                self.assertIn(r["context"], ("direct", "group_addressed"))
                self.assertIn("прямом обращении", r["avoid"])
                self.assertNotRegex(r["text"].lower(), r"\\b(?:забанил|замутил|выдал бан|удалил сообщение)\\b")
                bag = set(norm(r["text"]).split())
                for other in bags:
                    self.assertLess(len(bag & other) / len(bag | other), .78)
                bags.append(bag)
        self.assertEqual((len(ids), len(texts), len(notes)), (375, 375, 375))
        self.assertEqual((j["checkpoint"]["cumulative_candidates"], j["checkpoint"]["remaining_total"]), (375, 125))
        external = set()
        for path in sorted((ROOT / "staging/ru").glob("*.json")):
            if path == POOL: continue
            other = json.loads(path.read_text(encoding="utf-8"))
            if not isinstance(other, dict): continue
            for e in other.get("entries", []):
                if not isinstance(e, dict): continue
                for r in e.get("replies", []):
                    if isinstance(r, dict) and isinstance(r.get("text"), str): external.add(norm(r["text"]))
                    elif isinstance(r, str): external.add(norm(r))
        self.assertFalse(texts & external, "Duplicate against other staged reply pools")

if __name__ == "__main__":
    unittest.main()
