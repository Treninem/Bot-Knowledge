"""Validate the bilingual composable grammar against every approved package."""
from __future__ import annotations
import json
import re
from collections import Counter
from pathlib import Path
from composable_style import ROOT, PACK, POLICY, ComposableStyle, load_composable_style, normalized
from validate_style_preferences import VALUES

FIELDS = {"id", "dimension", "value", "language", "scope", "input", "audiences"}

def validate_composable_style(root: Path = ROOT) -> list[str]:
    try:
        book = load_composable_style(root)
        matcher = ComposableStyle(root)
    except (ValueError, OSError, KeyError, json.JSONDecodeError, TypeError) as exc:
        return [str(exc)]
    errors: list[str] = []
    prefixes = book.get("scope_prefixes")
    if not isinstance(prefixes, dict) or set(prefixes) != {"ru", "en"}:
        errors.append("Invalid language prefix matrix")
        return errors
    for lang in ("ru", "en"):
        if set(prefixes[lang]) != {"one_reply", "session"}:
            errors.append("Invalid scope matrix")
            continue
        for scope in ("one_reply", "session"):
            phrases = prefixes[lang][scope]
            if not isinstance(phrases, list) or len(phrases) != 2 or any(
                not isinstance(x, str) or not 10 <= len(x) <= 100 for x in phrases
            ):
                errors.append("Expected two safe prefixes per scope and language")
    directives = book.get("directives")
    if not isinstance(directives, list) or len(directives) != 20:
        return errors + ["Expected twenty distinct meanings"]
    meanings, phrase_keys = set(), set()
    for row in directives:
        if not isinstance(row, dict) or set(row) != {"dimension", "value", "ru", "en"}:
            errors.append("Invalid directive shape")
            continue
        pair = (row["dimension"], row["value"])
        if pair in meanings or row["value"] not in VALUES.get(row["dimension"], ()):
            errors.append("Duplicate or invalid meaning")
        meanings.add(pair)
        for lang in ("ru", "en"):
            v = row[lang]
            if not isinstance(v, str) or not 10 <= len(v) <= 110 or normalized(v) in phrase_keys:
                errors.append("Duplicate or invalid directive")
            phrase_keys.add(normalized(v))
    if meanings != {(d, v) for d in VALUES for v in VALUES[d]}:
        errors.append("Missing meaning pair")
    cases = book.get("cases")
    if not isinstance(cases, list) or len(cases) != 80:
        return errors + ["Expected exactly 80 synthetic full-message cases"]
    ids, inputs, cells = set(), set(), Counter()
    for row in cases:
        if not isinstance(row, dict) or set(row) != FIELDS:
            errors.append("Invalid case record")
            continue
        name, phrase = row["id"], row["input"]
        if not isinstance(name, str) or not re.fullmatch(r"compose_[a-z0-9_]+", name) or name in ids:
            errors.append("Invalid/duplicate case ID")
        ids.add(name)
        if not isinstance(phrase, str) or not 24 <= len(phrase) <= 180 or normalized(phrase) in inputs:
            errors.append("Invalid/duplicate normalized case")
        inputs.add(normalized(phrase))
        if row["audiences"] != ["all_ai_bots"]:
            errors.append("Unsafe audience")
        cell = (row["dimension"], row["value"], row["language"], row["scope"])
        cells[cell] += 1
        if row["language"] not in {"ru", "en"} or row["scope"] not in {"one_reply", "session"} or (row["dimension"], row["value"]) not in meanings:
            errors.append("Invalid semantic cell")
            continue
        expect = f'{prefixes[row["language"]][row["scope"]][0]}, {next(d[row["language"]] for d in directives if (d["dimension"], d["value"]) == (row["dimension"], row["value"]))}.'
        if phrase != expect or matcher.match(phrase, language=row["language"], addressed=True)["status"] != "updated":
            errors.append("Case does not match approved composed grammar")
    required = {(d, v, lang, scope) for d, v in meanings for lang in ("ru", "en") for scope in ("one_reply", "session")}
    if set(cells) != required or any(c != 1 for c in cells.values()):
        errors.append("Missing or duplicated semantic cell")
    manifest = json.loads((root / "manifest.json").read_text(encoding="utf-8"))
    prior_ids, prior = set(), set()
    for info in manifest["packs"]:
        if info["path"] == PACK:
            continue
        old = json.loads((root / info["path"]).read_text(encoding="utf-8"))
        for col in ("skills", "cases", "intents", "pairs", "triggers", "paraphrases", "scenarios"):
            for item in old.get(col, []):
                if not isinstance(item, dict):
                    continue
                if isinstance(item.get("id"), str):
                    prior_ids.add(item["id"])
                for field in ("input", "expression", "source", "message"):
                    if isinstance(item.get(field), str):
                        prior.add(normalized(item[field]))
                for value in item.get("examples", []):
                    if isinstance(value, str):
                        prior.add(normalized(value))
                if isinstance(item.get("variants"), dict):
                    prior.update(normalized(v) for v in item["variants"].values() if isinstance(v, str))
    if ids & prior_ids:
        errors.append("ID collision with an older pack")
    if inputs & prior:
        errors.append("Normalized case collision with an older pack")
    return errors

if __name__ == "__main__":
    errors = validate_composable_style()
    if errors:
        print("COMPOSABLE_STYLE_FAIL", errors)
        raise SystemExit(1)
    print("COMPOSABLE_STYLE_VALID 80 original RU/EN cases, 20 meanings, 160 approved grammar combinations")
