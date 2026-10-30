"""Conservative offline lookup of approved clarification questions.

Exact normalized matching only. The caller retains responsibility for context,
authorization and any subsequent action.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PACK = "packs/ru/clarification_boundaries.json"
WORD = re.compile(r"[^\W_]+", re.UNICODE)


def normalize(value: str) -> str:
    return " ".join(WORD.findall(value.casefold().replace("ё", "е")))


def choose(text: str, language: str, root: Path = ROOT) -> dict | None:
    if language not in {"ru", "en"} or not normalize(text):
        return None
    manifest = json.loads((root / "manifest.json").read_text(encoding="utf-8"))
    entry = next((item for item in manifest["packs"] if item["path"] == PACK), None)
    if entry is None:
        raise ValueError("Clarification pack absent from manifest")
    payload = (root / PACK).read_bytes()
    if hashlib.sha256(payload).hexdigest() != entry["sha256"]:
        raise ValueError("Clarification pack SHA-256 mismatch")
    cases = json.loads(payload.decode("utf-8"))["cases"]
    matches = [case for case in cases
               if case["language"] == language
               and case["audiences"] == ["all_ai_bots"]
               and normalize(case["input"]) == normalize(text)]
    if len(matches) != 1:
        return None
    case = matches[0]
    return {"id": case["id"], "question": case["clarifying_question"],
            "safe_next_step": case["safe_next_step"]}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--text", required=True)
    parser.add_argument("--language", required=True, choices=("ru", "en"))
    args = parser.parse_args()
    print(json.dumps(choose(args.text, args.language), ensure_ascii=False))
