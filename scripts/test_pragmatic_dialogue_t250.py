"""T250: 72 context-distinct spoken-pragmatics variants; confirmed registered pack SHA."""
import hashlib
import json
import re
import unittest
import unicodedata
from pathlib import Path
from scripts.validate_qa_v1 import validate_qa_pack

ROOT = Path(__file__).resolve().parents[1]
REL = "packs/ru/spoken_pragmatics_qa.json"

def norm(s):
    s = unicodedata.normalize("NFKC", s).casefold().replace("ё", "е")
    return " ".join("".join(" " if unicodedata.category(c)[0] in {"P", "S"} else c for c in s).split())

def jaccard(a, b):
    left, right = set(norm(a).split()), set(norm(b).split())
    return len(left & right) / len(left | right)

class T250(unittest.TestCase):
    def test_registration_scope_and_provenance(self):
        raw = (ROOT / REL).read_bytes()
        data = json.loads(raw)
        manifest = json.loads((ROOT / "manifest.json").read_text("utf-8"))
        matches = [p for p in manifest["packs"] if p["path"] == REL]
        self.assertEqual(len(matches), 1)
        self.assertEqual(hashlib.sha256(raw).hexdigest(), matches[0]["sha256"])
        self.assertEqual(validate_qa_pack(data), 24)
        self.assertEqual(data["pack_version"], "2026.11.06.042")
        self.assertEqual(data["catalog"]["audiences"], ["all_ai_bots"])
        self.assertEqual(data["catalog"]["constraints"],
                         {"read_only": True, "requires_direct_address": True,
                          "no_personal_data": True})

    def test_72_accepted_and_nonrepeating(self):
        data = json.loads((ROOT / REL).read_text("utf-8"))
        ids, canonical, texts = set(), set(), set()
        extras = 0
        for row in data["records"]:
            self.assertNotIn(row["id"], ids)
            ids.add(row["id"])
            self.assertNotIn(norm(row["question"]), canonical)
            canonical.add(norm(row["question"]))
            self.assertEqual(row["contexts"], ["direct", "private", "group_addressed"])
            answers = [row["answer"], *row["variants"]]
            self.assertEqual(len(answers), 9)
            for answer in answers:
                self.assertNotIn(norm(answer), texts)
                texts.add(norm(answer))
                self.assertIsNone(re.search(
                    r"(?i)(ghp_[a-z0-9]{12,}|sk-[a-z0-9]{12,}|bot_token|chat_id|user_id|bearer\\s+|https://t\\.me/)",
                    answer))
            for answer in answers[6:]:
                extras += 1
                self.assertTrue(all(jaccard(answer, old) < 0.78 for old in answers[:6]))
        self.assertEqual((len(ids), len(canonical), len(texts), extras), (24,24,216,72))

if __name__ == "__main__":
    unittest.main()
