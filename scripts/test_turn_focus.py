"""Exercise 56 RU/EN synthetic multi-turn focus cases and adversarial bounds."""
from __future__ import annotations

import json
import sys
import tempfile
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from turn_focus import TurnFocus
from validate_turn_focus import validate_turn_focus_pack, PACK
from search_knowledge import KnowledgeSearch


def execute(case: dict) -> dict:
    context = TurnFocus()
    context.present(case["candidates"], language=case["language"])
    if "initial_focus_id" in case:
        context.pin(case["initial_focus_id"])
    if "focus_id" in case:
        context.pin(case["focus_id"])
    if "advance" in case:
        context.advance(case["advance"])
    if case.get("reset"):
        context.clear()
    return context.choose(case["input"], language=case.get("query_language", case["language"]),
                          addressed=True,
                          require_confirmation=case.get("require_confirmation", False))


def main() -> None:
    issues = validate_turn_focus_pack(ROOT)
    assert not issues, issues
    cases = json.loads((ROOT / PACK).read_text(encoding="utf-8"))["scenarios"]
    assert len(cases) == 56
    assert sum(c["language"] == "ru" for c in cases) == 28
    assert sum(c["language"] == "en" for c in cases) == 28
    index = KnowledgeSearch()
    assert len(index.records) == 1179, len(index.records)
    for case in cases:
        actual = execute(case)
        expected = {"status": case["expected_status"], "ids": case["expected_ids"]}
        assert actual == expected, (case["id"], actual, expected)
        matches = index.search(case["input"], "all_ai_bots", 20)
        assert matches and matches[0][0] == case["id"], (case["id"], matches)
        assert matches[0][1] == PACK
    candidates = [{"id": "a", "label": "чертёж опоры", "gender": "m"},
                  {"id": "b", "label": "эскиз входа", "gender": "m"}]
    first = TurnFocus(ttl_turns=2)
    second = TurnFocus(ttl_turns=2)
    first.present(candidates, language="ru")
    second.present(candidates, language="ru")
    first.pin("b")
    assert first.choose("Открой его.", language="ru", addressed=True)["ids"] == ["b"]
    assert second.choose("Открой его.", language="ru", addressed=True)["status"] == "needs_clarification"
    assert not {"labels", "items", "focus_id", "messages"} & first.state.keys()
    assert first.choose("Открой его.", language="ru", addressed=False)["status"] == "not_addressed"
    assert first.choose("Open it.", language="en", addressed=True)["status"] == "no_context"
    assert first.choose("Не открывай его.", language="ru", addressed=True)["status"] == "negated_instruction"
    assert first.choose("Удали его.", language="ru", addressed=True)["status"] == "confirm_required"
    assert first.choose("В тексте: открой его.", language="ru", addressed=True)["status"] == "not_direct_request"
    assert first.choose("Открой первый и второй.", language="ru", addressed=True)["status"] == "needs_clarification"
    first.advance(2)
    assert first.choose("Покажи его.", language="ru", addressed=True)["ids"] == ["b"]
    first.advance()
    assert first.choose("Покажи его.", language="ru", addressed=True)["status"] == "no_context"
    first.present(candidates, language="ru")
    first.pin("a")
    first.present(candidates, language="ru")
    assert first.state["focus_confirmed"] is False
    assert first.choose("Покажи его.", language="ru", addressed=True)["status"] == "needs_clarification"
    try:
        first.pin("missing")
        raise AssertionError("Unknown object pinned")
    except ValueError:
        pass
    try:
        TurnFocus(ttl_turns=0)
        raise AssertionError("Invalid TTL accepted")
    except ValueError:
        pass
    try:
        TurnFocus(max_candidates=1).present(candidates, language="ru")
        raise AssertionError("Too many candidates accepted")
    except ValueError:
        pass
    try:
        first.advance(True)
        raise AssertionError("Boolean age accepted")
    except ValueError:
        pass
    with tempfile.TemporaryDirectory() as folder:
        root = Path(folder)
        (root / "packs/ru").mkdir(parents=True)
        (root / "manifest.json").write_bytes((ROOT / "manifest.json").read_bytes())
        (root / PACK).write_bytes((ROOT / PACK).read_bytes() + b" ")
        assert any("SHA-256" in item for item in validate_turn_focus_pack(root))
    started = time.perf_counter()
    for round_number in range(1, 11):
        for case in cases:
            actual = execute(case)
            assert actual == {"status": case["expected_status"],
                              "ids": case["expected_ids"]}, (round_number, case["id"], actual)
        print(f"TURN_FOCUS_PASS {round_number}/10 cases=56")
    first.present(candidates, language="ru")
    first.pin("b")
    for _ in range(1000):
        assert first.choose("Открой его.", language="ru", addressed=True)["ids"] == ["b"]
    print(f"TURN_FOCUS_1000_LOCAL_CALLS_OK elapsed_with_10_rounds_ms={(time.perf_counter()-started)*1000:.2f}")
    print("TURN_FOCUS_10_ROUNDS_OK")


if __name__ == "__main__":
    main()
