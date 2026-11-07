"""T317/T318 incremental context pool checks, immutable source/parent, opt-in only."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

from scripts.colloquial_t305 import ROOT, norm, blob_sha, PRIVATE
from scripts.context_t315_t316 import Stage as ParentStage, _keys
from scripts.context_t309_t310 import _read, GUARDS, CONTEXTS, FIELDS
from scripts.staged_context_selector import StagedSelection

STAGES = {
    "T317": {
        "source": "packs/ru/colloquial_ru_pragmatics_qa.json",
        "previous": "staging/ru/colloquial_t315_context_pool.json",
        "earlier": (
            "staging/ru/colloquial_t305_context_pool.json",
            "staging/ru/colloquial_t307_context_pool.json",
            "staging/ru/colloquial_t309_context_pool.json",
            "staging/ru/colloquial_t311_context_pool.json",
            "staging/ru/colloquial_t313_context_pool.json",
        ),
        "stage": "staging/ru/colloquial_t317_context_pool.json",
        "parent": "T315",
        "intents": 22,
        "prior": 20,
        "remaining": 1518,
    },
    "T318": {
        "source": "packs/ru/practical_recovery_qa.json",
        "previous": "staging/ru/practical_t316_context_pool.json",
        "earlier": (
            "staging/ru/practical_t306_salvage.json",
            "staging/ru/practical_t308_context_pool.json",
            "staging/ru/practical_t310_context_pool.json",
            "staging/ru/practical_t312_context_pool.json",
            "staging/ru/practical_t314_context_pool.json",
        ),
        "stage": "staging/ru/practical_t318_context_pool.json",
        "parent": "T316",
        "intents": 24,
        "prior": 19,
        "remaining": 1680,
    },
}

class Stage:
    def __init__(self, label: str, root: Path = ROOT):
        if label not in STAGES:
            raise ValueError("unknown staged corpus")
        cfg = STAGES[label]
        root = Path(root).resolve(strict=True)
        ParentStage(cfg["parent"], root)
        manifest = json.loads(_read(root, "manifest.json"))
        referenced = {p["path"]: p["sha256"] for p in manifest["packs"]}
        source_bytes = _read(root, cfg["source"])
        previous_bytes = _read(root, cfg["previous"])
        content_bytes = _read(root, cfg["stage"])
        original = json.loads(source_bytes)["records"]
        stage = json.loads(content_bytes)
        canonical = {r["id"]: r for r in original}
        expected = {
            "stage_id": label,
            "processed_intents": cfg["intents"],
            "baseline_registered": cfg["intents"] * 9,
            "baseline_staged": cfg["intents"] * cfg["prior"],
            "added_candidates": cfg["intents"] * 2,
            "finished_100": 0,
            "partial_intents": cfg["intents"],
            "remaining_total": cfg["remaining"],
            "rejected": 0,
        }
        if (cfg["stage"] in referenced
                or referenced.get(cfg["source"]) != hashlib.sha256(source_bytes).hexdigest()
                or len(canonical) != cfg["intents"] or len(original) != cfg["intents"]
                or stage.get("source_pack") != cfg["source"]
                or stage.get("source_pack_manifest_sha256") != referenced[cfg["source"]]
                or stage.get("source_pack_blob_sha") != blob_sha(source_bytes)
                or stage.get("previous_stage") != cfg["previous"]
                or stage.get("previous_stage_blob_sha") != blob_sha(previous_bytes)
                or stage.get("schema_version") != 1
                or stage.get("stage_type") != "supplemental_contextual_reply_pool"
                or stage.get("consumer_registered") is not False
                or stage.get("language") != "ru"
                or stage.get("audiences") != ["all_ai_bots"]
                or stage.get("constraints") != GUARDS
                or stage.get("checkpoint") != expected):
            raise ValueError("unreviewed scope or stale manifest/source/parent")
        ids, texts, notes = _keys(root, cfg, original)
        entries = stage.get("entries")
        if not isinstance(entries, list) or len(entries) != cfg["intents"]:
            raise ValueError("wrong canonical count")
        self.by_intent = {}
        for entry in entries:
            intent, replies = entry.get("intent_id"), entry.get("replies")
            if (intent not in canonical or intent in self.by_intent
                    or entry.get("question") != canonical[intent]["question"]
                    or entry.get("baseline_registered") != 9
                    or entry.get("previous_staged") != cfg["prior"]
                    or entry.get("new_staged") != 2
                    or not isinstance(replies, list) or len(replies) != 2):
                raise ValueError("invalid canonical mapping")
            approved = []
            for number, item in enumerate(replies, 1):
                if not isinstance(item, dict) or set(item) != FIELDS:
                    raise ValueError("unexpected reply attributes")
                text, note = item.get("text"), item.get("context_note")
                if not isinstance(text, str) or not isinstance(note, str):
                    raise ValueError("invalid response text")
                text_key, note_key = norm(text), norm(note)
                rid = item.get("id")
                if (rid != f"{intent}_{label.lower()}_{number:02d}"
                        or rid in ids or not text_key or not note_key
                        or text_key in texts or note_key in notes
                        or len(text) > 1600 or len(note) > 500
                        or PRIVATE.search(text) or PRIVATE.search(note)
                        or item.get("language") != "ru"
                        or item.get("style") != "neutral"
                        or item.get("audiences") != ["all_ai_bots"]
                        or item.get("context") not in CONTEXTS
                        or not isinstance(item.get("avoid"), str)
                        or not item["avoid"].strip()
                        or item.get("read_only") is not True):
                    raise ValueError("unapproved answer: " + str(rid))
                ids.add(rid)
                texts.add(text_key)
                notes.add(note_key)
                approved.append(item)
            self.by_intent[intent] = tuple(approved)
        if (set(self.by_intent) != set(canonical)
                or len(ids) != cfg["intents"] * (cfg["prior"] + 2)
                or len(texts) != cfg["intents"] * (9 + cfg["prior"] + 2)):
            raise ValueError("actual unique inventory does not match checkpoint")
        self.label = label
        self.checkpoint = expected
        self.stage_path = cfg["stage"]
        self.cache_identity = (
            manifest["knowledge_version"], referenced[cfg["source"]],
            blob_sha(previous_bytes), blob_sha(content_bytes),
        )

    def select(self, intent_id: str, *, approved_reply_ids: frozenset[str],
               audience: str, context: str, addressed: bool = False,
               local_permission: bool = False, recent_ids: tuple[str, ...] = ()):
        if (addressed is not True or local_permission is not True
                or audience != "all_ai_bots" or context not in CONTEXTS
                or not isinstance(approved_reply_ids, frozenset)
                or not approved_reply_ids or not isinstance(recent_ids, tuple)
                or not all(isinstance(i, str) for i in recent_ids)):
            return None
        for item in self.by_intent.get(intent_id, ()):
            if (item["id"] in approved_reply_ids
                    and item["id"] not in recent_ids
                    and item["context"] == context):
                return StagedSelection(
                    id=item["id"], text=item["text"],
                    intent_id=intent_id, context_note=item["context_note"],
                    stage_path=self.stage_path,
                )
        return None

def validate_both(root: Path = ROOT):
    a, b = Stage("T317", root), Stage("T318", root)
    texts = [norm(x["text"]) for model in (a, b)
             for group in model.by_intent.values() for x in group]
    notes = [norm(x["context_note"]) for model in (a, b)
             for group in model.by_intent.values() for x in group]
    if len(texts) != 92 or len(set(texts)) != 92 or len(set(notes)) != 92:
        raise ValueError("cross-stage normalized collision")
    return a, b

if __name__ == "__main__":
    a, b = validate_both()
    print("PASS T317=44, T318=48, all opted-in, unregistered")
