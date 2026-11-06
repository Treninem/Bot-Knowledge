"""Fail-closed, explicit opt-in selector for the T241 contextual delta.

The delta is a staging-only continuation of existing intent IDs; it is never
registered through manifest.json or enabled by ordinary search. An independent,
trusted consumer must approve an exact reply ID and check context first.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import re
import unicodedata

from scripts.staged_context_selector import StagedContextSelector, StagedSelection

_DELTA = "staging/ru/context_delta_t241.json"
_PARENT = frozenset({
    "staging/ru/recovery_t168_context_pool.json",
    "staging/ru/choice_t166_context_pool.json",
    "staging/ru/boundaries_t167_context_pool.json",
})
_CONTEXTS = frozenset({"direct", "private", "group_addressed"})
_GUARDS = {"read_only": True, "requires_direct_address": True, "no_personal_data": True}
_SECRET = re.compile(
    r"(?i)(ghp_[a-z0-9]{12,}|sk-[a-z0-9]{12,}|bot_token|chat_id|user_id|"
    r"bearer\s+|https://t\.me/|[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,})"
)


def _norm(value: str) -> str:
    value = unicodedata.normalize("NFKC", value).casefold().replace("ё", "е")
    return " ".join("".join(
        " " if unicodedata.category(ch)[0] in {"P", "S"} else ch
        for ch in value
    ).split())


def _blob_sha(raw: bytes) -> str:
    header = ("blob " + str(len(raw))).encode("ascii") + b"\0"
    return hashlib.sha1(header + raw).hexdigest()


class StagedContextDelta:
    """Read a pinned multi-pack delta, returning only caller-approved replies."""

    def __init__(self, repository_root: Path, delta_path: str):
        if delta_path != _DELTA:
            raise ValueError("untrusted or unreviewed staging delta")
        root = Path(repository_root).resolve(strict=True)
        payload = json.loads((root / delta_path).read_text("utf-8"))
        if (payload.get("schema_version") != 1
                or payload.get("stage_type") != "supplemental_contextual_reply_delta"
                or payload.get("consumer_registered") is not False
                or payload.get("language") != "ru"
                or payload.get("audiences") != ["all_ai_bots"]
                or payload.get("constraints") != _GUARDS):
            raise ValueError("invalid or untrusted staging delta metadata")

        parent_blobs = payload.get("parent_stage_blobs")
        if not isinstance(parent_blobs, dict) or set(parent_blobs) != _PARENT:
            raise ValueError("missing or unexpected staged parent")
        by_parent = {}
        canonical = {}
        known_ids = set()
        known_texts = set()
        known_notes = {}
        for stage_path, expected_sha in parent_blobs.items():
            raw = (root / stage_path).read_bytes()
            if not re.fullmatch(r"[a-f0-9]{40}", expected_sha) or _blob_sha(raw) != expected_sha:
                raise ValueError("parent stage changed since this delta was reviewed")
            StagedContextSelector(root, stage_path)  # validates source SHA, scope, catalog and counts
            parent = json.loads(raw)
            source = json.loads((root / parent["source_pack"]).read_text("utf-8"))
            rows = {rec["id"]: rec for rec in source["records"]}
            if len(rows) != len(source["records"]):
                raise ValueError("duplicate registered source ID")
            by_parent[stage_path] = {e["intent_id"]: e for e in parent["entries"]}
            for e in parent["entries"]:
                rec = rows[e["intent_id"]]
                canonical[e["intent_id"]] = (
                    stage_path, rec, e
                )
                known_notes[e["intent_id"]] = {_norm(r["context_note"]) for r in e["replies"]}
                for answer in [rec["answer"], *rec.get("variants", [])]:
                    t = _norm(answer)
                    if t:
                        known_texts.add(t)
                for reply in e["replies"]:
                    known_ids.add(reply["id"])
                    known_texts.add(_norm(reply["text"]))

        expected_intents = set(canonical)
        if len(expected_intents) != sum(len(e) for e in by_parent.values()):
            raise ValueError("parent intents overlap unexpectedly")
        self.stage_path = delta_path
        self._by_intent = {}
        for entry in payload.get("entries", []):
            intent = entry.get("intent_id")
            if intent not in canonical or intent in self._by_intent:
                raise ValueError("unknown or duplicate canonical intent")
            stage_path, original, parent_entry = canonical[intent]
            if (entry.get("source_stage") != stage_path
                    or entry.get("question") != original["question"]
                    or entry.get("baseline_registered") != 1 + len(original.get("variants", []))
                    or entry.get("baseline_staged") != len(parent_entry["replies"])):
                raise ValueError("incorrect source mapping or stale inventory")
            replies = entry.get("replies")
            if not isinstance(replies, list) or not replies:
                raise ValueError("empty or invalid incremental reply list")
            if entry["baseline_registered"] + entry["baseline_staged"] + len(replies) > 100:
                raise ValueError("overfull canonical intent")
            for reply in replies:
                rid, txt = reply.get("id"), reply.get("text")
                note, avoid = reply.get("context_note"), reply.get("avoid")
                if (not isinstance(rid, str)
                        or not re.fullmatch(re.escape(intent) + r"_t241_[0-9]{2}", rid)
                        or rid in known_ids
                        or not isinstance(txt, str) or not 1 <= len(txt) <= 1600
                        or _SECRET.search(txt)
                        or not isinstance(note, str) or not _norm(note)
                        or _norm(note) in known_notes[intent]
                        or not isinstance(avoid, str) or not avoid.strip()
                        or reply.get("language") != "ru"
                        or reply.get("style") != "neutral"
                        or reply.get("audiences") != ["all_ai_bots"]
                        or reply.get("read_only") is not True
                        or reply.get("context") not in _CONTEXTS
                        or not _norm(txt) or _norm(txt) in known_texts):
                    raise ValueError(f"duplicate, unsafe or unscoped incremental reply: {intent} / {rid}")
                known_notes[intent].add(_norm(note))
                known_ids.add(rid)
                known_texts.add(_norm(txt))
            self._by_intent[intent] = tuple(replies)

        if set(self._by_intent) != expected_intents:
            raise ValueError("delta does not cover every asserted canonical intent")
        cp = payload.get("checkpoint", {})
        counts = {
            "recovery": (24, 56, 96, 48),
            "choice": (30, 54, 120, 60),
            "boundaries": (31, 53, 124, 62),
        }
        if (cp.get("updated_in") != "T265" or cp.get("verified_new") != 1275
                or cp.get("rejected") != 0 or cp.get("processed_intents") != 85
                or cp.get("newly_finished_100") != 0
                or cp.get("prior_accepted") != 1190 or cp.get("added_in_current") != 85
                or sum(len(v) for v in self._by_intent.values()) != 1275):
            raise ValueError("delta checkpoint disagrees with content")
        for row in cp.get("per_source", []):
            spec = counts.pop(row.get("source"), None)
            if spec is None:
                raise ValueError("duplicate or unknown source inventory")
            n, before, old_new, old_additional = spec
            if (row.get("intents"), row.get("baseline_total_per_intent"),
                    row.get("new_total_per_intent"), row.get("remaining_per_intent"),
                    row.get("new_answers"), row.get("t242_added_answers"), row.get("t243_added_answers"), row.get("t244_added_answers"), row.get("t245_added_answers"),
                    row.get("t246_added_answers"), row.get("t247_added_answers"), row.get("t257_added_answers"), row.get("t261_added_answers"), row.get("t262_added_answers"), row.get("t265_added_answers")) != (n, before, before + 15, 85 - before, old_new + 11 * n, old_additional, 2 * n, n, n, 2 * n, n, n, n, n, n):
                raise ValueError("incorrect per-source counts")
        if counts:
            raise ValueError("missing per-source counts")

    def select(
        self, intent_id: str, *, approved_reply_ids: frozenset[str],
        audience: str, context: str, addressed: bool = False,
        local_permission: bool = False, recent_ids: tuple[str, ...] = (),
    ) -> StagedSelection | None:
        if (not addressed or not local_permission or audience != "all_ai_bots"
                or context not in _CONTEXTS
                or not isinstance(approved_reply_ids, frozenset)
                or not approved_reply_ids or not isinstance(recent_ids, tuple)):
            return None
        for reply in self._by_intent.get(intent_id, ()):
            if (reply["id"] in approved_reply_ids
                    and reply["context"] == context
                    and reply["id"] not in recent_ids):
                return StagedSelection(
                    id=reply["id"], text=reply["text"], intent_id=intent_id,
                    context_note=reply["context_note"], stage_path=self.stage_path
                )
        return None
