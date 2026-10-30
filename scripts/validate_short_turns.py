"""Check original RU/EN short turns for safe, unique, SHA-checked content."""
from __future__ import annotations

import json
import re
from collections import Counter
from pathlib import Path

from short_turns import ROOT, PACK, POLICY, INTENTS, normalize, load_pack

FIELDS = {"id", "language", "topic", "input", "context", "pending_kind",
          "meaning", "avoid", "audiences"}


def validate_short_turns(root: Path = ROOT) -> list[str]:
    errors = []
    try:
        book = load_pack(root)
    except (ValueError, KeyError, OSError, TypeError) as exc:
        return ["Cannot load short turns: " + str(exc)]
    cases = book.get("cases")
    if book.get("usage_policy") != POLICY or not isinstance(cases, list) or len(cases) != 48:
        return ["Short-turn policy or count invalid"]
    if len((root / PACK).read_bytes()) > 48 * 1024:
        errors.append("Short-turn pack exceeds 48KiB")
    ids, phrases, counts = set(), set(), Counter()
    for row in cases:
        if not isinstance(row, dict) or set(row) != FIELDS:
            errors.append("Invalid short-turn row shape")
            continue
        lang, intent, rid = row["language"], row["topic"], row["id"]
        if lang not in {"ru", "en"} or intent not in INTENTS:
            errors.append("Unknown language or intent")
            continue
        counts[(lang, intent)] += 1
        if (not re.fullmatch(r"short_(ru|en)_[a-z]+_[12]", rid)
                or not rid.startswith(f"short_{lang}_{intent}_") or rid in ids):
            errors.append("Invalid or repeated ID")
        ids.add(rid)
        phrase = normalize(row["input"])
        if not 1 <= len(phrase) <= 60 or phrase in phrases:
            errors.append("Empty, oversized or repeated normalized reply")
        phrases.add(phrase)
        pending = "confirmation" if intent in {"affirm", "deny"} else (
                  "choice" if intent in {"first", "second", "both", "neither"} else "any")
        if row["pending_kind"] != pending:
            errors.append("Unsafe pending kind")
        if row["audiences"] != ["all_ai_bots"]:
            errors.append("Unexpected short-turn audience")
        for field in ("context", "meaning", "avoid"):
            if not isinstance(row[field], str) or not 15 <= len(row[field]) <= 240:
                errors.append("Bad short-turn semantic context")
    if set(counts) != {(lang, intent) for lang in ("ru", "en") for intent in INTENTS}:
        errors.append("Missing intent or language")
    if any(value != 2 for value in counts.values()):
        errors.append("Unbalanced short reply variants")
    manifest = json.loads((root / "manifest.json").read_text(encoding="utf-8"))
    prior_ids, prior_phrases = set(), set()
    for info in manifest["packs"]:
        if info["path"] == PACK:
            continue
        other = json.loads((root / info["path"]).read_text(encoding="utf-8"))
        for field in ("skills", "cases", "intents", "pairs", "triggers",
                      "paraphrases", "scenarios", "entries"):
            for entry in other.get(field, []):
                if not isinstance(entry, dict):
                    continue
                if isinstance(entry.get("id"), str):
                    prior_ids.add(entry["id"])
                for col in ("input", "source", "expression", "message"):
                    if isinstance(entry.get(col), str):
                        prior_phrases.add(normalize(entry[col]))
    if ids & prior_ids:
        errors.append("ID collision with existing pack")
    if phrases & prior_phrases:
        errors.append("Short reply collides with prior original input")
    return errors


if __name__ == "__main__":
    issues = validate_short_turns()
    if issues:
        raise SystemExit("\\n".join(issues))
    print("SHORT_TURNS_VALID cases=48 ru=24 en=24 intents=12 duplicates=0")
