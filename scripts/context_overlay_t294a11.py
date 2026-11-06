"""T294A11: 170 opt-in, read-only RU responses on 85 existing contextual intents.

No new registered packages, side effects, memory, enforcement or consumer wiring.
The complete prior chain is revalidated from immutable checked-out sources.
"""
import hashlib
import json
from pathlib import Path

from scripts.context_overlay_t293 import ContextOverlayT293, OVERLAY as PARENT, LAYERS, EXPECTED
from scripts.context_overlay_t271 import PARENTS, GUARDS, CONTEXTS, SECRET, norm, overlap, blob
from scripts.staged_context_selector import StagedSelection

OVERLAY = "staging/ru/context_overlay_t294a11.json"
COUNTS = {"recovery": (24, 85), "choice": (30, 83), "boundaries": (31, 82)}
CARRY = (24 * 85 + 30 * 83 + 31 * 82)
PREVIOUS_STAGE_COUNT = 2465
TOTAL_AFTER = 24 * 87 + 30 * 85 + 31 * 84


class ContextOverlayT294A11:
    def __init__(self, root: Path, path: str = OVERLAY):
        if path != OVERLAY:
            raise ValueError("unreviewed stage path")
        root = Path(root).resolve(strict=True)
        self.parent = ContextOverlayT293(root)  # checks source, manifest and every earlier layer
        parent_raw = (root / PARENT).read_bytes()
        raw = (root / OVERLAY).read_bytes()
        data = json.loads(raw)
        manifest = json.loads((root / "manifest.json").read_bytes())
        registered = {p["path"]: p["sha256"] for p in manifest["packs"]}
        if (data.get("schema_version") != 1
                or data.get("stage_type") != "supplemental_context_delta_overlay"
                or data.get("consumer_registered") is not False
                or data.get("language") != "ru"
                or data.get("audiences") != ["all_ai_bots"]
                or data.get("constraints") != GUARDS
                or data.get("parent_delta_path") != PARENT
                or data.get("parent_delta_blob_sha") != blob(parent_raw)
                or OVERLAY in registered):
            raise ValueError("invalid metadata or stale parent SHA")

        historical = []
        for filename in (*LAYERS, PARENT):
            entries = json.loads((root / filename).read_bytes())["entries"]
            by_id = {e["intent_id"]: e for e in entries}
            if len(entries) != 85 or len(by_id) != 85:
                raise ValueError("broken historical intent inventory")
            historical.append(by_id)

        known, used_ids, seen_texts, oldnotes = {}, set(), set(), {}
        for group, (source_stage, n, _, _) in PARENTS.items():
            source = json.loads((root / source_stage).read_bytes())
            src_path = source["source_pack"]
            if src_path not in registered:
                raise ValueError("unregistered source")
            src_bytes = (root / src_path).read_bytes()
            if hashlib.sha256(src_bytes).hexdigest() != registered[src_path]:
                raise ValueError("source content differs from manifest SHA256")
            pack = json.loads(src_bytes)
            base = {e["intent_id"]: e for e in source["entries"]}
            if len(pack["records"]) != n or len(base) != n:
                raise ValueError("incorrect source inventory")
            for record in pack["records"]:
                ident = record["id"]
                if ident in known or ident not in base or any(ident not in h for h in historical):
                    raise ValueError("unknown/repeated canonical intent")
                texts = [record["answer"], *record["variants"]]
                notes = set()
                for stage_record in (base[ident], *(h[ident] for h in historical)):
                    for reply in stage_record["replies"]:
                        if reply["id"] in used_ids:
                            raise ValueError("duplicated historical reply ID")
                        used_ids.add(reply["id"])
                        texts.append(reply["text"])
                        notes.add(norm(reply["context_note"]))
                if len(texts) != COUNTS[group][1]:
                    raise ValueError("historical per-intent count does not match checkpoint")
                for text in texts:
                    normalized = norm(text)
                    if not normalized or normalized in seen_texts:
                        raise ValueError("normalized duplicate in history")
                    seen_texts.add(normalized)
                known[ident] = (record["question"], source_stage, group, texts)
                oldnotes[ident] = notes
        if len(known) != 85:
            raise ValueError("missing canonical intents")

        self._rows = {}
        for entry in data.get("entries", []):
            ident = entry.get("intent_id")
            if ident not in known or ident in self._rows:
                raise ValueError("new response has unknown or duplicate intent")
            question, source_stage, group, prior = known[ident]
            replies = entry.get("replies")
            if (entry.get("question") != question
                    or entry.get("source_stage") != source_stage
                    or entry.get("expected_total_before") != COUNTS[group][1]
                    or not isinstance(replies, list) or len(replies) != 2):
                raise ValueError("wrong source mapping or delta size")
            for index, reply in enumerate(replies, 1):
                rid, txt, note = reply.get("id"), reply.get("text"), reply.get("context_note")
                if (rid != f"{ident}_t294a11_{index:02d}" or rid in used_ids
                        or not isinstance(txt, str) or not 1 <= len(txt) <= 1600
                        or SECRET.search(txt) or not norm(txt) or norm(txt) in seen_texts
                        or not isinstance(note, str) or not norm(note) or norm(note) in oldnotes[ident]
                        or reply.get("language") != "ru" or reply.get("style") != "neutral"
                        or reply.get("audiences") != ["all_ai_bots"]
                        or reply.get("read_only") is not True
                        or reply.get("context") not in CONTEXTS
                        or not isinstance(reply.get("avoid"), str) or not reply["avoid"].strip()
                        or max((overlap(txt, old) for old in prior), default=0) >= 0.78):
                    raise ValueError(f"unsafe or duplicate response: {ident} #{index}")
                used_ids.add(rid)
                seen_texts.add(norm(txt))
                prior.append(txt)
                oldnotes[ident].add(norm(note))
            self._rows[ident] = tuple(replies)

        cp = data.get("checkpoint", {})
        expected = {
            "stage_id": "T294A11", "processed_intents": 85,
            "parent_staged_count": PREVIOUS_STAGE_COUNT, "added_in_current": 170,
            "total_staged_with_parent": PREVIOUS_STAGE_COUNT + 170,
            "remaining_total": 8500 - TOTAL_AFTER,
            "partial_intents": 85, "finished_100": 0, "rejected": 0,
        }
        if len(self._rows) != 85 or any(cp.get(k) != v for k, v in expected.items()):
            raise ValueError("checkpoint/count falsified")
        for group, (n, before) in COUNTS.items():
            actual = sum(known[ident][2] == group for ident in self._rows)
            points = [p for p in cp.get("per_source", []) if p.get("source") == group]
            if (actual != n or len(points) != 1
                    or points[0] != {"source": group, "intents": n, "before": before,
                                     "after": before+2, "remaining_per_intent": 98-before}):
                raise ValueError("per-group checkpoint mismatch")
        self.checkpoint = cp
        self.cache_identity = (manifest["knowledge_version"], blob(parent_raw), blob(raw))

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
