"""Validate synthetic bilingual focus scenarios, policy, IDs and distinct phrases."""
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from resolve_referents import norm, validate_candidates

ROOT = Path(__file__).resolve().parents[1]
PACK = "packs/ru/turn_focus_scenarios.json"
POLICY = {
    "synthetic_only": True,
    "no_persistent_memory": True,
    "no_automatic_actions": True,
    "no_automatic_sanctions": True,
    "explicit_focus_only": True,
}
STATUSES = {"resolved", "needs_clarification", "no_context",
            "negated_instruction", "not_direct_request", "confirm_required"}


def validate_turn_focus_pack(root: Path = ROOT) -> list[str]:
    errors: list[str] = []
    try:
        manifest = json.loads((root / "manifest.json").read_text(encoding="utf-8"))
        hashes = [p["sha256"] for p in manifest["packs"] if p["path"] == PACK]
        if len(hashes) != 1:
            return ["Missing or duplicate focus pack in manifest"]
        payload = (root / PACK).read_bytes()
        if hashlib.sha256(payload).hexdigest() != hashes[0]:
            return ["SHA-256 mismatch for turn-focus scenarios"]
        data = json.loads(payload.decode("utf-8"))
    except (KeyError, ValueError, OSError, TypeError) as exc:
        return [f"Unreadable focus pack: {exc}"]
    if (data.get("schema_version") != 1
            or data.get("language") != "multilingual"
            or data.get("usage_policy") != POLICY):
        errors.append("Invalid or unsafe metadata/policy")
    cases = data.get("scenarios")
    if not isinstance(cases, list) or not 1 <= len(cases) <= 300:
        return errors + ["Scenarios must be a bounded nonempty list"]
    ids, inputs = set(), set()
    categories, langs = set(), {"ru": 0, "en": 0}
    seen_phrases: list[tuple[str, set[str]]] = []
    for i, case in enumerate(cases):
        if not isinstance(case, dict):
            errors.append(f"Scenario {i} is not an object")
            continue
        ident, language, message = case.get("id"), case.get("language"), case.get("input")
        if not isinstance(ident, str) or not re.fullmatch(r"focus_[a-z0-9_]+", ident):
            errors.append(f"Invalid ID at {i}")
        if ident in ids:
            errors.append(f"Duplicate ID at {i}")
        ids.add(ident)
        if language not in langs:
            errors.append(f"Unsupported language at {i}")
            continue
        langs[language] += 1
        if not isinstance(message, str) or not 6 <= len(message) <= 280:
            errors.append(f"Invalid message at {i}")
            continue
        key = norm(message)
        if key in inputs:
            errors.append(f"Duplicate normalized text at {i}")
        inputs.add(key)
        tokens = set(key.split())
        for previous_id, previous in seen_phrases:
            shared = len(tokens & previous)
            union = len(tokens | previous)
            if union and shared / union >= .84:
                errors.append(f"Near-duplicate semantics by token overlap: {ident}/{previous_id}")
        seen_phrases.append((ident, tokens))
        category = case.get("category")
        if not isinstance(category, str) or not re.fullmatch(r"[a-z_]+", category):
            errors.append(f"Invalid category at {i}")
        categories.add(category)
        if case.get("audiences") != ["all_ai_bots"]:
            errors.append(f"Unsafe audience at {i}")
        candidates = case.get("candidates")
        try:
            validate_candidates(candidates)
            if len(candidates) > 8:
                errors.append(f"Too many candidates at {i}")
        except (ValueError, TypeError, KeyError) as exc:
            errors.append(f"Invalid candidates at {i}: {exc}")
            continue
        valid_ids = {c["id"] for c in candidates}
        for fld in ("focus_id", "initial_focus_id"):
            if fld in case and case[fld] not in valid_ids:
                errors.append(f"Invalid {fld} at {i}")
        expected = case.get("expected_ids")
        if (not isinstance(expected, list) or len(expected) != len(set(expected))
                or any(identifier not in valid_ids for identifier in expected)):
            errors.append(f"Invalid expected IDs at {i}")
        if case.get("expected_status") not in STATUSES:
            errors.append(f"Invalid expected status at {i}")
        if "advance" in case and (type(case["advance"]) is not int or not 1 <= case["advance"] <= 100):
            errors.append(f"Invalid age at {i}")
        if "reset" in case and case["reset"] is not True:
            errors.append(f"Invalid reset at {i}")
        if "require_confirmation" in case and case["require_confirmation"] is not True:
            errors.append(f"Invalid confirmation at {i}")
        if "query_language" in case and case["query_language"] not in langs:
            errors.append(f"Invalid query language at {i}")
    if len(cases) != 56 or langs != {"ru": 28, "en": 28} or len(categories) != 14:
        errors.append(f"Unexpected coverage: {len(cases)} / {langs} / {len(categories)} categories")
    # Reject source collisions across all previously published collections,
    # including nested contrast readings and reference situations.
    for other in manifest["packs"]:
        relative = other.get("path")
        if relative == PACK:
            continue
        if not isinstance(relative, str) or not relative.startswith("packs/ru/"):
            continue
        book = json.loads((root / relative).read_text(encoding="utf-8"))
        def visit(obj):
            if isinstance(obj, list):
                for value in obj:
                    yield from visit(value)
            elif isinstance(obj, dict):
                for field, value in obj.items():
                    if field in {"input", "source", "expression"} and isinstance(value, str):
                        yield value
                    yield from visit(value)
        for phrase in visit(book):
            if norm(phrase) in inputs:
                errors.append(f"Cross-pack normalized source collision in {relative}")
    return errors


if __name__ == "__main__":
    issues = validate_turn_focus_pack()
    if issues:
        for issue in issues:
            print("FOCUS_ERROR", issue)
        raise SystemExit(1)
    print("TURN_FOCUS_PACK_VALID scenarios=56 ru=28 en=28 categories=14")
