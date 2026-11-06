"""T298: verified, opt-in-only supplemental Russian dialogue reply layer.

The registered pack hashes and all parent stages must be intact.
No action, moderation permission, or consumer registration is granted.
"""
import hashlib
import json
from pathlib import Path

from scripts.context_overlay_t297a11 import ContextOverlayT297A11, OVERLAY as PARENT
from scripts.context_overlay_t293 import LAYERS, OVERLAY as T293
from scripts.context_overlay_t294a11 import OVERLAY as T294
from scripts.context_overlay_t295a11 import OVERLAY as T295
from scripts.context_overlay_t296a11 import OVERLAY as T296
from scripts.context_overlay_t271 import PARENTS, GUARDS, CONTEXTS, SECRET, norm, overlap, blob
from scripts.staged_context_selector import StagedSelection

OVERLAY = "staging/ru/context_overlay_t298.json"
STAGES = (*LAYERS, T293, T294, T295, T296, PARENT)
BEFORE = {"recovery": 93, "choice": 91, "boundaries": 90}
EXTRA_INTENTS = frozenset({"bk_recovery_no_steps", "bk_recovery_changed_symptom",
                            "bk_recovery_partial_success"})
EXPECTED_GROUPS = {
    "recovery": {"source": "recovery", "intents": 24, "before": 93,
                 "added": 42, "after_total": 2274, "completed": 3, "remaining_total": 126},
    "choice": {"source": "choice", "intents": 30, "before": 91,
               "added": 30, "after_total": 2760, "completed": 0, "remaining_total": 240},
    "boundaries": {"source": "boundaries", "intents": 31, "before": 90,
                   "added": 31, "after_total": 2821, "completed": 0, "remaining_total": 279},
}
EXPECTED_CHECKPOINT = {
    "stage_id": "T298", "processed_intents": 85, "parent_staged_count": 3145,
    "added_in_current": 103, "total_staged_with_parent": 3248,
    "remaining_total": 645, "partial_intents": 82, "finished_100": 3, "rejected": 0,
    "per_source": list(EXPECTED_GROUPS.values()),
}


class ContextOverlayT298:
    def __init__(self, root: Path, path: str = OVERLAY):
        if path != OVERLAY:
            raise ValueError("unreviewed stage path")
        root = Path(root).resolve(strict=True)
        self.parent = ContextOverlayT297A11(root)
        parent_bytes = (root / PARENT).read_bytes()
        stage_bytes = (root / OVERLAY).read_bytes()
        stage = json.loads(stage_bytes)
        manifest = json.loads((root / "manifest.json").read_bytes())
        registered = {p["path"]: p["sha256"] for p in manifest["packs"]}
        if (stage.get("schema_version") != 1
                or stage.get("stage_type") != "supplemental_context_delta_overlay"
                or stage.get("consumer_registered") is not False
                or stage.get("language") != "ru"
                or stage.get("audiences") != ["all_ai_bots"]
                or stage.get("constraints") != GUARDS
                or stage.get("parent_delta_path") != PARENT
                or stage.get("parent_delta_blob_sha") != blob(parent_bytes)
                or OVERLAY in registered):
            raise ValueError("untrusted stage, stale parent or wrong audience")
        previous = []
        for filename in STAGES:
            rows = json.loads((root / filename).read_bytes())["entries"]
            indexed = {e["intent_id"]: e for e in rows}
            if len(rows) != 85 or len(indexed) != 85:
                raise ValueError("historical inventory changed")
            previous.append(indexed)
        known = {}
        used_texts, used_ids = set(), set()
        used_notes = {}
        for group, (base_path, n, _, _) in PARENTS.items():
            base = json.loads((root / base_path).read_bytes())
            source_path = base["source_pack"]
            if source_path not in registered:
                raise ValueError("unregistered source")
            source_bytes = (root / source_path).read_bytes()
            if hashlib.sha256(source_bytes).hexdigest() != registered[source_path]:
                raise ValueError("registered source hash mismatch")
            records = json.loads(source_bytes)["records"]
            base_rows = {x["intent_id"]: x for x in base["entries"]}
            if len(records) != n or len(base_rows) != n:
                raise ValueError("stale source inventory")
            for rec in records:
                ident = rec["id"]
                if ident in known or ident not in base_rows or any(ident not in h for h in previous):
                    raise ValueError("missing or repeated canonical intent")
                old = [rec["answer"], *rec["variants"]]
                notes = set()
                for ent in (base_rows[ident], *(h[ident] for h in previous)):
                    for reply in ent["replies"]:
                        rid = reply["id"]
                        if rid in used_ids:
                            raise ValueError("historical duplicate ID")
                        used_ids.add(rid)
                        old.append(reply["text"])
                        notes.add(norm(reply["context_note"]))
                if len(old) != BEFORE[group]:
                    raise ValueError("stale historical reply count")
                for text in old:
                    key = norm(text)
                    if not key or key in used_texts:
                        raise ValueError("historical normalized duplicate")
                    used_texts.add(key)
                known[ident] = (rec["question"], base_path, group, old)
                used_notes[ident] = notes

        self._rows = {}
        group_added = {g: 0 for g in BEFORE}
        group_completed = {g: 0 for g in BEFORE}
        for entry in stage.get("entries", []):
            ident = entry.get("intent_id")
            if ident not in known or ident in self._rows:
                raise ValueError("unapproved or duplicate intent")
            question, base_path, group, old = known[ident]
            replies = entry.get("replies")
            expected_count = 7 if ident in EXTRA_INTENTS else 1
            if (entry.get("question") != question
                    or entry.get("source_stage") != base_path
                    or entry.get("expected_total_before") != BEFORE[group]
                    or not isinstance(replies, list) or len(replies) != expected_count):
                raise ValueError("stale source or incorrect reply count")
            if len(old) + len(replies) > 100:
                raise ValueError("over 100 replies in one intent")
            for j, reply in enumerate(replies, 1):
                rid, txt, note = reply.get("id"), reply.get("text"), reply.get("context_note")
                if (rid != f"{ident}_t298_{j:02d}" or rid in used_ids
                        or not isinstance(txt, str) or not 1 <= len(txt) <= 1600
                        or SECRET.search(txt) or not norm(txt) or norm(txt) in used_texts
                        or not isinstance(note, str) or not norm(note)
                        or norm(note) in used_notes[ident]
                        or reply.get("language") != "ru" or reply.get("style") != "neutral"
                        or reply.get("audiences") != ["all_ai_bots"]
                        or reply.get("read_only") is not True
                        or reply.get("context") not in CONTEXTS
                        or not isinstance(reply.get("avoid"), str) or not reply["avoid"].strip()
                        or max((overlap(txt, other) for other in old), default=0) >= 0.78):
                    raise ValueError(f"unsafe or redundant reply: {ident} #{j}")
                used_ids.add(rid)
                used_texts.add(norm(txt))
                used_notes[ident].add(norm(note))
                old.append(txt)
            group_added[group] += len(replies)
            group_completed[group] += len(old) == 100
            self._rows[ident] = tuple(replies)

        cp = stage.get("checkpoint")
        if (len(known) != 85 or len(self._rows) != 85
                or cp != EXPECTED_CHECKPOINT):
            raise ValueError("false progress checkpoint")
        for group, wanted in EXPECTED_GROUPS.items():
            n = sum(known[k][2] == group for k in self._rows)
            if (n != wanted["intents"] or group_added[group] != wanted["added"]
                    or group_completed[group] != wanted["completed"]):
                raise ValueError("group inventory disagrees with checkpoint")
        self.checkpoint = cp
        self.cache_identity = (manifest["knowledge_version"], blob(parent_bytes), blob(stage_bytes))

    def select(self, intent_id: str, *, approved_reply_ids: frozenset[str],
               audience: str, context: str, addressed: bool = False,
               local_permission: bool = False, recent_ids: tuple[str, ...] = ()) -> StagedSelection | None:
        if (audience != "all_ai_bots" or not addressed or not local_permission
                or context not in CONTEXTS or not isinstance(approved_reply_ids, frozenset)
                or not approved_reply_ids or not isinstance(recent_ids, tuple)):
            return None
        for reply in self._rows.get(intent_id, ()):
            if (reply["id"] in approved_reply_ids and reply["id"] not in recent_ids
                    and reply["context"] == context):
                return StagedSelection(id=reply["id"], text=reply["text"],
                                       intent_id=intent_id, context_note=reply["context_note"],
                                       stage_path=OVERLAY)
        return None
