"""Real functional tests for exact bilingual meaning-preserving paraphrases."""
from __future__ import annotations

import json
import sys
import tempfile
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from paraphrase_meaning import MeaningParaphraser, normalized
from validate_paraphrases import validate_paraphrase_pack
from search_knowledge import KnowledgeSearch

PACK = "packs/ru/meaning_paraphrases.json"


def main() -> None:
    assert validate_paraphrase_pack(ROOT) == [], validate_paraphrase_pack(ROOT)
    book = MeaningParaphraser()
    entries = json.loads((ROOT / PACK).read_text(encoding="utf-8"))["paraphrases"]
    assert len(entries) == book.count == 48
    assert len({e["id"] for e in entries}) == 48
    assert len({(e["language"], normalized(e["source"])) for e in entries}) == 48
    search = KnowledgeSearch()
    assert len(search.records) == 609, len(search.records)
    for e in entries:
        source, language = e["source"], e["language"]
        for tone in ("neutral", "casual"):
            result = book.rewrite(source, language=language, tone=tone, addressed=True)
            assert result["status"] == "ok", (e["id"], result)
            assert result["text"] == e["variants"][tone]
            assert result["semantic_guard"] == e["semantic_guard"]
            assert result["text"] != e["counterexample"]["text"]
            assert book.rewrite(source, language=language, tone=tone, addressed=True,
                                recent=(result["text"],))["status"] == "repeat_suppressed"
        assert book.rewrite(source, language=language, tone="casual", addressed=True,
                            sensitive=True)["status"] == "sensitive_tone_blocked"
        assert book.rewrite(source, language=language, addressed=False)["status"] == "not_addressed"
        other = "ru" if language == "en" else "en"
        assert book.rewrite(source, language=other, addressed=True)["status"] == "unknown_source"
        assert book.rewrite(e["counterexample"]["text"], language=language,
                            addressed=True)["status"] == "unknown_source"
        assert book.rewrite(source + "!", language=language, addressed=True)["status"] == "unknown_source"
        matches = search.search(source, "all_ai_bots", 20)
        assert matches and matches[0][0] == e["id"], (e["id"], matches)
        assert matches[0][1] == PACK
    for sentence, language in [
        ("Publish the draft without review.", "en"),
        ("Отправляй отчёт без проверки.", "ru"),
        ("I definitely promise.", "en"),
        ("The total was 64, not 46.", "en"),
        ("В отчёте можно указывать имена.", "ru"),
    ]:
        assert book.rewrite(sentence, language=language, addressed=True)["status"] == "unknown_source"
    try:
        book.rewrite(entries[0]["source"], addressed=True, recent=("test",) * 9)
        raise AssertionError("Unbounded reply history accepted")
    except ValueError:
        pass
    with tempfile.TemporaryDirectory() as temp:
        root = Path(temp)
        (root / "packs/ru").mkdir(parents=True)
        (root / "manifest.json").write_bytes((ROOT / "manifest.json").read_bytes())
        (root / PACK).write_bytes((ROOT / PACK).read_bytes() + b" ")
        try:
            MeaningParaphraser(root)
            raise AssertionError("Tampered pack accepted")
        except ValueError as error:
            assert "SHA" in str(error)
    started = time.perf_counter()
    for n in range(1, 11):
        for e in entries:
            for tone in ("neutral", "casual"):
                assert book.rewrite(e["source"], language=e["language"],
                                    tone=tone, addressed=True)["status"] == "ok"
        print(f"PARAPHRASE_PASS {n}/10 cases=48 approved_variants=96")
    for n in range(1000):
        e = entries[n % 48]
        assert book.rewrite(e["source"], language=e["language"],
                            addressed=True)["status"] == "ok"
    elapsed = (time.perf_counter() - started) * 1000
    print(f"PARAPHRASE_1000_LOCAL_CALLS_OK elapsed_with_10_rounds_ms={elapsed:.2f}")
    print("PARAPHRASE_10_ROUNDS_OK")


if __name__ == "__main__":
    main()
