"""A conservative local phrase selector over SHA-checked approved data.

No inference of mood or user identity. Caller MUST provide an explicit scenario
and opt-in flags; a language pack cannot execute moderation actions.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TONES = {"neutral", "warm", "casual"}
LANGUAGES = {"ru", "en"}
SENSITIVE = {"mourning", "crisis", "harassment", "grief"}

def load_phrasebook(root: Path = ROOT) -> dict:
    manifest = json.loads((root / "manifest.json").read_text(encoding="utf-8"))
    relative = "packs/ru/expression_choices.json"
    digests = [p["sha256"] for p in manifest["packs"] if p["path"] == relative]
    if len(digests) != 1:
        raise ValueError("Phrasebook manifest entry missing or duplicated")
    raw = (root / relative).read_bytes()
    if hashlib.sha256(raw).hexdigest() != digests[0]:
        raise ValueError("Phrasebook SHA-256 mismatch")
    book = json.loads(raw.decode("utf-8"))
    if book["schema_version"] != 1 or len(book["entries"]) < 25:
        raise ValueError("Unsupported phrasebook")
    return book

def pick_phrase(book: dict, *, scenario: str, language: str = "ru",
                tone: str = "neutral", dark_opt_in: bool = False,
                strong_opt_in: bool = False, sensitive: bool = False,
                recent_phrases: tuple[str, ...] = ()) -> dict:
    if language not in LANGUAGES or tone not in TONES:
        raise ValueError("Unsupported language or tone")
    match = [row for row in book["entries"] if row["id"] == scenario]
    if len(match) != 1:
        return {"status": "no_match", "text": None}
    row = match[0]
    if sensitive and (row["requires_dark_opt_in"] or row["requires_strong_opt_in"]):
        return {"status": "suppressed_sensitive", "text": None}
    if row["requires_dark_opt_in"] and not dark_opt_in:
        return {"status": "requires_dark_opt_in", "text": None}
    if row["requires_strong_opt_in"] and not strong_opt_in:
        return {"status": "requires_strong_opt_in", "text": None}
    values = row["language_variants"][language][tone]
    def normalize(s: str) -> str:
        return " ".join(unicodedata.normalize("NFKC", s).casefold().split())
    recently = {normalize(s) for s in recent_phrases}
    choices = [s for s in values if normalize(s) not in recently]
    if not choices:
        return {"status": "no_unused_phrase", "text": None}
    # Deterministic; no hidden RNG or personal profiling.
    return {"status": "ok", "text": choices[0], "scenario": scenario,
            "language": language, "tone": tone}

def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--scenario", required=True)
    parser.add_argument("--language", default="ru", choices=sorted(LANGUAGES))
    parser.add_argument("--tone", default="neutral", choices=sorted(TONES))
    parser.add_argument("--dark-opt-in", action="store_true")
    parser.add_argument("--strong-opt-in", action="store_true")
    parser.add_argument("--sensitive", action="store_true")
    args = parser.parse_args()
    response = pick_phrase(load_phrasebook(), scenario=args.scenario,
                           language=args.language, tone=args.tone,
                           dark_opt_in=args.dark_opt_in,
                           strong_opt_in=args.strong_opt_in,
                           sensitive=args.sensitive)
    print(json.dumps(response, ensure_ascii=False))

if __name__ == "__main__":
    main()
