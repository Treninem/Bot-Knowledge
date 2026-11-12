"""T307 read-only colloquial continuation. Never an automatic consumer router."""
from __future__ import annotations
import hashlib
import json
from pathlib import Path
from scripts.colloquial_t305 import ColloquialT305, ROOT, SOURCE, STAGE as PREVIOUS, GUARDS, CONTEXTS, PRIVATE, blob_sha, norm
from scripts.staged_context_selector import StagedSelection

STAGE = "staging/ru/colloquial_t307_context_pool.json"
class ColloquialT307:
    def __init__(self, root: Path = ROOT):
        root = Path(root).resolve(strict=True)
        previous = ColloquialT305(root)
        path = root / STAGE
        if path.is_symlink() or not path.resolve().is_relative_to(root):
            raise ValueError("unsafe stage path")
        stage = json.loads(path.read_text("utf-8"))
        manifest = json.loads((root / "manifest.json").read_text("utf-8"))
        manifest_hashes = {p["path"]: p["sha256"] for p in manifest["packs"]}
        registered = (root / SOURCE).read_bytes()
        previous_bytes = (root / PREVIOUS).read_bytes()
        expected = {"stage_id":"T307", "processed_intents":22, "baseline_registered":198,
                    "baseline_staged":110, "added_candidates":88, "finished_100":0,
                    "partial_intents":22, "remaining_total":1804, "rejected":0}
        if (STAGE in manifest_hashes or stage.get("stage_type") != "supplemental_contextual_reply_pool"
                or stage.get("schema_version") != 1 or stage.get("consumer_registered") is not False
                or stage.get("language") != "ru" or stage.get("audiences") != ["all_ai_bots"]
                or stage.get("constraints") != GUARDS or stage.get("source_pack") != SOURCE
                or stage.get("source_pack_manifest_sha256") != manifest_hashes.get(SOURCE)
                or hashlib.sha256(registered).hexdigest() != manifest_hashes.get(SOURCE)
                or stage.get("source_pack_blob_sha") != blob_sha(registered)
                or stage.get("previous_stage") != PREVIOUS
                or stage.get("previous_stage_blob_sha") != blob_sha(previous_bytes)
                or stage.get("checkpoint") != expected):
            raise ValueError("stale stage or inconsistent source/checkpoint")
        canonical = {r["id"]: r for r in json.loads(registered)["records"]}
        old = json.loads(previous_bytes)
        known_ids, known_texts, known_notes = set(), set(), set()
        for r in canonical.values():
            known_texts.update(norm(x) for x in [r["answer"], *r["variants"]])
        for entry in old["entries"]:
            for x in entry["replies"]:
                known_ids.add(x["id"])
                known_texts.add(norm(x["text"]))
                known_notes.add(norm(x["context_note"]))
        self.by_intent = {}
        for entry in stage.get("entries", []):
            intent = entry.get("intent_id")
            if (intent not in canonical or intent in self.by_intent
                    or entry.get("question") != canonical[intent]["question"]
                    or entry.get("baseline_registered") != 9
                    or entry.get("previous_staged") != 5 or entry.get("new_staged") != 4
                    or not isinstance(entry.get("replies"), list) or len(entry["replies"]) != 4):
                raise ValueError("unreviewed intent or count")
            approved = []
            for index, item in enumerate(entry["replies"], 1):
                key = item.get("id")
                phrase, note = item.get("text"), item.get("context_note")
                if (key != f"{intent}_t307_{index:02d}" or key in known_ids
                        or not isinstance(phrase, str) or not 1 <= len(phrase) <= 1600
                        or not isinstance(note, str) or not 1 <= len(note) <= 500
                        or norm(phrase) in known_texts or norm(note) in known_notes
                        or PRIVATE.search(phrase) or PRIVATE.search(note)
                        or item.get("context") not in CONTEXTS
                        or item.get("language") != "ru" or item.get("style") != "neutral"
                        or item.get("audiences") != ["all_ai_bots"]
                        or item.get("read_only") is not True
                        or not isinstance(item.get("avoid"), str) or not item["avoid"].strip()):
                    raise ValueError(f"duplicate or unsafe reply: {key}")
                known_ids.add(key); known_texts.add(norm(phrase)); known_notes.add(norm(note))
                approved.append(item)
            self.by_intent[intent] = tuple(approved)
        if set(self.by_intent) != set(canonical) or len(known_ids) != 198 or len(known_texts) != 396:
            raise ValueError("incomplete or repeated inventory")
        self.checkpoint = expected
        self.cache_identity = (manifest["knowledge_version"], manifest_hashes[SOURCE],
                               blob_sha(previous_bytes), blob_sha(path.read_bytes()))
        self.parent = previous

    def select(self, intent_id: str, *, approved_reply_ids: frozenset[str],
               audience: str, context: str, addressed: bool = False,
               local_permission: bool = False, recent_ids: tuple[str,...] = ()):
        if (not addressed or not local_permission or audience != "all_ai_bots"
                or context not in CONTEXTS or not isinstance(approved_reply_ids, frozenset)
                or not approved_reply_ids or not isinstance(recent_ids, tuple)):
            return None
        for reply in self.by_intent.get(intent_id, ()):
            if (reply["id"] in approved_reply_ids and reply["context"] == context
                    and reply["id"] not in recent_ids):
                return StagedSelection(id=reply["id"], text=reply["text"],
                    intent_id=intent_id, context_note=reply["context_note"], stage_path=STAGE)
        return None
