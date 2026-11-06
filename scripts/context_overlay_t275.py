"""T275: opt-in staged RU context overlay, pinned to the validated T271 layer.

No consumer integration, side effects, moderation decisions, or implicit activation.
"""
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

from scripts.context_overlay_t272 import ContextOverlayT272
from scripts.context_overlay_t271 import (
    ContextOverlayT271, PARENTS, CONTEXTS, GUARDS, SECRET, norm, overlap, blob
)
from scripts.staged_context_selector import StagedSelection

OVERLAY = "staging/ru/context_overlay_t275.json"
PARENT = "staging/ru/context_overlay_t272.json"
T271 = "staging/ru/context_overlay_t271.json"
T241 = "staging/ru/context_delta_t241.json"


class ContextOverlayT275:
    """Validate the complete prior chain before exposing explicit approved T275 IDs."""

    def __init__(self, root: Path, path: str = OVERLAY):
        if path != OVERLAY:
            raise ValueError("unreviewed overlay path")
        root = Path(root).resolve(strict=True)
        self.parent = ContextOverlayT272(root)
        parent_raw = (root / PARENT).read_bytes()
        raw = (root / path).read_bytes()
        data = json.loads(raw)
        manifest = json.loads((root / "manifest.json").read_text("utf-8"))
        manifest_paths = {entry["path"] for entry in manifest["packs"]}
        if (
            data.get("schema_version") != 1
            or data.get("stage_type") != "supplemental_context_delta_overlay"
            or data.get("consumer_registered") is not False
            or data.get("language") != "ru"
            or data.get("audiences") != ["all_ai_bots"]
            or data.get("constraints") != GUARDS
            or data.get("parent_delta_path") != PARENT
            or data.get("parent_delta_blob_sha") != blob(parent_raw)
            or path in manifest_paths
        ):
            raise ValueError("unverified stage provenance/registration")

        old = json.loads(parent_raw)
        t271 = json.loads((root / T271).read_text("utf-8"))
        t241 = json.loads((root / T241).read_text("utf-8"))
        t241_by_id = {entry["intent_id"]: entry for entry in t241["entries"]}
        old_by_id = {entry["intent_id"]: entry for entry in old["entries"]}
        t271_by_id = {entry["intent_id"]: entry for entry in t271["entries"]}
        if len(t241_by_id) != 85 or len(old_by_id) != 85 or len(t271_by_id) != 85:
            raise ValueError("unexpected parent inventory")

        known_texts = set()
        known_ids = set()
        canonical = {}
        for group, (stage_path, expected_count, _, before) in PARENTS.items():
            stage = json.loads((root / stage_path).read_text("utf-8"))
            pack = json.loads((root / stage["source_pack"]).read_text("utf-8"))
            staged_by_id = {entry["intent_id"]: entry for entry in stage["entries"]}
            if len(pack["records"]) != expected_count or len(staged_by_id) != expected_count:
                raise ValueError("stale registered/staged intent count")
            for rec in pack["records"]:
                ident = rec["id"]
                par, previous, earlier = staged_by_id.get(ident), old_by_id.get(ident), t241_by_id.get(ident)
                if not all((par, previous, earlier)) or ident in canonical:
                    raise ValueError("missing prior canonical record")
                texts = [rec["answer"], *rec.get("variants", [])]
                for row in (par, earlier, t271_by_id[ident], previous):
                    texts.extend(reply["text"] for reply in row["replies"])
                    for reply in row["replies"]:
                        if reply["id"] in known_ids:
                            raise ValueError("duplicate historical ID")
                        known_ids.add(reply["id"])
                if len(texts) != before + 2:
                    raise ValueError("incorrect source intent count")
                canonical[ident] = (rec["question"], stage_path, before + 2, texts, previous)
                known_texts.update(norm(t) for t in texts)

        self._new = {}
        added = 0
        for ent in data.get("entries", []):
            ident = ent.get("intent_id")
            if ident not in canonical or ident in self._new:
                raise ValueError("unknown/duplicate intent")
            question, stage_path, before, historic, previous = canonical[ident]
            replies = ent.get("replies")
            if (
                ent.get("question") != question
                or ent.get("source_stage") != stage_path
                or ent.get("expected_total_before") != before
                or not isinstance(replies, list)
                or len(replies) != 1
            ):
                raise ValueError("stale or malformed canonical entry")
            notes = {norm(v["context_note"]) for v in (*t271_by_id[ident]["replies"], *previous["replies"])}
            selected = []
            for i, reply in enumerate(replies, 1):
                rid, text = reply.get("id"), reply.get("text")
                note = reply.get("context_note")
                if (
                    rid != f"{ident}_t275_{i:02d}"
                    or rid in known_ids
                    or not isinstance(text, str) or not 1 <= len(text) <= 1600
                    or SECRET.search(text)
                    or reply.get("language") != "ru"
                    or reply.get("style") != "neutral"
                    or reply.get("audiences") != ["all_ai_bots"]
                    or reply.get("read_only") is not True
                    or reply.get("context") not in CONTEXTS
                    or not isinstance(note, str) or not norm(note)
                    or not isinstance(reply.get("avoid"), str) or not reply["avoid"].strip()
                    or norm(text) in known_texts or not norm(text)
                    or norm(note) in notes
                ):
                    raise ValueError("unsafe/duplicate content or context")
                if max((overlap(text, prior) for prior in historic), default=0) >= .78:
                    raise ValueError("near-duplicate within canonical intent")
                known_ids.add(rid)
                known_texts.add(norm(text))
                notes.add(norm(note))
                historic.append(text)
                selected.append(reply)
            if before + len(selected) > 100:
                raise ValueError("100 reply limit exceeded")
            self._new[ident] = tuple(selected)
            added += len(selected)

        cp = data.get("checkpoint", {})
        expected = {
            "stage_id": "T275",
            "processed_intents": 85,
            "parent_staged_count": 1615,
            "added_in_current": added,
            "total_staged_with_parent": 1615 + added,
            "remaining_total": sum(100 - before - len(self._new.get(ident, ()))
                                   for ident, (_, _, before, _, _) in canonical.items()),
            "partial_intents": sum(before + len(self._new.get(ident, ())) < 100
                                   for ident, (_, _, before, _, _) in canonical.items()),
            "finished_100": sum(before + len(self._new.get(ident, ())) == 100
                                for ident, (_, _, before, _, _) in canonical.items()),
            "rejected": 0,
        }
        if len(self._new) != 85 or any(cp.get(key) != value for key, value in expected.items()):
            raise ValueError("checkpoint not supported by actual content")
        for group, (stage_path, expected_n, _, before) in PARENTS.items():
            group_rows = [entry for entry in data["entries"] if entry["source_stage"] == stage_path]
            cp_row = next((row for row in cp.get("per_source", []) if row.get("source") == group), None)
            if (
                len(group_rows) != expected_n or cp_row is None
                or cp_row.get("intents") != expected_n or cp_row.get("before") != before + 2
                or cp_row.get("after") != before + 3
                or cp_row.get("remaining_per_intent") != 97 - before
            ):
                raise ValueError("per-source counts incorrect")
        self.checkpoint = cp
        self.cache_identity = (manifest["knowledge_version"], blob(parent_raw), blob(raw))

    def select(self, intent_id: str, *, approved_reply_ids: frozenset[str], audience: str,
               context: str, addressed: bool = False, local_permission: bool = False,
               recent_ids: tuple[str, ...] = ()) -> StagedSelection | None:
        if (
            not addressed or not local_permission or audience != "all_ai_bots"
            or context not in CONTEXTS or not isinstance(approved_reply_ids, frozenset)
            or not approved_reply_ids or not isinstance(recent_ids, tuple)
        ):
            return None
        for reply in self._new.get(intent_id, ()):
            if (
                reply["id"] in approved_reply_ids and reply["id"] not in recent_ids
                and reply["context"] == context
            ):
                return StagedSelection(
                    id=reply["id"], text=reply["text"], intent_id=intent_id,
                    context_note=reply["context_note"], stage_path=OVERLAY
                )
        return None
