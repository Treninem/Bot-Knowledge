"""T453: opt-in, SHA-pinned, read-only access to T448–T451 for trusted callers."""
import hashlib
import json
import unittest
from scripts.colloquial_t305 import ROOT
from scripts.staged_context_selector import StagedContextSelector

PINNED = {
    448: "6758fc811a5b41b9df277ae97f50f72e90b4497b",
    449: "8e775230ed9b21628119e73cfc0ca0964c478c98",
    450: "ffb24b69dce46c3459ed31c0f394d4e6fd2914ff",
    451: "1fe127da7259b2389812c76097047d9155e0f19f",
}
PARENTS = {448: (446, "fc0fddb01819ce0315d2d8175a99f99a32073e03"),
           449: (448, PINNED[448]),
           450: (449, PINNED[449]),
           451: (450, PINNED[450])}
SOURCE = "packs/ru/conversation_followthrough_qa.json"
SOURCE_SHA = "0862daf244df650bfd85217df3bedb9f2373a6e63dbabfa8d0c831a6fb289ff7"


def git_blob(data: bytes) -> str:
    return hashlib.sha1(b"blob " + str(len(data)).encode() + bytes([0]) + data).hexdigest()


class T453StageOptInTests(unittest.TestCase):
    def test_integrity_82_ids_and_explicit_approval(self):
        source = json.loads((ROOT / SOURCE).read_bytes())
        canon = {r["id"]: r["question"] for r in source["records"]}
        self.assertEqual(len(canon), 82)
        self.assertEqual(hashlib.sha256((ROOT / SOURCE).read_bytes()).hexdigest(), SOURCE_SHA)
        manifest = json.loads((ROOT / "manifest.json").read_bytes())
        self.assertEqual({r["path"]: r["sha256"] for r in manifest["packs"]}[SOURCE], SOURCE_SHA)

        all_ids = set()
        for n, expected_blob in PINNED.items():
            path = f"staging/ru/followthrough_t{n}_context_pool.json"
            raw = (ROOT / path).read_bytes()
            self.assertEqual(git_blob(raw), expected_blob)
            data = json.loads(raw)
            parent_n, parent_blob = PARENTS[n]
            self.assertEqual(data["previous_stage"], f"staging/ru/followthrough_t{parent_n}_context_pool.json")
            self.assertEqual(data["previous_stage_blob_sha"], parent_blob)
            self.assertFalse(data["consumer_registered"])
            self.assertEqual(data["constraints"], {"read_only": True, "requires_direct_address": True, "no_personal_data": True})
            self.assertEqual(len(data["entries"]), 82)
            self.assertEqual({r["intent_id"] for r in data["entries"]}, set(canon))
            selector = StagedContextSelector(ROOT, path)
            for row in data["entries"]:
                self.assertEqual(row["question"], canon[row["intent_id"]])
                reply = row["replies"][0]
                self.assertNotIn(reply["id"], all_ids)
                all_ids.add(reply["id"])
                kwargs = {"approved_reply_ids": frozenset({reply["id"]}), "audience": "all_ai_bots",
                          "context": reply["context"], "addressed": True, "local_permission": True}
                result = selector.select(row["intent_id"], **kwargs)
                self.assertIsNotNone(result)
                self.assertEqual((result.id, result.stage_path, result.context_note),
                                 (reply["id"], path, reply["context_note"]))
                for deny in ({"approved_reply_ids": frozenset()}, {"approved_reply_ids": frozenset({"not_approved"})},
                             {"addressed": False}, {"local_permission": False},
                             {"audience": "chat_moderators"}, {"recent_ids": (reply["id"],)},
                             {"context": next(c for c in ("direct", "private", "group_addressed")
                                              if c != reply["context"])}):
                    self.assertIsNone(selector.select(row["intent_id"], **{**kwargs, **deny}))
        self.assertEqual(len(all_ids), 328)

    def test_unreviewed_future_stage_fail_closed(self):
        with self.assertRaises(ValueError):
            StagedContextSelector(ROOT, "staging/ru/followthrough_t452_context_pool.json")


if __name__ == "__main__":
    unittest.main()
