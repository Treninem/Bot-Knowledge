"""Prepare a synthetic or reviewed abstract candidate for human GitHub PR publication.

Never run this on raw chat logs; this is an extra guard, not a privacy proof.
No GitHub credentials, network requests, commits or automatic approval.
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

BAD_KEYS = {"chat_id", "user_id", "telegram_id", "username", "first_name",
            "last_name", "phone", "email", "password", "cookie", "token",
            "raw_message", "raw_chat", "chat_history", "private_quote"}
SUSPICIOUS = [
    re.compile(r"https?://\\S+", re.I),
    re.compile(r"(?i)\\b[a-z0-9._%+-]+@[a-z0-9.-]+\\.[a-z]{2,}\\b"),
    re.compile(r"(?<!\\d)\\d{10,}(?!\\d)"),
    re.compile(r"(?i)\\b(?:token|password|secret|api.key)\\s*[:=]"),
]
AUDIENCES = {"all_ai_bots", "chat_moderators", "community_bots"}

def validate(data: dict) -> dict:
    if not isinstance(data, dict) or set(data) != {
        "candidate_id", "statement", "when", "avoid", "audiences",
        "origin", "reviewed"
    }:
        raise ValueError("Unexpected or missing fields; raw chat metadata is forbidden")
    if not re.fullmatch(r"[a-z][a-z0-9_]{7,70}", data["candidate_id"]):
        raise ValueError("Invalid candidate ID")
    if data["origin"] not in ("synthetic", "approved_aggregate"):
        raise ValueError("Only synthetic or anonymized reviewed aggregates")
    if data["reviewed"] is not True:
        raise ValueError("Human review must be explicitly recorded")
    if not isinstance(data["statement"], str) or not 30 <= len(data["statement"]) <= 280:
        raise ValueError("Expected concise transferable statement, not raw chat history")
    if not isinstance(data["audiences"], list) or not data["audiences"] or not set(data["audiences"]) <= AUDIENCES:
        raise ValueError("Invalid audiences")
    for field in ("when", "avoid"):
        values = data[field]
        if not isinstance(values, list) or not 1 <= len(values) <= 5 or any(
            not isinstance(x, str) or not 8 <= len(x) <= 160 for x in values
        ):
            raise ValueError("Invalid " + field)
    raw = json.dumps(data, ensure_ascii=False)
    if any(x in raw.casefold() for x in BAD_KEYS):
        raise ValueError("Private metadata key/string detected")
    if any(pattern.search(raw) for pattern in SUSPICIOUS):
        raise ValueError("Potential secret, link or personal identifier")
    return data

def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    candidate = validate(json.loads(args.input.read_text(encoding="utf-8")))
    if args.output.resolve().is_relative_to(Path(__file__).resolve().parents[1]):
        raise ValueError("Write review candidates OUTSIDE public repository")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(candidate, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("REVIEW_CANDIDATE_PREPARED; NOT PUBLISHED; manual privacy review and GitHub PR still required")

if __name__ == "__main__":
    main()
