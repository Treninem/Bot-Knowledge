"""Executable checks for conservative bilingual clarification cases."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "packs/ru/clarification_boundaries.json"
cases = json.loads(DATA.read_text(encoding="utf-8"))["cases"]
assert len(cases) == 12
assert len({c["id"] for c in cases}) == 12
assert len({" ".join(c["input"].casefold().split()) for c in cases}) == 12
assert {c["language"] for c in cases} == {"ru", "en"}
for case in cases:
    assert case["audiences"] == ["all_ai_bots"]
    assert case["missing_fact"] and case["clarifying_question"]
    assert case["forbidden_assumption"] and case["safe_next_step"]
manifest = json.loads((ROOT / "manifest.json").read_text(encoding="utf-8"))
entry = next(p for p in manifest["packs"] if p["path"] == "packs/ru/clarification_boundaries.json")
assert hashlib.sha256(DATA.read_bytes()).hexdigest() == entry["sha256"]
print("12 distinct RU/EN clarification boundary cases verified")
