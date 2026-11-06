"""T285: opt-in read-only layer of 48 synthetic RU pragmatic responses.

No consumer registration, user-data collection, chat moderation or execution.
Requires the immutable T284 parent and current registered source hash.
"""
import hashlib
import json
from pathlib import Path
from scripts.spoken_delta_t284 import SpokenDeltaT284
from scripts.spoken_delta_overlay import SOURCE, GUARDS, CONTEXTS, SECRET, norm, jaccard, blob_sha
from scripts.staged_context_selector import StagedSelection

DELTA = "staging/ru/spoken_pragmatics_t285_delta.json"
PARENT = "staging/ru/spoken_pragmatics_t284_delta.json"
HISTORY = (
    "staging/ru/spoken_pragmatics_t251_context_pool.json",
    "staging/ru/spoken_pragmatics_t270_delta.json",
    "staging/ru/spoken_pragmatics_t273_delta.json",
    "staging/ru/spoken_pragmatics_t274_delta.json",
    "staging/ru/spoken_pragmatics_t276_delta.json",
    "staging/ru/spoken_pragmatics_t278_delta.json",
    "staging/ru/spoken_pragmatics_t280_delta.json",
    "staging/ru/spoken_pragmatics_t282_delta.json",
    PARENT,
)

class SpokenDeltaT285:
    def __init__(self, root: Path, path: str = DELTA):
        if path != DELTA:
            raise ValueError("unreviewed staged path")
        root = Path(root).resolve(strict=True)
        self.parent = SpokenDeltaT284(root)
        parent_bytes = (root / PARENT).read_bytes()
        raw = (root / path).read_bytes()
        data = json.loads(raw)
        manifest = json.loads((root / "manifest.json").read_text("utf-8"))
        reg = {p["path"]: p["sha256"] for p in manifest["packs"]}
        if (data.get("schema_version") != 1 or
            data.get("delta_type") != "supplemental_contextual_reply_delta" or
            data.get("consumer_registered") is not False or
            data.get("language") != "ru" or
            data.get("audiences") != ["all_ai_bots"] or
            data.get("constraints") != GUARDS or
            data.get("parent_delta_path") != PARENT or
            data.get("parent_delta_blob_sha") != blob_sha(parent_bytes) or
            data.get("source_pack") != SOURCE or
            data.get("source_pack_manifest_sha256") != reg[SOURCE] or
            hashlib.sha256((root / SOURCE).read_bytes()).hexdigest() != reg[SOURCE] or
            DELTA in reg):
            raise ValueError("stale source, untrusted parent, or unsafe scope")
        records = json.loads((root / SOURCE).read_text("utf-8"))["records"]
        canonical = {r["id"]: r for r in records}
        if len(canonical) != 24:
            raise ValueError("registered intent inventory changed")
        oldtexts = {i: [r["answer"], *r["variants"]] for i,r in canonical.items()}
        oldnotes = {i: set() for i in canonical}
        oldids, allnorm = set(), set()
        for f in HISTORY:
            rows = json.loads((root / f).read_text("utf-8"))["entries"]
            keys = {r["intent_id"] for r in rows}
            if len(rows) != 24 or keys != set(canonical):
                raise ValueError("historical intent mismatch")
            for row in rows:
                for reply in row["replies"]:
                    if reply["id"] in oldids:
                        raise ValueError("duplicate historical ID")
                    oldids.add(reply["id"])
                    oldtexts[row["intent_id"]].append(reply["text"])
                    oldnotes[row["intent_id"]].add(norm(reply["context_note"]))
        for texts in oldtexts.values():
            if len(texts) != 86:
                raise ValueError("historical count not 86")
            for txt in texts:
                n = norm(txt)
                if n in allnorm:
                    raise ValueError("duplicate historical text")
                allnorm.add(n)
        self._rows = {}
        for entry in data.get("entries", []):
            ident = entry.get("intent_id")
            if ident not in canonical or ident in self._rows or
                entry.get("question") != canonical[ident]["question"] or
                entry.get("registered_reply_count") != 9 or
                entry.get("parent_staged_reply_count") != 77 or
                not isinstance(entry.get("replies"), list) or len(entry["replies"]) != 2):
                raise ValueError("stale identity or count")
            out = []
            for idx, reply in enumerate(entry["replies"], 1):
                rid = reply.get("id")
                txt = reply.get("text")
                note = reply.get("context_note")
                if (rid != f"{ident}_t285_{idx:02d}" or rid in oldids or
                    not isinstance(txt, str) or not 1 <= len(txt) <= 1600 or
                    SECRET.search(txt) or not norm(txt) or norm(txt) in allnorm or
                    not isinstance(note, str) or not norm(note) or
                    norm(note) in oldnotes[ident] or
                    reply.get("language") != "ru" or reply.get("style") != "neutral" or
                    reply.get("audiences") != ["all_ai_bots"] or
                    reply.get("read_only") is not True or
                    reply.get("context") not in CONTEXTS or
                    not isinstance(reply.get("avoid"), str) or not reply["avoid"].strip() or
                    max((jaccard(txt, old) for old in oldtexts[ident]), default=0) >= 0.78):
                    raise ValueError("unsafe, repeated, or mismatched reply")
                oldids.add(rid)
                allnorm.add(norm(txt))
                oldtexts[ident].append(txt)
                oldnotes[ident].add(norm(note))
                out.append(reply)
            self._rows[ident] = tuple(out)
        cp = data.get("checkpoint", {})
        expected = {
            "stage_id": "T285", "processed_intents": 24,
            "registered_count": 216, "parent_staged_count": 1848,
            "added_in_current": 48, "total_staged_with_parent": 1896,
            "previous_per_intent": 86, "now_per_intent": 88,
            "remaining_per_intent": 12, "remaining_total": 288,
            "partial_intents": 24, "finished_100": 0, "rejected": 0,
        }
        if len(self._rows) != 24 or any(cp.get(k) != v for k,v in expected.items()):
            raise ValueError("unverified checkpoint")
        self.checkpoint = cp
        self.cache_identity = (manifest["knowledge_version"], blob_sha(parent_bytes), blob_sha(raw))

    def select(self, intent_id: str, *, approved_reply_ids: frozenset[str],
               audience: str, context: str, addressed: bool = False,
               local_permission: bool = False, recent_ids: tuple[str,...] = ()) -> StagedSelection | None:
        if (audience != "all_ai_bots" or not addressed or not local_permission or
            context not in CONTEXTS or not isinstance(approved_reply_ids, frozenset) or
            not approved_reply_ids or not isinstance(recent_ids, tuple)):
            return None
        for item in self._rows.get(intent_id, ()):
            if (item["id"] in approved_reply_ids and
                item["id"] not in recent_ids and item["context"] == context):
                return StagedSelection(id=item["id"], text=item["text"],
                    intent_id=intent_id, context_note=item["context_note"], stage_path=DELTA)
        return None
