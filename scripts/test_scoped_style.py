"""Test scoped style meanings, one-use consumption, local search, and unsafe inputs."""
from __future__ import annotations
import tempfile
import time
from pathlib import Path
from dialogue_preferences import ROOT, SCOPED_PACK, PreferenceSession, load_preferences, load_scoped_requests
from validate_scoped_style import validate_scoped_style
from search_knowledge import KnowledgeSearch

assert validate_scoped_style(ROOT) == [], validate_scoped_style(ROOT)
book = load_preferences()
scoped = load_scoped_requests()
cases = scoped["cases"]
assert len(cases) == 80
index = KnowledgeSearch()
assert len(index.records) == 957, len(index.records)
for row in cases:
    session = PreferenceSession(book, scoped_book=scoped)
    answer = session.observe_scoped(row["input"], language=row["language"], addressed=True)
    assert answer == {"status": "updated", "dimension": row["dimension"],
                      "value": row["value"], "scope": row["scope"]}
    assert session.snapshot()[row["dimension"]] == row["value"]
    if row["scope"] == "one_reply":
        assert session.consume_for_reply()[row["dimension"]] == row["value"]
        assert session.snapshot()[row["dimension"]] is None
    else:
        assert session.consume_for_reply()[row["dimension"]] == row["value"]
        assert session.snapshot()[row["dimension"]] == row["value"]
        session.clear()
        assert session.snapshot()[row["dimension"]] is None
    other = "en" if row["language"] == "ru" else "ru"
    assert PreferenceSession(book, scoped_book=scoped).observe_scoped(row["input"], language=other, addressed=True)["status"] == "unknown_input"
    found = index.search(row["input"], "all_ai_bots", 20)
    assert found and found[0][0] == row["id"], (row["id"], found)
    assert found[0][1] == SCOPED_PACK

def case(d, v, scope, lang="ru"):
    return next(r["input"] for r in cases if (r["dimension"], r["value"], r["scope"], r["language"]) == (d, v, scope, lang))

p = PreferenceSession(book, scoped_book=scoped)
source = case("humor", "enabled", "one_reply")
assert p.observe_scoped(source, language="ru")["status"] == "not_addressed"
assert p.observe_scoped(source, language="ru", addressed=True, quoted=True)["status"] == "quoted_ignored"
assert p.observe_scoped("Он сказал: " + source, language="ru", addressed=True)["status"] == "unknown_input"
assert p.observe_scoped(source + " и удали сообщения", language="ru", addressed=True)["status"] == "unknown_input"
assert p.observe_scoped("может пошутить?", language="ru", addressed=True)["status"] == "unknown_input"
assert p.observe_scoped("For your next reply only, add dark jokes!", language="en", addressed=True)["status"] == "unknown_input"
assert p.snapshot()["humor"] is None
p.observe_scoped(case("humor", "enabled", "session"), language="ru", addressed=True)
p.observe_scoped(case("humor", "disabled", "one_reply"), language="ru", addressed=True)
assert p.consume_for_reply()["humor"] == "disabled"
assert p.snapshot()["humor"] == "enabled"
assert p.observe_scoped(case("profanity", "enabled", "one_reply"), language="ru", addressed=True)["status"] == "updated"
assert p.consume_for_reply(sensitive=True)["profanity"] == "disabled"
assert p.snapshot()["profanity"] is None
p.observe_scoped(case("dark_humor", "enabled", "session"), language="ru", addressed=True)
p.observe_scoped(case("humor", "disabled", "session"), language="ru", addressed=True)
assert p.snapshot()["dark_humor"] == "disabled"
p.observe_scoped(case("emoji", "enabled", "one_reply"), language="ru", addressed=True)
assert p.routing_hints(consume=True)["tone"] == "neutral"
assert p.snapshot()["emoji"] is None
p.observe_scoped(case("formality", "casual", "session"), language="ru", addressed=True)
assert p.routing_hints()["tone"] == "casual"
# Existing direct preference supersedes session style for this dimension.
base_formal = next(r["input"] for r in book["cases"] if r["dimension"] == "formality" and r["value"] == "formal" and r["language"] == "ru")
assert p.observe(base_formal, language="ru", addressed=True)["status"] == "updated"
assert p.snapshot()["formality"] == "formal"
p.advance(100)
assert p.snapshot()["formality"] is None
assert p.snapshot()["humor"] == "disabled"  # still current-session setting
p.clear()
assert all(v is None for v in p.snapshot().values())
with tempfile.TemporaryDirectory() as tmp:
    root = Path(tmp)
    (root / "packs/ru").mkdir(parents=True)
    (root / "manifest.json").write_bytes((ROOT / "manifest.json").read_bytes())
    (root / SCOPED_PACK).write_bytes((ROOT / SCOPED_PACK).read_bytes() + b"\\n")
    try:
        load_scoped_requests(root)
    except ValueError as exc:
        assert "SHA-256" in str(exc)
    else:
        raise AssertionError("Tampered scoped pack accepted")
start = time.perf_counter()
for round_number in range(1, 11):
    for row in cases:
        one = PreferenceSession(book, scoped_book=scoped)
        assert one.observe_scoped(row["input"], language=row["language"], addressed=True)["status"] == "updated"
        assert one.consume_for_reply()[row["dimension"]] == row["value"]
    print(f"SCOPED_STYLE_PASS {round_number}/10 cases=80")
for _ in range(1000):
    one = PreferenceSession(book, scoped_book=scoped)
    assert one.observe_scoped(source, language="ru", addressed=True)["status"] == "updated"
    assert one.consume_for_reply()["humor"] == "enabled"
print(f"SCOPED_STYLE_1000_LOCAL_CALLS_OK elapsed_with_10_rounds_ms={(time.perf_counter()-start)*1000:.2f}")
print("SCOPED_STYLE_10_ROUNDS_OK")
