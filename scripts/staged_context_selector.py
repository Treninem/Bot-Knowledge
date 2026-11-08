"""Opt-in, fail-closed read-only selector for reviewed *staged* contextual replies.

This module DOES NOT register packs or infer a situation from chat text. A trusted
consumer must first independently verify an explicit reply ID's context_note and
pass that ID as approved; raw user text or quoted instructions do not confer
permission. No network, writes, local memory, moderation or sanctions.
"""
from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
import re
import unicodedata

_ALLOWED = frozenset({
    "staging/ru/choice_t166_context_pool.json",
    "staging/ru/recovery_t168_context_pool.json",
    "staging/ru/boundaries_t167_context_pool.json",
    "staging/ru/spoken_pragmatics_t251_context_pool.json",
    "staging/ru/followthrough_t383_context_pool.json",
    "staging/ru/followthrough_t384_context_pool.json",
    "staging/ru/followthrough_t385_context_pool.json",
    "staging/ru/followthrough_t386_context_pool.json",
    "staging/ru/followthrough_t387_context_pool.json",
    "staging/ru/followthrough_t388_context_pool.json",
    "staging/ru/followthrough_t389_context_pool.json",
    "staging/ru/followthrough_t390_context_pool.json",
    "staging/ru/followthrough_t391_context_pool.json",
    "staging/ru/followthrough_t392_context_pool.json",
    "staging/ru/followthrough_t393_context_pool.json",
    "staging/ru/followthrough_t394_context_pool.json",
    "staging/ru/followthrough_t395_context_pool.json",
    "staging/ru/followthrough_t396_context_pool.json",
    "staging/ru/followthrough_t397_context_pool.json",
    "staging/ru/followthrough_t398_context_pool.json",
    "staging/ru/followthrough_t399_context_pool.json",
    "staging/ru/followthrough_t400_context_pool.json",
    "staging/ru/followthrough_t401_context_pool.json",
    "staging/ru/followthrough_t402_context_pool.json",
    "staging/ru/followthrough_t403_context_pool.json",
    "staging/ru/followthrough_t404_context_pool.json",
    "staging/ru/followthrough_t405_context_pool.json",
    "staging/ru/followthrough_t406_context_pool.json",
    "staging/ru/followthrough_t407_context_pool.json",
    "staging/ru/followthrough_t408_context_pool.json",
    "staging/ru/followthrough_t409_context_pool.json",
    "staging/ru/followthrough_t410_context_pool.json",
    "staging/ru/followthrough_t411_context_pool.json",
    "staging/ru/followthrough_t412_context_pool.json",
    "staging/ru/followthrough_t413_context_pool.json",
    "staging/ru/followthrough_t414_context_pool.json",
    "staging/ru/followthrough_t415_context_pool.json",
    "staging/ru/followthrough_t416_context_pool.json",
    "staging/ru/followthrough_t417_context_pool.json",
    "staging/ru/followthrough_t418_context_pool.json",
    "staging/ru/followthrough_t419_context_pool.json",
    "staging/ru/followthrough_t420_context_pool.json",
    "staging/ru/followthrough_t421_context_pool.json",
    "staging/ru/followthrough_t422_context_pool.json",
    "staging/ru/followthrough_t424_context_pool.json",
    "staging/ru/followthrough_t425_context_pool.json",
    "staging/ru/followthrough_t427_context_pool.json",
    "staging/ru/followthrough_t428_context_pool.json",
    "staging/ru/followthrough_t429_context_pool.json",
    "staging/ru/followthrough_t430_context_pool.json",
    "staging/ru/followthrough_t431_context_pool.json",
    "staging/ru/followthrough_t432_context_pool.json",
    "staging/ru/followthrough_t433_context_pool.json",
    "staging/ru/followthrough_t434_context_pool.json",
    "staging/ru/followthrough_t436_context_pool.json",
    "staging/ru/followthrough_t438_context_pool.json",
    "staging/ru/followthrough_t439_context_pool.json",
    "staging/ru/followthrough_t440_context_pool.json",
    "staging/ru/followthrough_t441_context_pool.json",
    "staging/ru/followthrough_t442_context_pool.json",
    "staging/ru/followthrough_t444_context_pool.json",
    "staging/ru/followthrough_t445_context_pool.json",
    "staging/ru/followthrough_t446_context_pool.json",
})
_PINNED_STAGE_BLOBS = {
    "staging/ru/followthrough_t383_context_pool.json": "6aa6b98c0a3fdb5a68ebcc0071d6c80f0967f5f3",
    "staging/ru/followthrough_t384_context_pool.json": "86dd0b4d5c7fbd298eacf82c8d2b5df6ff6013e5",
    "staging/ru/followthrough_t385_context_pool.json": "2484f31c20df35b0af67bc41d6579164da6686e5",
    "staging/ru/followthrough_t386_context_pool.json": "ebee173a7fd4003f832bbdca87cfd10da9ee3e82",
    "staging/ru/followthrough_t387_context_pool.json": "b1eb2222893e832ad8b9324d03a4615a8491e7b9",
    "staging/ru/followthrough_t388_context_pool.json": "68cd3474b7cafcec27c7627135d11e16330f9ab2",
    "staging/ru/followthrough_t389_context_pool.json": "dddfc5a9612fdd889c3acf92ad6e8c1bba3d1d50",
    "staging/ru/followthrough_t390_context_pool.json": "41bc57dbcc429f2bfeaa68ef28ca77450748f963",
    "staging/ru/followthrough_t391_context_pool.json": "66157082f9e60937f513f3e6bf9c5b6c1e0f99c5",
    "staging/ru/followthrough_t392_context_pool.json": "e3de3c687c3ee0a4122d92f78da82d69f5467bd1",
    "staging/ru/followthrough_t393_context_pool.json": "2cf87aa1622684d40e50f3cfc8be837c0efdc62f",
    "staging/ru/followthrough_t394_context_pool.json": "70610ea757b26e45779adb6b26a2b74307529eef",
    "staging/ru/followthrough_t395_context_pool.json": "d5c7907dcc64e4e2e7dd68941e616d841f897c91",
    "staging/ru/followthrough_t396_context_pool.json": "83d5d1f66d23989d2a0a42396194feb487daac4b",
    "staging/ru/followthrough_t397_context_pool.json": "1b15fc9a7bd48857d054a6c6634aa74597ad0567",
    "staging/ru/followthrough_t398_context_pool.json": "3997b6db7b36f7f27a693cf442ce84f6b4bab829",
    "staging/ru/followthrough_t399_context_pool.json": "dd51f07e16a5c2fa42291ecbb1f582f74d8545b2",
    "staging/ru/followthrough_t400_context_pool.json": "9c72702ef5c3c94d9f782f3ecdfc363bb2c422c5",
    "staging/ru/followthrough_t401_context_pool.json": "aefd9dcab4f3caf2db550752399bc612603ab938",
    "staging/ru/followthrough_t402_context_pool.json": "92bf99add2d6f08be09821014d870bd9301d6a77",
    "staging/ru/followthrough_t403_context_pool.json": "a9c28f3c598113f3c9dce298343f3fef8eeabe6e",
    "staging/ru/followthrough_t404_context_pool.json": "3476971b3e4147d4860872a58dba51d391edf039",
    "staging/ru/followthrough_t405_context_pool.json": "64dff05e9ac337f0cf2640e3325c8623b0591664",
    "staging/ru/followthrough_t406_context_pool.json": "577b8b899886b77fcfc20bb6e388de75f55ccc98",
    "staging/ru/followthrough_t407_context_pool.json": "4cd8bb75083984f948212999572e515f55ab31ac",
    "staging/ru/followthrough_t408_context_pool.json": "d270253f07299d773afbb591ed0fb88477712eba",
    "staging/ru/followthrough_t409_context_pool.json": "0384f8ea5277b2ce46a6d38e101528a92c905ae4",
    "staging/ru/followthrough_t410_context_pool.json": "95dfa757cc0cde14a88aa7aa6752baf1fb96397a",
    "staging/ru/followthrough_t411_context_pool.json": "836deea92279a4d03971c4b490e69c50deef2c71",
    "staging/ru/followthrough_t412_context_pool.json": "01e3db997548b2e3f96353a7c03e1cd3a4ce9f18",
    "staging/ru/followthrough_t413_context_pool.json": "ad933c69cf89fe9ccf243d2ee1f15c937d0ff71d",
    "staging/ru/followthrough_t414_context_pool.json": "c395fcea2e50156cf42e6c73f3569036430ebc7f",
    "staging/ru/followthrough_t415_context_pool.json": "7629632977cc01a319fed8934365a2c6aff5e28e",
    "staging/ru/followthrough_t416_context_pool.json": "f040d11225642a5c25adad50d5cc79f56526b0b1",
    "staging/ru/followthrough_t417_context_pool.json": "dd6102212e9be4e467b79825f5e9fb77a618e5ac",
    "staging/ru/followthrough_t418_context_pool.json": "a00acfec24d24702f32f03be245b72dd6a4be4ce",
    "staging/ru/followthrough_t419_context_pool.json": "eb3b6e5567b05e1e92d427b80b23106edec511a3",
    "staging/ru/followthrough_t420_context_pool.json": "c3964d60d48a4d5e83375bde7043062728bf0e8a",
    "staging/ru/followthrough_t421_context_pool.json": "4ca59f3c7538ac78e0103436d9f6d8dcb681b63a",
    "staging/ru/followthrough_t422_context_pool.json": "29fe137e2c2a396ba8b42238dc4788033cea3c1e",
    "staging/ru/followthrough_t424_context_pool.json": "955808243204e9e348e77f3f7d73072eefa2ae2d",
    "staging/ru/followthrough_t425_context_pool.json": "e89334c1ffcca0fb87d11a0400c7106e3393d67b",
    "staging/ru/followthrough_t427_context_pool.json": "4bad4fa90347dbd8123f49be0e732f88a5e096f3",
    "staging/ru/followthrough_t428_context_pool.json": "9947f434ebf95511d0f9ce00466a420aad0fd743",
    "staging/ru/followthrough_t429_context_pool.json": "cf0ad83036e0fafea4fa1a0d7c207bf0183e7528",
    "staging/ru/followthrough_t430_context_pool.json": "6004d03017463aee1545021cc2bcde5a6bfa48e8",
    "staging/ru/followthrough_t431_context_pool.json": "0b259f09db1d58004c48d6b298c573197e3ad191",
    "staging/ru/followthrough_t432_context_pool.json": "c462fe31b7c69432d46efbacc6df768d61cbfac4",
    "staging/ru/followthrough_t433_context_pool.json": "e2ec084c9f2259fcb71a572dfbf812b72042f0a0",
    "staging/ru/followthrough_t434_context_pool.json": "0c6d96d7ee06bd7a166e0e0535fce35bd937cfdb",
    "staging/ru/followthrough_t436_context_pool.json": "915d487e6234f1288f66f925136832812dd9fb2d",
    "staging/ru/followthrough_t438_context_pool.json": "5e6f4966d3ada0e5a727321cdb92c2d2ee8667fe",
    "staging/ru/followthrough_t439_context_pool.json": "cdc8260a60315a77fe47820716f51b1ea9dfb674",
    "staging/ru/followthrough_t440_context_pool.json": "56356ecdbe9b0d9eb5c83f699c5e178827f55a10",
    "staging/ru/followthrough_t441_context_pool.json": "49ead3c0961aa8ab82a75f4d8a0077041742d209",
    "staging/ru/followthrough_t442_context_pool.json": "6fc3f9721b51da3cd0317fab601181df0f7d871b",
    "staging/ru/followthrough_t444_context_pool.json": "e95a22fe46906bf0c8122aa7302a99ae4268bfcb",
    "staging/ru/followthrough_t445_context_pool.json": "446c78aa6b1f31dcd456acfe078df50e2310839e",
    "staging/ru/followthrough_t446_context_pool.json": "fc0fddb01819ce0315d2d8175a99f99a32073e03",
}

_CONTEXTS = frozenset({"direct", "private", "group_addressed"})
_GUARDS = {"read_only": True, "requires_direct_address": True, "no_personal_data": True}
_SECRET = re.compile(r"(?i)(ghp_[a-z0-9]{12,}|sk-[a-z0-9]{12,}|bot_token|chat_id|user_id|https://t\.me/|[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,})")


def _norm(value: str) -> str:
    value = unicodedata.normalize("NFKC", value).casefold().replace("ё", "е")
    return " ".join(
        "".join(" " if unicodedata.category(ch)[0] in {"P", "S"} else ch
                for ch in value).split()
    )


@dataclass(frozen=True)
class StagedSelection:
    id: str
    text: str
    intent_id: str
    context_note: str
    stage_path: str
    # The result is proposed language, not authority or a moderation command.


class StagedContextSelector:
    """Load an explicitly allowlisted stage; never silently attach it to a bot."""

    def __init__(self, repository_root: Path, stage_path: str):
        if stage_path not in _ALLOWED:
            raise ValueError("unsupported or untrusted staged path")
        root = Path(repository_root).resolve(strict=True)
        self.stage_path = stage_path
        manifest = json.loads((root / "manifest.json").read_text("utf-8"))
        packs = {entry["path"]: entry["sha256"] for entry in manifest["packs"]}
        raw = (root / stage_path).read_bytes()
        pinned = _PINNED_STAGE_BLOBS.get(stage_path)
        if pinned is not None:
            actual_blob = hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()
            if actual_blob != pinned:
                raise ValueError("Unreviewed staged content changed")
        stage = json.loads(raw)
        if stage_path == "staging/ru/followthrough_t384_context_pool.json":
            parent_path = "staging/ru/followthrough_t383_context_pool.json"
            parent_raw = (root / parent_path).read_bytes()
            parent_blob = hashlib.sha1(
                b"blob " + str(len(parent_raw)).encode() + b"\0" + parent_raw
            ).hexdigest()
            if (stage.get("previous_stage") != parent_path
                    or parent_blob != stage.get("previous_stage_blob_sha")
                    or parent_blob != _PINNED_STAGE_BLOBS[parent_path]):
                raise ValueError("unverified T383 stage ancestry")
            parent = json.loads(parent_raw)
            parent_entries = {row["intent_id"]: row for row in parent.get("entries", [])}
            child_entries = stage.get("entries", [])
            if (len(parent_entries) != 82 or not isinstance(child_entries, list)
                    or len(child_entries) != 82
                    or set(parent_entries) != {row.get("intent_id") for row in child_entries}
                    or parent.get("source_pack") != stage.get("source_pack")
                    or parent.get("consumer_registered") is not False
                    or stage.get("cumulative_checkpoint") != {
                        "baseline_registered": 246, "previous_staged": 82,
                        "added_candidates": 82, "total": 410,
                        "partial_intents": 82, "finished_100": 0,
                        "remaining_total": 7790,
                    }):
                raise ValueError("invalid T384 cumulative inventory")
            historical = set()
            for row in parent_entries.values():
                for item in row["replies"]:
                    historical.add(_norm(item["text"]))
            for row in child_entries:
                parent_row = parent_entries[row["intent_id"]]
                if row.get("question") != parent_row.get("question"):
                    raise ValueError("changed intent question across stages")
                for item in row.get("replies", []):
                    if _norm(item.get("text", "")) in historical:
                        raise ValueError("cross-stage duplicate")
        if stage_path == "staging/ru/followthrough_t385_context_pool.json":
            parent_path = "staging/ru/followthrough_t384_context_pool.json"
            ancestor_path = "staging/ru/followthrough_t383_context_pool.json"
            parent_raw = (root / parent_path).read_bytes()
            ancestor_raw = (root / ancestor_path).read_bytes()
            def git_blob(raw: bytes) -> str:
                return hashlib.sha1(
                    b"blob " + str(len(raw)).encode() + b"\0" + raw
                ).hexdigest()
            parent_blob = git_blob(parent_raw)
            ancestor_blob = git_blob(ancestor_raw)
            if (parent_blob != _PINNED_STAGE_BLOBS[parent_path]
                    or ancestor_blob != _PINNED_STAGE_BLOBS[ancestor_path]
                    or stage.get("previous_stage") != parent_path
                    or stage.get("previous_stage_blob_sha") != parent_blob):
                raise ValueError("unverified T385 parent SHA")
            parent = json.loads(parent_raw)
            ancestor = json.loads(ancestor_raw)
            if (parent.get("previous_stage") != ancestor_path
                    or parent.get("previous_stage_blob_sha") != ancestor_blob
                    or parent.get("source_pack") != stage.get("source_pack")
                    or ancestor.get("source_pack") != stage.get("source_pack")
                    or parent.get("consumer_registered") is not False
                    or ancestor.get("consumer_registered") is not False):
                raise ValueError("unverified T385 ancestry")
            parent_entries = {r["intent_id"]: r for r in parent.get("entries", [])}
            ancestor_entries = {r["intent_id"]: r for r in ancestor.get("entries", [])}
            children = stage.get("entries", [])
            if (len(parent_entries) != 82 or len(ancestor_entries) != 82
                    or not isinstance(children, list) or len(children) != 82
                    or set(parent_entries) != set(ancestor_entries)
                    or set(parent_entries) != {r.get("intent_id") for r in children}
                    or stage.get("cumulative_checkpoint") != {
                        "baseline_registered": 246, "previous_staged": 164,
                        "added_candidates": 164, "total": 574,
                        "partial_intents": 82, "finished_100": 0,
                        "remaining_total": 7626,
                    }):
                raise ValueError("invalid T385 cumulative checkpoint")
            historical = {
                _norm(reply["text"])
                for history in (parent_entries, ancestor_entries)
                for row in history.values()
                for reply in row["replies"]
            }
            for row in children:
                if (row.get("question") != parent_entries[row["intent_id"]]["question"]
                        or row.get("question") != ancestor_entries[row["intent_id"]]["question"]):
                    raise ValueError("modified canonical question")
                if any(_norm(reply["text"]) in historical
                       for reply in row.get("replies", [])):
                    raise ValueError("T385 cross-stage duplicate")
        if stage_path == "staging/ru/followthrough_t386_context_pool.json":
            parent_path = "staging/ru/followthrough_t385_context_pool.json"
            grandparent_path = "staging/ru/followthrough_t384_context_pool.json"
            ancestor_path = "staging/ru/followthrough_t383_context_pool.json"
            def blob_id(path: str) -> str:
                raw = (root / path).read_bytes()
                return hashlib.sha1(
                    b"blob " + str(len(raw)).encode() + b"\0" + raw
                ).hexdigest()
            for checked in (parent_path, grandparent_path, ancestor_path):
                if blob_id(checked) != _PINNED_STAGE_BLOBS[checked]:
                    raise ValueError("T386 source history changed")
            parent = json.loads((root / parent_path).read_bytes())
            grandparent = json.loads((root / grandparent_path).read_bytes())
            ancestor = json.loads((root / ancestor_path).read_bytes())
            if (stage.get("previous_stage") != parent_path
                    or stage.get("previous_stage_blob_sha") != _PINNED_STAGE_BLOBS[parent_path]
                    or parent.get("previous_stage") != grandparent_path
                    or parent.get("previous_stage_blob_sha") != _PINNED_STAGE_BLOBS[grandparent_path]
                    or grandparent.get("previous_stage") != ancestor_path
                    or grandparent.get("previous_stage_blob_sha") != _PINNED_STAGE_BLOBS[ancestor_path]
                    or len(stage.get("entries", [])) != 82
                    or stage.get("cumulative_checkpoint") != {
                        "baseline_registered": 246, "previous_staged": 328,
                        "added_candidates": 82, "total": 656,
                        "partial_intents": 82, "finished_100": 0,
                        "remaining_total": 7544,
                    }):
                raise ValueError("T386 ancestry or cumulative checkpoint mismatch")
            histories = (ancestor, grandparent, parent)
            old = {}
            old_texts = set()
            for historical in histories:
                if (historical.get("source_pack") != stage.get("source_pack")
                        or historical.get("consumer_registered") is not False
                        or len(historical.get("entries", [])) != 82):
                    raise ValueError("unverified T386 history")
                for row in historical["entries"]:
                    ident = row["intent_id"]
                    if ident in old and old[ident] != row["question"]:
                        raise ValueError("mutated canonical question")
                    old[ident] = row["question"]
                    old_texts.update(_norm(reply["text"]) for reply in row["replies"])
            if len(old) != 82 or set(old) != {x.get("intent_id") for x in stage["entries"]}:
                raise ValueError("changed historical intent set")
            for row in stage["entries"]:
                if row.get("question") != old[row["intent_id"]]:
                    raise ValueError("changed T386 canonical question")
                if any(_norm(reply.get("text", "")) in old_texts
                       for reply in row.get("replies", [])):
                    raise ValueError("repeated previous stage text")

        if stage_path == "staging/ru/followthrough_t387_context_pool.json":
            history_paths = tuple(
                f"staging/ru/followthrough_t{n}_context_pool.json"
                for n in (383, 384, 385, 386)
            )
            histories = []
            old_questions, old_texts, old_ids = {}, set(), set()
            for position, path in enumerate(history_paths):
                raw_history = (root / path).read_bytes()
                actual = hashlib.sha1(
                    b"blob " + str(len(raw_history)).encode() + b"\0" + raw_history
                ).hexdigest()
                if actual != _PINNED_STAGE_BLOBS[path]:
                    raise ValueError("unverified T387 ancestor bytes")
                previous = json.loads(raw_history)
                if (previous.get("source_pack") != stage.get("source_pack")
                        or previous.get("consumer_registered") is not False
                        or len(previous.get("entries", [])) != 82):
                    raise ValueError("invalid T387 ancestor inventory")
                if position:
                    if (previous.get("previous_stage") != history_paths[position - 1]
                            or previous.get("previous_stage_blob_sha")
                            != _PINNED_STAGE_BLOBS[history_paths[position - 1]]):
                        raise ValueError("broken T387 ancestry")
                histories.append(previous)
                for row in previous["entries"]:
                    ident = row["intent_id"]
                    if ident in old_questions and old_questions[ident] != row["question"]:
                        raise ValueError("changed T387 canonical question")
                    old_questions[ident] = row["question"]
                    for reply in row["replies"]:
                        if reply["id"] in old_ids or _norm(reply["text"]) in old_texts:
                            raise ValueError("duplicate in T387 ancestors")
                        old_ids.add(reply["id"])
                        old_texts.add(_norm(reply["text"]))
            if (stage.get("previous_stage") != history_paths[-1]
                    or stage.get("previous_stage_blob_sha")
                    != _PINNED_STAGE_BLOBS[history_paths[-1]]
                    or len(old_questions) != 82
                    or not isinstance(stage.get("entries"), list)
                    or len(stage["entries"]) != 82
                    or set(old_questions) != {row.get("intent_id") for row in stage["entries"]}
                    or stage.get("cumulative_checkpoint") != {
                        "baseline_registered": 246, "previous_staged": 410,
                        "added_candidates": 82, "total": 738,
                        "partial_intents": 82, "finished_100": 0,
                        "remaining_total": 7462,
                    }):
                raise ValueError("wrong T387 ancestry or count")
            for row in stage["entries"]:
                if row.get("question") != old_questions[row["intent_id"]]:
                    raise ValueError("changed question in T387")
                if any(item.get("id") in old_ids
                       or _norm(item.get("text", "")) in old_texts
                       for item in row.get("replies", [])):
                    raise ValueError("repeated answer in T387")


        if stage_path == "staging/ru/followthrough_t388_context_pool.json":
            history_paths = tuple(
                f"staging/ru/followthrough_t{n}_context_pool.json"
                for n in (383, 384, 385, 386, 387)
            )
            old_questions, old_texts, old_ids = {}, set(), set()
            for position, path in enumerate(history_paths):
                raw_history = (root / path).read_bytes()
                actual_blob = hashlib.sha1(
                    b"blob " + str(len(raw_history)).encode() + b"\0" + raw_history
                ).hexdigest()
                if actual_blob != _PINNED_STAGE_BLOBS[path]:
                    raise ValueError("unverified T388 ancestor bytes")
                ancestor = json.loads(raw_history)
                if (ancestor.get("source_pack") != stage.get("source_pack")
                        or ancestor.get("consumer_registered") is not False
                        or not isinstance(ancestor.get("entries"), list)
                        or len(ancestor["entries"]) != 82):
                    raise ValueError("invalid T388 ancestor inventory")
                if position and (
                    ancestor.get("previous_stage") != history_paths[position - 1]
                    or ancestor.get("previous_stage_blob_sha")
                    != _PINNED_STAGE_BLOBS[history_paths[position - 1]]
                ):
                    raise ValueError("broken T388 ancestor chain")
                for row in ancestor["entries"]:
                    ident = row["intent_id"]
                    if ident in old_questions and old_questions[ident] != row["question"]:
                        raise ValueError("changed T388 canonical question")
                    old_questions[ident] = row["question"]
                    for reply in row["replies"]:
                        normal = _norm(reply["text"])
                        if reply["id"] in old_ids or not normal or normal in old_texts:
                            raise ValueError("duplicate among T388 ancestors")
                        old_ids.add(reply["id"])
                        old_texts.add(normal)
            child_rows = stage.get("entries")
            if (stage.get("previous_stage") != history_paths[-1]
                    or stage.get("previous_stage_blob_sha")
                    != _PINNED_STAGE_BLOBS[history_paths[-1]]
                    or len(old_questions) != 82
                    or not isinstance(child_rows, list)
                    or len(child_rows) != 82
                    or {row.get("intent_id") for row in child_rows}
                    != set(old_questions)
                    or stage.get("cumulative_checkpoint") != {
                        "baseline_registered": 246, "previous_staged": 492,
                        "added_candidates": 82, "total": 820,
                        "partial_intents": 82, "finished_100": 0,
                        "remaining_total": 7380,
                    }):
                raise ValueError("wrong T388 ancestry or cumulative count")
            for row in child_rows:
                if row.get("question") != old_questions[row["intent_id"]]:
                    raise ValueError("changed question in T388")
                if any(item.get("id") in old_ids
                       or _norm(item.get("text", "")) in old_texts
                       for item in row.get("replies", [])):
                    raise ValueError("repeated answer in T388")

        if stage_path == "staging/ru/followthrough_t389_context_pool.json":
            history_paths = tuple(
                f"staging/ru/followthrough_t{n}_context_pool.json"
                for n in (383, 384, 385, 386, 387, 388)
            )
            old_questions, old_texts, old_ids = {}, set(), set()
            for position, path in enumerate(history_paths):
                raw_history = (root / path).read_bytes()
                actual_blob = hashlib.sha1(
                    b"blob " + str(len(raw_history)).encode() + b"\0" + raw_history
                ).hexdigest()
                if actual_blob != _PINNED_STAGE_BLOBS[path]:
                    raise ValueError("unverified T389 ancestor bytes")
                ancestor = json.loads(raw_history)
                if (ancestor.get("source_pack") != stage.get("source_pack")
                        or ancestor.get("consumer_registered") is not False
                        or not isinstance(ancestor.get("entries"), list)
                        or len(ancestor["entries"]) != 82):
                    raise ValueError("invalid T389 ancestor inventory")
                if position and (
                    ancestor.get("previous_stage") != history_paths[position - 1]
                    or ancestor.get("previous_stage_blob_sha")
                    != _PINNED_STAGE_BLOBS[history_paths[position - 1]]
                ):
                    raise ValueError("broken T389 ancestor chain")
                for row in ancestor["entries"]:
                    ident = row["intent_id"]
                    if ident in old_questions and old_questions[ident] != row["question"]:
                        raise ValueError("changed T389 canonical question")
                    old_questions[ident] = row["question"]
                    for reply in row["replies"]:
                        normal = _norm(reply["text"])
                        if reply["id"] in old_ids or not normal or normal in old_texts:
                            raise ValueError("duplicate among T389 ancestors")
                        old_ids.add(reply["id"])
                        old_texts.add(normal)
            child_rows = stage.get("entries")
            if (stage.get("previous_stage") != history_paths[-1]
                    or stage.get("previous_stage_blob_sha")
                    != _PINNED_STAGE_BLOBS[history_paths[-1]]
                    or len(old_questions) != 82
                    or not isinstance(child_rows, list)
                    or len(child_rows) != 82
                    or {row.get("intent_id") for row in child_rows}
                    != set(old_questions)
                    or stage.get("cumulative_checkpoint") != {
                        "baseline_registered": 246, "previous_staged": 574,
                        "added_candidates": 82, "total": 902,
                        "partial_intents": 82, "finished_100": 0,
                        "remaining_total": 7298,
                    }):
                raise ValueError("wrong T389 ancestry or cumulative count")
            for row in child_rows:
                if row.get("question") != old_questions[row["intent_id"]]:
                    raise ValueError("changed question in T389")
                if any(item.get("id") in old_ids
                       or _norm(item.get("text", "")) in old_texts
                       for item in row.get("replies", [])):
                    raise ValueError("repeated answer in T389")

        if stage_path == "staging/ru/followthrough_t390_context_pool.json":
            history_paths = tuple(
                f"staging/ru/followthrough_t{n}_context_pool.json"
                for n in (383, 384, 385, 386, 387, 388, 389)
            )
            old_questions, old_texts, old_ids = {}, set(), set()
            for position, path in enumerate(history_paths):
                raw_history = (root / path).read_bytes()
                actual_blob = hashlib.sha1(
                    b"blob " + str(len(raw_history)).encode() + b"\0" + raw_history
                ).hexdigest()
                if actual_blob != _PINNED_STAGE_BLOBS[path]:
                    raise ValueError("unverified T390 ancestor bytes")
                ancestor = json.loads(raw_history)
                if (ancestor.get("source_pack") != stage.get("source_pack")
                        or ancestor.get("consumer_registered") is not False
                        or not isinstance(ancestor.get("entries"), list)
                        or len(ancestor["entries"]) != 82):
                    raise ValueError("invalid T390 ancestor inventory")
                if position and (
                    ancestor.get("previous_stage") != history_paths[position - 1]
                    or ancestor.get("previous_stage_blob_sha")
                    != _PINNED_STAGE_BLOBS[history_paths[position - 1]]
                ):
                    raise ValueError("broken T390 ancestor chain")
                for row in ancestor["entries"]:
                    ident = row["intent_id"]
                    if ident in old_questions and old_questions[ident] != row["question"]:
                        raise ValueError("changed T390 canonical question")
                    old_questions[ident] = row["question"]
                    for reply in row["replies"]:
                        normal = _norm(reply["text"])
                        if reply["id"] in old_ids or not normal or normal in old_texts:
                            raise ValueError("duplicate among T390 ancestors")
                        old_ids.add(reply["id"])
                        old_texts.add(normal)
            child_rows = stage.get("entries")
            if (stage.get("previous_stage") != history_paths[-1]
                    or stage.get("previous_stage_blob_sha")
                    != _PINNED_STAGE_BLOBS[history_paths[-1]]
                    or len(old_questions) != 82
                    or not isinstance(child_rows, list)
                    or len(child_rows) != 82
                    or {row.get("intent_id") for row in child_rows}
                    != set(old_questions)
                    or stage.get("cumulative_checkpoint") != {
                        "baseline_registered": 246, "previous_staged": 656,
                        "added_candidates": 82, "total": 984,
                        "partial_intents": 82, "finished_100": 0,
                        "remaining_total": 7216,
                    }):
                raise ValueError("wrong T390 ancestry or cumulative count")
            for row in child_rows:
                if row.get("question") != old_questions[row["intent_id"]]:
                    raise ValueError("changed question in T390")
                if any(item.get("id") in old_ids
                       or _norm(item.get("text", "")) in old_texts
                       for item in row.get("replies", [])):
                    raise ValueError("repeated answer in T390")

        if stage_path == "staging/ru/followthrough_t391_context_pool.json":
            history_paths = tuple(
                f"staging/ru/followthrough_t{n}_context_pool.json"
                for n in (383, 384, 385, 386, 387, 388, 389, 390)
            )
            old_questions, old_texts, old_ids = {}, set(), set()
            for position, path in enumerate(history_paths):
                raw_history = (root / path).read_bytes()
                actual_blob = hashlib.sha1(
                    b"blob " + str(len(raw_history)).encode() + b"\0" + raw_history
                ).hexdigest()
                if actual_blob != _PINNED_STAGE_BLOBS[path]:
                    raise ValueError("unverified T391 ancestor bytes")
                ancestor = json.loads(raw_history)
                if (ancestor.get("source_pack") != stage.get("source_pack")
                        or ancestor.get("consumer_registered") is not False
                        or not isinstance(ancestor.get("entries"), list)
                        or len(ancestor["entries"]) != 82):
                    raise ValueError("invalid T391 ancestor inventory")
                if position and (
                    ancestor.get("previous_stage") != history_paths[position - 1]
                    or ancestor.get("previous_stage_blob_sha")
                    != _PINNED_STAGE_BLOBS[history_paths[position - 1]]
                ):
                    raise ValueError("broken T391 ancestor chain")
                for row in ancestor["entries"]:
                    ident = row["intent_id"]
                    if ident in old_questions and old_questions[ident] != row["question"]:
                        raise ValueError("changed T391 canonical question")
                    old_questions[ident] = row["question"]
                    for reply in row["replies"]:
                        normal = _norm(reply["text"])
                        if reply["id"] in old_ids or not normal or normal in old_texts:
                            raise ValueError("duplicate among T391 ancestors")
                        old_ids.add(reply["id"])
                        old_texts.add(normal)
            child_rows = stage.get("entries")
            if (stage.get("previous_stage") != history_paths[-1]
                    or stage.get("previous_stage_blob_sha")
                    != _PINNED_STAGE_BLOBS[history_paths[-1]]
                    or len(old_questions) != 82
                    or not isinstance(child_rows, list)
                    or len(child_rows) != 82
                    or {row.get("intent_id") for row in child_rows}
                    != set(old_questions)
                    or stage.get("cumulative_checkpoint") != {
                        "baseline_registered": 246, "previous_staged": 738,
                        "added_candidates": 82, "total": 1066,
                        "partial_intents": 82, "finished_100": 0,
                        "remaining_total": 7134,
                    }):
                raise ValueError("wrong T391 ancestry or cumulative count")
            for row in child_rows:
                if row.get("question") != old_questions[row["intent_id"]]:
                    raise ValueError("changed question in T391")
                if any(item.get("id") in old_ids
                       or _norm(item.get("text", "")) in old_texts
                       for item in row.get("replies", [])):
                    raise ValueError("repeated answer in T391")

        if stage_path == "staging/ru/followthrough_t392_context_pool.json":
            history_paths = tuple(
                f"staging/ru/followthrough_t{n}_context_pool.json"
                for n in (383, 384, 385, 386, 387, 388, 389, 390, 391)
            )
            old_questions, old_texts, old_ids = {}, set(), set()
            for position, path in enumerate(history_paths):
                raw_history = (root / path).read_bytes()
                actual_blob = hashlib.sha1(
                    b"blob " + str(len(raw_history)).encode() + b"\0" + raw_history
                ).hexdigest()
                if actual_blob != _PINNED_STAGE_BLOBS[path]:
                    raise ValueError("unverified T392 ancestor bytes")
                ancestor = json.loads(raw_history)
                if (ancestor.get("source_pack") != stage.get("source_pack")
                        or ancestor.get("consumer_registered") is not False
                        or not isinstance(ancestor.get("entries"), list)
                        or len(ancestor["entries"]) != 82):
                    raise ValueError("invalid T392 ancestor inventory")
                if position and (
                    ancestor.get("previous_stage") != history_paths[position - 1]
                    or ancestor.get("previous_stage_blob_sha")
                    != _PINNED_STAGE_BLOBS[history_paths[position - 1]]
                ):
                    raise ValueError("broken T392 ancestor chain")
                for row in ancestor["entries"]:
                    ident = row["intent_id"]
                    if ident in old_questions and old_questions[ident] != row["question"]:
                        raise ValueError("changed T392 canonical question")
                    old_questions[ident] = row["question"]
                    for reply in row["replies"]:
                        normal = _norm(reply["text"])
                        if reply["id"] in old_ids or not normal or normal in old_texts:
                            raise ValueError("duplicate among T392 ancestors")
                        old_ids.add(reply["id"])
                        old_texts.add(normal)
            child_rows = stage.get("entries")
            if (stage.get("previous_stage") != history_paths[-1]
                    or stage.get("previous_stage_blob_sha")
                    != _PINNED_STAGE_BLOBS[history_paths[-1]]
                    or len(old_questions) != 82
                    or not isinstance(child_rows, list)
                    or len(child_rows) != 82
                    or {row.get("intent_id") for row in child_rows}
                    != set(old_questions)
                    or stage.get("cumulative_checkpoint") != {
                        "baseline_registered": 246, "previous_staged": 820,
                        "added_candidates": 82, "total": 1148,
                        "partial_intents": 82, "finished_100": 0,
                        "remaining_total": 7052,
                    }):
                raise ValueError("wrong T392 ancestry or cumulative count")
            for row in child_rows:
                if row.get("question") != old_questions[row["intent_id"]]:
                    raise ValueError("changed question in T392")
                if any(item.get("id") in old_ids
                       or _norm(item.get("text", "")) in old_texts
                       for item in row.get("replies", [])):
                    raise ValueError("repeated answer in T392")

        if stage_path == "staging/ru/followthrough_t393_context_pool.json":
            history_paths = tuple(
                f"staging/ru/followthrough_t{n}_context_pool.json"
                for n in (383, 384, 385, 386, 387, 388, 389, 390, 391, 392)
            )
            old_questions, old_texts, old_ids = {}, set(), set()
            for position, path in enumerate(history_paths):
                raw_history = (root / path).read_bytes()
                actual_blob = hashlib.sha1(
                    b"blob " + str(len(raw_history)).encode() + b"\0" + raw_history
                ).hexdigest()
                if actual_blob != _PINNED_STAGE_BLOBS[path]:
                    raise ValueError("unverified T393 ancestor bytes")
                ancestor = json.loads(raw_history)
                if (ancestor.get("source_pack") != stage.get("source_pack")
                        or ancestor.get("consumer_registered") is not False
                        or not isinstance(ancestor.get("entries"), list)
                        or len(ancestor["entries"]) != 82):
                    raise ValueError("invalid T393 ancestor inventory")
                if position and (
                    ancestor.get("previous_stage") != history_paths[position - 1]
                    or ancestor.get("previous_stage_blob_sha")
                    != _PINNED_STAGE_BLOBS[history_paths[position - 1]]
                ):
                    raise ValueError("broken T393 ancestor chain")
                for row in ancestor["entries"]:
                    ident = row["intent_id"]
                    if ident in old_questions and old_questions[ident] != row["question"]:
                        raise ValueError("changed T393 canonical question")
                    old_questions[ident] = row["question"]
                    for reply in row["replies"]:
                        normal = _norm(reply["text"])
                        if reply["id"] in old_ids or not normal or normal in old_texts:
                            raise ValueError("duplicate among T393 ancestors")
                        old_ids.add(reply["id"])
                        old_texts.add(normal)
            child_rows = stage.get("entries")
            if (stage.get("previous_stage") != history_paths[-1]
                    or stage.get("previous_stage_blob_sha")
                    != _PINNED_STAGE_BLOBS[history_paths[-1]]
                    or len(old_questions) != 82
                    or not isinstance(child_rows, list)
                    or len(child_rows) != 82
                    or {row.get("intent_id") for row in child_rows}
                    != set(old_questions)
                    or stage.get("cumulative_checkpoint") != {
                        "baseline_registered": 246, "previous_staged": 902,
                        "added_candidates": 82, "total": 1230,
                        "partial_intents": 82, "finished_100": 0,
                        "remaining_total": 6970,
                    }):
                raise ValueError("wrong T393 ancestry or cumulative count")
            for row in child_rows:
                if row.get("question") != old_questions[row["intent_id"]]:
                    raise ValueError("changed question in T393")
                if any(item.get("id") in old_ids
                       or _norm(item.get("text", "")) in old_texts
                       for item in row.get("replies", [])):
                    raise ValueError("repeated answer in T393")

        if stage_path == "staging/ru/followthrough_t394_context_pool.json":
            history_paths = tuple(
                f"staging/ru/followthrough_t{n}_context_pool.json"
                for n in (383, 384, 385, 386, 387, 388, 389, 390, 391, 392, 393)
            )
            old_questions, old_texts, old_ids = {}, set(), set()
            for position, path in enumerate(history_paths):
                raw_history = (root / path).read_bytes()
                actual_blob = hashlib.sha1(
                    b"blob " + str(len(raw_history)).encode() + b"\0" + raw_history
                ).hexdigest()
                if actual_blob != _PINNED_STAGE_BLOBS[path]:
                    raise ValueError("unverified T394 ancestor bytes")
                ancestor = json.loads(raw_history)
                if (ancestor.get("source_pack") != stage.get("source_pack")
                        or ancestor.get("consumer_registered") is not False
                        or not isinstance(ancestor.get("entries"), list)
                        or len(ancestor["entries"]) != 82):
                    raise ValueError("invalid T394 ancestor inventory")
                if position and (
                    ancestor.get("previous_stage") != history_paths[position - 1]
                    or ancestor.get("previous_stage_blob_sha")
                    != _PINNED_STAGE_BLOBS[history_paths[position - 1]]
                ):
                    raise ValueError("broken T394 ancestor chain")
                for row in ancestor["entries"]:
                    ident = row["intent_id"]
                    if ident in old_questions and old_questions[ident] != row["question"]:
                        raise ValueError("changed T394 canonical question")
                    old_questions[ident] = row["question"]
                    for reply in row["replies"]:
                        normal = _norm(reply["text"])
                        if reply["id"] in old_ids or not normal or normal in old_texts:
                            raise ValueError("duplicate among T394 ancestors")
                        old_ids.add(reply["id"])
                        old_texts.add(normal)
            child_rows = stage.get("entries")
            if (stage.get("previous_stage") != history_paths[-1]
                    or stage.get("previous_stage_blob_sha")
                    != _PINNED_STAGE_BLOBS[history_paths[-1]]
                    or len(old_questions) != 82
                    or not isinstance(child_rows, list)
                    or len(child_rows) != 82
                    or {row.get("intent_id") for row in child_rows}
                    != set(old_questions)
                    or stage.get("cumulative_checkpoint") != {
                        "baseline_registered": 246, "previous_staged": 984,
                        "added_candidates": 82, "total": 1312,
                        "partial_intents": 82, "finished_100": 0,
                        "remaining_total": 6888,
                    }):
                raise ValueError("wrong T394 ancestry or cumulative count")
            for row in child_rows:
                if row.get("question") != old_questions[row["intent_id"]]:
                    raise ValueError("changed question in T394")
                if any(item.get("id") in old_ids
                       or _norm(item.get("text", "")) in old_texts
                       for item in row.get("replies", [])):
                    raise ValueError("repeated answer in T394")

        if stage_path == "staging/ru/followthrough_t395_context_pool.json":
            history_paths = tuple(
                f"staging/ru/followthrough_t{n}_context_pool.json"
                for n in (383, 384, 385, 386, 387, 388, 389, 390, 391, 392, 393, 394)
            )
            old_questions, old_texts, old_ids = {}, set(), set()
            for position, path in enumerate(history_paths):
                raw_history = (root / path).read_bytes()
                actual_blob = hashlib.sha1(
                    b"blob " + str(len(raw_history)).encode() + b"\0" + raw_history
                ).hexdigest()
                if actual_blob != _PINNED_STAGE_BLOBS[path]:
                    raise ValueError("unverified T395 ancestor bytes")
                ancestor = json.loads(raw_history)
                if (ancestor.get("source_pack") != stage.get("source_pack")
                        or ancestor.get("consumer_registered") is not False
                        or not isinstance(ancestor.get("entries"), list)
                        or len(ancestor["entries"]) != 82):
                    raise ValueError("invalid T395 ancestor inventory")
                if position and (
                    ancestor.get("previous_stage") != history_paths[position - 1]
                    or ancestor.get("previous_stage_blob_sha")
                    != _PINNED_STAGE_BLOBS[history_paths[position - 1]]
                ):
                    raise ValueError("broken T395 ancestor chain")
                for row in ancestor["entries"]:
                    ident = row["intent_id"]
                    if ident in old_questions and old_questions[ident] != row["question"]:
                        raise ValueError("changed T395 canonical question")
                    old_questions[ident] = row["question"]
                    for reply in row["replies"]:
                        normal = _norm(reply["text"])
                        if reply["id"] in old_ids or not normal or normal in old_texts:
                            raise ValueError("duplicate among T395 ancestors")
                        old_ids.add(reply["id"])
                        old_texts.add(normal)
            child_rows = stage.get("entries")
            if (stage.get("previous_stage") != history_paths[-1]
                    or stage.get("previous_stage_blob_sha")
                    != _PINNED_STAGE_BLOBS[history_paths[-1]]
                    or len(old_questions) != 82
                    or not isinstance(child_rows, list)
                    or len(child_rows) != 82
                    or {row.get("intent_id") for row in child_rows}
                    != set(old_questions)
                    or stage.get("cumulative_checkpoint") != {
                        "baseline_registered": 246, "previous_staged": 1066,
                        "added_candidates": 82, "total": 1394,
                        "partial_intents": 82, "finished_100": 0,
                        "remaining_total": 6806,
                    }):
                raise ValueError("wrong T395 ancestry or cumulative count")
            for row in child_rows:
                if row.get("question") != old_questions[row["intent_id"]]:
                    raise ValueError("changed question in T395")
                if any(item.get("id") in old_ids
                       or _norm(item.get("text", "")) in old_texts
                       for item in row.get("replies", [])):
                    raise ValueError("repeated answer in T395")

        if stage_path == "staging/ru/followthrough_t396_context_pool.json":
            history_paths = tuple(
                f"staging/ru/followthrough_t{n}_context_pool.json"
                for n in (383, 384, 385, 386, 387, 388, 389, 390, 391, 392, 393, 394, 395)
            )
            old_questions, old_texts, old_ids = {}, set(), set()
            for position, path in enumerate(history_paths):
                raw_history = (root / path).read_bytes()
                actual_blob = hashlib.sha1(
                    b"blob " + str(len(raw_history)).encode() + b"\0" + raw_history
                ).hexdigest()
                if actual_blob != _PINNED_STAGE_BLOBS[path]:
                    raise ValueError("unverified T396 ancestor bytes")
                ancestor = json.loads(raw_history)
                if (ancestor.get("source_pack") != stage.get("source_pack")
                        or ancestor.get("consumer_registered") is not False
                        or not isinstance(ancestor.get("entries"), list)
                        or len(ancestor["entries"]) != 82):
                    raise ValueError("invalid T396 ancestor inventory")
                if position and (
                    ancestor.get("previous_stage") != history_paths[position - 1]
                    or ancestor.get("previous_stage_blob_sha")
                    != _PINNED_STAGE_BLOBS[history_paths[position - 1]]
                ):
                    raise ValueError("broken T396 ancestor chain")
                for row in ancestor["entries"]:
                    ident = row["intent_id"]
                    if ident in old_questions and old_questions[ident] != row["question"]:
                        raise ValueError("changed T396 canonical question")
                    old_questions[ident] = row["question"]
                    for reply in row["replies"]:
                        normal = _norm(reply["text"])
                        if reply["id"] in old_ids or not normal or normal in old_texts:
                            raise ValueError("duplicate among T396 ancestors")
                        old_ids.add(reply["id"])
                        old_texts.add(normal)
            child_rows = stage.get("entries")
            if (stage.get("previous_stage") != history_paths[-1]
                    or stage.get("previous_stage_blob_sha")
                    != _PINNED_STAGE_BLOBS[history_paths[-1]]
                    or len(old_questions) != 82
                    or not isinstance(child_rows, list)
                    or len(child_rows) != 82
                    or {row.get("intent_id") for row in child_rows}
                    != set(old_questions)
                    or stage.get("cumulative_checkpoint") != {
                        "baseline_registered": 246, "previous_staged": 1148,
                        "added_candidates": 82, "total": 1476,
                        "partial_intents": 82, "finished_100": 0,
                        "remaining_total": 6724,
                    }):
                raise ValueError("wrong T396 ancestry or cumulative count")
            for row in child_rows:
                if row.get("question") != old_questions[row["intent_id"]]:
                    raise ValueError("changed question in T396")
                if any(item.get("id") in old_ids
                       or _norm(item.get("text", "")) in old_texts
                       for item in row.get("replies", [])):
                    raise ValueError("repeated answer in T396")

        if stage_path == "staging/ru/followthrough_t397_context_pool.json":
            history_paths = tuple(
                f"staging/ru/followthrough_t{n}_context_pool.json"
                for n in (383, 384, 385, 386, 387, 388, 389, 390, 391, 392, 393, 394, 395, 396)
            )
            old_questions, old_texts, old_ids = {}, set(), set()
            for position, path in enumerate(history_paths):
                raw_history = (root / path).read_bytes()
                actual_blob = hashlib.sha1(
                    b"blob " + str(len(raw_history)).encode() + b"\0" + raw_history
                ).hexdigest()
                if actual_blob != _PINNED_STAGE_BLOBS[path]:
                    raise ValueError("unverified T397 ancestor bytes")
                ancestor = json.loads(raw_history)
                if (ancestor.get("source_pack") != stage.get("source_pack")
                        or ancestor.get("consumer_registered") is not False
                        or not isinstance(ancestor.get("entries"), list)
                        or len(ancestor["entries"]) != 82):
                    raise ValueError("invalid T397 ancestor inventory")
                if position and (
                    ancestor.get("previous_stage") != history_paths[position - 1]
                    or ancestor.get("previous_stage_blob_sha")
                    != _PINNED_STAGE_BLOBS[history_paths[position - 1]]
                ):
                    raise ValueError("broken T397 ancestor chain")
                for row in ancestor["entries"]:
                    ident = row["intent_id"]
                    if ident in old_questions and old_questions[ident] != row["question"]:
                        raise ValueError("changed T397 canonical question")
                    old_questions[ident] = row["question"]
                    for reply in row["replies"]:
                        normal = _norm(reply["text"])
                        if reply["id"] in old_ids or not normal or normal in old_texts:
                            raise ValueError("duplicate among T397 ancestors")
                        old_ids.add(reply["id"])
                        old_texts.add(normal)
            child_rows = stage.get("entries")
            if (stage.get("previous_stage") != history_paths[-1]
                    or stage.get("previous_stage_blob_sha")
                    != _PINNED_STAGE_BLOBS[history_paths[-1]]
                    or len(old_questions) != 82
                    or not isinstance(child_rows, list)
                    or len(child_rows) != 82
                    or {row.get("intent_id") for row in child_rows}
                    != set(old_questions)
                    or stage.get("cumulative_checkpoint") != {
                        "baseline_registered": 246, "previous_staged": 1230,
                        "added_candidates": 82, "total": 1558,
                        "partial_intents": 82, "finished_100": 0,
                        "remaining_total": 6642,
                    }):
                raise ValueError("wrong T397 ancestry or cumulative count")
            for row in child_rows:
                if row.get("question") != old_questions[row["intent_id"]]:
                    raise ValueError("changed question in T397")
                if any(item.get("id") in old_ids
                       or _norm(item.get("text", "")) in old_texts
                       for item in row.get("replies", [])):
                    raise ValueError("repeated answer in T397")

        if stage_path == "staging/ru/followthrough_t398_context_pool.json":
            history_paths = tuple(
                f"staging/ru/followthrough_t{n}_context_pool.json"
                for n in (383, 384, 385, 386, 387, 388, 389, 390, 391, 392, 393, 394, 395, 396, 397)
            )
            old_questions, old_texts, old_ids = {}, set(), set()
            for position, path in enumerate(history_paths):
                raw_history = (root / path).read_bytes()
                actual_blob = hashlib.sha1(
                    b"blob " + str(len(raw_history)).encode() + b"\0" + raw_history
                ).hexdigest()
                if actual_blob != _PINNED_STAGE_BLOBS[path]:
                    raise ValueError("unverified T398 ancestor bytes")
                ancestor = json.loads(raw_history)
                if (ancestor.get("source_pack") != stage.get("source_pack")
                        or ancestor.get("consumer_registered") is not False
                        or not isinstance(ancestor.get("entries"), list)
                        or len(ancestor["entries"]) != 82):
                    raise ValueError("invalid T398 ancestor inventory")
                if position and (
                    ancestor.get("previous_stage") != history_paths[position - 1]
                    or ancestor.get("previous_stage_blob_sha")
                    != _PINNED_STAGE_BLOBS[history_paths[position - 1]]
                ):
                    raise ValueError("broken T398 ancestor chain")
                for row in ancestor["entries"]:
                    ident = row["intent_id"]
                    if ident in old_questions and old_questions[ident] != row["question"]:
                        raise ValueError("changed T398 canonical question")
                    old_questions[ident] = row["question"]
                    for reply in row["replies"]:
                        normal = _norm(reply["text"])
                        if reply["id"] in old_ids or not normal or normal in old_texts:
                            raise ValueError("duplicate among T398 ancestors")
                        old_ids.add(reply["id"])
                        old_texts.add(normal)
            child_rows = stage.get("entries")
            if (stage.get("previous_stage") != history_paths[-1]
                    or stage.get("previous_stage_blob_sha")
                    != _PINNED_STAGE_BLOBS[history_paths[-1]]
                    or len(old_questions) != 82
                    or not isinstance(child_rows, list)
                    or len(child_rows) != 82
                    or {row.get("intent_id") for row in child_rows}
                    != set(old_questions)
                    or stage.get("cumulative_checkpoint") != {
                        "baseline_registered": 246, "previous_staged": 1312,
                        "added_candidates": 82, "total": 1640,
                        "partial_intents": 82, "finished_100": 0,
                        "remaining_total": 6560,
                    }):
                raise ValueError("wrong T398 ancestry or cumulative count")
            for row in child_rows:
                if row.get("question") != old_questions[row["intent_id"]]:
                    raise ValueError("changed question in T398")
                if any(item.get("id") in old_ids
                       or _norm(item.get("text", "")) in old_texts
                       for item in row.get("replies", [])):
                    raise ValueError("repeated answer in T398")

        if stage_path == "staging/ru/followthrough_t399_context_pool.json":
            history_paths = tuple(
                f"staging/ru/followthrough_t{n}_context_pool.json"
                for n in (383, 384, 385, 386, 387, 388, 389, 390, 391, 392, 393, 394, 395, 396, 397, 398)
            )
            old_questions, old_texts, old_ids = {}, set(), set()
            for position, path in enumerate(history_paths):
                raw_history = (root / path).read_bytes()
                actual_blob = hashlib.sha1(
                    b"blob " + str(len(raw_history)).encode() + b"\0" + raw_history
                ).hexdigest()
                if actual_blob != _PINNED_STAGE_BLOBS[path]:
                    raise ValueError("unverified T399 ancestor bytes")
                ancestor = json.loads(raw_history)
                if (ancestor.get("source_pack") != stage.get("source_pack")
                        or ancestor.get("consumer_registered") is not False
                        or not isinstance(ancestor.get("entries"), list)
                        or len(ancestor["entries"]) != 82):
                    raise ValueError("invalid T399 ancestor inventory")
                if position and (
                    ancestor.get("previous_stage") != history_paths[position - 1]
                    or ancestor.get("previous_stage_blob_sha")
                    != _PINNED_STAGE_BLOBS[history_paths[position - 1]]
                ):
                    raise ValueError("broken T399 ancestor chain")
                for row in ancestor["entries"]:
                    ident = row["intent_id"]
                    if ident in old_questions and old_questions[ident] != row["question"]:
                        raise ValueError("changed T399 canonical question")
                    old_questions[ident] = row["question"]
                    for reply in row["replies"]:
                        normal = _norm(reply["text"])
                        if reply["id"] in old_ids or not normal or normal in old_texts:
                            raise ValueError("duplicate among T399 ancestors")
                        old_ids.add(reply["id"])
                        old_texts.add(normal)
            child_rows = stage.get("entries")
            if (stage.get("previous_stage") != history_paths[-1]
                    or stage.get("previous_stage_blob_sha")
                    != _PINNED_STAGE_BLOBS[history_paths[-1]]
                    or len(old_questions) != 82
                    or not isinstance(child_rows, list)
                    or len(child_rows) != 82
                    or {row.get("intent_id") for row in child_rows}
                    != set(old_questions)
                    or stage.get("cumulative_checkpoint") != {
                        "baseline_registered": 246, "previous_staged": 1394,
                        "added_candidates": 82, "total": 1722,
                        "partial_intents": 82, "finished_100": 0,
                        "remaining_total": 6478,
                    }):
                raise ValueError("wrong T399 ancestry or cumulative count")
            for row in child_rows:
                if row.get("question") != old_questions[row["intent_id"]]:
                    raise ValueError("changed question in T399")
                if any(item.get("id") in old_ids
                       or _norm(item.get("text", "")) in old_texts
                       for item in row.get("replies", [])):
                    raise ValueError("repeated answer in T399")

        if stage_path == "staging/ru/followthrough_t400_context_pool.json":
            # Historical SHA provenance and cumulative inventory are independently
            # checked before any language from this unregistered stage can be selected.
            history_paths = tuple(
                f"staging/ru/followthrough_t{n}_context_pool.json"
                for n in range(383, 400)
            )
            old_questions, old_texts, old_ids = {}, set(), set()
            for position, path in enumerate(history_paths):
                raw_history = (root / path).read_bytes()
                actual_blob = hashlib.sha1(
                    b"blob " + str(len(raw_history)).encode() + b"\0" + raw_history
                ).hexdigest()
                if actual_blob != _PINNED_STAGE_BLOBS[path]:
                    raise ValueError("unverified T400 ancestor bytes")
                ancestor = json.loads(raw_history)
                if (ancestor.get("source_pack") != stage.get("source_pack")
                        or ancestor.get("consumer_registered") is not False
                        or not isinstance(ancestor.get("entries"), list)
                        or len(ancestor["entries"]) != 82):
                    raise ValueError("invalid T400 ancestor inventory")
                if position and (
                    ancestor.get("previous_stage") != history_paths[position - 1]
                    or ancestor.get("previous_stage_blob_sha")
                    != _PINNED_STAGE_BLOBS[history_paths[position - 1]]
                ):
                    raise ValueError("broken T400 ancestor chain")
                for row in ancestor["entries"]:
                    ident = row["intent_id"]
                    if ident in old_questions and old_questions[ident] != row["question"]:
                        raise ValueError("changed T400 canonical question")
                    old_questions[ident] = row["question"]
                    for reply in row["replies"]:
                        normal = _norm(reply["text"])
                        if reply["id"] in old_ids or not normal or normal in old_texts:
                            raise ValueError("duplicate among T400 ancestors")
                        old_ids.add(reply["id"])
                        old_texts.add(normal)
            child_rows = stage.get("entries")
            if (stage.get("previous_stage") != history_paths[-1]
                    or stage.get("previous_stage_blob_sha")
                    != _PINNED_STAGE_BLOBS[history_paths[-1]]
                    or len(old_questions) != 82
                    or not isinstance(child_rows, list)
                    or len(child_rows) != 82
                    or {row.get("intent_id") for row in child_rows}
                    != set(old_questions)
                    or stage.get("cumulative_checkpoint") != {
                        "baseline_registered": 246, "previous_staged": 1476,
                        "added_candidates": 82, "total": 1804,
                        "partial_intents": 82, "finished_100": 0,
                        "remaining_total": 6396,
                    }):
                raise ValueError("wrong T400 ancestry or cumulative count")
            for row in child_rows:
                if row.get("question") != old_questions[row["intent_id"]]:
                    raise ValueError("changed question in T400")
                if any(item.get("id") in old_ids
                       or _norm(item.get("text", "")) in old_texts
                       for item in row.get("replies", [])):
                    raise ValueError("repeated answer in T400")

        if stage_path == "staging/ru/followthrough_t401_context_pool.json":
            # Historical SHA provenance and cumulative inventory are independently
            # checked before any language from this unregistered stage can be selected.
            history_paths = tuple(
                f"staging/ru/followthrough_t{n}_context_pool.json"
                for n in range(383, 401)
            )
            old_questions, old_texts, old_ids = {}, set(), set()
            for position, path in enumerate(history_paths):
                raw_history = (root / path).read_bytes()
                actual_blob = hashlib.sha1(
                    b"blob " + str(len(raw_history)).encode() + b"\0" + raw_history
                ).hexdigest()
                if actual_blob != _PINNED_STAGE_BLOBS[path]:
                    raise ValueError("unverified T401 ancestor bytes")
                ancestor = json.loads(raw_history)
                if (ancestor.get("source_pack") != stage.get("source_pack")
                        or ancestor.get("consumer_registered") is not False
                        or not isinstance(ancestor.get("entries"), list)
                        or len(ancestor["entries"]) != 82):
                    raise ValueError("invalid T401 ancestor inventory")
                if position and (
                    ancestor.get("previous_stage") != history_paths[position - 1]
                    or ancestor.get("previous_stage_blob_sha")
                    != _PINNED_STAGE_BLOBS[history_paths[position - 1]]
                ):
                    raise ValueError("broken T401 ancestor chain")
                for row in ancestor["entries"]:
                    ident = row["intent_id"]
                    if ident in old_questions and old_questions[ident] != row["question"]:
                        raise ValueError("changed T401 canonical question")
                    old_questions[ident] = row["question"]
                    for reply in row["replies"]:
                        normal = _norm(reply["text"])
                        if reply["id"] in old_ids or not normal or normal in old_texts:
                            raise ValueError("duplicate among T401 ancestors")
                        old_ids.add(reply["id"])
                        old_texts.add(normal)
            child_rows = stage.get("entries")
            if (stage.get("previous_stage") != history_paths[-1]
                    or stage.get("previous_stage_blob_sha")
                    != _PINNED_STAGE_BLOBS[history_paths[-1]]
                    or len(old_questions) != 82
                    or not isinstance(child_rows, list)
                    or len(child_rows) != 82
                    or {row.get("intent_id") for row in child_rows}
                    != set(old_questions)
                    or stage.get("cumulative_checkpoint") != {
                        "baseline_registered": 246, "previous_staged": 1558,
                        "added_candidates": 82, "total": 1886,
                        "partial_intents": 82, "finished_100": 0,
                        "remaining_total": 6314,
                    }):
                raise ValueError("wrong T401 ancestry or cumulative count")
            for row in child_rows:
                if row.get("question") != old_questions[row["intent_id"]]:
                    raise ValueError("changed question in T401")
                if any(item.get("id") in old_ids
                       or _norm(item.get("text", "")) in old_texts
                       for item in row.get("replies", [])):
                    raise ValueError("repeated answer in T401")

        if stage_path == "staging/ru/followthrough_t402_context_pool.json":
            # Historical SHA provenance and cumulative inventory are independently
            # checked before any language from this unregistered stage can be selected.
            history_paths = tuple(
                f"staging/ru/followthrough_t{n}_context_pool.json"
                for n in range(383, 402)
            )
            old_questions, old_texts, old_ids = {}, set(), set()
            for position, path in enumerate(history_paths):
                raw_history = (root / path).read_bytes()
                actual_blob = hashlib.sha1(
                    b"blob " + str(len(raw_history)).encode() + b"\0" + raw_history
                ).hexdigest()
                if actual_blob != _PINNED_STAGE_BLOBS[path]:
                    raise ValueError("unverified T402 ancestor bytes")
                ancestor = json.loads(raw_history)
                if (ancestor.get("source_pack") != stage.get("source_pack")
                        or ancestor.get("consumer_registered") is not False
                        or not isinstance(ancestor.get("entries"), list)
                        or len(ancestor["entries"]) != 82):
                    raise ValueError("invalid T402 ancestor inventory")
                if position and (
                    ancestor.get("previous_stage") != history_paths[position - 1]
                    or ancestor.get("previous_stage_blob_sha")
                    != _PINNED_STAGE_BLOBS[history_paths[position - 1]]
                ):
                    raise ValueError("broken T402 ancestor chain")
                for row in ancestor["entries"]:
                    ident = row["intent_id"]
                    if ident in old_questions and old_questions[ident] != row["question"]:
                        raise ValueError("changed T402 canonical question")
                    old_questions[ident] = row["question"]
                    for reply in row["replies"]:
                        normal = _norm(reply["text"])
                        if reply["id"] in old_ids or not normal or normal in old_texts:
                            raise ValueError("duplicate among T402 ancestors")
                        old_ids.add(reply["id"])
                        old_texts.add(normal)
            child_rows = stage.get("entries")
            if (stage.get("previous_stage") != history_paths[-1]
                    or stage.get("previous_stage_blob_sha")
                    != _PINNED_STAGE_BLOBS[history_paths[-1]]
                    or len(old_questions) != 82
                    or not isinstance(child_rows, list)
                    or len(child_rows) != 82
                    or {row.get("intent_id") for row in child_rows}
                    != set(old_questions)
                    or stage.get("cumulative_checkpoint") != {
                        "baseline_registered": 246, "previous_staged": 1640,
                        "added_candidates": 82, "total": 1968,
                        "partial_intents": 82, "finished_100": 0,
                        "remaining_total": 6232,
                    }):
                raise ValueError("wrong T402 ancestry or cumulative count")
            for row in child_rows:
                if row.get("question") != old_questions[row["intent_id"]]:
                    raise ValueError("changed question in T402")
                if any(item.get("id") in old_ids
                       or _norm(item.get("text", "")) in old_texts
                       for item in row.get("replies", [])):
                    raise ValueError("repeated answer in T402")

        if stage_path == "staging/ru/followthrough_t403_context_pool.json":
            # Historical SHA provenance and cumulative inventory are independently
            # checked before any language from this unregistered stage can be selected.
            history_paths = tuple(
                f"staging/ru/followthrough_t{n}_context_pool.json"
                for n in range(383, 403)
            )
            old_questions, old_texts, old_ids = {}, set(), set()
            for position, path in enumerate(history_paths):
                raw_history = (root / path).read_bytes()
                actual_blob = hashlib.sha1(
                    b"blob " + str(len(raw_history)).encode() + b"\0" + raw_history
                ).hexdigest()
                if actual_blob != _PINNED_STAGE_BLOBS[path]:
                    raise ValueError("unverified T403 ancestor bytes")
                ancestor = json.loads(raw_history)
                if (ancestor.get("source_pack") != stage.get("source_pack")
                        or ancestor.get("consumer_registered") is not False
                        or not isinstance(ancestor.get("entries"), list)
                        or len(ancestor["entries"]) != 82):
                    raise ValueError("invalid T403 ancestor inventory")
                if position and (
                    ancestor.get("previous_stage") != history_paths[position - 1]
                    or ancestor.get("previous_stage_blob_sha")
                    != _PINNED_STAGE_BLOBS[history_paths[position - 1]]
                ):
                    raise ValueError("broken T403 ancestor chain")
                for row in ancestor["entries"]:
                    ident = row["intent_id"]
                    if ident in old_questions and old_questions[ident] != row["question"]:
                        raise ValueError("changed T403 canonical question")
                    old_questions[ident] = row["question"]
                    for reply in row["replies"]:
                        normal = _norm(reply["text"])
                        if reply["id"] in old_ids or not normal or normal in old_texts:
                            raise ValueError("duplicate among T403 ancestors")
                        old_ids.add(reply["id"])
                        old_texts.add(normal)
            child_rows = stage.get("entries")
            if (stage.get("previous_stage") != history_paths[-1]
                    or stage.get("previous_stage_blob_sha")
                    != _PINNED_STAGE_BLOBS[history_paths[-1]]
                    or len(old_questions) != 82
                    or not isinstance(child_rows, list)
                    or len(child_rows) != 82
                    or {row.get("intent_id") for row in child_rows}
                    != set(old_questions)
                    or stage.get("cumulative_checkpoint") != {
                        "baseline_registered": 246, "previous_staged": 1722,
                        "added_candidates": 82, "total": 2050,
                        "partial_intents": 82, "finished_100": 0,
                        "remaining_total": 6150,
                    }):
                raise ValueError("wrong T403 ancestry or cumulative count")
            for row in child_rows:
                if row.get("question") != old_questions[row["intent_id"]]:
                    raise ValueError("changed question in T403")
                if any(item.get("id") in old_ids
                       or _norm(item.get("text", "")) in old_texts
                       for item in row.get("replies", [])):
                    raise ValueError("repeated answer in T403")

        if stage_path == "staging/ru/followthrough_t404_context_pool.json":
            # Historical SHA provenance and cumulative inventory are independently
            # checked before any language from this unregistered stage can be selected.
            history_paths = tuple(
                f"staging/ru/followthrough_t{n}_context_pool.json"
                for n in range(383, 404)
            )
            old_questions, old_texts, old_ids = {}, set(), set()
            for position, path in enumerate(history_paths):
                raw_history = (root / path).read_bytes()
                actual_blob = hashlib.sha1(
                    b"blob " + str(len(raw_history)).encode() + b"\0" + raw_history
                ).hexdigest()
                if actual_blob != _PINNED_STAGE_BLOBS[path]:
                    raise ValueError("unverified T404 ancestor bytes")
                ancestor = json.loads(raw_history)
                if (ancestor.get("source_pack") != stage.get("source_pack")
                        or ancestor.get("consumer_registered") is not False
                        or not isinstance(ancestor.get("entries"), list)
                        or len(ancestor["entries"]) != 82):
                    raise ValueError("invalid T404 ancestor inventory")
                if position and (
                    ancestor.get("previous_stage") != history_paths[position - 1]
                    or ancestor.get("previous_stage_blob_sha")
                    != _PINNED_STAGE_BLOBS[history_paths[position - 1]]
                ):
                    raise ValueError("broken T404 ancestor chain")
                for row in ancestor["entries"]:
                    ident = row["intent_id"]
                    if ident in old_questions and old_questions[ident] != row["question"]:
                        raise ValueError("changed T404 canonical question")
                    old_questions[ident] = row["question"]
                    for reply in row["replies"]:
                        normal = _norm(reply["text"])
                        if reply["id"] in old_ids or not normal or normal in old_texts:
                            raise ValueError("duplicate among T404 ancestors")
                        old_ids.add(reply["id"])
                        old_texts.add(normal)
            child_rows = stage.get("entries")
            if (stage.get("previous_stage") != history_paths[-1]
                    or stage.get("previous_stage_blob_sha")
                    != _PINNED_STAGE_BLOBS[history_paths[-1]]
                    or len(old_questions) != 82
                    or not isinstance(child_rows, list)
                    or len(child_rows) != 82
                    or {row.get("intent_id") for row in child_rows}
                    != set(old_questions)
                    or stage.get("cumulative_checkpoint") != {
                        "baseline_registered": 246, "previous_staged": 1804,
                        "added_candidates": 82, "total": 2132,
                        "partial_intents": 82, "finished_100": 0,
                        "remaining_total": 6068,
                    }):
                raise ValueError("wrong T404 ancestry or cumulative count")
            for row in child_rows:
                if row.get("question") != old_questions[row["intent_id"]]:
                    raise ValueError("changed question in T404")
                if any(item.get("id") in old_ids
                       or _norm(item.get("text", "")) in old_texts
                       for item in row.get("replies", [])):
                    raise ValueError("repeated answer in T404")

        if stage_path == "staging/ru/followthrough_t405_context_pool.json":
            # Historical SHA provenance and cumulative inventory are independently
            # checked before any language from this unregistered stage can be selected.
            history_paths = tuple(
                f"staging/ru/followthrough_t{n}_context_pool.json"
                for n in range(383, 405)
            )
            old_questions, old_texts, old_ids = {}, set(), set()
            for position, path in enumerate(history_paths):
                raw_history = (root / path).read_bytes()
                actual_blob = hashlib.sha1(
                    b"blob " + str(len(raw_history)).encode() + b"\0" + raw_history
                ).hexdigest()
                if actual_blob != _PINNED_STAGE_BLOBS[path]:
                    raise ValueError("unverified T405 ancestor bytes")
                ancestor = json.loads(raw_history)
                if (ancestor.get("source_pack") != stage.get("source_pack")
                        or ancestor.get("consumer_registered") is not False
                        or not isinstance(ancestor.get("entries"), list)
                        or len(ancestor["entries"]) != 82):
                    raise ValueError("invalid T405 ancestor inventory")
                if position and (
                    ancestor.get("previous_stage") != history_paths[position - 1]
                    or ancestor.get("previous_stage_blob_sha")
                    != _PINNED_STAGE_BLOBS[history_paths[position - 1]]
                ):
                    raise ValueError("broken T405 ancestor chain")
                for row in ancestor["entries"]:
                    ident = row["intent_id"]
                    if ident in old_questions and old_questions[ident] != row["question"]:
                        raise ValueError("changed T405 canonical question")
                    old_questions[ident] = row["question"]
                    for reply in row["replies"]:
                        normal = _norm(reply["text"])
                        if reply["id"] in old_ids or not normal or normal in old_texts:
                            raise ValueError("duplicate among T405 ancestors")
                        old_ids.add(reply["id"])
                        old_texts.add(normal)
            child_rows = stage.get("entries")
            if (stage.get("previous_stage") != history_paths[-1]
                    or stage.get("previous_stage_blob_sha")
                    != _PINNED_STAGE_BLOBS[history_paths[-1]]
                    or len(old_questions) != 82
                    or not isinstance(child_rows, list)
                    or len(child_rows) != 82
                    or {row.get("intent_id") for row in child_rows}
                    != set(old_questions)
                    or stage.get("cumulative_checkpoint") != {
                        "baseline_registered": 246, "previous_staged": 1886,
                        "added_candidates": 82, "total": 2214,
                        "partial_intents": 82, "finished_100": 0,
                        "remaining_total": 5986,
                    }):
                raise ValueError("wrong T405 ancestry or cumulative count")
            for row in child_rows:
                if row.get("question") != old_questions[row["intent_id"]]:
                    raise ValueError("changed question in T405")
                if any(item.get("id") in old_ids
                       or _norm(item.get("text", "")) in old_texts
                       for item in row.get("replies", [])):
                    raise ValueError("repeated answer in T405")

        if stage_path in {
            f"staging/ru/followthrough_t{n}_context_pool.json"
            for n in [*range(406, 423), 424, 425, *range(427, 435), 436, 438, 439, 440, 441, 442, 444, 445, 446]
        }:
            # T423, T426 and T435 were catalog-only PRs, not staged answer files.
            # Never guess missing sequence members or accept unpinned paths.
            number = int(stage_path.split("followthrough_t")[1].split("_")[0])
            reviewed_numbers = (*range(383, 423), 424, 425, *range(427, 435), 436, 438, 439, 440, 441, 442, 444, 445, 446)
            if number not in reviewed_numbers:
                raise ValueError("unreviewed followthrough stage")
            chain = [
                f"staging/ru/followthrough_t{n}_context_pool.json"
                for n in reviewed_numbers[:reviewed_numbers.index(number)]
            ]
            past_questions, past_ids, past_texts = {}, set(), set()
            count_prior = 0
            for pos, path in enumerate(chain):
                data = (root / path).read_bytes()
                git_sha = hashlib.sha1(
                    b"blob " + str(len(data)).encode() + bytes([0]) + data
                ).hexdigest()
                if git_sha != _PINNED_STAGE_BLOBS[path]:
                    raise ValueError("changed pinned followthrough ancestor")
                history = json.loads(data)
                if (history.get("source_pack") != stage.get("source_pack")
                        or history.get("audiences") != ["all_ai_bots"]
                        or history.get("consumer_registered") is not False
                        or history.get("constraints") != _GUARDS
                        or len(history.get("entries", [])) != 82):
                    raise ValueError("invalid historical scope")
                if pos and (
                    history.get("previous_stage") != chain[pos - 1]
                    or history.get("previous_stage_blob_sha")
                    != _PINNED_STAGE_BLOBS[chain[pos - 1]]
                ):
                    raise ValueError("broken historical chain")
                for entry in history["entries"]:
                    intent = entry["intent_id"]
                    if intent in past_questions and past_questions[intent] != entry["question"]:
                        raise ValueError("changed historical question")
                    past_questions[intent] = entry["question"]
                    for reply in entry["replies"]:
                        rid, normalized = reply["id"], _norm(reply["text"])
                        if rid in past_ids or not normalized or normalized in past_texts:
                            raise ValueError("duplicate reviewed ancestor")
                        past_ids.add(rid)
                        past_texts.add(normalized)
                        count_prior += 1
            children = stage.get("entries", [])
            current_count = sum(len(entry["replies"]) for entry in children)
            if (len(past_questions) != 82 or len(children) != 82
                    or {entry["intent_id"] for entry in children} != set(past_questions)
                    or stage.get("previous_stage") != chain[-1]
                    or stage.get("previous_stage_blob_sha") != _PINNED_STAGE_BLOBS[chain[-1]]
                    or stage.get("cumulative_checkpoint") != {
                        "baseline_registered": 246,
                        "previous_staged": count_prior,
                        "added_candidates": current_count,
                        "total": 246 + count_prior + current_count,
                        "partial_intents": 82,
                        "finished_100": 0,
                        "remaining_total": 8200 - 246 - count_prior - current_count,
                    }):
                raise ValueError("unverified cumulative stage")
            for entry in children:
                if entry["question"] != past_questions[entry["intent_id"]]:
                    raise ValueError("mutated canonical question")
                for reply in entry["replies"]:
                    if (reply["id"] in past_ids
                            or _norm(reply["text"]) in past_texts):
                        raise ValueError("reused historical reply")

        if (stage.get("schema_version") != 1
                or stage.get("stage_type") != "supplemental_contextual_reply_pool"
                or stage.get("consumer_registered") is not False
                or stage.get("language") != "ru"
                or stage.get("audiences") != ["all_ai_bots"]
                or stage.get("constraints") != _GUARDS):
            raise ValueError("stage metadata is not safe for read-only use")
        source = stage.get("source_pack")
        if source not in packs or not source.startswith("packs/ru/") or not source.endswith("_qa.json"):
            raise ValueError("stage source not registered")
        source_bytes = (root / source).read_bytes()
        digest = hashlib.sha256(source_bytes).hexdigest()
        blob = hashlib.sha1(b"blob " + str(len(source_bytes)).encode() + b"\0" + source_bytes).hexdigest()
        if (digest != packs[source] or digest != stage.get("source_pack_manifest_sha256")
                or blob != stage.get("source_pack_blob_sha")):
            raise ValueError("registered source SHA/blob mismatch")
        source_data = json.loads(source_bytes)
        source_rows = source_data["records"]
        by_id = {entry["id"]: entry for entry in source_rows}
        if len(by_id) != len(source_rows):
            raise ValueError("duplicate canonical source IDs")
        count = 0
        seen_ids: set[str] = set()
        seen_texts: set[str] = set()
        self._by_intent: dict[str, tuple[dict, ...]] = {}
        for entry in stage.get("entries", []):
            ident = entry.get("intent_id")
            original = by_id.get(ident)
            if original is None or entry.get("question") != original["question"] or ident in self._by_intent:
                raise ValueError("stale or duplicate canonical intent")
            original_count = 1 + len(original.get("variants", []))
            replies = entry.get("replies")
            if (not isinstance(replies, list) or not replies
                    or entry.get("registered_reply_count") != original_count
                    or entry.get("staged_reply_count") != len(replies)
                    or original_count + len(replies) > 100):
                raise ValueError("invalid per-intent inventory")
            for reply in replies:
                rid, text = reply.get("id"), reply.get("text")
                if (not isinstance(rid, str) or not rid.startswith(ident + "_")
                        or not re.fullmatch(r"[A-Za-z0-9_-]{1,96}", rid)
                        or rid in seen_ids or not isinstance(text, str)
                        or not 1 <= len(text) <= 1600 or _SECRET.search(text)
                        or reply.get("read_only") is not True
                        or reply.get("audiences") != ["all_ai_bots"]
                        or reply.get("language") != "ru"
                        or reply.get("style") != "neutral"
                        or reply.get("context") not in _CONTEXTS
                        or not isinstance(reply.get("context_note"), str)
                        or not reply["context_note"].strip()
                        or not isinstance(reply.get("avoid"), str) or not reply["avoid"].strip()):
                    raise ValueError("invalid reply identity, privacy or scope")
                norm = _norm(text)
                if not norm or norm in seen_texts:
                    raise ValueError("duplicate or empty normalized staged text")
                seen_ids.add(rid)
                seen_texts.add(norm)
            self._by_intent[ident] = tuple(replies)
            count += len(replies)
        checkpoint = stage.get("checkpoint", {})
        if (not self._by_intent or len(self._by_intent) != len(source_rows)
                or checkpoint.get("registered_count") != sum(1 + len(r.get("variants", [])) for r in source_rows)
                or checkpoint.get("added_candidates") != count
                or checkpoint.get("partial_intents") != sum(
                    1 for r in source_rows if 1 + len(r.get("variants", []))
                    + len(self._by_intent[r["id"]]) < 100)
                or checkpoint.get("finished_100") != sum(
                    1 for r in source_rows if 1 + len(r.get("variants", []))
                    + len(self._by_intent[r["id"]]) == 100)
                or checkpoint.get("remaining_total") != sum(
                    100 - 1 - len(r.get("variants", [])) - len(self._by_intent[r["id"]])
                    for r in source_rows)):
            raise ValueError("staged checkpoint disagrees with actual content")

    def select(
        self, intent_id: str, *, approved_reply_ids: frozenset[str],
        audience: str, context: str, addressed: bool = False,
        local_permission: bool = False, recent_ids: tuple[str, ...] = (),
    ) -> StagedSelection | None:
        """Only trusted caller-verified IDs are eligible; otherwise abstain.

        approved_reply_ids MUST be produced by consumer-side policy/context
        verification, never raw chat text or a guessed match.
        """
        if (addressed is not True or local_permission is not True
                or audience != "all_ai_bots" or context not in _CONTEXTS
                or not isinstance(approved_reply_ids, frozenset)
                or not approved_reply_ids or len(approved_reply_ids) > 100
                or not all(isinstance(x, str) for x in approved_reply_ids)
                or not isinstance(recent_ids, tuple) or len(recent_ids) > 100
                or not all(isinstance(x, str) for x in recent_ids)):
            return None
        recently_used = set(recent_ids)
        for reply in self._by_intent.get(intent_id, ()):
            if (reply["id"] in approved_reply_ids and reply["context"] == context
                    and reply["id"] not in recently_used):
                return StagedSelection(
                    id=reply["id"], text=reply["text"], intent_id=intent_id,
                    context_note=reply["context_note"], stage_path=self.stage_path,
                )
        return None
