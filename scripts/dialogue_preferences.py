"""Offline RU/EN style-preference guard. Enum-only memory per isolated session."""
from __future__ import annotations

import hashlib
import json
import re
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PACK = "packs/ru/style_preferences.json"
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


class PreferenceSession:
    """Separate instance per conversation. No texts, identity or history stored."""

    def __init__(self, book: dict, ttl_turns: int = 12):
        if type(ttl_turns) is not int or not 1 <= ttl_turns <= 100:
            raise ValueError("Invalid ttl_turns")
        self.ttl_turns = ttl_turns
        self.turn = 0
        self.rules: dict[str, tuple[str, int]] = {}
        self.examples = {}
        for row in book["cases"]:
            lookup = (row["language"], normalize(row["input"]))
            if lookup in self.examples or row["dimension"] not in DIMENSIONS:
                raise ValueError("Duplicate or unsupported preference")
            self.examples[lookup] = (row["dimension"], row["value"])

    def clear(self) -> None:
        self.rules.clear()
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
        self.rules[dimension] = (value, self.turn)
        return {"status": "updated", "dimension": dimension, "value": value}

    def snapshot(self, *, sensitive: bool = False) -> dict[str, str | None]:
        result = {name: (self.rules[name][0] if name in self.rules else None)
                  for name in DIMENSIONS}
        if sensitive:
            for name in ("humor", "dark_humor", "profanity"):
                result[name] = "disabled"
        elif result["humor"] == "disabled":
            result["dark_humor"] = "disabled"
        return result

    def routing_hints(self, *, sensitive: bool = False) -> dict:
        """Optional safe kwargs for existing ConversationRouter.reply."""
        state = self.snapshot(sensitive=sensitive)
        return {"dark_opt_in": state["dark_humor"] == "enabled",
                "strong_opt_in": state["profanity"] == "enabled",
                "sensitive": bool(sensitive),
                "tone": "casual" if state["formality"] == "casual" else "neutral"}
