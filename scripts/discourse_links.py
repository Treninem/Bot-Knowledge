"""Offline RU/EN discourse connector suggestions from caller-confirmed relations.

Never infers arbitrary free-text meaning, never rewrites user statements and
never performs actions. The consumer is responsible for semantic analysis,
punctuation and grammar when it uses the suggested standalone connector.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PACK = "packs/ru/discourse_links.json"
POLICY = {
    "synthetic_examples_only": True,
    "personal_data_allowed": False,
    "automatic_actions_allowed": False,
    "automatic_sanctions_allowed": False,
    "caller_confirms_relation": True,
}
REGISTERS = {"casual", "neutral", "formal"}
LANGUAGES = {"ru", "en"}
AUDIENCES = {"all_ai_bots", "chat_moderators", "community_bots"}


def normalized(text: str) -> str:
    return " ".join(unicodedata.normalize("NFKC", text).casefold().replace("ё", "е").split())


def load_pack(root: Path = ROOT) -> dict:
    manifest = json.loads((root / "manifest.json").read_text(encoding="utf-8"))
    matches = [entry["sha256"] for entry in manifest["packs"] if entry["path"] == PACK]
    if len(matches) != 1:
        raise ValueError("Discourse pack missing or duplicated in manifest")
    raw = (root / PACK).read_bytes()
    if hashlib.sha256(raw).hexdigest() != matches[0]:
        raise ValueError("Discourse pack SHA-256 mismatch")
    book = json.loads(raw.decode("utf-8"))
    if (book.get("schema_version") != 1 or book.get("language") != "multilingual"
            or book.get("usage_policy") != POLICY):
        raise ValueError("Unsupported or unsafe discourse pack")
    return book


class DiscourseLinks:
    """Propose a linker only when the caller's two semantic tags agree."""

    def __init__(self, root: Path = ROOT):
        book = load_pack(root)
        self._rows = {(row["language"], row["relation"]): row for row in book["cases"]}
        if len(self._rows) != len(book["cases"]):
            raise ValueError("Ambiguous discourse relation keys")

    def suggest(self, *, relation: str | None, confirmed_relation: str | None,
                language: str = "ru", register: str = "neutral",
                audience: str = "all_ai_bots", addressed: bool = True,
                quoted: bool = False, recent: tuple[str, ...] = ()) -> dict:
        if language not in LANGUAGES or register not in REGISTERS or audience not in AUDIENCES:
            raise ValueError("Invalid language, register or audience")
        if not isinstance(addressed, bool) or not isinstance(quoted, bool):
            raise ValueError("Addressed and quoted must be booleans")
        if (relation is not None and not isinstance(relation, str)
                or confirmed_relation is not None and not isinstance(confirmed_relation, str)):
            raise ValueError("Relation tags must be strings or None")
        if (not isinstance(recent, (tuple, list))
                or len(recent) > 16 or any(not isinstance(item, str) or len(item) > 100
                                           for item in recent)):
            raise ValueError("Recent connectors must be a bounded sequence")
        if not addressed:
            return {"status": "not_addressed", "connector": None}
        if quoted:
            return {"status": "quoted_ignored", "connector": None}
        if not relation or not confirmed_relation:
            return {"status": "needs_semantic_context", "connector": None}
        if relation != confirmed_relation:
            return {"status": "relation_conflict", "connector": None}
        row = self._rows.get((language, relation))
        if row is None:
            return {"status": "unknown_relation", "connector": None}
        if not ({"all_ai_bots", audience} & set(row["audiences"])):
            return {"status": "scope_denied", "connector": None}
        value = row["variants"][register]
        if normalized(value) in {normalized(item) for item in recent}:
            return {"status": "already_used", "connector": None}
        return {
            "status": "proposal", "connector": value, "relation": relation,
            "language": language, "register": register, "id": row["id"],
            "usage": row["usage"], "avoid": row["avoid"],
        }


def main() -> None:
    p = argparse.ArgumentParser(description="Read-only RU/EN discourse linker")
    p.add_argument("--relation", required=True)
    p.add_argument("--confirmed-relation", required=True)
    p.add_argument("--language", choices=sorted(LANGUAGES), default="ru")
    p.add_argument("--register", choices=sorted(REGISTERS), default="neutral")
    args = p.parse_args()
    result = DiscourseLinks().suggest(relation=args.relation,
        confirmed_relation=args.confirmed_relation, language=args.language,
        register=args.register)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
