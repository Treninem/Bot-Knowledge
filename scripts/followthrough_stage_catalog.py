"""Source-pinned, read-only local index over the seventy-eight reviewed followthrough stages.

No consumer integration, inference from chat text, network calls, actions, or
moderation. A trusted caller must verify and approve exact reply IDs.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

from scripts.colloquial_t305 import ROOT
from scripts.staged_context_selector import (
    StagedContextSelector, StagedSelection, _norm,
)

STAGES = (
    "staging/ru/followthrough_t383_context_pool.json",
    "staging/ru/followthrough_t384_context_pool.json",
    "staging/ru/followthrough_t385_context_pool.json",
    "staging/ru/followthrough_t386_context_pool.json",
    "staging/ru/followthrough_t387_context_pool.json",
    "staging/ru/followthrough_t388_context_pool.json",
    "staging/ru/followthrough_t389_context_pool.json",
    "staging/ru/followthrough_t390_context_pool.json",
    "staging/ru/followthrough_t391_context_pool.json",
    "staging/ru/followthrough_t392_context_pool.json",
    "staging/ru/followthrough_t393_context_pool.json",
    "staging/ru/followthrough_t394_context_pool.json",
    "staging/ru/followthrough_t395_context_pool.json",
    "staging/ru/followthrough_t396_context_pool.json",
    "staging/ru/followthrough_t397_context_pool.json",
    "staging/ru/followthrough_t398_context_pool.json",
    "staging/ru/followthrough_t399_context_pool.json",
    "staging/ru/followthrough_t400_context_pool.json",
    "staging/ru/followthrough_t401_context_pool.json",
    "staging/ru/followthrough_t402_context_pool.json",
    "staging/ru/followthrough_t403_context_pool.json",
    "staging/ru/followthrough_t404_context_pool.json",
    "staging/ru/followthrough_t405_context_pool.json",
    "staging/ru/followthrough_t406_context_pool.json",
    "staging/ru/followthrough_t407_context_pool.json",
    "staging/ru/followthrough_t408_context_pool.json",
    "staging/ru/followthrough_t409_context_pool.json",
    "staging/ru/followthrough_t410_context_pool.json",
    "staging/ru/followthrough_t411_context_pool.json",
    "staging/ru/followthrough_t412_context_pool.json",
    "staging/ru/followthrough_t413_context_pool.json",
    "staging/ru/followthrough_t414_context_pool.json",
    "staging/ru/followthrough_t415_context_pool.json",
    "staging/ru/followthrough_t416_context_pool.json",
    "staging/ru/followthrough_t417_context_pool.json",
    "staging/ru/followthrough_t418_context_pool.json",
    "staging/ru/followthrough_t419_context_pool.json",
    "staging/ru/followthrough_t420_context_pool.json",
    "staging/ru/followthrough_t421_context_pool.json",
    "staging/ru/followthrough_t422_context_pool.json",
    "staging/ru/followthrough_t424_context_pool.json",
    "staging/ru/followthrough_t425_context_pool.json",
    "staging/ru/followthrough_t427_context_pool.json",
    "staging/ru/followthrough_t428_context_pool.json",
    "staging/ru/followthrough_t429_context_pool.json",
    "staging/ru/followthrough_t430_context_pool.json",
    "staging/ru/followthrough_t431_context_pool.json",
    "staging/ru/followthrough_t432_context_pool.json",
    "staging/ru/followthrough_t433_context_pool.json",
    "staging/ru/followthrough_t434_context_pool.json",
    "staging/ru/followthrough_t436_context_pool.json",
    "staging/ru/followthrough_t438_context_pool.json",
    "staging/ru/followthrough_t439_context_pool.json",
    "staging/ru/followthrough_t440_context_pool.json",
    "staging/ru/followthrough_t441_context_pool.json",
    "staging/ru/followthrough_t442_context_pool.json",
    "staging/ru/followthrough_t444_context_pool.json",
    "staging/ru/followthrough_t445_context_pool.json",
    "staging/ru/followthrough_t446_context_pool.json",
    "staging/ru/followthrough_t448_context_pool.json",
    "staging/ru/followthrough_t449_context_pool.json",
    "staging/ru/followthrough_t450_context_pool.json",
    "staging/ru/followthrough_t451_context_pool.json",
    "staging/ru/followthrough_t452_context_pool.json",
    "staging/ru/followthrough_t454_context_pool.json",
    "staging/ru/followthrough_t455_context_pool.json",
    "staging/ru/followthrough_t456_context_pool.json",
    "staging/ru/followthrough_t458_context_pool.json",
    "staging/ru/followthrough_t459_context_pool.json",
    "staging/ru/followthrough_t460_context_pool.json",
    "staging/ru/followthrough_t461_context_pool.json",
    "staging/ru/followthrough_t462_context_pool.json",
    "staging/ru/followthrough_t463_context_pool.json",
    "staging/ru/followthrough_t464_context_pool.json",
    "staging/ru/followthrough_t465_context_pool.json",
    "staging/ru/followthrough_t466_context_pool.json",
    "staging/ru/followthrough_t467_context_pool.json",
    "staging/ru/followthrough_t468_context_pool.json",
)
SOURCE = "packs/ru/conversation_followthrough_qa.json"
CONTEXTS = frozenset({"direct", "private", "group_addressed"})


class FollowthroughStageCatalog:
    """Index already reviewed stages; choose only caller-authorized replies.

    The constructor validates immutable source and staged Git blobs via each
    StagedContextSelector, exact canonical intent inventory, IDs and uniqueness.
    This is a reference for use by a separately verified consumer, not a bot.
    """

    def __init__(self, root: Path = ROOT):
        root = Path(root).resolve(strict=True)
        manifest_bytes = (root / "manifest.json").read_bytes()
        manifest = json.loads(manifest_bytes)
        hashes = {p["path"]: p["sha256"] for p in manifest["packs"]}
        if SOURCE not in hashes:
            raise ValueError("unregistered followthrough source")
        source_bytes = (root / SOURCE).read_bytes()
        if hashlib.sha256(source_bytes).hexdigest() != hashes[SOURCE]:
            raise ValueError("source digest mismatch")
        source = json.loads(source_bytes)
        canon = {r["id"]: r["question"] for r in source["records"]}
        if len(canon) != 82 or len(source["records"]) != 82:
            raise ValueError("expected 82 existing canonical intentions")

        digest = hashlib.sha256(manifest_bytes)
        seen_ids, seen_texts = set(), set()
        by_intent = {ident: [] for ident in canon}
        selectors = []

        for path in STAGES:
            # This loader verifies the individual stage, all fixed Git blobs,
            # parent chain, language, scope and fail-closed opt-in contract.
            selectors.append(StagedContextSelector(root, path))
            raw = (root / path).read_bytes()
            digest.update(path.encode("utf-8") + b"\0" + raw)
            data = json.loads(raw)
            if data.get("consumer_registered") is not False:
                raise ValueError("staged file must not pretend to be registered")
            entries = data.get("entries")
            if (not isinstance(entries, list) or len(entries) != 82
                    or {x.get("intent_id") for x in entries} != set(canon)):
                raise ValueError("wrong reviewed stage inventory")
            for row in entries:
                ident = row["intent_id"]
                if row.get("question") != canon[ident]:
                    raise ValueError("changed canonical question")
                for reply in row["replies"]:
                    rid, text = reply["id"], _norm(reply["text"])
                    if rid in seen_ids or not text or text in seen_texts:
                        raise ValueError("duplicate cross-stage answer")
                    seen_ids.add(rid)
                    seen_texts.add(text)
                    by_intent[ident].append((path, rid))

        if (len(seen_ids) != 6560 or len(by_intent) != 82
                or any(len(items) != 80 for items in by_intent.values())):
            raise ValueError("incomplete or inconsistent seventy-eight-stage catalog")
        # Newest stage gets the first chance but only among explicitly
        # approved IDs; no automatic interpretation or hidden randomness.
        self._selectors = tuple(reversed(selectors))
        self._by_intent = {k: frozenset(rid for _, rid in v)
                           for k, v in by_intent.items()}
        self.intent_count = len(by_intent)
        self.reply_count = len(seen_ids)
        self.registered_reply_count = sum(1 + len(r.get("variants", []))
                                          for r in source["records"])
        if self.registered_reply_count != 246:
            raise ValueError("unexpected registered baseline")
        self.cache_identity = (manifest["knowledge_version"], digest.hexdigest())

    def select(
        self, intent_id: str, *, approved_reply_ids: frozenset[str],
        audience: str, context: str, addressed: bool = False,
        local_permission: bool = False, recent_ids: tuple[str, ...] = (),
    ) -> StagedSelection | None:
        """Return one read-only candidate after verified consumer-side opt-in."""
        if (addressed is not True or local_permission is not True
                or audience != "all_ai_bots" or context not in CONTEXTS
                or not isinstance(approved_reply_ids, frozenset)
                or not approved_reply_ids or len(approved_reply_ids) > 100
                or any(not isinstance(x, str) for x in approved_reply_ids)
                or not isinstance(recent_ids, tuple) or len(recent_ids) > 100
                or any(not isinstance(x, str) for x in recent_ids)):
            return None
        eligible = self._by_intent.get(intent_id)
        if not eligible or not approved_reply_ids.intersection(eligible):
            return None
        for selector in self._selectors:
            selected = selector.select(
                intent_id, approved_reply_ids=approved_reply_ids,
                audience=audience, context=context, addressed=addressed,
                local_permission=local_permission, recent_ids=recent_ids,
            )
            if selected is not None:
                return selected
        return None
