"""T309/T310 isolated read-only language stages. No automatic consumer activation."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

from scripts.colloquial_t305 import ROOT, norm, blob_sha
from scripts.colloquial_t307 import ColloquialT307
from scripts.practical_t308 import PracticalT308
from scripts.staged_context_selector import StagedSelection

CONFIG = {
    "T309": {
        "stage": "staging/ru/colloquial_t309_context_pool.json",
        "previous": "staging/ru/colloquial_t307_context_pool.json",
        "first": "staging/ru/colloquial_t305_context_pool.json",
        "source": "packs/ru/colloquial_ru_pragmatics_qa.json",
        "intents": 22, "base": 198, "staged": 198, "added": 66,
        "total": 462, "remaining": 1738, "prior_count": 9, "new_count": 3,
        "parent": ColloquialT307,
    },
    "T310": {
        "stage": "staging/ru/practical_t310_context_pool.json",
        "previous": "staging/ru/practical_t308_context_pool.json",
        "first": "staging/ru/practical_t306_salvage.json",
        "source": "packs/ru/practical_recovery_qa.json",
        "intents": 24, "base": 216, "staged": 168, "added": 96,
        "total": 480, "remaining": 1920, "prior_count": 7, "new_count": 4,
        "parent": PracticalT308,
    },
}
GUARDS = {"read_only": True, "requires_direct_address": True, "no_personal_data": True}
CONTEXTS = frozenset({"direct", "private", "group_addressed"})
FIELDS = {"id", "text", "context_note", "language", "style", "audiences",
          "context", "avoid", "read_only"}

def _read(root: Path, rel: str) -> bytes:
    path = root / rel
    if path.is_symlink() or not path.resolve(strict=True).is_relative_to(root):
        raise ValueError("unsafe knowledge path")
    return path.read_bytes()

def _reply_strings(root: Path, cfg: dict) -> tuple[dict, list, set, set, set]:
    base = json.loads(_read(root, cfg["source"]))
    canonical = {row["id"]: row for row in base["records"]}
    if len(canonical) != cfg["intents"] or len(base["records"]) != cfg["intents"]:
        raise ValueError("wrong canonical intents")
    first = json.loads(_read(root, cfg["first"]))
    previous = json.loads(_read(root, cfg["previous"]))
    old_ids, old_texts, old_notes = set(), set(), set()
    for row in base["records"]:
        if len(row.get("variants", [])) != 8:
            raise ValueError("qa.v1 baseline changed")
        for phrase in [row["answer"], *row["variants"]]:
            key = norm(phrase)
            if key in old_texts:
                raise ValueError("registered duplicate")
            old_texts.add(key)
    for part in (first, previous):
        for entry in part["entries"]:
            for item in entry["replies"]:
                key = norm(item["text"])
                note = norm(item["context_note"])
                if item["id"] in old_ids or key in old_texts or note in old_notes:
                    raise ValueError("old stage inventory has duplicates")
                old_ids.add(item["id"]); old_texts.add(key); old_notes.add(note)
    if len(old_ids) != cfg["staged"] or len(old_texts) != cfg["base"] + cfg["staged"]:
        raise ValueError("prior response counts changed")
    return canonical, previous, old_ids, old_texts, old_notes

class ReadOnlyContextStage:
    def __init__(self, label: str, root: Path = ROOT):
        if label not in CONFIG:
            raise ValueError("unreviewed stage label")
        cfg = CONFIG[label]
        root = Path(root).resolve(strict=True)
        cfg["parent"](root)
        manifest = json.loads(_read(root, "manifest.json"))
        registered = {p["path"]: p["sha256"] for p in manifest["packs"]}
        source_bytes = _read(root, cfg["source"])
        stage_bytes = _read(root, cfg["stage"])
        previous_bytes = _read(root, cfg["previous"])
        stage = json.loads(stage_bytes)
        checkpoint = {"stage_id": label, "processed_intents": cfg["intents"],
                      "baseline_registered": cfg["base"], "baseline_staged": cfg["staged"],
                      "added_candidates": cfg["added"], "finished_100": 0,
                      "partial_intents": cfg["intents"], "remaining_total": cfg["remaining"],
                      "rejected": 0}
        if (cfg["stage"] in registered or
                hashlib.sha256(source_bytes).hexdigest() != registered.get(cfg["source"]) or
                stage.get("schema_version") != 1 or
                stage.get("stage_type") != "supplemental_contextual_reply_pool" or
                stage.get("consumer_registered") is not False or
                stage.get("language") != "ru" or
                stage.get("audiences") != ["all_ai_bots"] or
                stage.get("constraints") != GUARDS or
                stage.get("source_pack") != cfg["source"] or
                stage.get("source_pack_manifest_sha256") != registered[cfg["source"]] or
                stage.get("source_pack_blob_sha") != blob_sha(source_bytes) or
                stage.get("previous_stage") != cfg["previous"] or
                stage.get("previous_stage_blob_sha") != blob_sha(previous_bytes) or
                stage.get("checkpoint") != checkpoint):
            raise ValueError("untrusted source, stale parent or incorrect checkpoint")
        canonical, old, ids, texts, notes = _reply_strings(root, cfg)
        entries = stage.get("entries")
        if not isinstance(entries, list) or len(entries) != cfg["intents"]:
            raise ValueError("missing canonical entries")
        self.by_intent = {}
        for entry in entries:
            intent = entry.get("intent_id")
            answers = entry.get("replies")
            if (intent not in canonical or intent in self.by_intent or
                    entry.get("question") != canonical[intent]["question"] or
                    entry.get("baseline_registered") != 9 or
                    entry.get("previous_staged") != cfg["prior_count"] or
                    entry.get("new_staged") != cfg["new_count"] or
                    not isinstance(answers, list) or len(answers) != cfg["new_count"]):
                raise ValueError("entry failed canonical/quantity checks")
            approved = []
            for index, item in enumerate(answers, 1):
                if not isinstance(item, dict) or set(item) != FIELDS:
                    raise ValueError("unreviewed reply keys")
                ident, phrase, note = item["id"], item["text"], item["context_note"]
                if (ident != f"{intent}_{label.lower()}_{index:02d}" or ident in ids or
                        not isinstance(phrase, str) or not 1 <= len(phrase) <= 1600 or
                        not isinstance(note, str) or not 1 <= len(note) <= 500 or
                        not norm(phrase) or not norm(note) or
                        norm(phrase) in texts or norm(note) in notes or
                        item["language"] != "ru" or item["style"] != "neutral" or
                        item["audiences"] != ["all_ai_bots"] or
                        item["context"] not in CONTEXTS or
                        not isinstance(item["avoid"], str) or not item["avoid"].strip() or
                        item["read_only"] is not True):
                    raise ValueError(f"repeated or unsafe reply: {ident}")
                from scripts.colloquial_t305 import PRIVATE
                if PRIVATE.search(phrase) or PRIVATE.search(note):
                    raise ValueError(f"private content in {ident}")
                ids.add(ident); texts.add(norm(phrase)); notes.add(norm(note))
                approved.append(item)
            self.by_intent[intent] = tuple(approved)
        if (set(self.by_intent) != set(canonical) or
                len(ids) != cfg["staged"] + cfg["added"] or
                len(texts) != cfg["total"]):
            raise ValueError("final inventory wrong")
        self.label = label
        self.stage_path = cfg["stage"]
        self.checkpoint = checkpoint
        self.cache_identity = (manifest["knowledge_version"],
                               registered[cfg["source"]],
                               blob_sha(previous_bytes), blob_sha(stage_bytes))

    def select(self, intent_id: str, *, approved_reply_ids: frozenset[str],
               audience: str, context: str, addressed: bool = False,
               local_permission: bool = False, recent_ids: tuple[str, ...] = ()):
        if (addressed is not True or local_permission is not True or
                audience != "all_ai_bots" or context not in CONTEXTS or
                not isinstance(approved_reply_ids, frozenset) or
                not isinstance(recent_ids, tuple) or
                not approved_reply_ids or not all(isinstance(x, str) for x in recent_ids)):
            return None
        for item in self.by_intent.get(intent_id, ()):
            if (item["id"] in approved_reply_ids and item["context"] == context
                    and item["id"] not in recent_ids):
                return StagedSelection(id=item["id"], text=item["text"],
                                       intent_id=intent_id, context_note=item["context_note"],
                                       stage_path=self.stage_path)
        return None

def validate_both(root: Path = ROOT):
    colloquial = ReadOnlyContextStage("T309", root)
    practical = ReadOnlyContextStage("T310", root)
    replies = [item["text"] for obj in (colloquial, practical)
               for group in obj.by_intent.values() for item in group]
    notes = [item["context_note"] for obj in (colloquial, practical)
             for group in obj.by_intent.values() for item in group]
    if (len(replies) != 162 or len({norm(x) for x in replies}) != 162 or
            len({norm(x) for x in notes}) != 162):
        raise ValueError("cross-stage duplicates")
    return colloquial, practical

if __name__ == "__main__":
    left, right = validate_both()
    print(f"PASS {left.label}={left.checkpoint['added_candidates']}, "
          f"{right.label}={right.checkpoint['added_candidates']}; read-only")
