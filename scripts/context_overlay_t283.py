"""T283: two distinct, opt-in read-only replies for each of 85 existing RU intents."""
from __future__ import annotations

import json
from pathlib import Path

from scripts.context_overlay_t281 import ContextOverlayT281
from scripts.context_overlay_t271 import PARENTS, GUARDS, CONTEXTS, SECRET, norm, overlap, blob
from scripts.staged_context_selector import StagedSelection

OVERLAY = "staging/ru/context_overlay_t283.json"
PARENT = "staging/ru/context_overlay_t281.json"
LAYERS = (
    "staging/ru/context_delta_t241.json",
    "staging/ru/context_overlay_t271.json",
    "staging/ru/context_overlay_t272.json",
    "staging/ru/context_overlay_t275.json",
    "staging/ru/context_overlay_t277.json",
    "staging/ru/context_overlay_t279.json",
    PARENT,
)
EXPECTED = {"recovery": (24, 80), "choice": (30, 78), "boundaries": (31, 77)}


class ContextOverlayT283:
    def __init__(self, root: Path, path: str = OVERLAY):
        if path != OVERLAY:
            raise ValueError("unreviewed stage path")
        root = Path(root).resolve(strict=True)
        self.parent = ContextOverlayT281(root)
        parent_bytes = (root / PARENT).read_bytes()
        raw = (root / OVERLAY).read_bytes()
        stage = json.loads(raw)
        manifest = json.loads((root / "manifest.json").read_text("utf-8"))
        registered = {item["path"] for item in manifest["packs"]}
        if (
            stage.get("schema_version") != 1
            or stage.get("stage_type") != "supplemental_context_delta_overlay"
            or stage.get("consumer_registered") is not False
            or stage.get("language") != "ru"
            or stage.get("audiences") != ["all_ai_bots"]
            or stage.get("constraints") != GUARDS
            or stage.get("parent_delta_path") != PARENT
            or stage.get("parent_delta_blob_sha") != blob(parent_bytes)
            or OVERLAY in registered
        ):
            raise ValueError("parent hash, scope or registration mismatch")

        layers = []
        for filename in LAYERS:
            entries = json.loads((root / filename).read_text("utf-8"))["entries"]
            by_id = {row["intent_id"]: row for row in entries}
            if len(entries) != 85 or len(by_id) != 85:
                raise ValueError("duplicate historical intent")
            layers.append(by_id)
        previous = layers[-1]
        source = {}
        old_texts = {}
        known_ids = set()
        known_texts = set()
        note_history = {}
        for group, (base_path, count, _, _) in PARENTS.items():
            base_stage = json.loads((root / base_path).read_text("utf-8"))
            pack = json.loads((root / base_stage["source_pack"]).read_text("utf-8"))
            base_by_id = {row["intent_id"]: row for row in base_stage["entries"]}
            expected_count, expected_before = EXPECTED[group]
            if count != expected_count or len(pack["records"]) != expected_count:
                raise ValueError("registered count drift")
            for rec in pack["records"]:
                ident = rec["id"]
                if ident in source or ident not in base_by_id or any(ident not in m for m in layers):
                    raise ValueError("missing/duplicated canonical intent")
                old = previous[ident]
                if old.get("source_stage") != base_path:
                    raise ValueError("source stage changed")
                texts = [rec["answer"], *rec.get("variants", [])]
                notes = set()
                for row in [base_by_id[ident], *(m[ident] for m in layers)]:
                    for reply in row["replies"]:
                        if reply["id"] in known_ids:
                            raise ValueError("historical reply ID reused")
                        known_ids.add(reply["id"])
                        texts.append(reply["text"])
                        notes.add(norm(reply["context_note"]))
                if len(texts) != expected_before:
                    raise ValueError("prior stage count drift")
                source[ident] = (rec["question"], base_path, expected_before, group)
                old_texts[ident] = texts
                note_history[ident] = notes
                known_texts.update(norm(t) for t in texts)
        if len(source) != 85:
            raise ValueError("incomplete source inventory")
        self._new = {}
        added = 0
        for entry in stage.get("entries", []):
            ident = entry.get("intent_id")
            if ident not in source or ident in self._new:
                raise ValueError("unknown or duplicate new intent")
            question, source_path, before, group = source[ident]
            replies = entry.get("replies")
            if (
                entry.get("question") != question
                or entry.get("source_stage") != source_path
                or entry.get("expected_total_before") != before
                or not isinstance(replies, list) or len(replies) != 1
            ):
                raise ValueError("stale canonical question, source or count")
            self._new[ident] = []
            for index, reply in enumerate(replies, 1):
                rid, text, note = reply.get("id"), reply.get("text"), reply.get("context_note")
                if (
                    rid != f"{ident}_t283_{index:02d}" or rid in known_ids
                    or not isinstance(text, str) or not 1 <= len(text) <= 1600
                    or SECRET.search(text)
                    or reply.get("language") != "ru"
                    or reply.get("style") != "neutral"
                    or reply.get("audiences") != ["all_ai_bots"]
                    or reply.get("read_only") is not True
                    or reply.get("context") not in CONTEXTS
                    or not isinstance(note, str) or not norm(note)
                    or norm(note) in note_history[ident]
                    or not isinstance(reply.get("avoid"), str) or not reply["avoid"].strip()
                    or not norm(text) or norm(text) in known_texts
                ):
                    raise ValueError("unsafe or duplicate reply/context")
                if max((overlap(text, old) for old in old_texts[ident]), default=0) >= .78:
                    raise ValueError("near-duplicate same-intent response")
                known_ids.add(rid)
                known_texts.add(norm(text))
                old_texts[ident].append(text)
                note_history[ident].add(norm(note))
                self._new[ident].append(reply)
                added += 1
            self._new[ident] = tuple(self._new[ident])
        cp = stage.get("checkpoint", {})
        expected = {
            "stage_id": "T283", "processed_intents": 85,
            "parent_staged_count": 2040, "added_in_current": 85,
            "total_staged_with_parent": 2125,
            "remaining_total": sum(100 - len(texts) for texts in old_texts.values()),
            "partial_intents": sum(len(texts) < 100 for texts in old_texts.values()),
            "finished_100": sum(len(texts) == 100 for texts in old_texts.values()),
            "rejected": 0,
        }
        if len(self._new) != 85 or added != 85 or any(cp.get(k) != v for k, v in expected.items()):
            raise ValueError("false checkpoint")
        for group, (count, before) in EXPECTED.items():
            rows = [e for e in stage["entries"] if source[e["intent_id"]][3] == group]
            item = next((x for x in cp.get("per_source", []) if x.get("source") == group), None)
            if (
                len(rows) != count or item is None
                or item.get("intents") != count
                or item.get("before") != before
                or item.get("after") != before + 1
                or item.get("remaining_per_intent") != 99 - before
            ):
                raise ValueError("false group checkpoint")
        self.checkpoint = cp
        self.cache_identity = (manifest["knowledge_version"], blob(parent_bytes), blob(raw))

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
        for reply in self._new.get(intent_id, ()):
            if reply["id"] in approved_reply_ids and reply["id"] not in recent_ids and reply["context"] == context:
                return StagedSelection(
                    id=reply["id"], text=reply["text"], intent_id=intent_id,
                    context_note=reply["context_note"], stage_path=OVERLAY
                )
        return None
