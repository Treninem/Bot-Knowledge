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
})
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
        stage = json.loads(raw)
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
        if (not addressed or not local_permission or audience != "all_ai_bots"
                or context not in _CONTEXTS or not isinstance(approved_reply_ids, frozenset)
                or not approved_reply_ids or not isinstance(recent_ids, tuple)):
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
