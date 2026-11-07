"""T306 safe salvage of 96 T159 draft replies into an isolated opt-in stage.

The stale T159 PR must not replace newer registered QA or manifest data.
This is a read-only, explicit-ID selector; no implicit routing, memory or actions.
"""
from __future__ import annotations
import hashlib
import json
import re
from pathlib import Path
from scripts.colloquial_t305 import norm, blob_sha
from scripts.staged_context_selector import StagedSelection

ROOT = Path(__file__).resolve().parents[1]
STAGE = "staging/ru/practical_t306_salvage.json"
SOURCE = "packs/ru/practical_recovery_qa.json"
GUARDS = {"read_only": True, "requires_direct_address": True, "no_personal_data": True}
CONTEXTS = frozenset({"direct", "private", "group_addressed"})
PRIVATE = re.compile(r"(?i)(ghp_[a-z0-9]{12,}|sk-[a-z0-9]{12,}|bot_token|chat_id|user_id|https://t\.me/|@[a-z0-9_]{4,}|[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,})")


class PracticalT306:
    def __init__(self, root: Path = ROOT, stage_path: str = STAGE):
        if stage_path != STAGE:
            raise ValueError("unreviewed staging path")
        root = Path(root).resolve(strict=True)
        file = root / STAGE
        if file.is_symlink() or not file.resolve().is_relative_to(root):
            raise ValueError("unsafe staging path")
        stage = json.loads(file.read_text("utf-8"))
        manifest = json.loads((root / "manifest.json").read_text("utf-8"))
        hashes = {entry["path"]: entry["sha256"] for entry in manifest["packs"]}
        source_bytes = (root / SOURCE).read_bytes()
        if (SOURCE not in hashes
                or hashlib.sha256(source_bytes).hexdigest() != hashes[SOURCE]
                or stage.get("source_pack") != SOURCE
                or stage.get("source_pack_manifest_sha256") != hashes[SOURCE]
                or stage.get("source_pack_blob_sha") != blob_sha(source_bytes)):
            raise ValueError("source SHA/blob changed")
        if (STAGE in hashes
                or stage.get("schema_version") != 1
                or stage.get("stage_type") != "salvaged_contextual_reply_delta"
                or stage.get("consumer_registered") is not False
                or stage.get("language") != "ru"
                or stage.get("audiences") != ["all_ai_bots"]
                or stage.get("constraints") != GUARDS
                or stage.get("provenance_pr") != 241
                or stage.get("provenance_head_sha") != "504c33e380ddf920a1c2693c736ff5aee34ae4a9"):
            raise ValueError("untrusted salvage metadata")
        records = json.loads(source_bytes)["records"]
        by_id = {row["id"]: row for row in records}
        if len(records) != 24 or len(by_id) != 24:
            raise ValueError("wrong canonical source inventory")
        known_texts, seen_notes, seen_ids = set(), set(), set()
        for row in records:
            if len(row.get("variants", [])) != 8:
                raise ValueError("registered baseline changed")
            for response in [row["answer"], *row["variants"]]:
                item = norm(response)
                if item in known_texts:
                    raise ValueError("source repeated reply")
                known_texts.add(item)
        self._by_intent = {}
        for entry in stage.get("entries", []):
            ident = entry.get("intent_id")
            source = by_id.get(ident)
            if (source is None or ident in self._by_intent
                    or entry.get("question") != source["question"]
                    or entry.get("source_pr") != 241
                    or entry.get("baseline_registered") != 9
                    or entry.get("salvaged_reply_count") != 4
                    or not isinstance(entry.get("replies"), list)
                    or len(entry["replies"]) != 4):
                raise ValueError("invalid or duplicated salvaged intent")
            replies = []
            for i, reply in enumerate(entry["replies"], 1):
                rid, text, note = reply.get("id"), reply.get("text"), reply.get("context_note")
                if (rid != f"{ident}_t306_{i:02d}" or rid in seen_ids
                        or not isinstance(text, str) or not 1 <= len(text) <= 1600
                        or not isinstance(note, str) or not 1 <= len(note) <= 500
                        or PRIVATE.search(text) or PRIVATE.search(note)
                        or reply.get("language") != "ru"
                        or reply.get("style") != "neutral"
                        or reply.get("audiences") != ["all_ai_bots"]
                        or reply.get("context") not in CONTEXTS
                        or reply.get("read_only") is not True
                        or not isinstance(reply.get("avoid"), str) or not reply["avoid"].strip()
                        or norm(text) in known_texts or norm(note) in seen_notes):
                    raise ValueError(f"duplicate, unsafe or unscoped salvaged reply: {rid}")
                seen_ids.add(rid)
                known_texts.add(norm(text))
                seen_notes.add(norm(note))
                replies.append(reply)
            self._by_intent[ident] = tuple(replies)
        if set(self._by_intent) != set(by_id) or len(seen_ids) != 96 or len(known_texts) != 312:
            raise ValueError("incomplete salvaged coverage")
        expected = {"stage_id": "T306", "processed_intents": 24,
                    "baseline_registered": 216, "salvaged_from_prior_draft": 96,
                    "finished_100": 0, "partial_intents": 24, "remaining_total": 2088,
                    "previously_authored_not_new": True, "salvaged_in_stage": 96,
                    "already_registered_identical": 120}
        if stage.get("checkpoint") != expected:
            raise ValueError("inconsistent salvage checkpoint")
        self.checkpoint = expected
        self.cache_identity = (manifest["knowledge_version"], hashes[SOURCE], blob_sha(file.read_bytes()))

    def select(self, intent_id: str, *, approved_reply_ids: frozenset[str],
               audience: str, context: str, addressed: bool = False,
               local_permission: bool = False, recent_ids: tuple[str, ...] = ()):
        if (not addressed or not local_permission or audience != "all_ai_bots"
                or context not in CONTEXTS or not isinstance(approved_reply_ids, frozenset)
                or not approved_reply_ids or not isinstance(recent_ids, tuple)):
            return None
        for reply in self._by_intent.get(intent_id, ()):
            if (reply["id"] in approved_reply_ids and reply["context"] == context
                    and reply["id"] not in recent_ids):
                return StagedSelection(
                    id=reply["id"], text=reply["text"], intent_id=intent_id,
                    context_note=reply["context_note"], stage_path=STAGE)
        return None
