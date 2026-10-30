"""Strict bounded RU/EN style composition with no action authority.

A caller must explicitly mark an instruction as addressed, supply the locale and
isolate its own PreferenceSession. Neither this matcher nor the knowledge pack
can execute messages, moderate chats or authorize offensive speech.
"""
from __future__ import annotations

import hashlib
import json
import re
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PACK = "packs/ru/composable_style.json"
POLICY = {"synthetic_examples_only": True, "personal_data_allowed": False,
          "automatic_actions_allowed": False, "automatic_sanctions_allowed": False,
          "caller_owns_context": True, "explicit_address_required": True,
          "ephemeral_only": True}
FORBIDDEN = {chr(c) for c in (34, 39, 171, 187, 8220, 8221, 8222, 8216, 8217, 96, 60, 62, 91, 93, 123, 125, 92, 124, 59, 58, 47, 13, 10)}
WORD = re.compile(r"[^\W_]+", re.UNICODE)


def normalized(text: str) -> str:
    return " ".join(WORD.findall(unicodedata.normalize("NFKC", text).casefold().replace("ё", "е")))


def load_composable_style(root: Path = ROOT) -> dict:
    manifest = json.loads((root / "manifest.json").read_text(encoding="utf-8"))
    hashes = [entry["sha256"] for entry in manifest["packs"] if entry["path"] == PACK]
    if len(hashes) != 1:
        raise ValueError("Missing or duplicated composable style package")
    raw = (root / PACK).read_bytes()
    if hashlib.sha256(raw).hexdigest() != hashes[0]:
        raise ValueError("Composable style SHA-256 mismatch")
    book = json.loads(raw.decode("utf-8"))
    if (book.get("schema_version") != 1 or book.get("language") != "multilingual"
            or book.get("pack_version") != "2026.10.30.16"
            or book.get("usage_policy") != POLICY):
        raise ValueError("Unsafe composable style metadata or policy")
    return book


class ComposableStyle:
    """Read-only approved grammar; lookup is local and deterministic."""

    def __init__(self, root: Path = ROOT):
        self.book = load_composable_style(root)
        self.lookup: dict[tuple[str, str], tuple[str, str, str]] = {}
        for row in self.book["directives"]:
            for language in ("ru", "en"):
                for scope in ("one_reply", "session"):
                    for prefix in self.book["scope_prefixes"][language][scope]:
                        phrase = normalized(prefix + " " + row[language])
                        key = (language, phrase)
                        value = (row["dimension"], row["value"], scope)
                        if key in self.lookup:
                            raise ValueError("Ambiguous or repeated composable rule")
                        self.lookup[key] = value

    def match(self, message: str, *, language: str,
              addressed: bool = False, quoted: bool = False) -> dict:
        if language not in {"ru", "en"}:
            raise ValueError("Unsupported language")
        if not addressed:
            return {"status": "not_addressed"}
        if quoted:
            return {"status": "quoted_ignored"}
        if not isinstance(message, str) or not 12 <= len(message) <= 180:
            return {"status": "unknown_input"}
        raw = unicodedata.normalize("NFKC", message)
        if any(char in FORBIDDEN for char in raw):
            return {"status": "unknown_input"}
        if not re.fullmatch(r"[\w\s,.!?]+", raw):
            return {"status": "unknown_input"}
        found = self.lookup.get((language, normalized(raw)))
        if found is None:
            return {"status": "unknown_input"}
        dimension, value, scope = found
        return {"status": "updated", "dimension": dimension,
                "value": value, "scope": scope}
