"""Read-only checks for communication integrity RU staged replies (2026-11-11)."""
import hashlib
import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STAGE = "staging/ru/communication_integrity_20261111_context_pool.json"
RELATED = [
    "greeting_exit_t544_context_pool.json",
    "conversation_contracts_t570_context_pool.json",
    "social_boundaries_t580_context_pool.json",
    "interpersonal_t590_context_pool.json",
    "group_pragmatics_t600_context_pool.json",
    "dialogue_repair_t554_context_pool.json",
    "evidence_boundaries_t560_context_pool.json",
    "practical_dialogue_t534_context_pool.json",
    "bot_help_t549_context_pool.json",
    "support_triage_20261110_context_pool.json",
]

def normalized(value):
    return " ".join(re.findall(r"[^\W_]+", value.casefold().replace("ё", "е")))

def tokens(value):
    return set(normalized(value).split())

def git_blob_sha(content):
    return hashlib.sha1(("blob " + str(len(content)) + "\0").encode() + content).hexdigest()

class CommunicationIntegrityA(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = json.loads((ROOT / STAGE).read_text("utf-8"))

    def test_source_manifest_unchanged(self):
        d = self.data
        source = (ROOT / d["source_pack"]).read_bytes()
        real_sha = hashlib.sha256(source).hexdigest()
        manifest = json.loads((ROOT / "manifest.json").read_text("utf-8"))
        self.assertEqual(d["source_pack_manifest_sha256"], real_sha)
        self.assertEqual(d["source_pack_blob_sha"], git_blob_sha(source))
        self.assertIn({"path": d["source_pack"], "sha256": real_sha}, manifest["packs"])
        self.assertNotIn(STAGE, [item["path"] for item in manifest["packs"]])
        self.assertEqual(d["consumer_registered"], False)

    def test_structural_privacy_and_scope(self):
        d = self.data
        self.assertEqual(d["language"], "ru")
        self.assertEqual(d["audiences"], ["all_ai_bots"])
        self.assertEqual(d["stage_type"], "supplemental_contextual_reply_pool")
        for flag in ("read_only", "requires_direct_address", "no_personal_data",
                     "no_sanctions", "requires_context_match"):
            self.assertIs(d["constraints"][flag], True)
        self.assertEqual(len(d["entries"]), 10)
        self.assertEqual(d["checkpoint"]["added_candidates"], 120)
        self.assertEqual(d["checkpoint"]["partial_intents"], 10)
        self.assertEqual(d["checkpoint"]["finished_100"], 0)
        ids, answers, conditions = set(), set(), set()
        for entry in d["entries"]:
            self.assertEqual((entry["prior_for_stable_id"], entry["added_candidates"],
                              entry["total_staged"], entry["target"], entry["remaining"]),
                             (0, 12, 12, 100, 88))
            self.assertEqual(entry["response_role"], "assistant_reply")
            self.assertEqual(len(entry["replies"]), 12)
            for index, reply in enumerate(entry["replies"], 1):
                self.assertEqual(reply["id"], entry["intent_id"] + "_" + f"{index:02d}")
                self.assertEqual(reply["audiences"], ["all_ai_bots"])
                self.assertEqual(reply["context"], "direct")
                self.assertEqual(reply["language"], "ru")
                self.assertIs(reply["read_only"], True)
                self.assertIn("совпадении контекста", reply["avoid"])
                self.assertGreater(len(reply["context_note"].strip()), 15)
                self.assertNotRegex(reply["text"], r"https?://|[A-Za-z0-9_.+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
                self.assertNotRegex(reply["text"], r"(?<!\w)\+?\d[\d ()-]{8,}\d(?!\w)")
                for item, seen in ((reply["id"], ids), (normalized(reply["text"]), answers),
                                   (normalized(reply["context_note"]), conditions)):
                    self.assertTrue(item)
                    self.assertNotIn(item, seen)
                    seen.add(item)
        self.assertEqual((len(ids), len(answers), len(conditions)), (120, 120, 120))

    def test_related_lexical_duplicates(self):
        old = []
        for filename in RELATED:
            d = json.loads((ROOT / "staging" / "ru" / filename).read_text("utf-8"))
            old.extend(r["text"] for e in d["entries"] for r in e["replies"])
        new = [r["text"] for e in self.data["entries"] for r in e["replies"]]
        prior = [tokens(t) for t in old]
        highest = 0.0
        for text in new:
            a = tokens(text)
            for b in prior:
                overlap = len(a & b) / len(a | b)
                highest = max(highest, overlap)
                self.assertLess(overlap, 0.80, (text, overlap))
        self.assertEqual(len(old), 1920)
        self.assertLess(highest, 0.80)

if __name__ == "__main__":
    unittest.main()
