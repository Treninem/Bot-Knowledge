"""Conservative RU/EN corrections of explicit numeric constraints (no actions).

The caller supplies a stable slot name, an exact inflected unit and the current
numeric state. Never infer chat rules, entities, units or intent from history.
"""
from __future__ import annotations

import hashlib
import json
import re
import unicodedata
from functools import lru_cache
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PACK = "packs/ru/numeric_repairs.json"
POLICY = {
    "synthetic_examples_only": True,
    "personal_data_allowed": False,
    "automatic_actions_allowed": False,
    "automatic_sanctions_allowed": False,
    "caller_supplies_context": True,
    "explicit_address_required": True,
    "no_persistent_memory": True,
}
NUMBER = r"(?P<{}>0|[1-9][0-9]{{0,3}})"


def compact(value: str) -> str | None:
    """Reject quotes, embedded instructions, unsafe delimiters and mixed scripts."""
    if not isinstance(value, str) or not 1 <= len(value) <= 180:
        return None
    value = unicodedata.normalize("NFKC", value).casefold().replace("ё", "е")
    if re.search(r"[^a-zа-я0-9\s,.!?]", value) or "\n" in value or "\r" in value:
        return None
    value = re.sub(r"[,.!?]", " ", value)
    return " ".join(value.split()) or None


@lru_cache(maxsize=128)
def patterns(language: str, unit: str) -> tuple[re.Pattern, ...]:
    clean = compact(unit)
    if (language not in {"ru", "en"} or clean is None or len(clean) > 32
            or not re.fullmatch(r"[a-zа-я]+(?: [a-zа-я]+)?", clean)):
        raise ValueError("Unsupported language or unit")
    u = re.escape(clean)
    old, new = NUMBER.format("old"), NUMBER.format("new")
    if language == "ru":
        grammars = (
            rf"не {old} а {new} {u}",
            rf"исправь {old} {u} на {new} {u}",
            rf"вместо {old} {u} сделай {new} {u}",
            rf"поменяй {old} {u} на {new} {u}",
        )
    else:
        grammars = (
            rf"not {old} but {new} {u}",
            rf"change {old} {u} to {new} {u}",
            rf"use {new} {u} instead of {old} {u}",
            rf"replace {old} {u} with {new} {u}",
        )
    return tuple(re.compile(r"\A" + grammar + r"\Z") for grammar in grammars)


def load_pack(root: Path = ROOT) -> dict:
    manifest = json.loads((root / "manifest.json").read_text(encoding="utf-8"))
    expected = [entry["sha256"] for entry in manifest["packs"] if entry["path"] == PACK]
    if len(expected) != 1:
        raise ValueError("Missing or duplicate numeric repair pack")
    raw = (root / PACK).read_bytes()
    if hashlib.sha256(raw).hexdigest() != expected[0]:
        raise ValueError("Numeric repair SHA-256 mismatch")
    book = json.loads(raw.decode("utf-8"))
    if (book.get("schema_version") != 1 or book.get("pack_version") != "2026.10.30.15"
            or book.get("language") != "multilingual" or book.get("usage_policy") != POLICY):
        raise ValueError("Unsafe numeric repair pack")
    return book


class NumericRepair:
    """Stateless proposal; the embedding consumer must review/commit changes."""

    def __init__(self, root: Path = ROOT):
        self.book = load_pack(root)

    def propose(self, message: str, *, language: str, state: dict[str, str],
                slot: str, unit: str, addressed: bool = False,
                quoted: bool = False) -> dict:
        if language not in {"ru", "en"}:
            raise ValueError("Unsupported language")
        if (not isinstance(state, dict) or not 1 <= len(state) <= 8
                or not isinstance(slot, str)
                or not re.fullmatch(r"[a-z][a-z0-9_]{0,39}", slot)
                or any(not isinstance(k, str) or not re.fullmatch(r"[a-z][a-z0-9_]{0,39}", k)
                       for k in state)):
            raise ValueError("Invalid bounded caller context")
        grammar = patterns(language, unit)
        if not addressed:
            return {"status": "not_addressed"}
        if quoted:
            return {"status": "quoted_ignored"}
        if slot not in state:
            return {"status": "no_context"}
        current = state[slot]
        if (not isinstance(current, str) or not re.fullmatch(r"0|[1-9][0-9]{0,3}", current)):
            raise ValueError("Current slot must be a canonical integer in 0..9999")
        source = compact(message)
        if source is None:
            return {"status": "unrecognized"}
        for pattern in grammar:
            found = pattern.fullmatch(source)
            if found:
                old, new = found.group("old"), found.group("new")
                if int(old) != int(current):
                    return {"status": "stale_context"}
                if old == new:
                    return {"status": "no_change"}
                proposed = dict(state)
                proposed[slot] = new
                return {"status": "updated", "slot": slot, "previous": old,
                        "new": new, "state": proposed}
        return {"status": "unrecognized"}
