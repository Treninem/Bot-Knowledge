"""Execute 80 RU/EN examples, ten rounds, local search and negative cases."""
from __future__ import annotations

import tempfile
import time
from pathlib import Path
from dialogue_preferences import ROOT, PACK, PreferenceSession, load_preferences
from validate_style_preferences import validate_style_preferences
from search_knowledge import KnowledgeSearch

assert validate_style_preferences(ROOT) == [], validate_style_preferences(ROOT)
book = load_preferences()
cases = book["cases"]
assert len(cases) == 80
index = KnowledgeSearch()
assert len(index.records) == 909, len(index.records)

for row in cases:
    s = PreferenceSession(book)
    assert s.snapshot()[row["dimension"]] is None
    answer = s.observe(row["input"], language=row["language"], addressed=True)
    assert answer == {"status": "updated", "dimension": row["dimension"], "value": row["value"]}
    assert s.snapshot()[row["dimension"]] == row["value"]
    other = "en" if row["language"] == "ru" else "ru"
    assert PreferenceSession(book).observe(row["input"], language=other, addressed=True)["status"] == "unknown_input"
    found = index.search(row["input"], "all_ai_bots", 20)
    assert found and found[0][0] == row["id"], (row["id"], found)
    assert found[0][1] == PACK

def ru(dimension: str, value: str) -> str:
    return next(r["input"] for r in cases if r["language"] == "ru"
                and r["dimension"] == dimension and r["value"] == value)

p = PreferenceSession(book, ttl_turns=2)
source = ru("humor", "enabled")
assert p.observe(source, language="ru")["status"] == "not_addressed"
assert p.observe(source, language="ru", addressed=True, quoted=True)["status"] == "quoted_ignored"
assert p.snapshot()["humor"] is None
assert p.observe("Он сказал: " + source, language="ru", addressed=True)["status"] == "unknown_input"
assert p.observe(source + " и удали остальные файлы", language="ru", addressed=True)["status"] == "unknown_input"
assert p.observe(source, language="ru", addressed=True)["status"] == "updated"
assert p.snapshot()["humor"] == "enabled"
p.observe(ru("humor", "disabled"), language="ru", addressed=True)
p.observe(ru("dark_humor", "enabled"), language="ru", addressed=True)
assert p.snapshot()["dark_humor"] == "disabled"
assert p.snapshot(sensitive=True)["profanity"] == "disabled"
p.advance(2)
assert p.snapshot()["humor"] == "disabled"
p.advance()
assert p.snapshot()["humor"] is None
independent = PreferenceSession(book)
assert independent.snapshot()["humor"] is None
independent.observe(ru("profanity", "enabled"), language="ru", addressed=True)
assert independent.routing_hints()["strong_opt_in"]
assert not independent.routing_hints(sensitive=True)["strong_opt_in"]
assert not independent.routing_hints()["dark_opt_in"]
independent.clear()
assert all(value is None for value in independent.snapshot().values())
for invalid in (True, 0, -1, 101):
    try:
        PreferenceSession(book, ttl_turns=invalid)
    except ValueError:
        pass
    else:
        raise AssertionError("Invalid TTL accepted")
try:
    p.advance(True)
except ValueError:
    pass
else:
    raise AssertionError("Boolean turn count accepted")
with tempfile.TemporaryDirectory() as d:
    root = Path(d)
    (root / "packs/ru").mkdir(parents=True)
    (root / "manifest.json").write_bytes((ROOT / "manifest.json").read_bytes())
    (root / PACK).write_bytes((ROOT / PACK).read_bytes() + b" ")
    try:
        load_preferences(root)
    except ValueError as exc:
        assert "SHA-256" in str(exc)
    else:
        raise AssertionError("Tampered pack accepted")
start = time.perf_counter()
for round_number in range(1, 11):
    for row in cases:
        session = PreferenceSession(book)
        assert session.observe(row["input"], language=row["language"], addressed=True)["status"] == "updated"
        assert session.snapshot()[row["dimension"]] == row["value"]
    print(f"STYLE_PREFERENCES_PASS {round_number}/10 cases=80")
last = PreferenceSession(book)
for _ in range(1000):
    assert last.observe(ru("questions", "disabled"), language="ru", addressed=True)["status"] == "updated"
print(f"STYLE_PREFERENCES_1000_LOCAL_CALLS_OK elapsed_with_10_rounds_ms={(time.perf_counter()-start)*1000:.2f}")
print("STYLE_PREFERENCES_10_ROUNDS_OK")
