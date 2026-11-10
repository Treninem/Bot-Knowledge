"""T538: complete eight scoped practical dialogue intents, 100 candidates each.

Staging only: the replies are never consumer-registered or authority-bearing.
"""
import hashlib
import json
import subprocess
import unicodedata
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
POOL = "staging/ru/practical_dialogue_t{}_context_pool.json"

def norm(s):
    s = unicodedata.normalize("NFKC", s).casefold().replace("ё", "е")
    return " ".join("".join(c if c.isalnum() else " " for c in s).split())

class PracticalDialogueT538(unittest.TestCase):
    def test_exact_source_and_all_eight_stable_intents(self):
        stages = [
            json.loads((ROOT / POOL.format(n)).read_text(encoding="utf-8"))
            for n in range(534, 539)
        ]
        source = ROOT / "packs/ru/dialogue.json"
        source_hash = hashlib.sha256(source.read_bytes()).hexdigest()
        blob = subprocess.check_output(
            ["git", "hash-object", str(source)], cwd=ROOT, text=True
        ).strip()
        manifest = json.loads((ROOT / "manifest.json").read_text(encoding="utf-8"))
        self.assertIn({"path": "packs/ru/dialogue.json", "sha256": source_hash}, manifest["packs"])
        self.assertFalse(any(x["path"].startswith("staging/") for x in manifest["packs"]))
        ids, answers, notes, bags = set(), set(), set(), []
        stable = {e["intent_id"] for e in stages[0]["entries"]}
        self.assertEqual(len(stable), 8)
        self.assertEqual({e["intent_id"] for e in stages[-1]["entries"]}, stable)
        for idx, stage in enumerate(stages):
            self.assertEqual(stage["schema_version"], 1)
            self.assertFalse(stage["consumer_registered"])
            self.assertEqual(stage["audiences"], ["all_ai_bots"])
            self.assertEqual(stage["source_pack"], "packs/ru/dialogue.json")
            self.assertEqual(
                (stage["source_pack_manifest_sha256"], stage["source_pack_blob_sha"]),
                (source_hash, blob),
            )
            self.assertEqual({e["intent_id"] for e in stage["entries"]}, stable)
            for flag in ("read_only", "requires_direct_address", "no_personal_data",
                         "no_sanctions", "requires_context_match"):
                self.assertTrue(stage["constraints"][flag])
            for entry in stage["entries"]:
                self.assertEqual(
                    (entry["baseline_registered"], entry["prior_for_stable_id"],
                     entry["added_candidates"], entry["total_staged"],
                     entry["remaining"], entry["target"]),
                    (0, idx * 20, 20, (idx + 1) * 20, 100 - (idx + 1) * 20, 100),
                )
                self.assertEqual(len(entry["replies"]), 20)
                for position, row in enumerate(entry["replies"], 1):
                    self.assertEqual(
                        row["id"], "{}_{}".format(entry["intent_id"], idx * 20 + position)
                    )
                    self.assertNotIn(row["id"], ids)
                    ids.add(row["id"])
                    for value, target in ((row["text"], answers),
                                          (row["context_note"], notes)):
                        key = norm(value)
                        self.assertTrue(key)
                        self.assertNotIn(key, target)
                        target.add(key)
                    self.assertEqual(row["language"], "ru")
                    self.assertEqual(row["audiences"], ["all_ai_bots"])
                    self.assertEqual(row["context"], "direct")
                    self.assertTrue(row["read_only"])
                    self.assertGreaterEqual(len(row["text"]), 40)
                    self.assertNotRegex(
                        row["text"].lower(),
                        r"(?<!\w)(?:забанил|замутил|выдал бан|удалил сообщение)(?!\w)",
                    )
                    bag = set(norm(row["text"]).split())
                    for previous in bags:
                        self.assertLess(len(bag & previous) / len(bag | previous), 0.78)
                    bags.append(bag)
        self.assertEqual((len(ids), len(answers), len(notes)), (800, 800, 800))
        last = stages[-1]["checkpoint"]
        self.assertEqual(
            (last["prior_candidates"], last["added_candidates"],
             last["cumulative_candidates"], last["finished_100"],
             last["partial_intents"], last["remaining_total"]),
            (640, 160, 800, 8, 0, 0),
        )

if __name__ == "__main__":
    unittest.main()
