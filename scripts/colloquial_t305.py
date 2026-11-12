"""T305: fail-closed read-only contextual continuation of registered T304 RU QA.

Not a published consumer pack, action router, moderator, learner, or live integration.
The caller independently confirms an explicit reply ID, matching context, and permission.
"""
from __future__ import annotations

import hashlib
import json
import re
import unicodedata
from pathlib import Path
from scripts.staged_context_selector import StagedSelection

ROOT = Path(__file__).resolve().parents[1]
STAGE = "staging/ru/colloquial_t305_context_pool.json"
SOURCE = "packs/ru/colloquial_ru_pragmatics_qa.json"
GUARDS = {"read_only": True, "requires_direct_address": True, "no_personal_data": True}
CONTEXTS = frozenset({"direct", "private", "group_addressed"})
PRIVATE = re.compile(r"(?i)(ghp_[a-z0-9]{12,}|sk-[a-z0-9]{12,}|bot_token|chat_id|user_id|https://t\.me/|@[a-z0-9_]{4,}|[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,})")


def norm(text: str) -> str:
    text = unicodedata.normalize("NFKC", text).casefold().replace("ё", "е")
    return " ".join("".join(
        " " if unicodedata.category(char)[0] in {"P", "S"} else char for char in text
    ).split())


def blob_sha(payload: bytes) -> str:
    return hashlib.sha1(b"blob " + str(len(payload)).encode("ascii") + b"\0" + payload).hexdigest()


class ColloquialT305:
    def __init__(self, root: Path = ROOT, stage_path: str = STAGE):
        if stage_path != STAGE:
            raise ValueError("unreviewed staging path")
        root = Path(root).resolve(strict=True)
        stage_file = root / STAGE
        if stage_file.is_symlink() or not stage_file.resolve().is_relative_to(root):
            raise ValueError("unsafe staging path")
        stage = json.loads(stage_file.read_text("utf-8"))
        manifest = json.loads((root / "manifest.json").read_text("utf-8"))
        references = {item["path"]: item["sha256"] for item in manifest["packs"]}
        registered = (root / SOURCE).read_bytes()
        if (SOURCE not in references or hashlib.sha256(registered).hexdigest() != references[SOURCE]
                or stage.get("source_pack") != SOURCE
                or stage.get("source_pack_manifest_sha256") != references[SOURCE]
                or stage.get("source_pack_blob_sha") != blob_sha(registered)):
            raise ValueError("source pack SHA, blob or manifest mismatch")
        if (STAGE in references
                or stage.get("schema_version") != 1
                or stage.get("stage_type") != "supplemental_contextual_reply_pool"
                or stage.get("consumer_registered") is not False
                or stage.get("language") != "ru"
                or stage.get("audiences") != ["all_ai_bots"]
                or stage.get("constraints") != GUARDS):
            raise ValueError("unregistered staging scope violated")
        registered_rows = json.loads(registered)["records"]
        originals = {row["id"]: row for row in registered_rows}
        if len(originals) != 22 or len(registered_rows) != 22:
            raise ValueError("unexpected registered canonical inventory")
        seen_ids, seen_texts, seen_notes = set(), set(), set()
        for row in registered_rows:
            for text in [row["answer"], *row["variants"]]:
                normalized = norm(text)
                if normalized in seen_texts:
                    raise ValueError("duplicate registered text")
                seen_texts.add(normalized)
        self._by_intent = {}
        for entry in stage.get("entries", []):
            intent = entry.get("intent_id")
            row = originals.get(intent)
            if (row is None or intent in self._by_intent or entry.get("question") != row["question"]
                    or entry.get("registered_reply_count") != 9
                    or entry.get("staged_reply_count") != 5
                    or not isinstance(entry.get("replies"), list)
                    or len(entry["replies"]) != 5):
                raise ValueError("stale/duplicate canonical intent or invalid inventory")
            checked = []
            for number, reply in enumerate(entry["replies"], start=1):
                rid, text, note = reply.get("id"), reply.get("text"), reply.get("context_note")
                if (rid != f"{intent}_t305_{number:02d}" or rid in seen_ids
                        or not isinstance(text, str) or not text.strip() or len(text) > 1600
                        or not isinstance(note, str) or not note.strip() or len(note) > 500
                        or PRIVATE.search(text) or PRIVATE.search(note)
                        or reply.get("language") != "ru"
                        or reply.get("style") != "neutral"
                        or reply.get("audiences") != ["all_ai_bots"]
                        or reply.get("context") not in CONTEXTS
                        or reply.get("read_only") is not True
                        or not isinstance(reply.get("avoid"), str) or not reply["avoid"].strip()
                        or norm(text) in seen_texts or norm(note) in seen_notes):
                    raise ValueError(f"unreviewed, repeated, unsafe or unscoped response {rid}")
                seen_ids.add(rid)
                seen_texts.add(norm(text))
                seen_notes.add(norm(note))
                checked.append(reply)
            self._by_intent[intent] = tuple(checked)
        if set(self._by_intent) != set(originals):
            raise ValueError("partial canonical intent coverage")
        checkpoint = stage.get("checkpoint")
        expected = {"stage_id": "T305", "processed_intents": 22, "registered_count": 198,
                    "added_candidates": 110, "finished_100": 0, "partial_intents": 22,
                    "remaining_total": 1892, "rejected": 0}
        if checkpoint != expected or len(seen_ids) != 110 or len(seen_texts) != 308:
            raise ValueError("checkpoint or actual count mismatch")
        self.checkpoint = checkpoint
        self.cache_identity = (manifest["knowledge_version"], references[SOURCE],
                               blob_sha(stage_file.read_bytes()))

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
                return StagedSelection(id=reply["id"], text=reply["text"],
                                       intent_id=intent_id, context_note=reply["context_note"],
                                       stage_path=STAGE)
        return None
