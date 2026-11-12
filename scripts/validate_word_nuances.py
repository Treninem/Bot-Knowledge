"""Validate synthetically authored RU/EN near-synonym meanings and privacy."""
from __future__ import annotations

from collections import defaultdict
import hashlib
import json
import re
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PACK = "packs/ru/word_nuances.json"
POLICY = {"synthetic_only": True, "no_private_memory": True,
          "no_automatic_actions": True, "no_automatic_sanctions": True,
          "caller_provides_explicit_meaning": True,
          "no_claims_of_consumer_integration": True}
FIELDS = {"id", "family", "category", "language", "sense", "source",
          "meaning", "semantic_guard", "variants", "audiences",
          "requires_dark_opt_in", "requires_strong_opt_in"}
LANGUAGES = {"ru", "en"}
TONES = {"neutral", "formal", "casual"}


def normalized(value: str) -> str:
    value = unicodedata.normalize("NFKC", value).casefold().replace("ё", "е")
    return " ".join(re.findall(r"[a-zа-я0-9]+", value))


def version_not_newer(pack_version: str, knowledge_version: str) -> bool:
    """Existing immutable packs may have an earlier version than the manifest."""
    def parse(value: str):
        if not isinstance(value, str) or not re.fullmatch(r"\d{4}\.\d{2}\.\d{2}\.\d+", value):
            return None
        return tuple(int(part) for part in value.split("."))
    pack, manifest = parse(pack_version), parse(knowledge_version)
    return pack is not None and manifest is not None and pack <= manifest


def validate_word_nuances_pack(root: Path = ROOT) -> list[str]:
    issues: list[str] = []
    try:
        manifest = json.loads((root / "manifest.json").read_text(encoding="utf-8"))
        hashes = [row["sha256"] for row in manifest["packs"] if row["path"] == PACK]
        if len(hashes) != 1:
            return ["word nuances manifest entry missing or duplicated"]
        raw = (root / PACK).read_bytes()
        if hashlib.sha256(raw).hexdigest() != hashes[0]:
            return ["word nuances SHA-256 mismatch"]
        book = json.loads(raw.decode("utf-8"))
    except (OSError, ValueError, KeyError, TypeError) as exc:
        return [f"word nuances cannot load: {exc}"]

    if (book.get("schema_version") != 1 or book.get("language") != "multilingual"
            or not version_not_newer(book.get("pack_version"), manifest.get("knowledge_version"))
            or book.get("usage_policy") != POLICY or not isinstance(book.get("tones"), list)
            or len(book["tones"]) != 3 or set(book["tones"]) != TONES):
        issues.append("invalid word nuances schema/version/policy/tones")
    cases = book.get("cases")
    if not isinstance(cases, list) or len(cases) != 72:
        return issues + ["word nuances require 72 original sense cases"]

    ids, sources, variants = set(), set(), set()
    by_family: dict[str, dict[str, set[str]]] = defaultdict(lambda: defaultdict(set))
    source_rows: list[tuple[str, set[str], str]] = []
    for case in cases:
        if not isinstance(case, dict) or set(case) != FIELDS:
            issues.append("unsafe or incomplete word nuance fields")
            continue
        cid = case["id"]
        family, sense, lang = case["family"], case["sense"], case["language"]
        if not all(isinstance(x, str) and re.fullmatch(r"[a-z][a-z0-9_]{1,50}", x)
                   for x in (family, sense)) or lang not in LANGUAGES:
            issues.append(f"invalid family, sense or language: {cid}")
            continue
        if not isinstance(cid, str) or cid != f"lex_{family}_{sense}_{lang}" or cid in ids:
            issues.append(f"duplicate/malformed word nuance ID: {cid}")
        ids.add(cid)
        if not isinstance(case["category"], str) or not 3 <= len(case["category"]) <= 60:
            issues.append(f"invalid category: {cid}")
        if case["audiences"] != ["all_ai_bots"]:
            issues.append(f"word nuance audience must be general: {cid}")
        if (type(case["requires_dark_opt_in"]) is not bool
                or type(case["requires_strong_opt_in"]) is not bool
                or (case["requires_dark_opt_in"] != (family == "humor" and sense == "dark"))
                or (case["requires_strong_opt_in"] != (family == "emotion" and sense == "anger"))):
            issues.append(f"unsafe opt-in flags: {cid}")
        for field in ("source", "meaning", "semantic_guard"):
            value = case[field]
            if not isinstance(value, str) or not 10 <= len(value) <= 250:
                issues.append(f"invalid {field}: {cid}")
        if not isinstance(case["source"], str):
            continue
        key = normalized(case["source"])
        if not key or key in sources:
            issues.append(f"duplicate or empty normalized source: {cid}")
        sources.add(key)
        source_rows.append((cid, set(key.split()), lang))
        ph = case["variants"]
        if not isinstance(ph, dict) or set(ph) != TONES:
            issues.append(f"invalid variant tones: {cid}")
            continue
        for tone in TONES:
            text = ph[tone]
            if not isinstance(text, str) or not 9 <= len(text) <= 180:
                issues.append(f"invalid {tone} phrase: {cid}")
                continue
            norm = normalized(text)
            if not norm or norm in variants:
                issues.append(f"reused normalized lexical expression: {cid} {tone}")
            variants.add(norm)
        by_family[family][lang].add(sense)

    if len(ids) != 72 or len(sources) != 72 or len(variants) != 216:
        issues.append("wrong count of unique ids/sources/phrases")
    if len(by_family) != 12:
        issues.append("expected 12 non-overlapping meaning families")
    for family, languages in by_family.items():
        if set(languages) != LANGUAGES or len(languages["ru"]) != 3 or languages["ru"] != languages["en"]:
            issues.append(f"missing bilingual sense counterpart: {family}")

    for i, (id_a, words_a, lang_a) in enumerate(source_rows):
        for id_b, words_b, lang_b in source_rows[i + 1:]:
            if lang_a == lang_b and len(words_a | words_b) >= 5:
                similarity = len(words_a & words_b) / len(words_a | words_b)
                if similarity >= 0.85:
                    issues.append(f"near-duplicate sources: {id_a}/{id_b} Jaccard={similarity:.2f}")

    # Only approved examples, never raw chat data or arbitrary execution keys.
    # Compare exact normalized new input examples with existing public pack inputs.
    def existing_inputs(node) -> set[str]:
        out = set()
        def walk(obj):
            if isinstance(obj, list):
                for v in obj:
                    walk(v)
            elif isinstance(obj, dict):
                for key, val in obj.items():
                    if key in {"input", "source", "expression", "message"} and isinstance(val, str):
                        out.add(normalized(val))
                    elif key == "examples" and isinstance(val, list):
                        out.update(normalized(v) for v in val if isinstance(v, str))
                    elif isinstance(val, (dict, list)):
                        walk(val)
        walk(node)
        return out
    other = set()
    for entry in manifest["packs"]:
        if entry["path"] == PACK:
            continue
        try:
            other.update(existing_inputs(json.loads((root / entry["path"]).read_text(encoding="utf-8"))))
        except (OSError, ValueError):
            issues.append(f"unable to compare previous pack {entry['path']}")
    duplicates = sources & other
    if duplicates:
        issues.append(f"{len(duplicates)} new source examples duplicate prior packs")
    return issues


if __name__ == "__main__":
    errors = validate_word_nuances_pack()
    if errors:
        print("WORD_NUANCES_VALIDATE_FAIL", errors)
        raise SystemExit(1)
    print("WORD_NUANCES_VALIDATE_PASS families=12 bilingual_cases=72 variants=216")
