"""T95: synthetic, offline qa.v1 context and audience isolation.

Requires only Python stdlib. Uses no external calls, real chats, or installed
bot state; this is a reference-search test, NOT a live consumer check.
"""
from __future__ import annotations

import hashlib
import json
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from search_knowledge import KnowledgeSearch

REL = "packs/ru/synthetic_qa.json"
GROUP_QUERY = "Где обсуждают маршрут совместной прогулки?"
PRIVATE_QUERY = "Как составить личный список покупок?"
COMMON_QUERY = "Как уточнить неясную дату встречи?"
IMPULS_QUERY = "Где посмотреть групповой игровой список?"


def row(key: str, question: str, audiences: list[str],
        contexts: list[str] | None, aliases: list[str] | None = None) -> dict:
    entry = {
        "id": key, "question": question, "aliases": aliases or [],
        "answer": "Уточни контекст и отвечай только в рамках нужного разговора.",
        "variants": [], "audiences": audiences, "language": "ru",
    }
    if contexts is not None:
        entry["contexts"] = contexts
    return entry


def fixture(root: Path) -> None:
    document = {
        "schema_version": 1, "language": "ru",
        "catalog": {
            "adapter": "qa.v1", "id": "synthetic_qa",
            "audiences": ["all_ai_bots"],
            "contexts": ["direct", "private", "group_addressed"],
        },
        "records": [
            row("qa_group", GROUP_QUERY, ["all_ai_bots"], ["group_addressed"],
                ["Общий маршрут прогулки где обсудить?"]),
            row("qa_private", PRIVATE_QUERY, ["all_ai_bots"], ["private"]),
            row("qa_common", COMMON_QUERY, ["all_ai_bots"], None),
            row("qa_impuls", IMPULS_QUERY, ["impuls"], ["group_addressed"]),
        ],
    }
    blob = (json.dumps(document, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    target = root / REL
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(blob)
    (root / "manifest.json").write_text(
        json.dumps({"schema_version": 1, "language": "ru",
                    "packs": [{"path": REL, "sha256": hashlib.sha256(blob).hexdigest()}]},
                   ensure_ascii=False, indent=2) + "\n", encoding="utf-8",
    )


def ids(index: KnowledgeSearch, query: str, audience: str = "all_ai_bots",
        context: str | None = None) -> set[str]:
    return {result[0] for result in index.search(query, audience, limit=20, context=context)}


def main() -> None:
    with tempfile.TemporaryDirectory() as folder:
        root = Path(folder)
        fixture(root)
        index = KnowledgeSearch(root)
        assert len(index.records) == 4
        checks = 0
        for context in ("direct", "private"):
            assert "qa_group" not in ids(index, GROUP_QUERY, context=context)
            assert "qa_impuls" not in ids(index, IMPULS_QUERY, "impuls", context)
            checks += 2
        assert "qa_group" in ids(index, GROUP_QUERY, context="group_addressed")
        checks += 1
        assert "qa_group" in ids(index, "Общий маршрут прогулки где обсудить?",
                                  context="group_addressed")
        checks += 1
        assert "qa_private" in ids(index, PRIVATE_QUERY, context="private")
        assert "qa_private" not in ids(index, PRIVATE_QUERY, context="direct")
        checks += 2
        for context in ("direct", "private", "group_addressed"):
            assert "qa_common" in ids(index, COMMON_QUERY, context=context)
            checks += 1
        assert "qa_impuls" in ids(index, IMPULS_QUERY, "impuls", "group_addressed")
        assert "qa_impuls" not in ids(index, IMPULS_QUERY, "all_ai_bots", "group_addressed")
        checks += 2
        # Existing calls lacking context retain the previous unscoped behaviour.
        assert "qa_group" in ids(index, GROUP_QUERY)
        assert index.search(GROUP_QUERY)[0][0] == "qa_group"
        checks += 2
        # Cached results must remain separate for different contexts.
        assert "qa_group" in ids(index, GROUP_QUERY, context="group_addressed")
        assert "qa_group" not in ids(index, GROUP_QUERY, context="private")
        assert index._cached_search.cache_info().hits > 0
        checks += 3
        for bad in ("", "group", "other", "DIRECT"):
            try:
                index.search(GROUP_QUERY, context=bad)
            except ValueError as exc:
                assert str(exc) == "Unknown context"
            else:
                raise AssertionError("Invalid context accepted")
            checks += 1
        assert "qa_group" in ids(index, GROUP_QUERY, context=None)
        checks += 1

    print(f"T95_QA_CONTEXT_SCOPE_OK {checks}/{checks} synthetic checks")


if __name__ == "__main__":
    main()
