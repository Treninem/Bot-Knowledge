"""Bounded in-memory follow-up focus for RU/EN, using the existing referent resolver.

An embedding application must instantiate ONE object per isolated conversation,
provide trusted candidate objects and explicitly pin a confirmed focus. No chat
logs, private identifiers, networking, permissions, actions or persistence.
"""
from __future__ import annotations

import argparse
import json
from resolve_referents import (ALL, BOTH, ORD, VERBS, norm, resolve,
                               validate_candidates)

PRONOUNS = {
    "ru": {"его", "ее", "это", "этот", "эту", "тот", "ту"},
    "en": {"it", "this", "that"},
}
BLOCK_FOCUS = {
    "ru": {"не", "никогда", "кроме", "без", "и", "или", "а", "оба", "обе", "все"},
    "en": {"not", "never", "except", "without", "and", "or", "but",
           "both", "all", "every", "them", "those"},
}


class TurnFocus:
    """Only short-lived candidate labels and confirmed opaque IDs are retained."""

    def __init__(self, *, max_candidates: int = 8, ttl_turns: int = 2) -> None:
        if (type(max_candidates) is not int or not 1 <= max_candidates <= 12
                or type(ttl_turns) is not int or not 1 <= ttl_turns <= 20):
            raise ValueError("Invalid memory bounds")
        self.max_candidates = max_candidates
        self.ttl_turns = ttl_turns
        self.clear()

    def clear(self) -> None:
        self._items: list[dict] = []
        self._language: str | None = None
        self._focus: str | None = None
        self._age = 0

    @property
    def state(self) -> dict:
        # Do not expose private labels, user messages or object IDs.
        return {"candidate_count": len(self._items), "focus_confirmed": self._focus is not None,
                "age_turns": self._age, "language": self._language}

    def present(self, candidates: list[dict], *, language: str) -> None:
        if language not in PRONOUNS:
            raise ValueError("Unknown language")
        validate_candidates(candidates)
        if len(candidates) > self.max_candidates:
            raise ValueError("Candidate limit exceeded")
        # Replace (never merge) the caller-supplied scope; focus cannot leak.
        self._items = [dict(entry) for entry in candidates]
        self._language = language
        self._focus = None
        self._age = 0

    def pin(self, identifier: str) -> None:
        if not any(item["id"] == identifier for item in self._items):
            raise ValueError("Focus must be a confirmed current candidate ID")
        self._focus = identifier

    def advance(self, turns: int = 1) -> None:
        if type(turns) is not int or not 1 <= turns <= 100:
            raise ValueError("Invalid turn advance")
        self._age += turns
        if self._age > self.ttl_turns:
            self.clear()

    def _can_use_focus(self, message: str, language: str) -> bool:
        words = set(norm(message).split())
        if not words.intersection(PRONOUNS[language]):
            return False
        if not words.intersection(VERBS[language]):
            return False
        if (words.intersection(BLOCK_FOCUS[language])
                or words.intersection(ORD[language])
                or words.intersection(ALL[language])
                or words.intersection(BOTH[language])):
            return False
        phrase = " " + norm(message) + " "
        # An explicit label overrides any previously pinned object. A partial
        # name is never guessed, nor is a collective or ordinal reference.
        return not any(" " + norm(item["label"]) + " " in phrase for item in self._items)

    def choose(self, message: str, *, language: str, addressed: bool = False,
               require_confirmation: bool = False) -> dict:
        if language not in PRONOUNS:
            raise ValueError("Unknown language")
        if not addressed:
            return {"status": "not_addressed", "ids": []}
        if language != self._language or not self._items:
            return {"status": "no_context", "ids": []}
        result = resolve(message, self._items, language=language, addressed=True,
                         require_confirmation=require_confirmation)
        # Only an ambiguous, singular pronominal follow-up can use a separately
        # confirmed focus. Quoted/negated/destructive instructions still pass
        # through all original resolver safety checks.
        if (result["status"] == "needs_clarification" and self._focus is not None
                and self._can_use_focus(message, language)):
            selected = [item for item in self._items if item["id"] == self._focus]
            if len(selected) == 1:
                return resolve(message, selected, language=language, addressed=True,
                               require_confirmation=require_confirmation)
        return result


def main() -> None:
    parser = argparse.ArgumentParser(description="Local ephemeral referent focus; no actions")
    parser.add_argument("--candidates-json", required=True)
    parser.add_argument("--message", required=True)
    parser.add_argument("--language", choices=("ru", "en"), default="ru")
    parser.add_argument("--focus-id")
    parser.add_argument("--advance", type=int, default=0)
    parser.add_argument("--addressed", action="store_true")
    parser.add_argument("--require-confirmation", action="store_true")
    args = parser.parse_args()
    context = TurnFocus()
    context.present(json.loads(args.candidates_json), language=args.language)
    if args.focus_id:
        context.pin(args.focus_id)
    if args.advance:
        context.advance(args.advance)
    print(json.dumps(context.choose(args.message, language=args.language,
                 addressed=args.addressed, require_confirmation=args.require_confirmation),
                 ensure_ascii=False))


if __name__ == "__main__":
    main()
