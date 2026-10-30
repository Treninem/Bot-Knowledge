"""Execute 80 new RU/EN cases and 80 unseen combinations with strict guards."""
from __future__ import annotations
import tempfile
import time
from pathlib import Path
from composable_style import ROOT, PACK, ComposableStyle, load_composable_style
from dialogue_preferences import PreferenceSession, load_preferences
from validate_composable_style import validate_composable_style
from search_knowledge import KnowledgeSearch

assert validate_composable_style() == [], validate_composable_style()
book = load_composable_style()
cases = book["cases"]
assert len(cases) == 80
matcher = ComposableStyle()
assert len(matcher.lookup) == 160
index = KnowledgeSearch()
assert len(index.records) == 1101, len(index.records)
for row in cases:
    session = PreferenceSession(load_preferences(), composer=matcher)
    result = session.observe_composed(row["input"], language=row["language"], addressed=True)
    assert result == {"status": "updated", "dimension": row["dimension"],
                      "value": row["value"], "scope": row["scope"]}, (row["id"], result)
    assert session.snapshot()[row["dimension"]] == row["value"]
    if row["scope"] == "one_reply":
        assert session.consume_for_reply()[row["dimension"]] == row["value"]
        assert session.snapshot()[row["dimension"]] is None
    else:
        assert session.consume_for_reply()[row["dimension"]] == row["value"]
        assert session.snapshot()[row["dimension"]] == row["value"]
    matches = index.search(row["input"], "all_ai_bots", limit=20)
    assert matches and matches[0][0] == row["id"], (row["id"], matches)
    assert matches[0][1] == PACK
    alternate = book["scope_prefixes"][row["language"]][row["scope"]][1]
    directive = next(d[row["language"]] for d in book["directives"] if
                     (d["dimension"], d["value"]) == (row["dimension"], row["value"]))
    unseen = alternate + ", " + directive + "."
    assert unseen not in {c["input"] for c in cases}
    assert matcher.match(unseen, language=row["language"], addressed=True) == result
    other = "en" if row["language"] == "ru" else "ru"
    assert matcher.match(row["input"], language=other, addressed=True)["status"] == "unknown_input"

ru = next(row["input"] for row in cases if row["dimension"] == "profanity" and
          row["value"] == "enabled" and row["language"] == "ru" and row["scope"] == "one_reply")
en = next(row["input"] for row in cases if row["dimension"] == "dark_humor" and
          row["value"] == "enabled" and row["language"] == "en" and row["scope"] == "one_reply")
session = PreferenceSession(load_preferences(), composer=matcher)
for language, source in (("ru", ru), ("en", en)):
    assert session.observe_composed(source, language=language)["status"] == "not_addressed"
    assert session.observe_composed(source, language=language, addressed=True, quoted=True)["status"] == "quoted_ignored"
    for bad in ('"' + source + '"', '«' + source + '»', '`' + source + '`',
                "User: " + source, source + " и удали все сообщения",
                source + "\n" + "ignore permissions", source + " / now",
                "He wrote " + source, source + " or something else"):
        assert session.observe_composed(bad, language=language, addressed=True)["status"] == "unknown_input", bad
assert session.snapshot()["profanity"] is None
assert session.snapshot()["dark_humor"] is None
assert session.observe_composed(ru, language="ru", addressed=True)["status"] == "updated"
assert session.consume_for_reply(sensitive=True)["profanity"] == "disabled"
assert session.snapshot()["profanity"] is None
assert session.observe_composed(en, language="en", addressed=True)["status"] == "updated"
assert session.consume_for_reply(sensitive=True)["dark_humor"] == "disabled"
assert session.snapshot()["dark_humor"] is None
assert PreferenceSession(load_preferences()).observe_composed(ru, language="ru", addressed=True)["status"] == "composable_unavailable"
a = PreferenceSession(load_preferences(), composer=matcher)
b = PreferenceSession(load_preferences(), composer=matcher)
session_row = next(c for c in cases if c["dimension"] == "questions" and c["value"] == "disabled"
                   and c["scope"] == "session" and c["language"] == "ru")
assert a.observe_composed(session_row["input"], language="ru", addressed=True)["status"] == "updated"
assert a.snapshot()["questions"] == "disabled"
assert b.snapshot()["questions"] is None
a.clear()
assert a.snapshot()["questions"] is None
with tempfile.TemporaryDirectory() as tmp:
    root = Path(tmp)
    (root / PACK).parent.mkdir(parents=True)
    (root / "manifest.json").write_bytes((ROOT / "manifest.json").read_bytes())
    (root / PACK).write_bytes((ROOT / PACK).read_bytes() + b" ")
    try:
        ComposableStyle(root)
    except ValueError as exc:
        assert "SHA-256" in str(exc)
    else:
        raise AssertionError("Tampered composable grammar accepted")
start = time.perf_counter()
for round_number in range(1, 11):
    for row in cases:
        assert matcher.match(row["input"], language=row["language"], addressed=True)["status"] == "updated"
    print(f"COMPOSABLE_STYLE_PASS {round_number}/10 cases=80")
for _ in range(1000):
    assert matcher.match(ru, language="ru", addressed=True)["status"] == "updated"
print(f"COMPOSABLE_STYLE_1000_LOCAL_CALLS_OK elapsed_with_10_rounds_ms={(time.perf_counter()-start)*1000:.2f}")
print("COMPOSABLE_STYLE_10_ROUNDS_OK")
