"""T273 opt-in spoken-pragmatics reply overlay, preserving the complete T270 chain.

Staged read-only language examples only; neither a bot skill installation nor an action.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

from scripts.spoken_delta_overlay import (
    SpokenDeltaOverlay, SOURCE, PARENT as ORIGINAL_STAGE, GUARDS, CONTEXTS,
    SECRET, norm, jaccard, blob_sha
)
from scripts.staged_context_selector import StagedSelection

DELTA = "staging/ru/spoken_pragmatics_t273_delta.json"
PREVIOUS = "staging/ru/spoken_pragmatics_t270_delta.json"


class SpokenDeltaT273:
    def __init__(self, root: Path, path: str = DELTA):
        if path != DELTA:
            raise ValueError("unreviewed spoken-pragmatics overlay path")
        root = Path(root).resolve(strict=True)
        self.parent = SpokenDeltaOverlay(root)  # validates registered SHA and entire original stage
        parent_raw = (root / PREVIOUS).read_bytes()
        delta_raw = (root / DELTA).read_bytes()
        data = json.loads(delta_raw)
        previous = json.loads(parent_raw)
        manifest = json.loads((root / "manifest.json").read_text("utf-8"))
        registered = {pack["path"]: pack["sha256"] for pack in manifest["packs"]}
        if (
            data.get("schema_version") != 1
            or data.get("delta_type") != "supplemental_contextual_reply_delta"
            or data.get("consumer_registered") is not False
            or data.get("language") != "ru"
            or data.get("audiences") != ["all_ai_bots"]
            or data.get("constraints") != GUARDS
            or data.get("parent_delta_path") != PREVIOUS
            or data.get("parent_delta_blob_sha") != blob_sha(parent_raw)
            or data.get("source_pack") != SOURCE
            or data.get("source_pack_manifest_sha256") != registered[SOURCE]
            or path in registered
        ):
            raise ValueError("stage/source provenance or scope mismatch")

        source = json.loads((root / SOURCE).read_text("utf-8"))
        earlier = json.loads((root / ORIGINAL_STAGE).read_text("utf-8"))
        source_rows = {row["id"]: row for row in source["records"]}
        earlier_rows = {row["intent_id"]: row for row in earlier["entries"]}
        previous_rows = {row["intent_id"]: row for row in previous["entries"]}
        if (len(source_rows), len(earlier_rows), len(previous_rows)) != (24, 24, 24):
            raise ValueError("unexpected canonical inventory")

        seen_texts = set()
        seen_ids = set()
        history = {}
        for ident, row in source_rows.items():
            stage, old = earlier_rows[ident], previous_rows[ident]
            texts = [row["answer"], *row["variants"]]
            for collection in (stage["replies"], old["replies"]):
                texts.extend(reply["text"] for reply in collection)
                for reply in collection:
                    if reply["id"] in seen_ids:
                        raise ValueError("duplicate prior stage ID")
                    seen_ids.add(reply["id"])
            if len(texts) != 65 or len(stage["replies"]) != 51 or len(old["replies"]) != 5:
                raise ValueError("stale previous reply count")
            history[ident] = texts
            seen_texts.update(norm(text) for text in texts)

        self._new = {}
        count = 0
        for entry in data.get("entries", []):
            ident = entry.get("intent_id")
            if ident not in source_rows or ident in self._new:
                raise ValueError("unexpected intent ID")
            row, stage, old = source_rows[ident], earlier_rows[ident], previous_rows[ident]
            replies = entry.get("replies")
            if (
                entry.get("question") != row["question"]
                or entry.get("registered_reply_count") != 9
                or entry.get("parent_staged_reply_count") != 51
                or entry.get("prior_delta_reply_count") != 5
                or not isinstance(replies, list) or len(replies) != 3
            ):
                raise ValueError("stale question/count or malformed entry")
            notes = {norm(reply["context_note"]) for reply in old["replies"]}
            selected = []
            for index, reply in enumerate(replies, 1):
                rid, text, note = reply.get("id"), reply.get("text"), reply.get("context_note")
                if (
                    rid != f"{ident}_t273_{index:02d}"
                    or rid in seen_ids
                    or not isinstance(text, str) or not 1 <= len(text) <= 1600
                    or SECRET.search(text)
                    or reply.get("language") != "ru"
                    or reply.get("style") != "neutral"
                    or reply.get("audiences") != ["all_ai_bots"]
                    or reply.get("read_only") is not True
                    or reply.get("context") not in CONTEXTS
                    or not isinstance(note, str) or not norm(note) or norm(note) in notes
                    or not isinstance(reply.get("avoid"), str) or not reply["avoid"].strip()
                    or not norm(text) or norm(text) in seen_texts
                ):
                    raise ValueError("invalid privacy, text or context")
                if max((jaccard(text, past) for past in history[ident]), default=0) >= .78:
                    raise ValueError("near-duplicate in canonical intent")
                seen_ids.add(rid)
                seen_texts.add(norm(text))
                notes.add(norm(note))
                history[ident].append(text)
                selected.append(reply)
            if len(history[ident]) > 100:
                raise ValueError("intent limit breached")
            self._new[ident] = tuple(selected)
            count += len(selected)

        cp = data.get("checkpoint", {})
        expected = {
            "stage_id": "T273",
            "processed_intents": 24,
            "registered_count": 216,
            "parent_staged_count": 1344,
            "added_in_current": count,
            "total_staged_with_parent": 1344 + count,
            "previous_per_intent": 65,
            "now_per_intent": 68,
            "remaining_per_intent": 32,
            "remaining_total": sum(100 - len(history[ident]) for ident in source_rows),
            "partial_intents": sum(len(history[ident]) < 100 for ident in source_rows),
            "finished_100": sum(len(history[ident]) == 100 for ident in source_rows),
            "rejected": 0,
        }
        if len(self._new) != 24 or any(cp.get(k) != v for k, v in expected.items()):
            raise ValueError("invalid checkpoint")
        self.checkpoint = cp
        self.cache_identity = (manifest["knowledge_version"], blob_sha(parent_raw), blob_sha(delta_raw))

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
                    context_note=reply["context_note"], stage_path=DELTA
                )
        return None
