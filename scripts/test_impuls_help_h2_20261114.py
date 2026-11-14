"""H2: independent, read-only scoped ImPULS FAQ staged answers."""
import hashlib, json, re, unittest
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
STAGE = ROOT / "staging/ru/impuls_help_context_h2_20261114.json"
H1 = ROOT / "staging/ru/impuls_help_context_h1_20261114.json"
SOURCE = ROOT / "packs/ru/impuls_help_qa.json"

def norm(s):
    return " ".join(re.findall(r"[^\W_]+", s.casefold().replace("ё", "е")))

class HelpH2(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.d = json.loads(STAGE.read_text(encoding="utf-8"))
        cls.h1 = json.loads(H1.read_text(encoding="utf-8"))
        cls.source = json.loads(SOURCE.read_text(encoding="utf-8"))
        cls.manifest = json.loads((ROOT / "manifest.json").read_text(encoding="utf-8"))

    def test_manifest_and_safety(self):
        known={v["path"]:v["sha256"] for v in self.manifest["packs"]}
        self.assertNotIn(STAGE.relative_to(ROOT).as_posix(),known)
        self.assertEqual(self.d["source_pack_manifest_sha256"],known[self.d["source_pack"]])
        self.assertEqual(hashlib.sha256(SOURCE.read_bytes()).hexdigest(),known[self.d["source_pack"]])
        self.assertFalse(self.d["consumer_registered"])
        self.assertTrue(all(self.d["constraints"].values()))
        self.assertLess(STAGE.stat().st_size,2*1024*1024)

    def test_count_id_scope(self):
        e=self.d["entries"]
        self.assertEqual((len(e),sum(len(x["replies"]) for x in e)),(15,45))
        self.assertEqual((self.d["checkpoint"]["aggregate_new_in_H1_and_H2"],self.d["checkpoint"]["distinct_intents_H1_and_H2"]),(90,30))
        old={x["id"]:x for x in self.source["records"]}
        idset=set()
        for x in e:
            self.assertEqual(x["canonical_question"],old[x["intent_id"]]["question"])
            self.assertEqual(x["published_count"],1+len(old[x["intent_id"]]["variants"]))
            self.assertEqual(x["remaining_to_target_excluding_other_prs"],100-x["published_count"]-3)
            for v in x["replies"]:
                self.assertNotIn(v["id"],idset)
                idset.add(v["id"])
                self.assertEqual(v["audiences"],["impuls"])
                self.assertEqual(v["editorial_status"],"candidate_pending_full_semantic_review")
                self.assertTrue(v["read_only"])
                self.assertGreater(len(v["context_note"]),34)
                self.assertIn("прямом вопросе",v["avoid"])

    def test_no_exact_duplicate_across_published_h1_h2(self):
        earlier={norm(t) for e in self.source["records"] for t in [e["answer"],*e["variants"]]}
        earlier.update(norm(v["text"]) for e in self.h1["entries"] for v in e["replies"])
        for e in self.d["entries"]:
            for v in e["replies"]:
                t=norm(v["text"])
                self.assertNotIn(t,earlier)
                earlier.add(t)
                self.assertNotIn("@",v["text"])

if __name__ == "__main__":
    unittest.main()
