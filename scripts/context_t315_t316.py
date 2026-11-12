"""T315/T316 contextual RU stages: verified lineage, explicit opt-in only.

These pools are deliberately NOT manifest-registered, distributed, executed or
automatically routed to consumers. They provide passive language examples.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

from scripts.colloquial_t305 import ROOT, norm, blob_sha, PRIVATE
from scripts.context_t313_t314 import Stage as ParentStage
from scripts.context_t309_t310 import _read, GUARDS, CONTEXTS, FIELDS
from scripts.staged_context_selector import StagedSelection

STAGES = {
    "T315": {
        "source": "packs/ru/colloquial_ru_pragmatics_qa.json",
        "previous": "staging/ru/colloquial_t313_context_pool.json",
        "earlier": (
            "staging/ru/colloquial_t305_context_pool.json",
            "staging/ru/colloquial_t307_context_pool.json",
            "staging/ru/colloquial_t309_context_pool.json",
            "staging/ru/colloquial_t311_context_pool.json",
        ),
        "stage": "staging/ru/colloquial_t315_context_pool.json",
        "parent": "T313",
        "intents": 22,
        "prior": 17,
        "remaining": 1562,
    },
    "T316": {
        "source": "packs/ru/practical_recovery_qa.json",
        "previous": "staging/ru/practical_t314_context_pool.json",
        "earlier": (
            "staging/ru/practical_t306_salvage.json",
            "staging/ru/practical_t308_context_pool.json",
            "staging/ru/practical_t310_context_pool.json",
            "staging/ru/practical_t312_context_pool.json",
        ),
        "stage": "staging/ru/practical_t316_context_pool.json",
        "parent": "T314",
        "intents": 24,
        "prior": 16,
        "remaining": 1728,
    },
}

def _keys(root: Path, cfg: dict, records: list[dict]):
    ids, texts, notes = set(), set(), set()
    for row in records:
        if len(row.get("variants", ())) != 8:
            raise ValueError("registered qa.v1 baseline changed")
        for phrase in (row["answer"], *row["variants"]):
            key = norm(phrase)
            if not key or key in texts:
                raise ValueError("registered text duplicate")
            texts.add(key)
    for path in (*cfg["earlier"], cfg["previous"]):
        for entry in json.loads(_read(root, path))["entries"]:
            for item in entry["replies"]:
                ident, phrase, note = item["id"], norm(item["text"]), norm(item["context_note"])
                if ident in ids or phrase in texts or note in notes or not note:
                    raise ValueError("history is not unique")
                ids.add(ident)
                texts.add(phrase)
                notes.add(note)
    if len(ids) != cfg["intents"] * cfg["prior"]:
        raise ValueError("previous staged reply total changed")
    return ids, texts, notes

class Stage:
    def __init__(self, label: str, root: Path = ROOT):
        if label not in STAGES:
            raise ValueError("unknown stage")
        root = Path(root).resolve(strict=True)
        cfg = STAGES[label]
        ParentStage(cfg["parent"], root)
        manifest = json.loads(_read(root, "manifest.json"))
        indexed = {p["path"]: p["sha256"] for p in manifest["packs"]}
        source_bytes = _read(root, cfg["source"])
        parent_bytes = _read(root, cfg["previous"])
        stage_bytes = _read(root, cfg["stage"])
        source = json.loads(source_bytes)
        content = json.loads(stage_bytes)
        canonical = {row["id"]: row for row in source["records"]}
        expected = {
            "stage_id": label,
            "processed_intents": cfg["intents"],
            "baseline_registered": 9 * cfg["intents"],
            "baseline_staged": cfg["prior"] * cfg["intents"],
            "added_candidates": 3 * cfg["intents"],
            "finished_100": 0,
            "partial_intents": cfg["intents"],
            "remaining_total": cfg["remaining"],
            "rejected": 0,
        }
        if (len(canonical) != cfg["intents"] or len(source["records"]) != cfg["intents"]
                or cfg["stage"] in indexed
                or indexed.get(cfg["source"]) != hashlib.sha256(source_bytes).hexdigest()
                or content.get("source_pack") != cfg["source"]
                or content.get("source_pack_manifest_sha256") != indexed[cfg["source"]]
                or content.get("source_pack_blob_sha") != blob_sha(source_bytes)
                or content.get("previous_stage") != cfg["previous"]
                or content.get("previous_stage_blob_sha") != blob_sha(parent_bytes)
                or content.get("schema_version") != 1
                or content.get("stage_type") != "supplemental_contextual_reply_pool"
                or content.get("consumer_registered") is not False
                or content.get("language") != "ru"
                or content.get("audiences") != ["all_ai_bots"]
                or content.get("constraints") != GUARDS
                or content.get("checkpoint") != expected):
            raise ValueError("unapproved stage, manifest or parent SHA")
        ids, texts, notes = _keys(root, cfg, source["records"])
        entries = content.get("entries")
        if not isinstance(entries, list) or len(entries) != cfg["intents"]:
            raise ValueError("missing canonical rows")
        self.by_intent = {}
        for entry in entries:
            ident = entry.get("intent_id")
            replies = entry.get("replies")
            if (ident not in canonical or ident in self.by_intent
                    or entry.get("question") != canonical[ident]["question"]
                    or entry.get("baseline_registered") != 9
                    or entry.get("previous_staged") != cfg["prior"]
                    or entry.get("new_staged") != 3
                    or not isinstance(replies, list) or len(replies) != 3):
                raise ValueError("unknown or repeated canonical intent")
            kept = []
            for index, item in enumerate(replies, 1):
                if not isinstance(item, dict) or set(item) != FIELDS:
                    raise ValueError("unreviewed fields")
                phrase = item.get("text")
                note = item.get("context_note")
                if not isinstance(phrase, str) or not isinstance(note, str):
                    raise ValueError("non-text reply")
                p, n = norm(phrase), norm(note)
                rid = item.get("id")
                if (rid != f"{ident}_{label.lower()}_{index:02d}"
                        or rid in ids or not p or not n or p in texts or n in notes
                        or len(phrase) > 1600 or len(note) > 500
                        or PRIVATE.search(phrase) or PRIVATE.search(note)
                        or item.get("language") != "ru"
                        or item.get("style") != "neutral"
                        or item.get("audiences") != ["all_ai_bots"]
                        or item.get("context") not in CONTEXTS
                        or not isinstance(item.get("avoid"), str)
                        or not item["avoid"].strip()
                        or item.get("read_only") is not True):
                    raise ValueError("unsafe, unscoped or duplicate answer: " + str(rid))
                ids.add(rid)
                texts.add(p)
                notes.add(n)
                kept.append(item)
            self.by_intent[ident] = tuple(kept)
        if (set(self.by_intent) != set(canonical)
                or len(ids) != cfg["intents"] * (cfg["prior"] + 3)
                or len(texts) != cfg["intents"] * (9 + cfg["prior"] + 3)):
            raise ValueError("inventory count differs from actual verified data")
        self.label = label
        self.stage_path = cfg["stage"]
        self.checkpoint = expected
        self.cache_identity = (
            manifest["knowledge_version"], indexed[cfg["source"]],
            blob_sha(parent_bytes), blob_sha(stage_bytes),
        )

    def select(self, intent_id: str, *, approved_reply_ids: frozenset[str],
               audience: str, context: str, addressed: bool = False,
               local_permission: bool = False, recent_ids: tuple[str, ...] = ()):
        if (addressed is not True or local_permission is not True
                or audience != "all_ai_bots" or context not in CONTEXTS
                or not isinstance(approved_reply_ids, frozenset)
                or not approved_reply_ids or not isinstance(recent_ids, tuple)
                or not all(isinstance(x, str) for x in recent_ids)):
            return None
        for item in self.by_intent.get(intent_id, ()):
            if (item["id"] in approved_reply_ids
                    and item["context"] == context
                    and item["id"] not in recent_ids):
                return StagedSelection(
                    id=item["id"], text=item["text"],
                    intent_id=intent_id, context_note=item["context_note"],
                    stage_path=self.stage_path,
                )
        return None

def validate_both(root: Path = ROOT):
    left, right = Stage("T315", root), Stage("T316", root)
    replies = [norm(x["text"]) for obj in (left, right)
               for group in obj.by_intent.values() for x in group]
    notes = [norm(x["context_note"]) for obj in (left, right)
             for group in obj.by_intent.values() for x in group]
    if len(replies) != 138 or len(set(replies)) != 138 or len(set(notes)) != 138:
        raise ValueError("cross-stage duplicate reply or context note")
    return left, right

if __name__ == "__main__":
    a, b = validate_both()
    print("PASS T315=66 + T316=72; 46 partial intents; strict read-only opt-in")
