"""T293 independent, fail-closed continuation of 85 contextual Russian QA intents.

The staged candidates are neither registered packs nor permissions for actions.
Requires full prior T286 chain and byte-identical source catalogues.
"""
import json
import hashlib
from pathlib import Path
from scripts.context_overlay_t292 import ContextOverlayT292
from scripts.context_overlay_t271 import PARENTS, GUARDS, CONTEXTS, SECRET, norm, overlap, blob
from scripts.staged_context_selector import StagedSelection

OVERLAY = "staging/ru/context_overlay_t293.json"
PARENT = "staging/ru/context_overlay_t292.json"
LAYERS = (
    "staging/ru/context_delta_t241.json",
    "staging/ru/context_overlay_t271.json",
    "staging/ru/context_overlay_t272.json",
    "staging/ru/context_overlay_t275.json",
    "staging/ru/context_overlay_t277.json",
    "staging/ru/context_overlay_t279.json",
    "staging/ru/context_overlay_t281.json",
    "staging/ru/context_overlay_t283.json",
    "staging/ru/context_overlay_t286.json",
    "staging/ru/context_overlay_t288.json",
    PARENT,
)
EXPECTED = {"recovery": (24,84), "choice": (30,82), "boundaries": (31,81)}

class ContextOverlayT293:
    def __init__(self, root: Path, path: str = OVERLAY):
        if path != OVERLAY:
            raise ValueError("unreviewed stage path")
        root = Path(root).resolve(strict=True)
        self.parent = ContextOverlayT292(root)
        parent_bytes = (root / PARENT).read_bytes()
        data_bytes = (root / path).read_bytes()
        data = json.loads(data_bytes)
        manifest = json.loads((root / "manifest.json").read_text("utf-8"))
        registered = {p["path"]:p["sha256"] for p in manifest["packs"]}
        if (data.get("schema_version") != 1 or
            data.get("stage_type") != "supplemental_context_delta_overlay" or
            data.get("consumer_registered") is not False or
            data.get("language") != "ru" or
            data.get("audiences") != ["all_ai_bots"] or
            data.get("constraints") != GUARDS or
            data.get("parent_delta_path") != PARENT or
            data.get("parent_delta_blob_sha") != blob(parent_bytes) or
            OVERLAY in registered):
            raise ValueError("invalid source hash, audience or untrusted parent")
        historical = []
        for filename in LAYERS:
            rows = json.loads((root / filename).read_text("utf-8"))["entries"]
            by_id = {row["intent_id"]:row for row in rows}
            if len(rows) != 85 or len(by_id) != 85:
                raise ValueError("stale historical inventory")
            historical.append(by_id)
        known = {}
        global_texts, old_ids = set(), set()
        oldnotes = {}
        for group, (stage_path, expected_count, _, _) in PARENTS.items():
            initial_stage = json.loads((root / stage_path).read_text("utf-8"))
            source_path = initial_stage["source_pack"]
            if source_path not in registered:
                raise ValueError("unregistered source pack")
            source_bytes = (root / source_path).read_bytes()
            if hashlib.sha256(source_bytes).hexdigest() != registered[source_path]:
                raise ValueError("registered source content hash changed")
            pack = json.loads(source_bytes)
            base = {e["intent_id"]:e for e in initial_stage["entries"]}
            n, before = EXPECTED[group]
            if len(pack["records"]) != n or expected_count != n:
                raise ValueError("source count mismatch")
            for record in pack["records"]:
                ident = record["id"]
                if ident in known or ident not in base or any(ident not in h for h in historical):
                    raise ValueError("unknown or repeated canonical intent")
                texts = [record["answer"], *record["variants"]]
                notes = set()
                for stage_entry in (base[ident], *(h[ident] for h in historical)):
                    for reply in stage_entry["replies"]:
                        if reply["id"] in old_ids:
                            raise ValueError("reused historical ID")
                        old_ids.add(reply["id"])
                        texts.append(reply["text"])
                        notes.add(norm(reply["context_note"]))
                if len(texts) != before:
                    raise ValueError("wrong historical per-intent total")
                for txt in texts:
                    key = norm(txt)
                    if key in global_texts:
                        raise ValueError("duplicate historical text")
                    global_texts.add(key)
                known[ident] = (record["question"],stage_path,before,group,texts)
                oldnotes[ident] = notes
        if len(known) != 85:
            raise ValueError("incomplete canonical inventory")
        self._rows = {}
        for entry in data.get("entries", []):
            ident = entry.get("intent_id")
            if ident not in known or ident in self._rows:
                raise ValueError("unknown or duplicate new intent")
            question, source_stage, before, group, texts = known[ident]
            replies = entry.get("replies")
            if (entry.get("question") != question or
                entry.get("source_stage") != source_stage or
                entry.get("expected_total_before") != before or
                not isinstance(replies, list) or len(replies) != 1):
                raise ValueError("stale source or wrong addition count")
            reply = replies[0]
            rid, txt, note = reply.get("id"), reply.get("text"), reply.get("context_note")
            if (rid != f"{ident}_t293_01" or rid in old_ids or
                not isinstance(txt,str) or not 1 <= len(txt) <= 1600 or
                SECRET.search(txt) or not norm(txt) or norm(txt) in global_texts or
                not isinstance(note,str) or not norm(note) or
                norm(note) in oldnotes[ident] or
                reply.get("language") != "ru" or reply.get("style") != "neutral" or
                reply.get("audiences") != ["all_ai_bots"] or
                reply.get("read_only") is not True or
                reply.get("context") not in CONTEXTS or
                not isinstance(reply.get("avoid"),str) or not reply["avoid"].strip() or
                max((overlap(txt,past) for past in texts),default=0) >= .78):
                raise ValueError("unsafe or near-duplicate response")
            global_texts.add(norm(txt))
            old_ids.add(rid)
            texts.append(txt)
            oldnotes[ident].add(norm(note))
            self._rows[ident] = tuple(replies)
        cp = data.get("checkpoint",{})
        expected = dict(stage_id="T293", processed_intents=85,
                        parent_staged_count=2380, added_in_current=85,
                        total_staged_with_parent=2465, remaining_total=1428,
                        partial_intents=85, finished_100=0, rejected=0)
        if len(self._rows) != 85 or any(cp.get(k) != v for k,v in expected.items()):
            raise ValueError("unverified progress checkpoint")
        for group,(n,before) in EXPECTED.items():
            actual = sum(known[id][3] == group for id in self._rows)
            point = next((p for p in cp.get("per_source",[]) if p.get("source")==group),None)
            if actual != n or point is None or any((
                point.get("intents") != n, point.get("before") != before,
                point.get("after") != before+1,
                point.get("remaining_per_intent") != 99-before
            )):
                raise ValueError("false group progress")
        self.checkpoint = cp
        self.cache_identity = (manifest["knowledge_version"],blob(parent_bytes),blob(data_bytes))

    def select(self, intent_id: str, *, approved_reply_ids: frozenset[str],
               audience: str, context: str, addressed: bool = False,
               local_permission: bool = False, recent_ids: tuple[str,...]=()) -> StagedSelection | None:
        if (audience != "all_ai_bots" or not addressed or not local_permission or
            context not in CONTEXTS or not isinstance(approved_reply_ids,frozenset) or
            not approved_reply_ids or not isinstance(recent_ids,tuple)):
            return None
        for item in self._rows.get(intent_id,()):
            if (item["id"] in approved_reply_ids and
                item["id"] not in recent_ids and item["context"]==context):
                return StagedSelection(id=item["id"],text=item["text"],intent_id=intent_id,
                    context_note=item["context_note"],stage_path=OVERLAY)
        return None
