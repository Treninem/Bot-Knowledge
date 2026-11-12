"""T303A11: validate 181 new Russian contextual replies in disjoint T301 partial sets.

Historical sources and all earlier overlays must pass T301 first. Staged replies
never grant authority, cause an action, or become a consumer-installed package.
"""
from pathlib import Path
import hashlib
import json
from scripts.context_overlay_t301 import ContextOverlayT301, OVERLAY as PARENT, HISTORY as ANCESTORS, TARGET_IDS as T301_COMPLETED, EXCEPTIONS as PREVIOUS_COMPLETED
from scripts.context_overlay_t271 import PARENTS, GUARDS, CONTEXTS, SECRET, norm, overlap, blob
from scripts.staged_context_selector import StagedSelection

OVERLAY = "staging/ru/context_overlay_t303a11.json"
HISTORY = ANCESTORS  # the full 85-intent layers; T299/T300/T301 are partial
BEFORE = {"recovery": 94, "choice": 92, "boundaries": 91}
EXCEPTIONS = PREVIOUS_COMPLETED | frozenset().union(*(frozenset(items) for items in T301_COMPLETED.values()))
TARGET_COUNTS = {"recovery": 6, "choice": 8, "boundaries": 9}
TARGET_IDS = {
    "recovery": (),
    "choice": (
        "bk_choice_trial_evidence", "bk_choice_fallback_plan",
        "bk_choice_shared_time", "bk_choice_warranty_limits",
        "bk_choice_offline_resilience", "bk_choice_metric_tradeoff",
        "bk_choice_patch_vs_cause", "bk_choice_no_fit",
    ),
    "boundaries": (
        "bk_conversation_reset_preference", "bk_conversation_repeat_after_fix",
        "bk_conversation_refuse_unasked_action", "bk_conversation_unknown_past",
        "bk_conversation_request_example_register", "bk_conversation_constructive_disagreement",
        "bk_conversation_joke_after_apology", "bk_conversation_dark_humor_safe",
        "bk_conversation_stop_provocation", "bk_conversation_silence_after_finish",
        "bk_conversation_privacy_public_example", "bk_conversation_unknown_interface",
        "bk_conversation_no_false_done",
    ),
}
EXPECTED = {
    "stage_id": "T303A11", "processed_intents": 21,
    "parent_staged_count": 3576, "added_in_current": 181,
    "total_staged_with_parent": 3757,
    "finished_100_on_T301_base": 69,
    "partial_intents_on_T301_base": 16,
    "remaining_total_on_T301_base": 136,
    "rejected": 0,
    "per_source": [
        {"source": "choice", "completed_now": 8, "added": 64},
        {"source": "boundaries", "completed_now": 13, "added": 117},
    ],
}

class ContextOverlayT303A11:
    def __init__(self, root: Path, path: str = OVERLAY):
        if path != OVERLAY:
            raise ValueError("unreviewed stage path")
        root = Path(root).resolve(strict=True)
        self.parent = ContextOverlayT301(root)
        parent_raw = (root / PARENT).read_bytes()
        stage_raw = (root / OVERLAY).read_bytes()
        stage = json.loads(stage_raw)
        manifest = json.loads((root / "manifest.json").read_bytes())
        registered = {p["path"]: p["sha256"] for p in manifest["packs"]}
        if (stage.get("schema_version") != 1
                or stage.get("stage_type") != "supplemental_context_delta_overlay"
                or stage.get("consumer_registered") is not False
                or stage.get("language") != "ru"
                or stage.get("audiences") != ["all_ai_bots"]
                or stage.get("constraints") != GUARDS
                or stage.get("parent_delta_path") != PARENT
                or stage.get("parent_delta_blob_sha") != blob(parent_raw)
                or OVERLAY in registered):
            raise ValueError("untrusted stage provenance, scope or consumer registration")

        # T299, T300 and T301 are validated partial overlays (14/15/16 intents),
        # not full 85-intent inventories.
        partial_layers = []
        for path, expected_count in (
            ("staging/ru/context_overlay_t299.json", 14),
            ("staging/ru/context_overlay_t300.json", 15),
            (PARENT, 16),
        ):
            source_entries = json.loads((root / path).read_bytes())["entries"]
            indexed = {e["intent_id"]: e for e in source_entries}
            if len(source_entries) != expected_count or len(indexed) != expected_count:
                raise ValueError("parent partial overlay inventory changed")
            partial_layers.append(indexed)
        history = []
        for fname in HISTORY:
            rows = json.loads((root / fname).read_bytes())["entries"]
            by_id = {e["intent_id"]: e for e in rows}
            if len(rows) != 85 or len(by_id) != 85:
                raise ValueError("historical stage inventory changed")
            history.append(by_id)
        prior = {}
        all_texts, all_ids, all_notes = set(), set(), {}
        for group, (pool, expected_n, _, _) in PARENTS.items():
            pool_data = json.loads((root / pool).read_bytes())
            source = pool_data["source_pack"]
            if source not in registered:
                raise ValueError("source pack not in manifest")
            source_bytes = (root / source).read_bytes()
            if hashlib.sha256(source_bytes).hexdigest() != registered[source]:
                raise ValueError("registered source content checksum mismatch")
            records = json.loads(source_bytes)["records"]
            pooled = {e["intent_id"]: e for e in pool_data["entries"]}
            if len(records) != expected_n or len(pooled) != expected_n:
                raise ValueError("source inventory mismatch")
            for rec in records:
                ident = rec["id"]
                if ident in prior or ident not in pooled or any(ident not in h for h in history):
                    raise ValueError("invalid historical intent identity")
                text = [rec["answer"], *rec.get("variants", [])]
                notes = set()
                for item in (pooled[ident], *(h[ident] for h in history),
                             *(h[ident] for h in partial_layers if ident in h)):
                    for reply in item["replies"]:
                        rid = reply["id"]
                        if rid in all_ids:
                            raise ValueError("duplicate historical reply ID")
                        all_ids.add(rid)
                        text.append(reply["text"])
                        note = norm(reply["context_note"])
                        if not note or note in notes:
                            raise ValueError("repeated or missing historical context")
                        notes.add(note)
                expected_before = 100 if ident in EXCEPTIONS else BEFORE[group]
                if len(text) != expected_before:
                    raise ValueError(f"stale count in {ident}: {len(text)}")
                for txt in text:
                    key = norm(txt)
                    if not key or key in all_texts:
                        raise ValueError("historical normalized duplicate")
                    all_texts.add(key)
                prior[ident] = (rec["question"], pool, group, text)
                all_notes[ident] = notes

        self._rows = {}
        group_added = {g: 0 for g in TARGET_IDS}
        for entry in stage.get("entries", []):
            ident = entry.get("intent_id")
            if ident not in prior or ident in self._rows:
                raise ValueError("unknown or repeated canonical intent")
            question, pool, group, old = prior[ident]
            replies = entry.get("replies")
            if (ident not in TARGET_IDS[group] or entry.get("question") != question
                    or entry.get("source_stage") != pool
                    or entry.get("expected_total_before") != BEFORE[group]
                    or not isinstance(replies, list)
                    or len(replies) != TARGET_COUNTS[group]
                    or len(old) + len(replies) != 100):
                raise ValueError("stale, misplaced or incomplete 100/100 intent")
            for i, reply in enumerate(replies, 1):
                rid, txt, note = reply.get("id"), reply.get("text"), reply.get("context_note")
                if (rid != f"{ident}_t303a11_{i:02d}" or rid in all_ids
                        or not isinstance(txt, str) or not 1 <= len(txt) <= 1600
                        or SECRET.search(txt) or not norm(txt) or norm(txt) in all_texts
                        or not isinstance(note, str) or not norm(note)
                        or norm(note) in all_notes[ident]
                        or reply.get("language") != "ru" or reply.get("style") != "neutral"
                        or reply.get("audiences") != ["all_ai_bots"]
                        or reply.get("read_only") is not True
                        or reply.get("context") not in CONTEXTS
                        or not isinstance(reply.get("avoid"), str)
                        or not reply["avoid"].strip()
                        or max((overlap(txt, old_txt) for old_txt in old), default=0) >= .78):
                    raise ValueError(f"unsafe, stale or redundant reply: {ident} #{i}")
                all_ids.add(rid)
                all_texts.add(norm(txt))
                all_notes[ident].add(norm(note))
                old.append(txt)
            group_added[group] += len(replies)
            self._rows[ident] = tuple(replies)
        if (set(self._rows) != set().union(*map(set, TARGET_IDS.values()))
                or stage.get("checkpoint") != EXPECTED
                or group_added != {"recovery": 0, "choice": 64, "boundaries": 117}):
            raise ValueError("false progress checkpoint")
        self.checkpoint = EXPECTED
        self.cache_identity = (manifest["knowledge_version"], blob(parent_raw), blob(stage_raw))

    def select(self, intent_id: str, *, approved_reply_ids: frozenset[str],
               audience: str, context: str, addressed: bool = False,
               local_permission: bool = False, recent_ids: tuple[str, ...] = ()) -> StagedSelection | None:
        if (audience != "all_ai_bots" or not addressed or not local_permission
                or context not in CONTEXTS or not isinstance(approved_reply_ids, frozenset)
                or not approved_reply_ids or not isinstance(recent_ids, tuple)):
            return None
        for r in self._rows.get(intent_id, ()):
            if (r["id"] in approved_reply_ids and r["id"] not in recent_ids
                    and r["context"] == context):
                return StagedSelection(id=r["id"], text=r["text"],
                                       intent_id=intent_id, context_note=r["context_note"],
                                       stage_path=OVERLAY)
        return None
