"""Regression: quotes, hypotheticals and syntax must not grant style consent."""
from __future__ import annotations

import json
import tempfile
import time
from pathlib import Path

from composable_style import ComposableStyle
from dialogue_preferences import ROOT, PreferenceSession, load_preferences, load_scoped_requests
from validate_style_boundaries import PACK, validate_style_boundaries

assert validate_style_boundaries() == [], validate_style_boundaries()
rows = json.loads((ROOT / PACK).read_text(encoding="utf-8"))["adversarial_cases"]
assert len(rows) == 48
book, scoped = load_preferences(), load_scoped_requests()
composer = ComposableStyle()


def fresh() -> PreferenceSession:
    return PreferenceSession(book, scoped_book=scoped, composer=composer)


for row in rows:
    session = fresh()
    for method in (session.observe, session.observe_scoped, session.observe_composed):
        got = method(row["input"], language=row["language"], addressed=True)
        assert got["status"] == "unknown_input", (row["id"], method.__name__, got)
        assert all(value is None for value in session.snapshot().values())
    assert session.turn == 0 and not session.one_reply and not session.session_rules

# All 160 previously approved literal legacy/scoped requests still work.
for field, method_name in ((book["cases"], "observe"),
                           (scoped["cases"], "observe_scoped")):
    for row in field:
        session = fresh()
        result = getattr(session, method_name)(
            row["input"], language=row["language"], addressed=True
        )
        assert result["status"] == "updated", row["id"]


def wrappers(source: str) -> tuple[str, ...]:
    return (
        '«' + source + '»',
        '"' + source + '"',
        chr(96) + source + chr(96),
        '[' + source + ']',
        source + ';',
        source + ':',
        source + '?!',
        source + "\n",
        '**' + source + '**',
        '<quote>' + source + '</quote>',
    )


# Previously outer quotation or extra punctuation could disappear under norm().
negative_wrappers = 0
for field, method_name in ((book["cases"], "observe"),
                           (scoped["cases"], "observe_scoped")):
    for row in field:
        for attack in wrappers(row["input"]):
            session = fresh()
            result = getattr(session, method_name)(
                attack, language=row["language"], addressed=True
            )
            assert result["status"] == "unknown_input", (
                method_name, row["id"], attack, result
            )
            assert all(value is None for value in session.snapshot().values())
            negative_wrappers += 1

base = next(r for r in book["cases"] if r["language"] == "ru")
for changed in (base["input"].upper(), "  " + base["input"] + "  ",
                base["input"].replace(" ", "   ")):
    assert fresh().observe(changed, language="ru", addressed=True)["status"] == "updated"

for bad in (None, 7, {}, [], "\x00", "\u200b", "A" * 300):
    for method in ("observe", "observe_scoped"):
        session = fresh()
        assert getattr(session, method)(
            bad, language="ru", addressed=True
        )["status"] == "unknown_input"
        assert all(x is None for x in session.snapshot().values())

with tempfile.TemporaryDirectory() as tmp:
    root = Path(tmp)
    (root / "packs/ru").mkdir(parents=True)
    (root / "manifest.json").write_bytes((ROOT / "manifest.json").read_bytes())
    (root / PACK).write_bytes((ROOT / PACK).read_bytes() + b" ")
    assert any("SHA-256" in item for item in validate_style_boundaries(root))

started = time.perf_counter()
for cycle in range(1, 11):
    for row in rows:
        session = fresh()
        assert session.observe(row["input"], language=row["language"], addressed=True)["status"] == "unknown_input"
        assert session.observe_scoped(row["input"], language=row["language"], addressed=True)["status"] == "unknown_input"
        assert session.observe_composed(row["input"], language=row["language"], addressed=True)["status"] == "unknown_input"
    print(f"STYLE_BOUNDARIES_PASS {cycle}/10 original_cases=48 checks=144")
for _ in range(1000):
    session = fresh()
    assert session.observe('«' + base["input"] + '»', language="ru", addressed=True)["status"] == "unknown_input"
print(f"STYLE_BOUNDARIES_WRAPPERS_OK count={negative_wrappers}")
print(f"STYLE_BOUNDARIES_1000_LOCAL_CALLS_OK elapsed_with_10_rounds_ms={(time.perf_counter()-started)*1000:.2f}")
