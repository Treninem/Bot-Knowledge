"""Read-only staging validation for quantitative clarity A–E (200 new in D/E)."""
import hashlib
import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PATHS = [
    "staging/ru/quantitative_clarity_20261111_context_pool.json",
    "staging/ru/quantitative_clarity_20261111_context_delta_b.json",
    "staging/ru/quantitative_clarity_20261111_context_delta_c.json",
    "staging/ru/quantitative_clarity_20261111_context_delta_d.json",
    "staging/ru/quantitative_clarity_20261111_context_delta_e.json",
]


def normalized(s):
    return " ".join(re.findall(r"[^\W_]+", s.casefold().replace("ё", "е")))


def git_blob(raw):
    return hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()


class QuantitativeClarityExtensionTest(unittest.TestCase):
    def test_five_stage_lineage_integrity_and_isolation(self):
        raw = [(ROOT / p).read_bytes() for p in PATHS]
        data = [json.loads(x) for x in raw]
        manifest = json.loads((ROOT / "manifest.json").read_text(encoding="utf-8"))
        pack = data[0]["source_pack"]
        source = (ROOT / pack).read_bytes()
        expected_sha = hashlib.sha256(source).hexdigest()
        self.assertEqual(data[0]["source_pack_manifest_sha256"], expected_sha)
        self.assertEqual(data[0]["source_pack_blob_sha"], git_blob(source))
        self.assertIn({"path": pack, "sha256": expected_sha}, manifest["packs"])
        published = {p["path"] for p in manifest["packs"]}
        self.assertTrue(set(PATHS).isdisjoint(published))
        stable = {entry["intent_id"] for entry in data[0]["entries"]}
        self.assertEqual(len(stable), 10)
        for i, stage in enumerate(data):
            self.assertFalse(stage["consumer_registered"])
            self.assertEqual(stage["audiences"], ["all_ai_bots"])
            self.assertEqual(stage["language"], "ru")
            self.assertTrue(all(stage["constraints"].values()))
            self.assertEqual({entry["intent_id"] for entry in stage["entries"]}, stable)
            self.assertEqual(stage["source_pack"], pack)
            self.assertEqual(stage["source_pack_manifest_sha256"], expected_sha)
            self.assertEqual(stage["source_pack_blob_sha"], git_blob(source))
            self.assertEqual(stage["checkpoint"]["cumulative_candidates"], (i+1)*100)
            self.assertEqual(stage["checkpoint"]["prior_candidates"], i*100)
            self.assertEqual(stage["checkpoint"]["added_candidates"], 100)
            self.assertEqual(stage["checkpoint"]["remaining_total"], 900-i*100)
            self.assertEqual(stage["checkpoint"]["finished_100"], 0)
            self.assertEqual(stage["checkpoint"]["partial_intents"], 10)
            if i:
                self.assertEqual(stage["parent_stage"], PATHS[i-1])
                self.assertEqual(stage["parent_stage_blob_sha"], git_blob(raw[i-1]))
        ids, texts, notes, sets = set(), set(), set(), []
        for i, stage in enumerate(data):
            for entry in stage["entries"]:
                self.assertEqual(entry["audiences"], ["all_ai_bots"])
                self.assertEqual(entry["target"], 100)
                self.assertEqual(entry["prior_for_stable_id"], i*10)
                self.assertEqual(entry["added_candidates"], 10)
                self.assertEqual(entry["total_staged"], (i+1)*10)
                self.assertEqual(entry["remaining"], 90-i*10)
                self.assertEqual(len(entry["replies"]), 10)
                for j, reply in enumerate(entry["replies"], start=i*10+1):
                    self.assertEqual(reply["id"], f'{entry["intent_id"]}_{j:02d}')
                    self.assertTrue(reply["read_only"])
                    self.assertEqual(reply["context"], "direct")
                    self.assertEqual(reply["language"], "ru")
                    self.assertEqual(reply["audiences"], ["all_ai_bots"])
                    self.assertIn("не применять санкции", reply["avoid"])
                    self.assertNotRegex(reply["text"], r"(?i)[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,}")
                    self.assertNotRegex(reply["text"], r"\b(?:\+?\d[ -]?){11,}\b")
                    for value, bag in ((reply["id"], ids), (normalized(reply["text"]), texts), (normalized(reply["context_note"]), notes)):
                        self.assertNotIn(value, bag)
                        self.assertGreater(len(value), 12)
                        bag.add(value)
                    sets.append(set(normalized(reply["text"]).split()))
        self.assertEqual((len(ids), len(texts), len(notes)), (500, 500, 500))
        for i, left in enumerate(sets):
            for right in sets[i+1:]:
                self.assertLess(len(left & right) / len(left | right), 0.8)


if __name__ == "__main__":
    unittest.main()
