"""T582–T583: staged contextual social replies, exact-parent and dedup checks."""
import json
import subprocess
import unittest
from pathlib import Path
from scripts.test_social_boundaries_t580 import norm

ROOT = Path(__file__).resolve().parents[1]
PATHS = [
    Path("staging/ru/social_boundaries_t580_context_pool.json"),
    Path("staging/ru/social_boundaries_t581_context_delta.json"),
    Path("staging/ru/social_boundaries_t582_context_delta.json"),
    Path("staging/ru/social_boundaries_t583_context_delta.json"),
]


class TestT582T583(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.documents = [
            json.loads((ROOT / path).read_text(encoding="utf-8"))
            for path in PATHS
        ]

    def test_parents_source_and_read_only_scope(self):
        data = self.documents
        root = data[0]
        for index, document in enumerate(data):
            self.assertFalse(document["consumer_registered"])
            self.assertEqual((document["language"], document["audiences"]), ("ru", ["all_ai_bots"]))
            for flag in ("read_only", "requires_context_match", "requires_direct_address",
                         "no_personal_data", "no_sanctions"):
                self.assertIs(document["constraints"][flag], True)
            for field in ("source_pack", "source_pack_blob_sha", "source_pack_manifest_sha256"):
                self.assertEqual(document[field], root[field])
            if index:
                parent = str(PATHS[index-1])
                digest = subprocess.check_output(
                    ["git", "hash-object", parent], cwd=ROOT, text=True
                ).strip()
                self.assertEqual((document["parent_stage"], document["parent_stage_blob_sha"]),
                                 (parent, digest))

    def test_four_hundred_exact_contextual_replies(self):
        documents = self.documents
        expected = [(entry["intent_id"], entry["canonical_question"], entry["section"])
                    for entry in documents[0]["entries"]]
        ids, texts, contexts = set(), set(), set()
        all_replies = []
        for stage_index, document in enumerate(documents):
            entries = document["entries"]
            self.assertEqual(len(entries), 10)
            self.assertEqual(
                [(entry["intent_id"], entry["canonical_question"], entry["section"])
                 for entry in entries], expected
            )
            self.assertEqual(document["checkpoint"]["prior_candidates"], stage_index*100)
            self.assertEqual(document["checkpoint"]["added_candidates"], 100)
            self.assertEqual(document["checkpoint"]["cumulative_candidates"], (stage_index+1)*100)
            for entry in entries:
                self.assertEqual((entry["prior_for_stable_id"], entry["added_candidates"],
                                  entry["total_staged"], entry["remaining"], entry["target"]),
                                 (stage_index*10, 10, (stage_index+1)*10,
                                  100-(stage_index+1)*10, 100))
                self.assertEqual(len(entry["replies"]), 10)
                for position, reply in enumerate(entry["replies"], stage_index*10+1):
                    self.assertEqual(reply["id"], f'{entry["intent_id"]}_{position:02d}')
                    self.assertEqual((reply["language"], reply["style"], reply["audiences"],
                                      reply["context"], reply["read_only"]),
                                     ("ru", "neutral", ["all_ai_bots"], "direct", True))
                    self.assertTrue(reply["avoid"].startswith("Только при подтверждённом контексте"))
                    self.assertNotRegex(reply["text"], r"(?i)https?://|@[a-z0-9_]+|\b\+?\d[ -]?\d{2,}")
                    for value, seen in ((reply["id"], ids), (norm(reply["text"]), texts),
                                        (norm(reply["context_note"]), contexts)):
                        self.assertTrue(value)
                        self.assertNotIn(value, seen)
                        seen.add(value)
                    all_replies.append(reply)
        self.assertEqual((len(ids), len(texts), len(contexts)), (400, 400, 400))
        tokens = [set(norm(reply["text"]).split()) for reply in all_replies]
        for index, left in enumerate(tokens):
            for right in tokens[index+1:]:
                self.assertLess(len(left & right)/len(left | right), .8)


if __name__ == "__main__":
    unittest.main()
