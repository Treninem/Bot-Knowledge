"""Structure, privacy, number-preservation and duplicate checks for paraphrases."""
from __future__ import annotations

import json
import re
from collections import Counter
from pathlib import Path

from paraphrase_meaning import normalized, POLICY, PACK

ID = re.compile(r"para_(ru|en)_[a-z0-9_]+\Z")
CATEGORY = re.compile(r"[a-z_]{4,36}\Z")
NUM = re.compile(r"(?<!\w)\d+(?:[.,]\d+)?(?!\w)")


def validate_paraphrase_pack(root: Path) -> list[str]:
    errors: list[str] = []
    path = root / PACK
    if not path.exists():
        return ["Missing bilingual paraphrase pack"]
    if path.stat().st_size > 128 * 1024:
        errors.append("Paraphrase pack exceeds 128 KiB")
    try:
        book = json.loads(path.read_text(encoding="utf-8"))
    except (ValueError, UnicodeError):
        return errors + ["Invalid paraphrase pack JSON"]
    if (book.get("schema_version") != 1 or book.get("language") != "multilingual"
            or book.get("usage_policy") != POLICY
            or book.get("tones") != ["neutral", "casual"]):
        errors.append("Invalid paraphrase metadata or safety policy")
    cases = book.get("paraphrases")
    if not isinstance(cases, list) or len(cases) != 48:
        return errors + ["Paraphrase pack must contain 48 approved pairs"]
    ids, seen, categories, locales = set(), set(), set(), Counter()
    for n, entry in enumerate(cases):
        if not isinstance(entry, dict):
            errors.append("Non-object paraphrase case")
            continue
        ident, lang = entry.get("id"), entry.get("language")
        if not isinstance(ident, str) or not ID.fullmatch(ident) or ident in ids:
            errors.append(f"Invalid or duplicate paraphrase ID #{n}")
        ids.add(ident)
        if lang not in {"ru", "en"} or not ident.startswith("para_" + str(lang) + "_"):
            errors.append(f"Invalid language: {ident}")
        locales[lang] += 1
        category = entry.get("category")
        if not isinstance(category, str) or not CATEGORY.fullmatch(category):
            errors.append(f"Invalid category: {ident}")
        categories.add(category)
        if entry.get("audiences") != ["all_ai_bots"]:
            errors.append(f"Unsafe scope: {ident}")
        guard = entry.get("semantic_guard")
        if not isinstance(guard, str) or not 15 <= len(guard) <= 200:
            errors.append(f"Missing semantic guard: {ident}")
        source, variants, bad = entry.get("source"), entry.get("variants"), entry.get("counterexample")
        if (not isinstance(source, str) or not 12 <= len(source) <= 300
                or not isinstance(variants, dict) or set(variants) != {"neutral", "casual"}
                or not isinstance(bad, dict) or set(bad) != {"text", "reason"}
                or not isinstance(bad.get("reason"), str)):
            errors.append(f"Malformed paraphrase case: {ident}")
            continue
        texts = [source, variants["neutral"], variants["casual"], bad["text"]]
        if any(not isinstance(t, str) or not 12 <= len(t) <= 300 for t in texts):
            errors.append(f"Invalid paraphrase text: {ident}")
            continue
        for t in texts:
            k = normalized(t).replace("ё", "е")
            if k in seen:
                errors.append(f"Duplicate normalized paraphrase text: {ident}")
            seen.add(k)
        numeric = set(NUM.findall(source))
        for variant in (variants["neutral"], variants["casual"]):
            if set(NUM.findall(variant)) != numeric:
                errors.append(f"Numbers changed: {ident}")
        if any(k in entry for k in ("action", "auto_apply", "sanction", "github_token")):
            errors.append(f"Unsafe privileged field: {ident}")
    if locales != Counter({"ru": 24, "en": 24}):
        errors.append("Expected 24 RU and 24 EN examples")
    if len(categories) < 15:
        errors.append("Insufficiently diverse semantic categories")
    return errors
