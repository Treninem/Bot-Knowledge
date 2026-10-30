"""One-typo correction over approved benign dialogue utterances, entirely offline.

A correction must preserve word count, all short/protected tokens and language
script. Only one longer token may differ by a single edit/transposition.
No fuzzy moderation, account permissions, or sanctions.
"""
from __future__ import annotations

import re
from dataclasses import dataclass

from interpret_pragmatics import norm

SAFE_KINDS = {"congratulations", "support", "conversation", "creative"}
EXCLUDED_IDS = {
    "talk_stop_when_asked", "talk_no_profanity_request",
    "talk_sarcasm_uncertain", "en_context_this",
}
PROTECTED = {
    "не", "нет", "ни", "без", "not", "no", "never", "dont",
    "without", "stop", "ban", "mute", "admin", "owner",
}

@dataclass(frozen=True)
class Example:
    language: str
    source: str
    case_id: str

def _script(text: str, language: str) -> bool:
    if language == "ru":
        return bool(re.fullmatch(r"[а-яё]+", text))
    return bool(re.fullmatch(r"[a-z]+", text))

def one_typo(word: str, candidate: str, language: str) -> bool:
    if word == candidate or min(len(word), len(candidate)) < 5:
        return False
    if word in PROTECTED or candidate in PROTECTED:
        return False
    if not _script(word, language) or not _script(candidate, language):
        return False
    if abs(len(word) - len(candidate)) > 1:
        return False
    if len(word) == len(candidate):
        differences = [i for i, (a, b) in enumerate(zip(word, candidate)) if a != b]
        if len(differences) == 1:
            return True
        if len(differences) == 2:
            a, b = differences
            return b == a + 1 and word[a] == candidate[b] and word[b] == candidate[a]
        return False
    longer, shorter = (word, candidate) if len(word) > len(candidate) else (candidate, word)
    return any(longer[:i] + longer[i+1:] == shorter for i in range(len(longer)))

class ConservativeTypoMatcher:
    def __init__(self, examples: list[Example]):
        self.by_language: dict[str, list[Example]] = {"ru": [], "en": []}
        for e in examples:
            if e.language not in self.by_language:
                raise ValueError("Unsupported language")
            self.by_language[e.language].append(e)

    def match(self, text: str, language: str) -> dict:
        if language not in self.by_language:
            raise ValueError("Unsupported language")
        phrase = norm(text)
        words = phrase.split()
        if not 3 <= len(words) <= 40 or not 16 <= len(phrase) <= 220:
            return {"status": "none"}
        matches = []
        for e in self.by_language[language]:
            candidate = e.source.split()
            if len(candidate) != len(words):
                continue
            changed = [(w, c) for w, c in zip(words, candidate) if w != c]
            if len(changed) == 1 and one_typo(changed[0][0], changed[0][1], language):
                matches.append(e)
        # If two unrelated approved intents compete, refuse to guess.
        distinct = {e.case_id for e in matches}
        if len(distinct) > 1:
            return {"status": "ambiguous"}
        if not matches:
            return {"status": "none"}
        # Deterministic stable selection among examples of the same intent.
        match = sorted(matches, key=lambda e: e.source)[0]
        return {"status": "match", "case_id": match.case_id,
                "source": match.source}
