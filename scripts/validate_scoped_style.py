"""Verify deterministic RU/EN reply/session style data, safety and uniqueness."""
from __future__ import annotations
import json
import re
from collections import Counter
from pathlib import Path
from dialogue_preferences import ROOT, SCOPED_PACK, DIMENSIONS, load_scoped_requests, normalize
from validate_style_preferences import VALUES

POLICY = {"synthetic_examples_only": True, "personal_data_allowed": False,
          "automatic_actions_allowed": False, "automatic_sanctions_allowed": False,
          "ephemeral_only": True, "caller_owns_context": True, "scope_enforced": True}
FIELDS = {"id", "dimension", "value", "language", "scope", "input", "audiences"}


def validate_scoped_style(root: Path = ROOT) -> list[str]:
    try:
        book = load_scoped_requests(root)
    except (ValueError, OSError, KeyError, json.JSONDecodeError) as exc:
        return [str(exc)]
    errors = []
    if book.get("usage_policy") != POLICY or book.get("pack_version") != "2026.10.30.14":
        errors.append("Unsafe scoped style metadata or policy")
    cases = book.get("cases")
    if not isinstance(cases, list) or len(cases) != 80:
        return errors + ["Expected exactly 80 scoped examples"]
    ids, inputs, groups = set(), set(), Counter()
    for row in cases:
        if not isinstance(row, dict) or set(row) != FIELDS:
            errors.append("Invalid scoped record")
            continue
        identifier = row["id"]
        if not isinstance(identifier, str) or not re.fullmatch(r"[a-z0-9_]+", identifier) or identifier in ids:
            errors.append("Duplicate/invalid scoped ID")
        ids.add(identifier)
        d, v, lang, scope = (row[k] for k in ("dimension", "value", "language", "scope"))
        if d not in DIMENSIONS or v not in VALUES.get(d, ()) or lang not in ("ru", "en") or scope not in ("one_reply", "session"):
            errors.append("Invalid scoped dimension, value, language or scope")
        if row["audiences"] != ["all_ai_bots"]:
            errors.append("Unsafe audience")
        source = row["input"]
        if not isinstance(source, str) or not 25 <= len(source) <= 210:
            errors.append("Invalid input text")
            continue
        phrase = normalize(source)
        if not phrase or phrase in inputs:
            errors.append("Duplicate normalized scoped text")
        inputs.add(phrase)
        groups[(d, v, lang, scope)] += 1
    required = {(d, v, lang, scope) for d in DIMENSIONS for v in VALUES[d]
                for lang in ("ru", "en") for scope in ("one_reply", "session")}
    if set(groups) != required or any(n != 1 for n in groups.values()):
        errors.append("Expected one distinct RU/EN case per meaning/scope")
    manifest = json.loads((root / "manifest.json").read_text(encoding="utf-8"))
    prior_ids, prior_phrases = set(), set()
    for entry in manifest["packs"]:
        if entry["path"] == SCOPED_PACK:
            continue
        book_old = json.loads((root / entry["path"]).read_text(encoding="utf-8"))
        for col in ("skills", "cases", "intents", "pairs", "triggers", "paraphrases", "scenarios"):
            for item in book_old.get(col, []):
                if isinstance(item, dict):
                    if isinstance(item.get("id"), str):
                        prior_ids.add(item["id"])
                    for field in ("input", "expression", "source", "message"):
                        if isinstance(item.get(field), str):
                            prior_phrases.add(normalize(item[field]))
                    for v in item.get("examples", []):
                        if isinstance(v, str):
                            prior_phrases.add(normalize(v))
                    if isinstance(item.get("variants"), dict):
                        for v in item["variants"].values():
                            if isinstance(v, str):
                                prior_phrases.add(normalize(v))
    if ids & prior_ids:
        errors.append("Scoped ID collision with existing pack")
    if inputs & prior_phrases:
        errors.append("Scoped normalized input collision with existing pack")
    return errors


if __name__ == "__main__":
    errors = validate_scoped_style()
    if errors:
        print("SCOPED_STYLE_FAIL", errors)
        raise SystemExit(1)
    print("SCOPED_STYLE_VALID cases=80 dimensions=10 meanings=20 scopes=2 languages=2")
