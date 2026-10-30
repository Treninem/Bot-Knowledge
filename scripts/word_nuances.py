"""Conservative RU/EN word choice after a caller has confirmed the intended sense.

No free-text intent inference, permissions, network, storage or moderation actions.
Each embedding application must determine meaning and authorization itself.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PACK = "packs/ru/word_nuances.json"
LANGUAGES = {"ru", "en"}
TONES = {"neutral", "formal", "casual"}
AUDIENCES = {"all_ai_bots", "chat_moderators", "community_bots"}


def normalized(value: str) -> str:
    return " ".join(unicodedata.normalize("NFKC", value).casefold().replace("ё", "е").split())


def load_word_nuances(root: Path = ROOT) -> dict:
    manifest = json.loads((root / "manifest.json").read_text(encoding="utf-8"))
    hashes = [item["sha256"] for item in manifest["packs"] if item["path"] == PACK]
    if len(hashes) != 1:
        raise ValueError("Word nuance pack is missing or duplicated in manifest")
    raw = (root / PACK).read_bytes()
    if hashlib.sha256(raw).hexdigest() != hashes[0]:
        raise ValueError("Word nuance pack SHA-256 mismatch")
    data = json.loads(raw.decode("utf-8"))
    if data.get("schema_version") != 1 or data.get("language") != "multilingual":
        raise ValueError("Unsupported word nuance pack")
    return data


def choose_word(book: dict, *, family: str, sense: str | None,
                language: str = "ru", tone: str = "neutral",
                audience: str = "all_ai_bots", dark_opt_in: bool = False,
                strong_opt_in: bool = False, sensitive: bool = False,
                recent_phrases: tuple[str, ...] = ()) -> dict:
    """Return one approved expression, never guess from an ambiguous intent.

    The caller supplies a confirmed semantic tag. No result is an instruction to
    act or evidence that the statement is true. Read-only lexical suggestion.
    """
    if language not in LANGUAGES or tone not in TONES or audience not in AUDIENCES:
        raise ValueError("Unsupported language, tone or audience")
    if not isinstance(family, str) or sense is not None and not isinstance(sense, str):
        raise ValueError("Family and sense must be strings")
    eligible = [row for row in book["cases"]
                if row["family"] == family and row["language"] == language]
    if not eligible:
        return {"status": "no_family", "text": None}
    if not sense or not any(row["sense"] == sense for row in eligible):
        return {"status": "needs_semantic_context", "text": None,
                "available_senses": sorted(row["sense"] for row in eligible)}
    row = next(row for row in eligible if row["sense"] == sense)
    if not ({"all_ai_bots", audience} & set(row["audiences"])):
        return {"status": "scope_denied", "text": None}
    if sensitive and (family == "humor" or row["requires_dark_opt_in"]
                      or row["requires_strong_opt_in"]):
        return {"status": "suppressed_sensitive", "text": None}
    if row["requires_dark_opt_in"] and not dark_opt_in:
        return {"status": "requires_dark_opt_in", "text": None}
    if row["requires_strong_opt_in"] and not strong_opt_in:
        return {"status": "requires_strong_opt_in", "text": None}
    phrase = row["variants"][tone]
    if normalized(phrase) in {normalized(s) for s in recent_phrases}:
        return {"status": "no_unused_variant", "text": None}
    return {"status": "ok", "text": phrase, "id": row["id"],
            "family": family, "sense": sense, "tone": tone,
            "language": language, "meaning": row["meaning"]}


def main() -> None:
    parser = argparse.ArgumentParser(description="Local verified RU/EN sense-aware word choice")
    parser.add_argument("--family", required=True)
    parser.add_argument("--sense")
    parser.add_argument("--language", choices=sorted(LANGUAGES), default="ru")
    parser.add_argument("--tone", choices=sorted(TONES), default="neutral")
    parser.add_argument("--audience", choices=sorted(AUDIENCES), default="all_ai_bots")
    parser.add_argument("--dark-opt-in", action="store_true")
    parser.add_argument("--strong-opt-in", action="store_true")
    parser.add_argument("--sensitive", action="store_true")
    args = parser.parse_args()
    result = choose_word(load_word_nuances(), family=args.family, sense=args.sense,
                         language=args.language, tone=args.tone, audience=args.audience,
                         dark_opt_in=args.dark_opt_in, strong_opt_in=args.strong_opt_in,
                         sensitive=args.sensitive)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
