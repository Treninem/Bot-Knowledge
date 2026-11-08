"""T443 reviewed explicit opt-in selector for stages T439–T442."""
import hashlib
import json
import unittest
from scripts.colloquial_t305 import ROOT
from scripts.staged_context_selector import StagedContextSelector

PINNED = {
    439: "cdc8260a60315a77fe47820716f51b1ea9dfb674",
    440: "56356ecdbe9b0d9eb5c83f699c5e178827f55a10",
    441: "49ead3c0961aa8ab82a75f4d8a0077041742d209",
    442: "6fc3f9721b51da3cd0317fab601181df0f7d871b",
}

def blob(raw):
    return hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()

class T443CatalogTests(unittest.TestCase):
    def test_all_82_intents_per_stage_require_explicit_verified_approval(self):
        for n, expected in PINNED.items():
            path = f"staging/ru/followthrough_t{n}_context_pool.json"
            raw = (ROOT / path).read_bytes()
            self.assertEqual(blob(raw), expected)
            data = json.loads(raw)
            self.assertFalse(data["consumer_registered"])
            self.assertEqual(len(data["entries"]), 82)
            selector = StagedContextSelector(ROOT, path)
            for entry in data["entries"]:
                reply = entry["replies"][0]
                kwargs = {
                    "approved_reply_ids": frozenset({reply["id"]}),
                    "audience": "all_ai_bots",
                    "context": reply["context"],
                    "addressed": True,
                    "local_permission": True,
                }
                result = selector.select(entry["intent_id"], **kwargs)
                self.assertIsNotNone(result)
                self.assertEqual((result.id, result.stage_path), (reply["id"], path))
                self.assertEqual(result.context_note, reply["context_note"])
                for reject in (
                    {"approved_reply_ids": frozenset()},
                    {"approved_reply_ids": frozenset({"unapproved"})},
                    {"addressed": False},
                    {"local_permission": False},
                    {"audience": "chat_moderators"},
                    {"context": next(c for c in ("direct", "private", "group_addressed") if c != reply["context"])},
                    {"recent_ids": (reply["id"],)},
                ):
                    self.assertIsNone(selector.select(entry["intent_id"], **{**kwargs, **reject}))

    def test_unknown_stage_is_fail_closed(self):
        with self.assertRaises(ValueError):
            StagedContextSelector(ROOT, "staging/ru/followthrough_t443_context_pool.json")

if __name__ == "__main__":
    unittest.main()
