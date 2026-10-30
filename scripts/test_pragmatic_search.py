"""Exercise exact-phrase search and moderation audience isolation."""
from __future__ import annotations
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from search_knowledge import KnowledgeSearch, exact_phrase

def main() -> None:
    index = KnowledgeSearch()
    pairs = json.loads((ROOT / "packs/ru/pragmatic_contrasts.json").read_text(encoding="utf-8"))["pairs"]
    assert len(index.records) == 609
    assert len(pairs) == 48
    assert exact_phrase(" Ну, ты гений! ") == exact_phrase("ну ты гений")
    for pair in pairs:
        audience = "chat_moderators" if pair["category"] == "moderation_context" else "all_ai_bots"
        results = index.search(pair["expression"], audience, 20)
        assert results and results[0][0] == pair["id"], (pair["id"], results)
        if pair["category"] == "moderation_context":
            neutral = index.search(pair["expression"], "all_ai_bots", 20)
            assert pair["id"] not in {row[0] for row in neutral}
    assert index.search("unindexedNovelTerm987654321", "all_ai_bots") == ()
    for i in range(1, 11):
        for pair in pairs:
            audience = "chat_moderators" if pair["category"] == "moderation_context" else "all_ai_bots"
            assert index.search(pair["expression"], audience, 5)[0][0] == pair["id"]
        print(f"PRAGMATIC_SEARCH_PASS {i}/10 records={len(index.records)}")
    print("PRAGMATIC_SEARCH_10_ROUNDS_OK")

if __name__ == "__main__":
    main()
