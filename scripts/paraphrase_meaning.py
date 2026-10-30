"""Exact-source RU/EN paraphrase selector over reviewed, SHA-verified synthetic data.

Only approved outputs; no inference over arbitrary text, memory, external calls,
sanctions, permission changes or GitHub writes.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PACK = "packs/ru/meaning_paraphrases.json"
LANGUAGES = {"ru", "en"}
TONES = {"neutral", "casual"}
POLICY = {
    "synthetic_examples_only": True,
    "personal_data_allowed": False,
    "automatic_actions_allowed": False,
    "automatic_sanctions_allowed": False,
    "approved_outputs_only": True,
    "exact_source_only": True,
}


def normalized(text: str) -> str:
    """Case and whitespace only: negations, amounts and punctuation stay intact."""
    return " ".join(unicodedata.normalize("NFKC", text).casefold().split())


class MeaningParaphraser:
    def __init__(self, root: Path = ROOT):
        manifest = json.loads((root / "manifest.json").read_text(encoding="utf-8"))
        expected = [row["sha256"] for row in manifest["packs"] if row["path"] == PACK]
        if len(expected) != 1:
            raise ValueError("Missing or duplicate paraphrase manifest entry")
        raw = (root / PACK).read_bytes()
        if hashlib.sha256(raw).hexdigest() != expected[0]:
            raise ValueError("Paraphrase SHA-256 mismatch")
        book = json.loads(raw.decode("utf-8"))
        if (book.get("schema_version") != 1
                or book.get("language") != "multilingual"
                or book.get("usage_policy") != POLICY):
            raise ValueError("Unsupported or unsafe paraphrase pack")
        self.by_source = {}
        for entry in book["paraphrases"]:
            key = (entry["language"], normalized(entry["source"]))
            if key in self.by_source:
                raise ValueError("Duplicate paraphrase source")
            self.by_source[key] = entry
        self.count = len(self.by_source)

    def rewrite(self, source: str, *, language: str = "ru",
                tone: str = "neutral", addressed: bool = False,
                sensitive: bool = False, recent: tuple[str, ...] = ()) -> dict:
        if language not in LANGUAGES or tone not in TONES:
            raise ValueError("Unsupported language or tone")
        if len(recent) > 8:
            raise ValueError("History exceeds eight responses")
        if not addressed:
            return {"status": "not_addressed", "text": None}
        if not isinstance(source, str) or not 1 <= len(source) <= 300:
            return {"status": "unknown_source", "text": None}
        entry = self.by_source.get((language, normalized(source)))
        if entry is None:
            return {"status": "unknown_source", "text": None}
        if sensitive and tone == "casual":
            return {"status": "sensitive_tone_blocked", "text": None}
        output = entry["variants"][tone]
        if normalized(output) in {normalized(s) for s in recent}:
            return {"status": "repeat_suppressed", "text": None}
        return {"status": "ok", "text": output, "source_id": entry["id"],
                "language": language, "tone": tone,
                "semantic_guard": entry["semantic_guard"]}


def main() -> None:
    parser = argparse.ArgumentParser(description="Exact approved bilingual rewrites")
    parser.add_argument("--source", required=True)
    parser.add_argument("--language", choices=sorted(LANGUAGES), default="ru")
    parser.add_argument("--tone", choices=sorted(TONES), default="neutral")
    parser.add_argument("--addressed", action="store_true")
    parser.add_argument("--sensitive", action="store_true")
    parser.add_argument("--recent", action="append", default=[])
    args = parser.parse_args()
    result = MeaningParaphraser().rewrite(
        args.source, language=args.language, tone=args.tone,
        addressed=args.addressed, sensitive=args.sensitive,
        recent=tuple(args.recent)
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
