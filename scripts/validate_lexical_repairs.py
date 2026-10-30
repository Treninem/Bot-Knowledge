"""Validate unique RU/EN lexical repairs, prior-pack collisions and policy."""
from __future__ import annotations

import json
import re
from collections import Counter
from pathlib import Path

from lexical_repair import ROOT, PACK, POLICY, canonical_value, load_pack

FIELDS = {
    "id", "language", "domain", "kind", "guard", "slot", "current",
    "options", "input", "expected_status", "expected_new",
    "addressed", "quoted", "audiences",
}
GUARDS = {
    "quoted": "quoted_ignored",
    "not_addressed": "not_addressed",
    "stale_context": "stale_context",
    "no_change": "no_change",
    "reported_quote": "unrecognized",
    "extra_instruction": "unrecognized",
    "mixed_language": "unrecognized",
    "unapproved_candidate": "unrecognized",
}


def normalized(text: str) -> str:
    return " ".join(re.findall(r"[^\W_]+", text.casefold().replace("ё", "е")))


def validate_lexical_repairs(root: Path = ROOT) -> list[str]:
    errors: list[str] = []
    try:
        book = load_pack(root)
    except (OSError, ValueError, KeyError, TypeError) as exc:
        return ["Cannot load lexical repair pack: " + str(exc)]
    cases = book.get("cases")
    if book.get("usage_policy") != POLICY or not isinstance(cases, list) or len(cases) != 64:
        return ["Lexical repair policy or number of cases invalid"]
    if len((root / PACK).read_bytes()) > 64 * 1024:
        errors.append("Lexical repair pack too large")
    seen_ids, seen_inputs = set(), set()
    domains, balance, guards = set(), Counter(), Counter()
    for row in cases:
        if not isinstance(row, dict) or set(row) != FIELDS:
            errors.append("Unexpected lexical repair fields")
            continue
        lang, identifier = row["language"], row["id"]
        if (lang not in ("ru", "en") or not isinstance(identifier, str)
                or re.fullmatch(r"lexical_repair_(ru|en)_(ok|guard)_[0-9]{2}", identifier) is None
                or identifier in seen_ids):
            errors.append("Invalid or repeated lexical repair ID")
        seen_ids.add(identifier)
        text = row["input"]
        if not isinstance(text, str) or not 8 <= len(text) <= 180:
            errors.append("Invalid lexical repair sentence")
            continue
        key = (lang, normalized(text))
        if key in seen_inputs:
            errors.append("Duplicate normalized lexical repair input")
        seen_inputs.add(key)
        if not isinstance(row["domain"], str) or not re.fullmatch(r"[a-z_]+", row["domain"]):
            errors.append("Invalid lexical domain")
        if row["slot"] != row["domain"] or row["audiences"] != ["all_ai_bots"]:
            errors.append("Unexpected scope or audience")
        options = row["options"]
        if not isinstance(options, list) or len(options) != 3:
            errors.append("Invalid lexical options")
            continue
        try:
            cleaned = [canonical_value(v, lang) for v in options]
            if len(set(cleaned)) != 3 or row["current"] != cleaned[0]:
                errors.append("Invalid/duplicate choice or stale fixture")
        except ValueError as exc:
            errors.append(str(exc))
        kind, guard = row["kind"], row["guard"]
        if kind not in ("ok", "guard"):
            errors.append("Invalid lexical case kind")
            continue
        balance[(lang, kind)] += 1
        domains.add(row["domain"])
        if kind == "ok":
            if (guard != "explicit_correction" or row["expected_status"] != "proposal"
                    or row["expected_new"] != cleaned[1] or row["addressed"] is not True
                    or row["quoted"] is not False):
                errors.append("Unsafe lexical positive case")
        else:
            guards[(lang, guard)] += 1
            if (guard not in GUARDS or row["expected_status"] != GUARDS.get(guard)
                    or row["expected_new"] is not None
                    or row["addressed"] is not (guard != "not_addressed")
                    or row["quoted"] is not (guard == "quoted")):
                errors.append("Unsafe lexical guard case")
    if set(domains) != {
        "material", "color", "format", "layout", "chart", "vehicle",
        "instrument", "season", "room", "resource", "finish", "shape",
        "document", "tree", "stage", "art",
    }:
        errors.append("Lexical domains incomplete")
    if any(balance[(lang, kind)] != 16 for lang in ("ru", "en") for kind in ("ok", "guard")):
        errors.append("Missing language/positive/negative lexical cases")
    if any(guards[(lang, guard)] != 2 for lang in ("ru", "en") for guard in GUARDS):
        errors.append("Lexical guards are not balanced")
    # Reject IDs and normalized source inputs already approved in other packs.
    manifest = json.loads((root / "manifest.json").read_text(encoding="utf-8"))
    prior_ids, prior_sources = set(), set()
    for info in manifest["packs"]:
        if info["path"] == PACK:
            continue
        other = json.loads((root / info["path"]).read_text(encoding="utf-8"))
        for field in ("skills", "cases", "intents", "pairs", "triggers",
                      "paraphrases", "scenarios", "adversarial_cases"):
            for item in other.get(field, []):
                if not isinstance(item, dict):
                    continue
                if isinstance(item.get("id"), str):
                    prior_ids.add(item["id"])
                for name in ("input", "source", "expression", "message"):
                    value = item.get(name)
                    if isinstance(value, str):
                        prior_sources.add(normalized(value))
                for value in item.get("examples", []):
                    if isinstance(value, str):
                        prior_sources.add(normalized(value))
                if isinstance(item.get("variants"), dict):
                    for value in item["variants"].values():
                        if isinstance(value, str):
                            prior_sources.add(normalized(value))
    if prior_ids.intersection(seen_ids):
        errors.append("Lexical IDs collide with previous packs")
    if prior_sources.intersection(key[1] for key in seen_inputs):
        errors.append("Lexical source phrases collide with previous packs")
    # Token overlap is not semantic verification, but prevents mechanical near-copies.
    token_sets = [set(key[1].split()) for key in sorted(seen_inputs)]
    for i, left in enumerate(token_sets):
        for right in token_sets[:i]:
            if len(left & right) / len(left | right) >= 0.86:
                errors.append("Near-duplicate lexical inputs (Jaccard >= 0.86)")
                return errors
    return errors


if __name__ == "__main__":
    issues = validate_lexical_repairs()
    if issues:
        raise SystemExit("\n".join(issues))
    print("LEXICAL_REPAIRS_VALID cases=64 languages=2 positive=32 guards=32 domains=16")
