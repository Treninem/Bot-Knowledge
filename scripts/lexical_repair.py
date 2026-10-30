"""Offline, fail-closed RU/EN lexical corrections against caller-approved choices.

Only proposes a replacement to the embedding application. No writes, user memory,
moderation actions, identity inference, network access or persistent conversation state.
"""
from __future__ import annotations

import hashlib
import json
import re
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PACK = "packs/ru/lexical_repairs.json"
POLICY = {
    "synthetic_examples_only": True,
    "personal_data_allowed": False,
    "automatic_actions_allowed": False,
    "automatic_sanctions_allowed": False,
    "caller_supplies_context": True,
    "explicit_address_required": True,
    "no_persistent_memory": True,
    "caller_must_review_proposal": True,
}
SLOT = re.compile(r"[a-z][a-z0-9_]{0,39}\Z")
VALUE = {"ru": re.compile(r"[а-я]+(?: [а-я]+)?\Z"),
         "en": re.compile(r"[a-z]+(?: [a-z]+)?\Z")}
MESSAGE = {"ru": re.compile(r"[а-я ,:.!?]+\Z"),
           "en": re.compile(r"[a-z ,:.!?]+\Z")}


def canonical_value(value: str, language: str) -> str:
    """Recognize short, plain lexical labels supplied by a trusted caller."""
    if language not in VALUE or not isinstance(value, str) or not 1 <= len(value) <= 32:
        raise ValueError("Invalid lexical choice or language")
    result = unicodedata.normalize("NFKC", value).casefold().replace("ё", "е")
    if not VALUE[language].fullmatch(result):
        raise ValueError("Choice must be a canonical one/two-word lexical label")
    return result


def compact_message(value: str, language: str) -> str | None:
    """Keep commas/colons; reject quotes, code, mixed alphabets and extra clauses."""
    if language not in MESSAGE or not isinstance(value, str) or not 1 <= len(value) <= 180:
        return None
    if any(unicodedata.category(c).startswith("C") for c in value):
        return None
    result = unicodedata.normalize("NFKC", value).casefold().replace("ё", "е")
    if not MESSAGE[language].fullmatch(result):
        return None
    result = " ".join(result.split())
    if result.endswith((".", "!", "?")):
        result = result[:-1]
    if not result or any(c in ".!?" for c in result):
        return None
    return result


def patterns(language: str, choices: tuple[str, ...]) -> tuple[re.Pattern, ...]:
    # Every captured label must come from the caller's approved value set.
    values = sorted(choices, key=len, reverse=True)
    value = "(?:" + "|".join(re.escape(x) for x in values) + ")"
    old, new = f"(?P<old>{value})", f"(?P<new>{value})"
    if language == "ru":
        sources = (
            rf"не {old},? а {new}",
            rf"замени {old} на {new}",
            rf"я имел в виду {new},? не {old}",
            rf"поправка: не {old},? а {new}",
        )
    else:
        sources = (
            rf"not {old},? but {new}",
            rf"replace {old} with {new}",
            rf"i meant {new},? not {old}",
            rf"correction: use {new},? not {old}",
        )
    return tuple(re.compile(r"\A" + source + r"\Z") for source in sources)


def load_pack(root: Path = ROOT) -> dict:
    manifest = json.loads((root / "manifest.json").read_text(encoding="utf-8"))
    matches = [item["sha256"] for item in manifest["packs"] if item["path"] == PACK]
    if len(matches) != 1:
        raise ValueError("Lexical correction pack absent or duplicated in manifest")
    raw = (root / PACK).read_bytes()
    if hashlib.sha256(raw).hexdigest() != matches[0]:
        raise ValueError("Lexical correction SHA-256 mismatch")
    book = json.loads(raw.decode("utf-8"))
    if (book.get("schema_version") != 1
            or book.get("pack_version") != "2026.10.30.18"
            or book.get("language") != "multilingual"
            or book.get("usage_policy") != POLICY):
        raise ValueError("Unsafe lexical correction pack")
    return book


class LexicalRepair:
    """A stateless suggestion engine; caller decides if/how to use its result."""

    def __init__(self, root: Path = ROOT):
        self.book = load_pack(root)

    def propose(self, message: str, *, language: str, state: dict,
                slot: str, choices: list[str], addressed: bool = False,
                quoted: bool = False) -> dict:
        if language not in VALUE:
            raise ValueError("Unsupported language")
        if (not isinstance(state, dict) or not 1 <= len(state) <= 8
                or not isinstance(slot, str) or SLOT.fullmatch(slot) is None
                or any(not isinstance(key, str) or SLOT.fullmatch(key) is None
                       for key in state)):
            raise ValueError("Invalid caller context")
        if (not isinstance(choices, list) or not 2 <= len(choices) <= 12):
            raise ValueError("Invalid approved choices")
        approved = tuple(canonical_value(item, language) for item in choices)
        if len(approved) != len(set(approved)):
            raise ValueError("Repeated approved lexical choice")
        if not addressed:
            return {"status": "not_addressed"}
        if quoted:
            return {"status": "quoted_ignored"}
        if slot not in state:
            return {"status": "no_context"}
        current = canonical_value(state[slot], language)
        if current not in approved:
            raise ValueError("Current value must be one of the approved choices")
        sentence = compact_message(message, language)
        if sentence is None:
            return {"status": "unrecognized"}
        for expression in patterns(language, approved):
            match = expression.fullmatch(sentence)
            if match is None:
                continue
            old, new = match.group("old"), match.group("new")
            if old != current:
                return {"status": "stale_context"}
            if old == new:
                return {"status": "no_change"}
            return {"status": "proposal", "slot": slot,
                    "previous": current, "new": new}
        return {"status": "unrecognized"}
