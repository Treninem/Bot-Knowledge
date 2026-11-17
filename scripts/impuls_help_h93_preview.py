"""Offline preview for the H93 ImPULS staging batch, never an automatic bot route.

Only an independently reviewed reply ID, confirmed conversation context and
trusted local permission may produce text. This does not classify messages,
publish knowledge, access chats or carry out any moderation action.
"""
from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STAGE = "staging/ru/impuls_help_context_h93_20261115.json"
PACK = "packs/ru/impuls_help_qa.json"
H93_SHA256 = "0115a93800dd67c0ec85c429f4e2bbce3b7e8f3b4d5b9500735de115e00f6d20"
_CONTEXTS = frozenset(("direct", "private", "group_addressed"))
_SCOPE = {
    "read_only": True,
    "requires_direct_address": True,
    "requires_context_match": True,
    "no_personal_data": True,
    "no_sanctions": True,
}


@dataclass(frozen=True)
class PreviewReply:
    id: str
    intent_id: str
    text: str
    context_note: str
    stage_sha256: str


class H93Preview:
    """Fail-closed preview: the trusted caller must approve exactly one reply."""

    def __init__(self, root: Path = ROOT):
        root = Path(root).resolve(strict=True)
        raw = (root / STAGE).read_bytes()
        if hashlib.sha256(raw).hexdigest() != H93_SHA256:
            raise ValueError("H93 staged bytes differ from pinned review snapshot")
        stage = json.loads(raw)
        manifest = json.loads((root / "manifest.json").read_bytes())
        pack_hashes = {p["path"]: p["sha256"] for p in manifest["packs"]}
        source_hash = hashlib.sha256((root / PACK).read_bytes()).hexdigest()
        if (
            PACK not in pack_hashes or source_hash != pack_hashes[PACK]
            or source_hash != stage.get("source_pack_manifest_sha256")
            or stage.get("source_pack") != PACK
            or stage.get("consumer_registered") is not False
            or stage.get("audiences") != ["impuls"]
            or stage.get("constraints") != _SCOPE
            or STAGE in pack_hashes
            or stage.get("checkpoint", {}).get("new_candidates") != 70
            or len(stage.get("entries", [])) != 61
        ):
            raise ValueError("H93 stage scope or source snapshot is invalid")
        self._by_intent = {}
        ids = set()
        for entry in stage["entries"]:
            ident = entry.get("intent_id")
            if not isinstance(ident, str) or ident in self._by_intent:
                raise ValueError("duplicate or invalid staged intent")
            rows = {}
            for reply in entry.get("replies", ()):
                rid = reply.get("id")
                if (
                    not isinstance(rid, str) or not rid.startswith("impuls_help_" + ident + "_h93_")
                    or rid in ids or reply.get("read_only") is not True
                    or reply.get("audiences") != ["impuls"]
                    or reply.get("context") not in _CONTEXTS
                    or reply.get("editorial_status") != "candidate_pending_full_semantic_review"
                    or not isinstance(reply.get("text"), str)
                    or not isinstance(reply.get("context_note"), str)
                    or not reply["context_note"].strip()
                ):
                    raise ValueError("invalid staged reply or metadata")
                ids.add(rid)
                rows[rid] = reply
            if not rows:
                raise ValueError("empty staged intent")
            self._by_intent[ident] = rows
        if len(ids) != 70:
            raise ValueError("H93 reply count changed")
        self._ids = frozenset(ids)
        self.cache_identity = (manifest["knowledge_version"], H93_SHA256)

    def select(
        self, intent_id: str, *, approved_reply_ids: frozenset[str],
        audience: str, context: str, addressed: bool = False,
        chat_scope_verified: bool = False, local_permission: bool = False,
        recent_ids: tuple[str, ...] = (),
    ) -> PreviewReply | None:
        """Never infer approval from chat text, role names, or a quoted command.

        approved_reply_ids must be supplied by an independently trusted reviewer
        that checked the full context_note. A stage candidate is never approved
        automatically. This function has no write or action path.
        """
        if (
            type(addressed) is not bool or addressed is not True
            or type(chat_scope_verified) is not bool or chat_scope_verified is not True
            or type(local_permission) is not bool or local_permission is not True
            or audience != "impuls" or context not in _CONTEXTS
            or not isinstance(intent_id, str)
            or not isinstance(approved_reply_ids, frozenset)
            or len(approved_reply_ids) != 1
            or not approved_reply_ids.issubset(self._ids)
            or not isinstance(recent_ids, tuple) or len(recent_ids) > 100
            or not all(isinstance(x, str) for x in recent_ids)
        ):
            return None
        reply_id = next(iter(approved_reply_ids))
        item = self._by_intent.get(intent_id, {}).get(reply_id)
        if item is None or item["context"] != context or reply_id in recent_ids:
            return None
        return PreviewReply(
            id=reply_id, intent_id=intent_id, text=item["text"],
            context_note=item["context_note"], stage_sha256=H93_SHA256,
        )
