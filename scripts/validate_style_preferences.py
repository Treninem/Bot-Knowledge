"""Validate RU/EN synthetic explicit style preferences and normalized uniqueness."""
from __future__ import annotations

import json
import re
from collections import Counter
from pathlib import Path
from dialogue_preferences import ROOT, PACK, DIMENSIONS, load_preferences, normalize

VALUES = {x: ("enabled", "disabled") for x in DIMENSIONS}
VALUES["verbosity"] = ("concise", "detailed")
VALUES["formality"] = ("formal", "casual")
POLICY = {"synthetic_examples_only": True, "personal_data_allowed": False,
          "automatic_actions_allowed": False, "automatic_sanctions_allowed": False,
          "ephemeral_only": True, "caller_owns_context": True}
FIELDS = {"id", "dimension", "value", "language", "input", "audiences"}


def validate_style_preferences(root: Path = ROOT) -> list[str]:
    try:
        book = load_preferences(root)
    except (ValueError, OSError, KeyError, json.JSONDecodeError) as exc:
        return [str(exc)]
    errors = []
    if book.get("usage_policy") != POLICY:
        errors.append("Unsafe preference policy")
    cases = book.get("cases")
    if not isinstance(cases, list) or len(cases) != 80:
        return errors + ["Expected exactly 80 preference examples"]
    ids, normalized, groups = set(), set(), Counter()
    for row in cases:
        if not isinstance(row, dict) or set(row) != FIELDS:
            errors.append("Invalid preference record")
            continue
        rid = row["id"]
        if not isinstance(rid, str) or not re.fullmatch(r"[a-z0-9_]+", rid) or rid in ids:
            errors.append("Duplicate or invalid ID")
        ids.add(rid)
        d, v, language = row["dimension"], row["value"], row["language"]
        if d not in VALUES or v not in VALUES.get(d, ()) or language not in ("ru", "en"):
            errors.append("Bad preference meaning or language")
        if row["audiences"] != ["all_ai_bots"]:
            errors.append("Unsafe preference audience")
        s = row["input"]
        if not isinstance(s, str) or not 15 <= len(s) <= 180:
            errors.append("Invalid preference input")
            continue
        key = normalize(s)
        if not key or key in normalized:
            errors.append("Repeated normalized input: " + rid)
        normalized.add(key)
        groups[(d, v, language)] += 1
    required = {(d, v, l) for d in DIMENSIONS for v in VALUES[d] for l in ("ru", "en")}
    if set(groups) != required or any(n != 2 for n in groups.values()):
        errors.append("Missing or duplicated meaning/language cells")
    manifest = json.loads((root / "manifest.json").read_text(encoding="utf-8"))
    prior = set()
    for entry in manifest["packs"]:
        if entry["path"] == PACK:
            continue
        old = json.loads((root / entry["path"]).read_text(encoding="utf-8"))
        for collection in ("skills", "cases", "intents", "pairs", "triggers", "paraphrases", "scenarios"):
            for record in old.get(collection, []):
                for field in ("input", "expression", "source", "message"):
                    if isinstance(record.get(field), str):
                        prior.add(normalize(record[field]))
                for ex in record.get("examples", []):
                    if isinstance(ex, str):
                        prior.add(normalize(ex))
                if isinstance(record.get("variants"), dict):
                    for ex in record["variants"].values():
                        if isinstance(ex, str):
                            prior.add(normalize(ex))
    if normalized & prior:
        errors.append("Normalized collision with existing packs: " + repr(sorted(normalized & prior)))
    return errors


if __name__ == "__main__":
    problems = validate_style_preferences()
    if problems:
        print("STYLE_PREFERENCES_FAIL", problems)
        raise SystemExit(1)
    print("STYLE_PREFERENCES_VALID 80 entries and 40 RU/EN cells")
