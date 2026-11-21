"""Read-only structural and privacy gate for T711 editorial candidates.

This does not certify semantic originality or consumer compatibility.
"""
import json
import re
import sys
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PATH = ROOT / "staging/ru/correction_followup_t711_candidates.json"
EXPECTED = "user_corrects_prior_assumption"


def norm(value):
    value = unicodedata.normalize("NFKC", value).casefold().replace("ё", "е")
    return " ".join(re.findall(r"\w+", value))


def validate(path=PATH):
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    if data.get("intent_id") != EXPECTED or data.get("consumer_registered") is not False:
        raise ValueError("wrong intent or registered staging")
    if data.get("target") != 100 or data.get("language") != "ru":
        raise ValueError("wrong target/language")
    rules = data.get("constraints", {})
    if any(rules.get(k) is not True for k in
           ("read_only", "requires_direct_address", "requires_context_match",
            "no_sanctions", "no_personal_data")):
        raise ValueError("unsafe constraints")
    if (data.get("editorially_accepted") != 0 or
            data.get("remaining_to_target_accepted") != 100 or
            data.get("new_staged_candidates") != 100 or
            data.get("prior_verified_accepted") != 0 or
            data.get("remaining_to_target_if_all_accepted") != 0):
        raise ValueError("staging accounting mismatch: candidates are not accepted")
    rows = data.get("replies")
    if not isinstance(rows, list) or len(rows) != 100:
        raise ValueError("expected 100 staging candidates")
    for i, row in enumerate(rows, 1):
        if not isinstance(row, dict):
            raise ValueError(f"invalid candidate object at {i}")
        if row.get("id") != f"correction_followup_{i:03d}":
            raise ValueError(f"non-sequential or unexpected candidate ID at {i}")
    for key in ("id", "scenario", "text", "context_note"):
        values = []
        for i, row in enumerate(rows, 1):
            if not isinstance(row, dict) or not isinstance(row.get(key), str):
                raise ValueError(f"invalid {key} at {i}")
            val = norm(row[key])
            if not val:
                raise ValueError(f"empty {key} at {i}")
            values.append(val)
        if len(set(values)) != len(values):
            raise ValueError(f"normalized duplicate {key}")
    for i, row in enumerate(rows, 1):
        if (row.get("language") != "ru" or row.get("context") != "direct_correction"
                or row.get("read_only") is not True
                or row.get("audiences") != ["all_ai_bots"]
                or not isinstance(row.get("context_note"), str)
                or not row["context_note"].strip()
                or not isinstance(row.get("avoid"), str) or not row["avoid"].strip()):
            raise ValueError(f"invalid selection metadata at {i}")
        # Context notes and exclusion guidance are public staging content too.
        for field in ("scenario", "context_note", "text", "avoid"):
            if re.search(r"(?i)(?:https?://|[\w.+-]+@[\w.-]+\.[^\W\d_]{2,})", row[field]):
                raise ValueError(f"possible URL or email in {field} at reply {i}")
    return len(rows)


if __name__ == "__main__":
    try:
        count = validate()
    except (ValueError, OSError, json.JSONDecodeError) as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        raise SystemExit(1)
    print(f"PASS: {count} structurally unique staging candidates; editorial acceptance NOT verified")
