"""Executable 48-case short reply + no-action + local short-token search tests."""
from __future__ import annotations

import tempfile
import time
from pathlib import Path

from short_turns import ShortTurns, load_pack, ROOT, PACK
from search_knowledge import KnowledgeSearch
from validate_short_turns import validate_short_turns

assert validate_short_turns() == [], validate_short_turns()
cases = load_pack()["cases"]
assert len(cases) == 48
engine = ShortTurns()
index = KnowledgeSearch()
assert len(index.records) >= 1179, len(index.records)
assert len({row["id"] for row in cases}) == 48
assert len({row["input"].casefold() for row in cases}) == 48

for row in cases:
    kind = row["pending_kind"] if row["pending_kind"] != "any" else "information"
    opts = {"allow_multiple": True, "options_count": 2}
    result = engine.interpret(row["input"], language=row["language"],
                              pending_kind=kind, **opts)
    if row["topic"] == "ambiguous":
        assert result["status"] == "needs_clarification", (row["id"], result)
    else:
        assert result["status"] == "recognized", (row["id"], result)
        assert result["intent"] == row["topic"]
        assert result["id"] == row["id"]
        assert result["action_authorized"] is False
    assert engine.interpret(row["input"], language=row["language"],
        pending_kind=kind, side_effects=True, **opts)["status"] in {
            "side_effect_blocked", "needs_clarification"}
    assert engine.interpret(row["input"], language=row["language"],
        pending_kind=kind, addressed=False)["status"] == "not_addressed"
    assert engine.interpret(row["input"], language=row["language"],
        pending_kind=kind, quoted=True)["status"] == "quoted_ignored"
    assert engine.interpret("«" + row["input"] + "»", language=row["language"],
        pending_kind=kind)["status"] == "quoted_ignored"
    assert engine.interpret(row["input"], language=row["language"],
        pending_kind=kind, pending_turns=3)["status"] == "expired_context"
    assert engine.interpret(row["input"], language=row["language"],
        pending_kind=None)["status"] == "no_pending_context"
    if row["pending_kind"] != "any":
        wrong = "choice" if kind == "confirmation" else "confirmation"
        assert engine.interpret(row["input"], language=row["language"],
            pending_kind=wrong)["status"] == "context_mismatch"
    hits = index.search(row["input"], "all_ai_bots", 20)
    assert hits and hits[0][0] == row["id"], (row["id"], hits[:3])
    assert hits[0][1] == PACK

assert engine.interpret("оба", pending_kind="choice")["status"] == "multiple_not_allowed"
assert engine.interpret("both", pending_kind="choice", language="en",
                        allow_multiple=True, options_count=1)["status"] == "insufficient_options"
assert engine.interpret("да, удали всё", pending_kind="confirmation")["status"] == "unknown_reply"
assert engine.interpret("yes, ban them", pending_kind="confirmation", language="en")["status"] == "unknown_reply"
assert engine.interpret("да?", pending_kind="confirmation")["status"] == "needs_clarification"
assert engine.interpret("no", pending_kind="confirmation")["status"] == "wrong_language"
assert engine.interpret("ДА!", pending_kind="confirmation")["status"] == "recognized"
assert engine.interpret("I don't know", language="en", pending_kind="information")["status"] == "recognized"
for invalid in (
    {"message": 0}, {"pending_kind": "mod_action"}, {"language": "fr"},
    {"pending_turns": True}, {"pending_turns": -1}, {"options_count": True},
    {"addressed": "yes"}, {"quoted": 1}, {"side_effects": None},
    {"allow_multiple": 1},
):
    params = {"message": "да", "pending_kind": "confirmation"}
    params.update(invalid)
    try:
        engine.interpret(**params)
    except ValueError:
        pass
    else:
        raise AssertionError("Accepted invalid parameter " + str(invalid))

with tempfile.TemporaryDirectory() as temp:
    root = Path(temp)
    (root / PACK).parent.mkdir(parents=True)
    (root / "manifest.json").write_bytes((ROOT / "manifest.json").read_bytes())
    (root / PACK).write_bytes((ROOT / PACK).read_bytes() + b" ")
    try:
        ShortTurns(root)
    except ValueError as exc:
        assert "SHA-256" in str(exc)
    else:
        raise AssertionError("Tampered short-turn pack was accepted")

start = time.perf_counter()
for round_number in range(1, 11):
    for row in cases:
        kind = row["pending_kind"] if row["pending_kind"] != "any" else "information"
        result = engine.interpret(row["input"], language=row["language"],
                                  pending_kind=kind, allow_multiple=True)
        assert result["status"] == ("needs_clarification" if row["topic"] == "ambiguous" else "recognized")
    print(f"SHORT_TURNS_PASS {round_number}/10 cases=48")
for _ in range(1000):
    assert engine.interpret("ага", pending_kind="confirmation")["intent"] == "affirm"
assert index.search("да", "all_ai_bots")[0][0] == "short_ru_affirm_1"
assert index.search("no", "all_ai_bots")[0][0] == "short_en_deny_1"
print(f"SHORT_TURNS_1000_CALLS_OK elapsed_with_10_rounds_ms={(time.perf_counter()-start)*1000:.2f}")
print("SHORT_TURNS_10_ROUNDS_OK")
