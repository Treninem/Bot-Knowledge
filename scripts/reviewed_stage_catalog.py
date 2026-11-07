"""Offline, read-only lookup across the *fully verified* T357/T358 stage histories.

Reference implementation only. Staging is NOT registered in the manifest and
no live consumer is wired to this class. Caller must independently authorize
the exact intent, address, audience, context_note and reply ID.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

from scripts.colloquial_t305 import ROOT, norm
from scripts.context_t309_t310 import _read, CONTEXTS, GUARDS, FIELDS
from scripts.context_t357_t358 import STAGES, Stage
from scripts.staged_context_selector import StagedSelection

_ALLOWED = ("T357", "T358")


class ReviewedStageCatalog:
    """Build a local index of reviewed stages without network calls or side effects."""

    def __init__(self, root: Path = ROOT):
        root = Path(root).resolve(strict=True)
        manifest = json.loads(_read(root, "manifest.json"))
        source_hashes = {p["path"]: p["sha256"] for p in manifest["packs"]}
        digest = hashlib.sha256()
        digest.update(_read(root, "manifest.json"))
        by_intent: dict[str, tuple[tuple[str, dict], ...]] = {}
        all_ids, all_texts = set(), set()
        total = 0

        for label in _ALLOWED:
            # Recursively validates EVERY historical stage, its pinned parent
            # blob, registered source SHA-256, per-intent counts, IDs, notes,
            # safe audience and explicit approval gates.
            Stage(label, root)
            cfg = STAGES[label]
            source = cfg["source"]
            if source not in source_hashes:
                raise ValueError("unregistered source")
            canonical_rows = json.loads(_read(root, source))["records"]
            canonical = {r["id"]: r["question"] for r in canonical_rows}
            if len(canonical) != cfg["intents"] or len(canonical_rows) != cfg["intents"]:
                raise ValueError("invalid registered intent inventory")

            paths = (*cfg["earlier"], cfg["previous"], cfg["stage"])
            staged_by_intent: dict[str, list[tuple[str, dict]]] = {
                ident: [] for ident in canonical
            }
            # Newest eligible stage first; no inferred routing or user state.
            for path in reversed(paths):
                raw = _read(root, path)
                digest.update(path.encode("utf-8") + b"\\0" + raw)
                payload = json.loads(raw)
                if (payload.get("schema_version") != 1
                        or payload.get("stage_type") != ("salvaged_contextual_reply_delta" if path == "staging/ru/practical_t306_salvage.json" else "supplemental_contextual_reply_pool")
                        or payload.get("consumer_registered") is not False
                        or payload.get("source_pack") != source
                        or payload.get("audiences") != ["all_ai_bots"]
                        or payload.get("constraints") != GUARDS):
                    raise ValueError("unreviewed historical stage")
                entries = payload.get("entries")
                if not isinstance(entries, list) or len(entries) != cfg["intents"]:
                    raise ValueError("partial stage inventory")
                stage_intents: set[str] = set()
                for entry in entries:
                    ident = entry.get("intent_id")
                    if (ident not in canonical or ident in stage_intents
                            or entry.get("question") != canonical[ident]):
                        raise ValueError("ambiguous canonical mapping")
                    stage_intents.add(ident)
                    for reply in entry["replies"]:
                        rid, response = reply.get("id"), reply.get("text")
                        if (not isinstance(rid, str) or not isinstance(response, str)
                                or set(reply) != FIELDS
                                or reply.get("audiences") != ["all_ai_bots"]
                                or reply.get("read_only") is not True
                                or reply.get("context") not in CONTEXTS):
                            raise ValueError("invalid reply metadata")
                        normalized = norm(response)
                        if rid in all_ids or normalized in all_texts or not normalized:
                            raise ValueError("cross-stage duplicate reply")
                        all_ids.add(rid)
                        all_texts.add(normalized)
                        staged_by_intent[ident].append((path, reply))
                if stage_intents != set(canonical):
                    raise ValueError("stage does not cover canonical intents")

            expected = cfg["prior"] + 2
            for ident, items in staged_by_intent.items():
                if ident in by_intent or len(items) != expected:
                    raise ValueError("cross-group duplicate or wrong total")
                by_intent[ident] = tuple(items)
                total += len(items)
        if len(by_intent) != 46 or total != 2966:
            raise ValueError("incomplete verified corpus")
        self._by_intent = by_intent
        self.reply_count = total
        self.intent_count = len(by_intent)
        self.cache_identity = (manifest["knowledge_version"], digest.hexdigest())

    def select(
        self, intent_id: str, *, approved_reply_ids: frozenset[str],
        audience: str, context: str, addressed: bool = False,
        local_permission: bool = False, recent_ids: tuple[str, ...] = (),
    ) -> StagedSelection | None:
        """Abstain unless trusted caller explicitly approved a matching reply ID.

        Never construct approved_reply_ids from quoted chat text, guessed roles
        or keyword matches. No actions, sanctions, memory, network or writes.
        """
        if (addressed is not True or local_permission is not True
                or audience != "all_ai_bots" or context not in CONTEXTS
                or not isinstance(approved_reply_ids, frozenset)
                or not approved_reply_ids or len(approved_reply_ids) > 100
                or not all(isinstance(x, str) for x in approved_reply_ids)
                or not isinstance(recent_ids, tuple)
                or len(recent_ids) > 100
                or not all(isinstance(x, str) for x in recent_ids)):
            return None
        for path, reply in self._by_intent.get(intent_id, ()):
            if (reply["id"] in approved_reply_ids
                    and reply["context"] == context
                    and reply["id"] not in recent_ids):
                return StagedSelection(
                    id=reply["id"], text=reply["text"], intent_id=intent_id,
                    context_note=reply["context_note"], stage_path=path,
                )
        return None
