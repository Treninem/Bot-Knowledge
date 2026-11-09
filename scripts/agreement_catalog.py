"""Opt-in, SHA-verified conversational agreement suggestions.

No natural-language inference, global memory, network or actions. An approved
consumer must first confirm the prior conversation context and direct address.
"""
from __future__ import annotations

import hashlib
import json
import re
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PACK = "packs/ru/dialogue.json"
AUDIENCE = "all_ai_bots"


def norm(text: str) -> str:
    text = unicodedata.normalize("NFKC", text).casefold().replace("ё", "е")
    return " ".join(re.findall(r"[\w]+", text, flags=re.UNICODE))


class AgreementCatalog:
    """Read-only, deterministic selector using a verified immutable snapshot."""

    def __init__(self, root: Path = ROOT):
        root = Path(root)
        manifest = json.loads((root / "manifest.json").read_text(encoding="utf-8"))
        matches = [x for x in manifest.get("packs", []) if x.get("path") == PACK]
        if manifest.get("schema_version") != 1 or manifest.get("language") != "ru" or len(matches) != 1:
            raise ValueError("untrusted manifest")
        raw = (root / PACK).read_bytes()
        digest = hashlib.sha256(raw).hexdigest()
        if matches[0].get("sha256") != digest:
            raise ValueError("dialogue SHA mismatch")
        obj = json.loads(raw.decode("utf-8"))
        meta = obj.get("agreement_catalog", {})
        expected = {"schema_version": 1, "intent": "agreement",
                    "section": "общение", "language": "ru",
                    "audiences": [AUDIENCE], "synthetic_examples_only": True,
                    "automatic_sanctions_allowed": False, "personal_data_allowed": False,
                    "requires_explicit_address": True, "requires_local_permission": True,
                    "default_context": "neutral"}
        if any(meta.get(k) != v or type(meta.get(k)) != type(v) for k, v in expected.items()):
            raise ValueError("agreement policy")
        legacy = obj.get("reactions", {}).get("agreement")
        contexts = meta.get("contexts")
        conditions = meta.get("context_conditions")
        inputs = meta.get("accepted_inputs")
        if (not isinstance(legacy, list) or len(legacy) != 2
                or not isinstance(contexts, dict) or len(contexts) != 25
                or "neutral" not in contexts or not isinstance(conditions, dict)
                or set(conditions) != set(contexts)
                or not isinstance(inputs, list) or len(inputs) != 4
                or inputs != ["согласен", "согласна", "договорились", "давай так"]):
            raise ValueError("agreement catalog structure")
        seen = {norm(s) for s in legacy}
        groups = {}
        counts = []
        for key, replies in contexts.items():
            if not isinstance(key, str) or not re.fullmatch(r"[a-z][a-z_]*", key):
                raise ValueError("unsafe context")
            note = conditions[key]
            if not isinstance(note, str) or not 40 <= len(note) <= 300:
                raise ValueError("insufficient selection condition")
            if not isinstance(replies, list) or not 3 <= len(replies) <= 4:
                raise ValueError("bad context reply count")
            for item in replies:
                if (not isinstance(item, str) or not 12 <= len(item) <= 300
                        or norm(item) in seen
                        or re.search(r"(?i)(ghp_[a-z0-9]{12,}|sk-[a-z0-9]{12,}|https?://|@[a-z0-9_]+)", item)):
                    raise ValueError("duplicate, unsafe or invalid reply")
                seen.add(norm(item))
            groups[key] = tuple(replies)
            counts.append(len(replies))
        if sum(counts) != 98 or counts.count(3) != 2 or counts.count(4) != 23 or len(seen) != 100:
            raise ValueError("incomplete 100/100 agreement catalog")
        self._groups = groups
        self._conditions = dict(conditions)
        self._inputs = frozenset(norm(x) for x in inputs)
        self.snapshot_key = (manifest["knowledge_version"], digest)

    def reply(
        self, message: str, *, addressed: bool = False,
        local_permission: bool = False, context: str = "neutral",
        audience: str = AUDIENCE, language: str = "ru",
        sensitive: bool = False, silence_requested: bool = False,
        recent: tuple[str, ...] = (),
    ) -> dict:
        if not isinstance(message, str) or len(message) > 1000:
            raise ValueError("invalid message")
        if any(type(flag) is not bool for flag in
               (addressed, local_permission, sensitive, silence_requested)):
            raise ValueError("invalid trust flags")
        if (not isinstance(recent, (list, tuple)) or len(recent) > 128
                or any(not isinstance(t, str) or len(t) > 1000 for t in recent)):
            raise ValueError("invalid caller-local history")
        if audience != AUDIENCE or context not in self._groups:
            raise ValueError("unsupported audience or context")

        def deny(reason: str) -> dict:
            return {"status": reason, "text": None}

        if not addressed:
            return deny("not_addressed")
        if not local_permission:
            return deny("not_authorized")
        if sensitive or silence_requested:
            return deny("suppressed")
        if language != "ru":
            return deny("wrong_language")
        normalized_message = unicodedata.normalize("NFKC", message).casefold().strip()
        if (not re.fullmatch(r"[а-яё ,.!\s]+", normalized_message)
                or norm(normalized_message) not in self._inputs):
            return deny("no_match")
        history = {norm(v) for v in recent}
        for index, answer in enumerate(self._groups[context], 1):
            if norm(answer) not in history:
                return {"status": "ok", "text": answer,
                        "source_pack": PACK,
                        "source_id": f"agreement_{context}_{index:02}",
                        "context": context,
                        "selection_condition": self._conditions[context],
                        "snapshot_key": self.snapshot_key}
        return deny("repeat_suppressed")
