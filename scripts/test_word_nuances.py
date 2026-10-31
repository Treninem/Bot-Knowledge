"""Ten full RU/EN sense-aware selection rounds plus negative/safety checks."""
from __future__ import annotations

import json
import sys
import tempfile
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from word_nuances import load_word_nuances, choose_word, PACK
from validate_word_nuances import validate_word_nuances_pack, version_not_newer
from search_knowledge import KnowledgeSearch


def main() -> None:
    assert version_not_newer('2026.10.30.12', '2026.10.30.13')
    assert not version_not_newer('2026.10.30.14', '2026.10.30.13')
    assert not version_not_newer('unversioned', '2026.10.30.13')
    issues = validate_word_nuances_pack(ROOT)
    assert issues == [], issues
    book = load_word_nuances()
    cases = book["cases"]
    assert len(cases) == 72
    assert len({x["family"] for x in cases}) == 12
    assert sum(c["language"] == "ru" for c in cases) == 36
    assert sum(c["language"] == "en" for c in cases) == 36
    index = KnowledgeSearch()
    assert len(index.records) >= 1179, len(index.records)
    for case in cases:
        search = index.search(case["source"], "all_ai_bots", 20)
        assert search and search[0][0] == case["id"], (case["id"], search)
        assert search[0][1] == PACK
        assert "action" not in case and "sanction" not in case
        for tone, text in case["variants"].items():
            result = choose_word(book, family=case["family"], sense=case["sense"],
                                 language=case["language"], tone=tone,
                                 dark_opt_in=True, strong_opt_in=True)
            assert result["status"] == "ok", (case["id"], result)
            assert result["id"] == case["id"] and result["text"] == text
            assert result["meaning"] == case["meaning"]
            assert choose_word(book, family=case["family"], sense=case["sense"],
                               language=case["language"], tone=tone,
                               recent_phrases=(text,), dark_opt_in=True,
                               strong_opt_in=True)["status"] == "no_unused_variant"

    assert choose_word(book, family="review_depth", sense=None)["status"] == "needs_semantic_context"
    assert choose_word(book, family="review_depth", sense="guess")["status"] == "needs_semantic_context"
    assert choose_word(book, family="absent", sense="skim")["status"] == "no_family"
    assert choose_word(book, family="review_depth", sense="skim", language="en")["text"] == "skim the report"
    assert choose_word(book, family="review_depth", sense="skim", language="ru")["text"] == "бегло просмотреть отчёт"
    assert choose_word(book, family="review_depth", sense="audit")["text"] != choose_word(
        book, family="review_depth", sense="skim")["text"]
    assert choose_word(book, family="progress", sense="planned")["text"] != choose_word(
        book, family="progress", sense="complete")["text"]
    assert choose_word(book, family="humor", sense="dark")["status"] == "requires_dark_opt_in"
    assert choose_word(book, family="emotion", sense="anger")["status"] == "requires_strong_opt_in"
    assert choose_word(book, family="humor", sense="dark", dark_opt_in=True,
                       sensitive=True)["status"] == "suppressed_sensitive"
    assert choose_word(book, family="humor", sense="playful",
                       sensitive=True)["status"] == "suppressed_sensitive"
    assert choose_word(book, family="emotion", sense="anger", strong_opt_in=True,
                       sensitive=True)["status"] == "suppressed_sensitive"
    for invalid in ("xx", "", "EN"):
        try:
            choose_word(book, family="progress", sense="planned", language=invalid)
            raise AssertionError("Unsupported language accepted")
        except ValueError:
            pass
    # SHA mismatch always blocks selection, even when JSON syntax is unchanged.
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        (root / "packs/ru").mkdir(parents=True)
        (root / "manifest.json").write_bytes((ROOT / "manifest.json").read_bytes())
        (root / PACK).write_bytes((ROOT / PACK).read_bytes() + b" ")
        try:
            load_word_nuances(root)
            raise AssertionError("Modified pack accepted")
        except ValueError as exc:
            assert "SHA-256" in str(exc)

    started = time.perf_counter()
    for number in range(1, 11):
        for case in cases:
            for tone in ("neutral", "formal", "casual"):
                result = choose_word(book, family=case["family"], sense=case["sense"],
                                     language=case["language"], tone=tone,
                                     dark_opt_in=True, strong_opt_in=True)
                assert result["text"] == case["variants"][tone]
        print(f"WORD_NUANCES_PASS {number}/10 bilingual_cases=72 choices=216")
    for i in range(1000):
        case = cases[i % len(cases)]
        result = choose_word(book, family=case["family"], sense=case["sense"],
                             language=case["language"], tone="neutral",
                             dark_opt_in=True, strong_opt_in=True)
        assert result["status"] == "ok"
    print(f"WORD_NUANCES_1000_LOCAL_CALLS_OK elapsed_with_10_rounds_ms={(time.perf_counter()-started)*1000:.2f}")
    print("WORD_NUANCES_10_ROUNDS_OK")


if __name__ == "__main__":
    main()
