"""SHA-checked, read-only RU/EN short replies grounded in an explicit pending turn.

Not an autonomous language model. Never executes actions, updates a chat,
authorizes sanctions or stores personal details. One instance is safe to share:
the caller supplies the pending kind and freshness for each independent chat.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PACK = "packs/ru/short_turns.json"
POLICY = {
    "synthetic_examples_only": True,
    "personal_data_allowed": False,
    "automatic_actions_allowed": False,
    "automatic_sanctions_allowed": False,
    "requires_confirmed_pending_context": True,
}
PENDING = {"confirmation", "choice", "information"}
INTENTS = {"affirm", "deny", "unsure", "defer", "cancel", "first",
           "second", "both", "neither", "repeat", "explain", "ambiguous"}
WORD = re.compile(r"[^\W_]+", re.UNICODE)


def normalize(value: str) -> str:
    return " ".join(WORD.findall(unicodedata.normalize("NFKC", value).casefold().replace("ё", "е")))


def load_pack(root: Path = ROOT) -> dict:
    manifest = json.loads((root / "manifest.json").read_text(encoding="utf-8"))
    digests = [row["sha256"] for row in manifest["packs"] if row["path"] == PACK]
    if len(digests) != 1:
        raise ValueError("Short-turn pack missing or duplicated in manifest")
    raw = (root / PACK).read_bytes()
    if hashlib.sha256(raw).hexdigest() != digests[0]:
        raise ValueError("Short-turn SHA-256 mismatch")
    data = json.loads(raw.decode("utf-8"))
    if (data.get("schema_version") != 1 or data.get("language") != "multilingual"
            or data.get("usage_policy") != POLICY):
        raise ValueError("Unsupported or unsafe short-turn policy")
    return data


class ShortTurns:
    def __init__(self, root: Path = ROOT):
        book = load_pack(root)
        self.rows = {(row["language"], normalize(row["input"])): row
                     for row in book["cases"]}
        if len(self.rows) != len(book["cases"]):
            raise ValueError("Ambiguous normalized short replies")

    def interpret(self, message: str, *, pending_kind: str | None,
                  language: str = "ru", pending_turns: int = 0,
                  addressed: bool = True, quoted: bool = False,
                  side_effects: bool = False, options_count: int = 2,
                  allow_multiple: bool = False) -> dict:
        if not isinstance(message, str) or len(message) > 80:
            raise ValueError("Message must be a short string")
        if language not in {"ru", "en"} or pending_kind not in (PENDING | {None}):
            raise ValueError("Unsupported language or pending kind")
        if type(pending_turns) is not int or not 0 <= pending_turns <= 100:
            raise ValueError("Pending age must be an integer in 0..100")
        if type(options_count) is not int or not 0 <= options_count <= 20:
            raise ValueError("Options count must be an integer in 0..20")
        if any(type(v) is not bool for v in (addressed, quoted, side_effects, allow_multiple)):
            raise ValueError("Safety flags must be explicit booleans")
        empty = {"intent": None, "action_authorized": False}
        if not addressed:
            return {"status": "not_addressed", **empty}
        if (quoted or any(mark in message for mark in ('"', "«", "»", "“", "”"))
                or message.strip().startswith("'") or message.strip().endswith("'")):
            return {"status": "quoted_ignored", **empty}
        if any(mark in message for mark in ("?", "？", "…", ";", ":", "\n", "\r")):
            return {"status": "needs_clarification", **empty}
        key = normalize(message)
        if not key:
            return {"status": "empty", **empty}
        if pending_kind is None:
            return {"status": "no_pending_context", **empty}
        if pending_turns > 2:
            return {"status": "expired_context", **empty}
        row = self.rows.get((language, key))
        if row is None:
            other = "en" if language == "ru" else "ru"
            status = "wrong_language" if (other, key) in self.rows else "unknown_reply"
            return {"status": status, **empty}
        intent = row["topic"]
        if row["pending_kind"] not in {"any", pending_kind}:
            return {"status": "context_mismatch", **empty}
        if intent == "ambiguous":
            return {"status": "needs_clarification", **empty}
        if side_effects:
            return {"status": "side_effect_blocked", **empty}
        if intent in {"first", "second", "both", "neither"} and options_count < 2:
            return {"status": "insufficient_options", **empty}
        if intent == "both" and not allow_multiple:
            return {"status": "multiple_not_allowed", **empty}
        return {"status": "recognized", "intent": intent, "id": row["id"],
                "pending_kind": pending_kind, "action_authorized": False}


def main() -> None:
    p = argparse.ArgumentParser(description="Safe read-only bilingual short replies")
    p.add_argument("--message", required=True)
    p.add_argument("--pending-kind", choices=sorted(PENDING), required=True)
    p.add_argument("--language", choices=("ru", "en"), default="ru")
    p.add_argument("--pending-turns", type=int, default=0)
    args = p.parse_args()
    print(json.dumps(ShortTurns().interpret(args.message, pending_kind=args.pending_kind,
        language=args.language, pending_turns=args.pending_turns), ensure_ascii=False))


if __name__ == "__main__":
    main()
