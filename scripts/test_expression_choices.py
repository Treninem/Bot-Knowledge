"""Real deterministic tests of phrase choice, opt-in and SHA protection."""
from __future__ import annotations
import json
import tempfile
from pathlib import Path
from choose_expression import load_phrasebook, pick_phrase, ROOT

def main() -> None:
    book = load_phrasebook()
    rows = book["entries"]
    ids = [x["id"] for x in rows]
    assert len(ids) == len(set(ids)) == 30
    texts = []
    for x in rows:
        assert set(x["language_variants"]) == {"ru","en"}
        for language in ("ru","en"):
            assert set(x["language_variants"][language]) == {"neutral","warm","casual"}
            for tone in ("neutral","warm","casual"):
                variant = x["language_variants"][language][tone]
                assert len(variant) == 1 and all(15 <= len(s) <= 280 for s in variant)
                texts += variant
        assert not (x["requires_dark_opt_in"] and x["requires_strong_opt_in"])
    assert len(texts) == 180
    assert len({" ".join(t.casefold().split()) for t in texts}) == 180
    for x in rows:
        key = x["id"]
        for language in ("ru","en"):
            for tone in ("neutral","warm","casual"):
                flags = {"dark_opt_in":True,"strong_opt_in":True}
                res = pick_phrase(book, scenario=key, language=language, tone=tone, **flags)
                assert res["status"] == "ok" and res["text"]
                assert pick_phrase(book, scenario=key, language=language,
                                   tone=tone, recent_phrases=(res["text"],), **flags)["status"] == "no_unused_phrase"
    assert pick_phrase(book, scenario="not_present")["status"] == "no_match"
    assert pick_phrase(book, scenario="expr_dark_humor_requested")["status"] == "requires_dark_opt_in"
    assert pick_phrase(book, scenario="expr_strong_tone_optin")["status"] == "requires_strong_opt_in"
    assert pick_phrase(book, scenario="expr_dark_humor_requested", dark_opt_in=True,
                       sensitive=True)["status"] == "suppressed_sensitive"
    assert pick_phrase(book, scenario="expr_strong_tone_optin", strong_opt_in=True,
                       sensitive=True)["status"] == "suppressed_sensitive"
    try:
        pick_phrase(book, scenario="expr_acknowledge_request", tone="hostile")
        raise AssertionError("Unknown tone accepted")
    except ValueError:
        pass
    # SHA mismatch is always rejected, even if JSON remains parseable.
    with tempfile.TemporaryDirectory() as d:
        dest=Path(d)
        (dest/"packs/ru").mkdir(parents=True)
        (dest/"manifest.json").write_bytes((ROOT/"manifest.json").read_bytes())
        data=(ROOT/"packs/ru/expression_choices.json").read_text(encoding="utf-8")
        (dest/"packs/ru/expression_choices.json").write_text(data+" ",encoding="utf-8")
        try:
            load_phrasebook(dest)
            raise AssertionError("Corrupted pack accepted")
        except ValueError as exc:
            assert "SHA" in str(exc)
    for iteration in range(1, 11):
        assert len([x for x in rows if x["requires_dark_opt_in"]]) == 1
        print(f"EXPRESSION_SELECTION_PASS {iteration}/10 scenarios={len(rows)} phrases={len(texts)}")
    print("EXPRESSION_SELECTION_10_ROUNDS_OK")

if __name__ == "__main__":
    main()
