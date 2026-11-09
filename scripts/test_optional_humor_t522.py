"""T522 opt-in humor: source integrity, stage counts, privacy and dedup."""
import hashlib
import json
import re
import unicodedata
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PACK = "packs/ru/optional_humor_qa.json"
STAGES = (518, 519, 520, 521, 522)
CATS = ("daily","absurd","work","tech","procrastination",
        "selfirony","friendly","dry","darkfiction","mini")

def norm(s):
    s = unicodedata.normalize("NFKC", s).casefold().replace("ё", "е")
    return " ".join("".join(c if c.isalnum() else " " for c in s).split())

def words(s):
    return {w for w in norm(s).split() if len(w) > 2}

class T522(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.raw = (ROOT / PACK).read_bytes()
        cls.pack = json.loads(cls.raw)
        cls.stages = {n: json.loads((ROOT / f"staging/ru/optional_humor_t{n}_context_pool.json").read_text(encoding="utf-8")) for n in STAGES}

    def test_manifest_sha_blob_and_scopes(self):
        manifest = json.loads((ROOT/"manifest.json").read_text())
        expected = next(p["sha256"] for p in manifest["packs"] if p["path"] == PACK)
        self.assertEqual(hashlib.sha256(self.raw).hexdigest(), expected)
        self.assertNotIn("staging/ru/optional_humor_t522_context_pool.json", [p["path"] for p in manifest["packs"]])
        git_blob = hashlib.sha1(b"blob " + str(len(self.raw)).encode() + bytes([0]) + self.raw).hexdigest()
        for n, stage in self.stages.items():
            self.assertFalse(stage["consumer_registered"], n)
            self.assertEqual(stage["source_pack_manifest_sha256"], expected)
            self.assertEqual(stage["source_pack_blob_sha"], git_blob)
            self.assertEqual(stage["audiences"], ["all_ai_bots"])
            for name in ("read_only", "requires_direct_address", "requires_humor_opt_in", "no_personal_data", "no_sanctions", "requires_context_match"):
                self.assertTrue(stage["constraints"].get(name), (n, name))

    def test_cumulative_counts_and_ids(self):
        intents = ["humor_t517_"+c for c in CATS]
        self.assertEqual([r["id"] for r in self.pack["records"]], intents)
        totals = dict.fromkeys(intents, 9)
        for n, stage in self.stages.items():
            self.assertEqual([e["intent_id"] for e in stage["entries"]], intents)
            for e in stage["entries"]:
                key = e["intent_id"]
                self.assertEqual(e["prior_for_stable_id"], totals[key])
                self.assertEqual(e["added_candidates"], len(e["replies"]))
                totals[key] += len(e["replies"])
                self.assertEqual((e["total_staged"],e["remaining"]),(totals[key],100-totals[key]))
        self.assertEqual(set(totals.values()), {79})
        stage=self.stages[522]
        self.assertEqual((stage["checkpoint"]["processed_intents"],stage["checkpoint"]["added_candidates"],stage["checkpoint"]["remaining_total"]),(10,200,210))

    def test_new_reply_uniqueness_and_privacy(self):
        existing = [v for r in self.pack["records"] for v in [r["answer"],*r["variants"]]]
        for n in STAGES[:-1]:
            existing.extend(r["text"] for e in self.stages[n]["entries"] for r in e["replies"])
        norms = set(map(norm,existing))
        bags = [words(s) for s in existing]
        seen_ids = set()
        for e in self.stages[522]["entries"]:
            self.assertEqual(len(e["replies"]),20)
            notes=set()
            for r in e["replies"]:
                self.assertNotIn(r["id"],seen_ids)
                seen_ids.add(r["id"])
                self.assertEqual(r["language"],"ru")
                self.assertEqual(r["audiences"],["all_ai_bots"])
                self.assertIn(r["context"],("direct","private"))
                self.assertTrue(r["read_only"])
                self.assertTrue(r["context_note"].startswith("Вымышленная ситуация: "))
                self.assertNotIn(r["context_note"],notes)
                notes.add(r["context_note"])
                self.assertIn("прямому запросу",r["avoid"])
                self.assertIn("санкций",r["avoid"])
                s=r["text"]
                self.assertGreater(len(s),49)
                self.assertNotRegex(s,r"https?://|@[A-Za-z0-9_]+|[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Za-z]{2,}")
                n=norm(s)
                self.assertNotIn(n,norms)
                bag=words(s)
                self.assertLess(max((len(bag&old)/max(1,len(bag|old)) for old in bags),default=0),.78)
                bags.append(bag)
                norms.add(n)

if __name__ == "__main__":
    unittest.main()
