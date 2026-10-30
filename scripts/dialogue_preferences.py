"""Offline RU/EN style-preference guard. Enum-only memory per isolated session."""
from __future__ import annotations

import hashlib
import json
import re
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PACK = "packs/ru/style_preferences.json"
SCOPED_PACK = "packs/ru/scoped_style_requests.json"
WORD = re.compile(r"[^\W_]+", re.UNICODE)
DIMENSIONS = ("questions", "humor", "profanity", "dark_humor", "suggestions",
              "greetings", "verbosity", "formality", "emoji", "metaphors")


def normalize(text: str) -> str:
    value = unicodedata.normalize("NFKC", text).casefold().replace("ё", "е")
    return " ".join(WORD.findall(value))


def load_preferences(root: Path = ROOT) -> dict:
    manifest = json.loads((root / "manifest.json").read_text(encoding="utf-8"))
    hashes = [x["sha256"] for x in manifest["packs"] if x["path"] == PACK]
    if len(hashes) != 1:
        raise ValueError("Preference pack absent or duplicated in manifest")
    raw = (root / PACK).read_bytes()
    if hashlib.sha256(raw).hexdigest() != hashes[0]:
        raise ValueError("Preference SHA-256 mismatch")
    book = json.loads(raw.decode("utf-8"))
    if book.get("schema_version") != 1 or book.get("language") != "multilingual":
        raise ValueError("Unsupported preference pack")
    return book


def load_scoped_requests(root: Path = ROOT) -> dict:
    """Read an approved, SHA-checked scoped style package (no remote calls)."""
    manifest = json.loads((root / "manifest.json").read_text(encoding="utf-8"))
    hashes = [x["sha256"] for x in manifest["packs"] if x["path"] == SCOPED_PACK]
    if len(hashes) != 1:
        raise ValueError("Scoped preference pack absent or duplicated in manifest")
    raw = (root / SCOPED_PACK).read_bytes()
    if hashlib.sha256(raw).hexdigest() != hashes[0]:
        raise ValueError("Scoped preference SHA-256 mismatch")
    book = json.loads(raw.decode("utf-8"))
    if book.get("schema_version") != 1 or book.get("language") != "multilingual":
        raise ValueError("Unsupported scoped preference pack")
    return book


class PreferenceSession:
    """Separate instance per conversation. No texts, identity or history stored."""

    def __init__(self, book: dict, ttl_turns: int = 12, scoped_book: dict | None = None, composer=None):
        if type(ttl_turns) is not int or not 1 <= ttl_turns <= 100:
            raise ValueError("Invalid ttl_turns")
        self.ttl_turns = ttl_turns
        self.turn = 0
        self.rules: dict[str, tuple[str, int]] = {}
        self.examples = {}
        self.scoped_examples = {}
        self.composer = composer
        self.one_reply: dict[str, str] = {}
        self.session_rules: dict[str, str] = {}
        for row in book["cases"]:
            lookup = (row["language"], normalize(row["input"]))
            if lookup in self.examples or row["dimension"] not in DIMENSIONS:
                raise ValueError("Duplicate or unsupported preference")
            self.examples[lookup] = (row["dimension"], row["value"])
        if scoped_book is not None:
            for row in scoped_book["cases"]:
                lookup = (row["language"], normalize(row["input"]))
                if lookup in self.examples or lookup in self.scoped_examples:
                    raise ValueError("Duplicate scoped preference input")
                if row["dimension"] not in DIMENSIONS or row["scope"] not in {"one_reply", "session"}:
                    raise ValueError("Unsafe scoped preference")
                self.scoped_examples[lookup] = (row["dimension"], row["value"], row["scope"])

    def clear(self) -> None:
        self.rules.clear()
        self.session_rules.clear()
        self.one_reply.clear()
        self.turn = 0

    def advance(self, turns: int = 1) -> None:
        if type(turns) is not int or not 1 <= turns <= 100:
            raise ValueError("Invalid number of turns")
        self.turn += turns
        self.rules = {key: entry for key, entry in self.rules.items()
                      if self.turn - entry[1] <= self.ttl_turns}

    def observe(self, message: str, *, language: str,
                addressed: bool = False, quoted: bool = False) -> dict:
        if language not in {"ru", "en"}:
            raise ValueError("Unsupported language")
        if not addressed:
            return {"status": "not_addressed"}
        if quoted:
            return {"status": "quoted_ignored"}
        match = self.examples.get((language, normalize(message)))
        if match is None:
            return {"status": "unknown_input"}
        dimension, value = match
        self.session_rules.pop(dimension, None)
        self.one_reply.pop(dimension, None)
        self.rules[dimension] = (value, self.turn)
        return {"status": "updated", "dimension": dimension, "value": value}

    def observe_scoped(self, message: str, *, language: str,
                       addressed: bool = False, quoted: bool = False) -> dict:
        """Accept only explicit whole-message scope instructions, never quotes or fragments."""
        if language not in {"ru", "en"}:
            raise ValueError("Unsupported language")
        if not addressed:
            return {"status": "not_addressed"}
        if quoted:
            return {"status": "quoted_ignored"}
        match = self.scoped_examples.get((language, normalize(message)))
        if match is None:
            return {"status": "unknown_input"}
        dimension, value, scope = match
        if scope == "one_reply":
            self.one_reply[dimension] = value
        else:
            self.session_rules[dimension] = value
            self.one_reply.pop(dimension, None)
        return {"status": "updated", "dimension": dimension,
                "value": value, "scope": scope}

    def observe_composed(self, message: str, *, language: str,
                         addressed: bool = False, quoted: bool = False) -> dict:
        """Apply only a complete approved RU/EN compositional request."""
        if self.composer is None:
            return {"status": "composable_unavailable"}
        result = self.composer.match(message, language=language, addressed=addressed, quoted=quoted)
        if result["status"] != "updated":
            return result
        dimension, value, scope = result["dimension"], result["value"], result["scope"]
        if scope == "one_reply":
            self.one_reply[dimension] = value
        else:
            self.session_rules[dimension] = value
            self.one_reply.pop(dimension, None)
        return result

    def snapshot(self, *, sensitive: bool = False) -> dict[str, str | None]:
        result = {name: (self.rules[name][0] if name in self.rules else None)
                  for name in DIMENSIONS}
        result.update(self.session_rules)
        result.update(self.one_reply)
        if sensitive:
            for name in ("humor", "dark_humor", "profanity"):
                result[name] = "disabled"
        elif result["humor"] == "disabled":
            result["dark_humor"] = "disabled"
        return result

    def consume_for_reply(self, *, sensitive: bool = False) -> dict[str, str | None]:
        """Return effective style and consume one-reply overrides once only."""
        state = self.snapshot(sensitive=sensitive)
        self.one_reply.clear()
        return state

    def routing_hints(self, *, sensitive: bool = False, consume: bool = False) -> dict:
        """Optional safe kwargs for existing ConversationRouter.reply."""
        state = self.consume_for_reply(sensitive=sensitive) if consume else self.snapshot(sensitive=sensitive)
        return {"dark_opt_in": state["dark_humor"] == "enabled",
                "strong_opt_in": state["profanity"] == "enabled",
                "sensitive": bool(sensitive),
                "tone": "casual" if state["formality"] == "casual" else "neutral"}
