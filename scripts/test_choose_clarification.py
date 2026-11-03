"""Behavioral tests for the conservative clarification selector."""
import json
import tempfile
from pathlib import Path

from choose_clarification import ROOT, choose

cases = json.loads((ROOT / "packs/ru/clarification_boundaries.json").read_text(encoding="utf-8"))["cases"]
for case in cases:
    answer = choose(case["input"], case["language"])
    assert answer == {"id": case["id"], "question": case["clarifying_question"],
                      "safe_next_step": case["safe_next_step"]}
    assert choose("  " + case["input"].upper() + "  ", case["language"]) == answer
    assert choose(case["input"], "en" if case["language"] == "ru" else "ru") is None

assert choose("Please guess the recipient", "en") is None
assert choose("Сделай это к субботе", "ru") is None
assert choose("Удали тот файл и второй тоже", "ru") is None
assert choose("", "ru") is None
assert choose(cases[0]["input"], "unknown") is None

with tempfile.TemporaryDirectory() as tmp:
    root = Path(tmp)
    (root / "packs/ru").mkdir(parents=True)
    (root / "manifest.json").write_bytes((ROOT / "manifest.json").read_bytes())
    (root / "packs/ru/clarification_boundaries.json").write_bytes(
        (ROOT / "packs/ru/clarification_boundaries.json").read_bytes() + b" ")
    try:
        choose(cases[0]["input"], "ru", root)
    except ValueError as exc:
        assert "SHA-256" in str(exc)
    else:
        raise AssertionError("Tampered pack was accepted")

print("12 approved cases, normalization, abstention and SHA failure verified")
