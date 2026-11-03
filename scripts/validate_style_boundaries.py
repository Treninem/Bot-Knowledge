"""Validate synthetic RU/EN negative language cases (not instructions)."""
from __future__ import annotations

import hashlib
import json
import re
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PACK = "packs/ru/style_instruction_boundaries.json"
CATEGORIES = {
    "reported_speech", "hypothetical", "negated_instruction",
    "quoted_document", "metadiscussion", "indirect_request",
    "example_not_command", "mixed_intentions"
}
POLICY = {
    "synthetic_examples_only": True,
    "personal_data_allowed": False,
    "automatic_actions_allowed": False,
    "automatic_sanctions_allowed": False,
    "test_vectors_only": True,
    "no_style_authority": True,
}


def normalized(text: str) -> str:
    return " ".join(re.findall(r"[^\W_]+", text.casefold().replace("ё", "е")))


def validate_style_boundaries(root: Path = ROOT) -> list[str]:
    problems = []
    try:
        manifest = json.loads((root / "manifest.json").read_text(encoding="utf-8"))
        hits = [p["sha256"] for p in manifest["packs"] if p["path"] == PACK]
        if len(hits) != 1:
            return ["Missing or duplicated boundary pack manifest entry"]
        raw = (root / PACK).read_bytes()
        if hashlib.sha256(raw).hexdigest() != hits[0]:
            problems.append("Style boundary SHA-256 mismatch")
        book = json.loads(raw.decode("utf-8"))
    except (OSError, KeyError, ValueError, TypeError) as exc:
        return ["Cannot load style boundary pack: " + str(exc)]
    if (book.get("schema_version") != 1 or book.get("language") != "multilingual"
            or book.get("pack_version") != "2026.10.30.17"
            or book.get("usage_policy") != POLICY):
        problems.append("Incorrect style boundary schema or safety policy")
    cases = book.get("adversarial_cases")
    if not isinstance(cases, list) or len(cases) != 48:
        return problems + ["Boundary pack must contain 48 adversarial cases"]
    ids, inputs = set(), set()
    by_kind = Counter()
    for row in cases:
        if not isinstance(row, dict) or set(row) != {
            "id", "language", "category", "input", "expected_status", "audiences"
        }:
            problems.append("Unexpected boundary case fields")
            continue
        cid, lang, category, source = (
            row["id"], row["language"], row["category"], row["input"]
        )
        if (not isinstance(cid, str) or not cid.isascii()
                or not cid.replace("_", "").isalnum() or cid in ids):
            problems.append("Invalid or duplicated boundary ID")
        ids.add(cid)
        if (lang not in {"ru", "en"} or category not in CATEGORIES
                or row["expected_status"] != "unknown_input"
                or row["audiences"] != ["all_ai_bots"]):
            problems.append("Unsafe or invalid boundary record")
        if not isinstance(source, str) or not 20 <= len(source) <= 200:
            problems.append("Invalid boundary sentence")
            continue
        key = (lang, normalized(source))
        if key in inputs:
            problems.append("Duplicate normalized boundary input")
        inputs.add(key)
        by_kind[(lang, category)] += 1
    if any(by_kind[(lang, category)] != 3
           for lang in ("ru", "en") for category in CATEGORIES):
        problems.append("Expected three distinct cases per language/category")
    # Negative vectors cannot duplicate positive inputs from approved packs.
    known = set()
    for item in manifest["packs"]:
        if item["path"] == PACK:
            continue
        try:
            other = json.loads((root / item["path"]).read_text(encoding="utf-8"))
        except (OSError, ValueError):
            problems.append("Unable to read another pack for duplicate audit")
            continue
        for field in ("cases", "paraphrases", "scenarios", "triggers"):
            for example in other.get(field, []):
                if not isinstance(example, dict):
                    continue
                sentence = example.get("input") or example.get("source")
                if isinstance(sentence, str):
                    known.add((example.get("language", "ru"), normalized(sentence)))
    if inputs.intersection(known):
        problems.append("Boundary sentence duplicates a positive example")
    return problems


if __name__ == "__main__":
    errors = validate_style_boundaries()
    if errors:
        raise SystemExit("\n".join(errors))
    print("STYLE_BOUNDARIES_VALID 48 negative RU/EN contexts, SHA and policy")
