"""T289: opt-in, read-only continuation of 24 spoken intents; never automatically registered."""
import hashlib
import json
from pathlib import Path
from scripts.spoken_delta_t287 import SpokenDeltaT287, HISTORY
from scripts.spoken_delta_overlay import SOURCE, GUARDS, CONTEXTS, SECRET, norm, jaccard, blob_sha
from scripts.staged_context_selector import StagedSelection

DELTA = "staging/ru/spoken_pragmatics_t289_delta.json"
PARENT = "staging/ru/spoken_pragmatics_t287_delta.json"

class SpokenDeltaT289:
    def __init__(self, root: Path, path: str = DELTA):
        if path != DELTA:
            raise ValueError("unreviewed stage path")
        root = Path(root).resolve(strict=True)
        self.parent = SpokenDeltaT287(root)
        parent_bytes = (root / PARENT).read_bytes()
        raw = (root / DELTA).read_bytes()
        stage = json.loads(raw)
        manifest = json.loads((root / "manifest.json").read_text("utf-8"))
        reg = {p["path"]: p["sha256"] for p in manifest["packs"]}
        if (stage.get("schema_version") != 1
                or stage.get("delta_type") != "supplemental_contextual_reply_delta"
                or stage.get("consumer_registered") is not False
                or stage.get("language") != "ru"
                or stage.get("audiences") != ["all_ai_bots"]
                or stage.get("constraints") != GUARDS
                or stage.get("parent_delta_path") != PARENT
                or stage.get("parent_delta_blob_sha") != blob_sha(parent_bytes)
                or stage.get("source_pack") != SOURCE
                or stage.get("source_pack_manifest_sha256") != reg[SOURCE]
                or hashlib.sha256((root / SOURCE).read_bytes()).hexdigest() != reg[SOURCE]
                or DELTA in reg):
            raise ValueError("untrusted scope, source or parent")
        canonical = {r["id"]: r for r in json.loads((root / SOURCE).read_text("utf-8"))["records"]}
        if len(canonical) != 24:
            raise ValueError("registered intent inventory changed")
        known = {i: [r["answer"], *r["variants"]] for i, r in canonical.items()}
        notes = {i: set() for i in canonical}
        used_ids = set()
        all_text = set()
        for filename in (*HISTORY, PARENT):
            rows = json.loads((root / filename).read_text("utf-8"))["entries"]
            if len(rows) != 24 or {x["intent_id"] for x in rows} != set(canonical):
                raise ValueError("historical intent inventory differs")
            for entry in rows:
                for reply in entry["replies"]:
                    if reply["id"] in used_ids:
                        raise ValueError("historical duplicate ID")
                    used_ids.add(reply["id"])
                    known[entry["intent_id"]].append(reply["text"])
                    notes[entry["intent_id"]].add(norm(reply["context_note"]))
        for texts in known.values():
            if len(texts) != 90:
                raise ValueError("historical count is not 90")
            for txt in texts:
                key = norm(txt)
                if not key or key in all_text:
                    raise ValueError("historical duplicate text")
                all_text.add(key)
        self._rows = {}
        for row in stage.get("entries", []):
            ident = row.get("intent_id")
            if (ident not in canonical or ident in self._rows
                    or row.get("question") != canonical[ident]["question"]
                    or row.get("registered_reply_count") != 9
                    or row.get("parent_staged_reply_count") != 81
                    or not isinstance(row.get("replies"), list)
                    or len(row["replies"]) != 2):
                raise ValueError("stale identity, repeated intent or wrong count")
            out = []
            for n, reply in enumerate(row["replies"], 1):
                rid, txt, note = reply.get("id"), reply.get("text"), reply.get("context_note")
                if (rid != f"{ident}_t289_{n:02d}" or rid in used_ids
                        or not isinstance(txt, str) or not 1 <= len(txt) <= 1600
                        or SECRET.search(txt) or not norm(txt) or norm(txt) in all_text
                        or not isinstance(note, str) or not norm(note) or norm(note) in notes[ident]
                        or reply.get("language") != "ru" or reply.get("style") != "neutral"
                        or reply.get("audiences") != ["all_ai_bots"]
                        or reply.get("read_only") is not True
                        or reply.get("context") not in CONTEXTS
                        or not isinstance(reply.get("avoid"), str) or not reply["avoid"].strip()
                        or max((jaccard(txt, old) for old in known[ident]), default=0) >= .78):
                    raise ValueError("unsafe or repeated staged response")
                used_ids.add(rid)
                all_text.add(norm(txt))
                known[ident].append(txt)
                notes[ident].add(norm(note))
                out.append(reply)
            self._rows[ident] = tuple(out)
        cp = stage.get("checkpoint", {})
        expected = dict(stage_id="T289", processed_intents=24, registered_count=216,
                        parent_staged_count=1944, added_in_current=48,
                        total_staged_with_parent=1992, previous_per_intent=90,
                        now_per_intent=92, remaining_per_intent=8,
                        remaining_total=192, partial_intents=24, finished_100=0, rejected=0)
        if len(self._rows) != 24 or any(cp.get(k) != v for k, v in expected.items()):
            raise ValueError("checkpoint does not match validated stage")
        self.checkpoint = cp
        self.cache_identity = (manifest["knowledge_version"], blob_sha(parent_bytes), blob_sha(raw))

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
                                       stage_path=DELTA)
        return None
