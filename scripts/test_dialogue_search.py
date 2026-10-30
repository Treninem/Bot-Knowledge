"""Ensure all 60 approved paraphrases are retrievable without leaking other scopes."""
from __future__ import annotations
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from search_knowledge import KnowledgeSearch, exact_phrase

def main() -> None:
    index = KnowledgeSearch()
    triggers = json.loads((ROOT/"packs/ru/dialogue_triggers.json").read_text(encoding="utf-8"))["triggers"]
    assert len(index.records) == 677
    assert len(triggers) == 60
    for trigger in triggers:
        matches = index.search(trigger["input"], "all_ai_bots", limit=20)
        assert matches and matches[0][0] == trigger["id"], (trigger["id"], matches)
        assert matches[0][2] == trigger["target_case_id"]
        assert matches[0][1] == "packs/ru/dialogue_triggers.json"
    assert exact_phrase(" ДА,  БЛИН! ") == exact_phrase("да блин")
    # Moderator examples must never appear for generic assistant consumers.
    for query in ("Он назвал меня идиотом.", "You're a genius."):
        rows = index.search(query, "all_ai_bots", limit=20)
        assert all(p != "packs/ru/moderation_cases.json" for _, p, _, _ in rows)
        assert all(p != "packs/ru/pragmatic_contrasts.json" or x not in {
            "prag_moderation_context_ru_01","prag_moderation_context_en_01"
        } for x,p,_,_ in rows)
    for n in range(1, 11):
        for entry in triggers:
            result = index.search(entry["input"], "all_ai_bots", limit=5)
            assert result[0][0] == entry["id"]
        print(f"DIALOGUE_SEARCH_PASS {n}/10 records={len(index.records)}")
    print("DIALOGUE_SEARCH_10_ROUNDS_OK")

if __name__ == "__main__":
    main()
