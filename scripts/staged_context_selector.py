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
