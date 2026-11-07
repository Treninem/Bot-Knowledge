"""T323/T324: immutable provenance and read-only approval-gated language stages.

Not a manifest consumer pack, live assistant integration or action engine.
"""
from __future__ import annotations
import hashlib
import json
from pathlib import Path

from scripts.colloquial_t305 import ROOT, norm, blob_sha, PRIVATE
from scripts.context_t321_t322 import Stage as Previous, _keys
from scripts.context_t309_t310 import _read, GUARDS, CONTEXTS, FIELDS
from scripts.staged_context_selector import StagedSelection

STAGES = {
    "T323": {
        "source": "packs/ru/colloquial_ru_pragmatics_qa.json",
        "earlier": (
            "staging/ru/colloquial_t305_context_pool.json",
            "staging/ru/colloquial_t307_context_pool.json",
            "staging/ru/colloquial_t309_context_pool.json",
            "staging/ru/colloquial_t311_context_pool.json",
            "staging/ru/colloquial_t313_context_pool.json",
            "staging/ru/colloquial_t315_context_pool.json",
            "staging/ru/colloquial_t317_context_pool.json",
            "staging/ru/colloquial_t319_context_pool.json",
        ),
        "previous": "staging/ru/colloquial_t321_context_pool.json",
        "stage": "staging/ru/colloquial_t323_context_pool.json",
        "parent": "T321",
        "intents": 22, "prior": 26, "remaining": 1408,
    },
    "T324": {
        "source": "packs/ru/practical_recovery_qa.json",
        "earlier": (
            "staging/ru/practical_t306_salvage.json",
            "staging/ru/practical_t308_context_pool.json",
            "staging/ru/practical_t310_context_pool.json",
            "staging/ru/practical_t312_context_pool.json",
            "staging/ru/practical_t314_context_pool.json",
            "staging/ru/practical_t316_context_pool.json",
            "staging/ru/practical_t318_context_pool.json",
            "staging/ru/practical_t320_context_pool.json",
        ),
        "previous": "staging/ru/practical_t322_context_pool.json",
        "stage": "staging/ru/practical_t324_context_pool.json",
        "parent": "T322",
        "intents": 24, "prior": 25, "remaining": 1560,
    },
}

class Stage:
    def __init__(self, label: str, root: Path = ROOT):
        if label not in STAGES:
            raise ValueError("unreviewed stage")
        c = STAGES[label]
        root = Path(root).resolve(strict=True)
        Previous(c["parent"], root)
        manifest = json.loads(_read(root, "manifest.json"))
        registered = {x["path"]: x["sha256"] for x in manifest["packs"]}
        source_bytes = _read(root, c["source"])
        previous_bytes = _read(root, c["previous"])
        stage_bytes = _read(root, c["stage"])
        original = json.loads(source_bytes)["records"]
        stage = json.loads(stage_bytes)
        canonical = {record["id"]: record for record in original}
        checkpoint = dict(
            stage_id=label, processed_intents=c["intents"],
            baseline_registered=c["intents"] * 9,
            baseline_staged=c["intents"] * c["prior"],
            added_candidates=c["intents"] * 1,
            finished_100=0, partial_intents=c["intents"],
            remaining_total=c["remaining"], rejected=0,
        )
        if (len(canonical) != c["intents"] or len(original) != c["intents"]
                or c["stage"] in registered
                or registered.get(c["source"]) != hashlib.sha256(source_bytes).hexdigest()
                or stage.get("source_pack") != c["source"]
                or stage.get("source_pack_manifest_sha256") != registered[c["source"]]
                or stage.get("source_pack_blob_sha") != blob_sha(source_bytes)
                or stage.get("previous_stage") != c["previous"]
                or stage.get("previous_stage_blob_sha") != blob_sha(previous_bytes)
                or stage.get("schema_version") != 1
                or stage.get("stage_type") != "supplemental_contextual_reply_pool"
                or stage.get("consumer_registered") is not False
                or stage.get("language") != "ru"
                or stage.get("audiences") != ["all_ai_bots"]
                or stage.get("constraints") != GUARDS
                or stage.get("checkpoint") != checkpoint):
            raise ValueError("unapproved manifest, parent, source or stage")
        ids, texts, notes = _keys(root, c, original)
        rows = stage.get("entries")
        if not isinstance(rows, list) or len(rows) != c["intents"]:
            raise ValueError("wrong canonical inventory")
        self.by_intent = {}
        for row in rows:
            ident, replies = row.get("intent_id"), row.get("replies")
            if (ident not in canonical or ident in self.by_intent
                    or row.get("question") != canonical[ident]["question"]
                    or row.get("baseline_registered") != 9
                    or row.get("previous_staged") != c["prior"]
                    or row.get("new_staged") != 1
                    or not isinstance(replies, list) or len(replies) != 1):
                raise ValueError("incorrect canonical mapping")
            approved = []
            for index, item in enumerate(replies, 1):
                if not isinstance(item, dict) or set(item) != FIELDS:
                    raise ValueError("unexpected reply fields")
                phrase, note = item.get("text"), item.get("context_note")
                if not isinstance(phrase, str) or not isinstance(note, str):
                    raise ValueError("non-text reply")
                text_key, note_key = norm(phrase), norm(note)
                rid = item.get("id")
                if (rid != f"{ident}_{label.lower()}_{index:02d}"
                        or rid in ids or text_key in texts or note_key in notes
                        or not text_key or not note_key
                        or len(phrase) > 1600 or len(note) > 500
                        or PRIVATE.search(phrase) or PRIVATE.search(note)
                        or item.get("language") != "ru"
                        or item.get("style") != "neutral"
                        or item.get("audiences") != ["all_ai_bots"]
                        or item.get("context") not in CONTEXTS
                        or not isinstance(item.get("avoid"), str)
                        or not item["avoid"].strip()
                        or item.get("read_only") is not True):
                    raise ValueError("unsafe, repeated or unscoped response: " + str(rid))
                ids.add(rid)
                texts.add(text_key)
                notes.add(note_key)
                approved.append(item)
            self.by_intent[ident] = tuple(approved)
        if (set(self.by_intent) != set(canonical)
                or len(ids) != c["intents"] * (c["prior"] + 1)
                or len(texts) != c["intents"] * (9 + c["prior"] + 2)):
            raise ValueError("count differs from actual verified replies")
        self.label = label
        self.checkpoint = checkpoint
        self.stage_path = c["stage"]
        self.cache_identity = (manifest["knowledge_version"], registered[c["source"]],
                               blob_sha(previous_bytes), blob_sha(stage_bytes))

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
            if (item["id"] in approved_reply_ids and item["id"] not in recent_ids
                    and item["context"] == context):
                return StagedSelection(
                    id=item["id"], text=item["text"], intent_id=intent_id,
                    context_note=item["context_note"], stage_path=self.stage_path,
                )
        return None

def validate_both(root: Path = ROOT):
    a, b = Stage("T323", root), Stage("T324", root)
    text_keys = [norm(x["text"]) for model in (a, b)
                 for group in model.by_intent.values() for x in group]
    note_keys = [norm(x["context_note"]) for model in (a, b)
                 for group in model.by_intent.values() for x in group]
    if len(text_keys) != 46 or len(set(text_keys)) != 92 or len(set(note_keys)) != 92:
        raise ValueError("cross-stage normalized collisions")
    return a, b

if __name__ == "__main__":
    a, b = validate_both()
    print("PASS T323=22, T324=24 synthetic read-only opt-in replies")
