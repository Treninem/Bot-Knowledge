"""Validate bilingual discourse choices and collision-free synthetic examples."""
from __future__ import annotations

import json
import re
from collections import Counter
from pathlib import Path

from discourse_links import ROOT, PACK, POLICY, REGISTERS, load_pack

RELATIONS = {
    "addition", "contrast", "concession", "cause", "result", "condition",
    "exception", "sequence", "example", "reformulation", "correction",
    "alternative", "summary", "comparison", "simultaneity",
}
FIELDS = {"id", "language", "relation", "topic", "input", "usage",
          "avoid", "wrong_relation", "variants", "audiences"}


def normalized(text: str) -> str:
    return " ".join(re.findall(r"[^\W_]+", text.casefold().replace("ё", "е")))


def validate_discourse(root: Path = ROOT) -> list[str]:
    errors: list[str] = []
    try:
        book = load_pack(root)
    except (ValueError, KeyError, OSError, TypeError) as exc:
        return ["Cannot load discourse pack: " + str(exc)]
    cases = book.get("cases")
    if book.get("usage_policy") != POLICY or not isinstance(cases, list) or len(cases) != 30:
        return ["Discourse policy/count invalid"]
    if len((root / PACK).read_bytes()) > 64 * 1024:
        errors.append("Discourse pack exceeds 64KiB")
    seen_ids, seen_inputs = set(), set()
    counts = Counter()
    tokens = []
    for row in cases:
        if not isinstance(row, dict) or set(row) != FIELDS:
            errors.append("Invalid discourse row shape")
            continue
        lang, relation, cid = row["language"], row["relation"], row["id"]
        if (lang not in {"ru", "en"} or relation not in RELATIONS
                or cid != f"discourse_{lang}_{relation}" or cid in seen_ids):
            errors.append("Invalid or repeated discourse ID")
        seen_ids.add(cid)
        counts[lang] += 1
        if row["topic"] != relation or row["wrong_relation"] not in RELATIONS or row["wrong_relation"] == relation:
            errors.append("Invalid relation contrast")
        if row["audiences"] != ["all_ai_bots"]:
            errors.append("Unexpected discourse audience")
        for label in ("input", "usage", "avoid"):
            val = row[label]
            if not isinstance(val, str) or not 10 <= len(val) <= 240:
                errors.append("Bad discourse example or semantic guard")
        inp = normalized(row["input"])
        if inp in seen_inputs:
            errors.append("Duplicate normalized discourse example")
        seen_inputs.add(inp)
        tokens.append(set(inp.split()))
        variants = row["variants"]
        if (not isinstance(variants, dict) or set(variants) != REGISTERS
                or any(not isinstance(v, str) or not 2 <= len(v) <= 65
                       or "\n" in v or "\r" in v for v in variants.values())):
            errors.append("Invalid discourse connector register")
    if seen_ids != {f"discourse_{lang}_{relation}"
                   for lang in ("ru", "en") for relation in RELATIONS}:
        errors.append("Incomplete discourse relation coverage")
    if counts != {"ru": 15, "en": 15}:
        errors.append("Unbalanced discourse languages")
    for i, left in enumerate(tokens):
        for right in tokens[:i]:
            if left and right and len(left & right) / len(left | right) >= 0.85:
                errors.append("Near-duplicate input (Jaccard >= .85)")
                break
    manifest = json.loads((root / "manifest.json").read_text(encoding="utf-8"))
    prior_ids, prior_inputs = set(), set()
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
                for key in ("input", "source", "expression", "message"):
                    if isinstance(item.get(key), str):
                        prior_inputs.add(normalized(item[key]))
                if isinstance(item.get("examples"), list):
                    for value in item["examples"]:
                        if isinstance(value, str):
                            prior_inputs.add(normalized(value))
                if isinstance(item.get("variants"), dict):
                    for value in item["variants"].values():
                        if isinstance(value, str):
                            prior_inputs.add(normalized(value))
    if prior_ids & seen_ids:
        errors.append("Discourse IDs collide with existing packs")
    if prior_inputs & seen_inputs:
        errors.append("Discourse examples collide with existing packs")
    return errors


if __name__ == "__main__":
    issues = validate_discourse()
    if issues:
        raise SystemExit("\n".join(issues))
    print("DISCOURSE_VALID cases=30 ru=15 en=15 relations=15 register_variants=90")
