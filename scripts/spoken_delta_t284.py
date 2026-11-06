"""T284: checked read-only RU spoken-pragmatics continuation (24 intents × 3).

A staged language proposal, not a consumer plugin, bot action or authorization.
Historical data/registered SHA are validated through the immutable T276 parent.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

from scripts.spoken_delta_t282 import SpokenDeltaT282
from scripts.spoken_delta_overlay import SOURCE, GUARDS, CONTEXTS, SECRET, norm, jaccard, blob_sha
from scripts.staged_context_selector import StagedSelection

DELTA = "staging/ru/spoken_pragmatics_t284_delta.json"
PARENT = "staging/ru/spoken_pragmatics_t282_delta.json"
HISTORY = (
    "staging/ru/spoken_pragmatics_t251_context_pool.json",
    "staging/ru/spoken_pragmatics_t270_delta.json",
    "staging/ru/spoken_pragmatics_t273_delta.json",
    "staging/ru/spoken_pragmatics_t274_delta.json",
    "staging/ru/spoken_pragmatics_t276_delta.json",
    "staging/ru/spoken_pragmatics_t278_delta.json",
    "staging/ru/spoken_pragmatics_t280_delta.json",
    PARENT,
)


class SpokenDeltaT284:
    def __init__(self, root: Path, path: str = DELTA):
        if path != DELTA:
            raise ValueError("T278 only permits its reviewed staged path")
        root = Path(root).resolve(strict=True)
        self.parent = SpokenDeltaT282(root)
        parent_bytes = (root / PARENT).read_bytes()
        raw = (root / DELTA).read_bytes()
        stage = json.loads(raw)
        manifest = json.loads((root / "manifest.json").read_text("utf-8"))
        registered = {e["path"]: e["sha256"] for e in manifest["packs"]}
        if (
            stage.get("schema_version") != 1
            or stage.get("delta_type") != "supplemental_contextual_reply_delta"
            or stage.get("consumer_registered") is not False
            or stage.get("language") != "ru"
            or stage.get("audiences") != ["all_ai_bots"]
            or stage.get("constraints") != GUARDS
            or stage.get("parent_delta_path") != PARENT
            or stage.get("parent_delta_blob_sha") != blob_sha(parent_bytes)
            or stage.get("source_pack") != SOURCE
            or stage.get("source_pack_manifest_sha256") != registered[SOURCE]
            or DELTA in registered
        ):
            raise ValueError("untrusted parent, source hash, or audience")
        source = json.loads((root / SOURCE).read_text("utf-8"))
        canonical = {rec["id"]: rec for rec in source["records"]}
        historical = []
        for filename in HISTORY:
            rows = json.loads((root / filename).read_text("utf-8"))["entries"]
            by_id = {row["intent_id"]: row for row in rows}
            if len(rows) != 24 or set(by_id) != set(canonical):
                raise ValueError("historical intent inventory drift")
            historical.append(by_id)
        if len(canonical) != 24:
            raise ValueError("wrong registered intent count")

        self._new = {}
        history_texts = {}
        note_history = {}
        seen_ids = set()
        seen_texts = set()
        for ident, rec in canonical.items():
            texts = [rec["answer"], *rec["variants"]]
            notes = set()
            for stage_rows in historical:
                for reply in stage_rows[ident]["replies"]:
                    if reply["id"] in seen_ids:
                        raise ValueError("duplicate historical ID")
                    seen_ids.add(reply["id"])
                    texts.append(reply["text"])
                    notes.add(norm(reply["context_note"]))
            if len(texts) != 84:
                raise ValueError("historical per-intent count != 84")
            history_texts[ident] = texts
            note_history[ident] = notes
            seen_texts.update(norm(t) for t in texts)

        added = 0
        for entry in stage.get("entries", []):
            ident = entry.get("intent_id")
            if ident not in canonical or ident in self._new:
                raise ValueError("unexpected or repeated intent")
            replies = entry.get("replies")
            if (
                entry.get("question") != canonical[ident]["question"]
                or entry.get("registered_reply_count") != 9
                or entry.get("parent_staged_reply_count") != 75
                or not isinstance(replies, list)
                or len(replies) != 2
            ):
                raise ValueError("stale counts, question, or reply collection")
            selected = []
            for position, reply in enumerate(replies, 1):
                rid, text, note = reply.get("id"), reply.get("text"), reply.get("context_note")
                if (
                    rid != f"{ident}_t284_{position:02d}" or rid in seen_ids
                    or not isinstance(text, str) or not 1 <= len(text) <= 1600
                    or SECRET.search(text)
                    or reply.get("language") != "ru"
                    or reply.get("style") != "neutral"
                    or reply.get("audiences") != ["all_ai_bots"]
                    or reply.get("read_only") is not True
                    or reply.get("context") not in CONTEXTS
                    or not isinstance(note, str) or not norm(note)
                    or norm(note) in note_history[ident]
                    or not isinstance(reply.get("avoid"), str)
                    or not reply["avoid"].strip()
                    or not norm(text) or norm(text) in seen_texts
                ):
                    raise ValueError("unsafe/duplicate identity, reply or context")
                if max((jaccard(text, past) for past in history_texts[ident]), default=0) >= .78:
                    raise ValueError("near duplicate within canonical question")
                seen_ids.add(rid)
                seen_texts.add(norm(text))
                note_history[ident].add(norm(note))
                history_texts[ident].append(text)
                selected.append(reply)
            self._new[ident] = tuple(selected)
            added += len(selected)

        cp = stage.get("checkpoint", {})
        expected = {
            "stage_id": "T284",
            "processed_intents": 24,
            "registered_count": 216,
            "parent_staged_count": 1800,
            "added_in_current": added,
            "total_staged_with_parent": 1800 + added,
            "previous_per_intent": 84,
            "now_per_intent": 86,
            "remaining_per_intent": 14,
            "remaining_total": sum(100 - len(t) for t in history_texts.values()),
            "partial_intents": sum(len(t) < 100 for t in history_texts.values()),
            "finished_100": sum(len(t) == 100 for t in history_texts.values()),
            "rejected": 0,
        }
        if len(self._new) != 24 or any(cp.get(key) != val for key, val in expected.items()):
            raise ValueError("checkpoint not supported by actual records")
        self.checkpoint = cp
        self.cache_identity = (manifest["knowledge_version"], blob_sha(parent_bytes), blob_sha(raw))

    def select(self, intent_id: str, *, approved_reply_ids: frozenset[str],
               audience: str, context: str, addressed: bool = False,
               local_permission: bool = False,
               recent_ids: tuple[str, ...] = ()) -> StagedSelection | None:
        if (
            not addressed or not local_permission or audience != "all_ai_bots"
            or context not in CONTEXTS or not isinstance(approved_reply_ids, frozenset)
            or not approved_reply_ids or not isinstance(recent_ids, tuple)
        ):
            return None
        for item in self._new.get(intent_id, ()):
            if (
                item["id"] in approved_reply_ids
                and item["id"] not in recent_ids
                and item["context"] == context
            ):
                return StagedSelection(
                    id=item["id"], text=item["text"], intent_id=intent_id,
                    context_note=item["context_note"], stage_path=DELTA
                )
        return None
