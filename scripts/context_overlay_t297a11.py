"""T297A11 continues 85 existing scoped RU intents with 170 more staged replies.

No manifest or deployed-consumer change. Fail closed on missing or altered parent.
"""
import hashlib
import json
from pathlib import Path

from scripts.context_overlay_t296a11 import ContextOverlayT296A11, OVERLAY as PARENT
from scripts.context_overlay_t295a11 import OVERLAY as T295
from scripts.context_overlay_t294a11 import OVERLAY as T294
from scripts.context_overlay_t293 import LAYERS, OVERLAY as T293
from scripts.context_overlay_t271 import PARENTS, GUARDS, CONTEXTS, SECRET, norm, overlap, blob
from scripts.staged_context_selector import StagedSelection

OVERLAY = "staging/ru/context_overlay_t297a11.json"
COUNTS = {"recovery": (24, 91), "choice": (30, 89), "boundaries": (31, 88)}
FINAL_COUNT = 24 * 93 + 30 * 91 + 31 * 90
BEFORE_STAGED = 2975


class ContextOverlayT297A11:
    def __init__(self, root: Path, path: str = OVERLAY):
        if path != OVERLAY:
            raise ValueError("unreviewed stage path")
        root = Path(root).resolve(strict=True)
        self.parent = ContextOverlayT296A11(root)
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
            raise ValueError("untrusted stage or stale source parent")
        history = []
        for filename in (*LAYERS, T293, T294, T295, PARENT):
            entries = json.loads((root / filename).read_bytes())["entries"]
            indexed = {e["intent_id"]: e for e in entries}
            if len(entries) != 85 or len(indexed) != 85:
                raise ValueError("historical inventory changed")
            history.append(indexed)
        known, ids, seen_texts, seen_notes = {}, set(), set(), {}
        for group, (base_path, n, _, _) in PARENTS.items():
            base = json.loads((root / base_path).read_bytes())
            src_path = base["source_pack"]
            if src_path not in registered:
                raise ValueError("unregistered source pack")
            source_bytes = (root / src_path).read_bytes()
            if hashlib.sha256(source_bytes).hexdigest() != registered[src_path]:
                raise ValueError("registered source SHA256 changed")
            records = json.loads(source_bytes)["records"]
            base_rows = {e["intent_id"]: e for e in base["entries"]}
            if len(records) != n or len(base_rows) != n:
                raise ValueError("wrong base inventory")
            for record in records:
                ident = record["id"]
                if ident in known or ident not in base_rows or any(ident not in h for h in history):
                    raise ValueError("missing or repeated canonical intent")
                texts = [record["answer"], *record["variants"]]
                notes = set()
                for e in (base_rows[ident], *(layer[ident] for layer in history)):
                    for reply in e["replies"]:
                        if reply["id"] in ids:
                            raise ValueError("duplicate historical reply ID")
                        ids.add(reply["id"])
                        texts.append(reply["text"])
                        notes.add(norm(reply["context_note"]))
                if len(texts) != COUNTS[group][1]:
                    raise ValueError("stale historical reply counter")
                for txt in texts:
                    key = norm(txt)
                    if not key or key in seen_texts:
                        raise ValueError("normalized duplicate already in history")
                    seen_texts.add(key)
                known[ident] = (record["question"], base_path, group, texts)
                seen_notes[ident] = notes

        self._rows = {}
        for entry in stage.get("entries", []):
            ident = entry.get("intent_id")
            if ident not in known or ident in self._rows:
                raise ValueError("new intent mismatch or duplicate")
            question, base_path, group, old = known[ident]
            replies = entry.get("replies")
            if (entry.get("question") != question
                    or entry.get("source_stage") != base_path
                    or entry.get("expected_total_before") != COUNTS[group][1]
                    or not isinstance(replies, list) or len(replies) != 2):
                raise ValueError("new delta references stale data")
            for i, reply in enumerate(replies, 1):
                rid, txt, note = reply.get("id"), reply.get("text"), reply.get("context_note")
                if (rid != f"{ident}_t297a11_{i:02d}" or rid in ids
                        or not isinstance(txt, str) or not 1 <= len(txt) <= 1600
                        or SECRET.search(txt) or not norm(txt) or norm(txt) in seen_texts
                        or not isinstance(note, str) or not norm(note)
                        or norm(note) in seen_notes[ident]
                        or reply.get("language") != "ru" or reply.get("style") != "neutral"
                        or reply.get("audiences") != ["all_ai_bots"]
                        or reply.get("read_only") is not True
                        or reply.get("context") not in CONTEXTS
                        or not isinstance(reply.get("avoid"), str) or not reply["avoid"].strip()
                        or max((overlap(txt, other) for other in old), default=0) >= 0.78):
                    raise ValueError(f"unsafe or duplicate response: {ident} #{i}")
                ids.add(rid)
                seen_texts.add(norm(txt))
                old.append(txt)
                seen_notes[ident].add(norm(note))
            self._rows[ident] = tuple(replies)
        cp = stage.get("checkpoint", {})
        expected = {
            "stage_id": "T297A11", "processed_intents": 85,
            "parent_staged_count": BEFORE_STAGED, "added_in_current": 170,
            "total_staged_with_parent": BEFORE_STAGED + 170,
            "remaining_total": 8500 - FINAL_COUNT,
            "partial_intents": 85, "finished_100": 0, "rejected": 0,
        }
        if len(known) != 85 or len(self._rows) != 85 or any(cp.get(k) != v for k, v in expected.items()):
            raise ValueError("false checkpoint")
        for group, (n, before) in COUNTS.items():
            points = [p for p in cp.get("per_source", ()) if p.get("source") == group]
            if (len(points) != 1 or sum(known[k][2] == group for k in self._rows) != n
                    or points[0] != {"source": group, "intents": n, "before": before,
                                     "after": before + 2, "remaining_per_intent": 98 - before}):
                raise ValueError("group checkpoint disagrees with materialized replies")
        self.checkpoint = cp
        self.cache_identity = (manifest["knowledge_version"], blob(parent_bytes), blob(stage_bytes))

    def select(self, intent_id: str, *, approved_reply_ids: frozenset[str],
               audience: str, context: str, addressed: bool = False,
               local_permission: bool = False, recent_ids: tuple[str, ...] = ()) -> StagedSelection | None:
        if (audience != "all_ai_bots" or not addressed or not local_permission
                or context not in CONTEXTS or not isinstance(approved_reply_ids, frozenset)
                or not approved_reply_ids or not isinstance(recent_ids, tuple)):
            return None
        for r in self._rows.get(intent_id, ()):
            if r["id"] in approved_reply_ids and r["id"] not in recent_ids and r["context"] == context:
                return StagedSelection(id=r["id"], text=r["text"], intent_id=intent_id,
                                       context_note=r["context_note"], stage_path=OVERLAY)
        return None
