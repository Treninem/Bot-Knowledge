"""Check precise retrieval of six reviewed RU paraphrases and their scope."""
import json
from pathlib import Path

from search_knowledge import KnowledgeSearch, exact_phrase

ROOT = Path(__file__).resolve().parents[1]
index = KnowledgeSearch(ROOT)
cases = [
    ("После обжалования сразу восстановят?", "dlg_t10_appeal_not_outcome"),
    ("Подал апелляцию — меня автоматически вернут?", "dlg_t10_appeal_not_outcome"),
    ("Если поменял стиль, изменятся ли полномочия?", "dlg_t56_024"),
    ("Новый тон ответа даёт ИИ право банить?", "dlg_t56_024"),
    ("Бот отсутствовал ночью, можно ли утверждать, что нарушений не было?", "dlg_t10_negative_no_event"),
    ("Раз бот был отключён, значит в чате всё было спокойно?", "dlg_t10_negative_no_event"),
]
seen = set()
for path in ("packs/ru/dialogue_help_qa.json", "packs/ru/moderation_explanations_qa.json"):
    data = json.loads((ROOT / path).read_text(encoding="utf-8"))
    for row in data["records"]:
        for phrase in [row["question"], *row.get("aliases", [])]:
            key = exact_phrase(phrase)
            assert key not in seen, f"duplicate normalized QA phrase: {phrase}"
            seen.add(key)
for question, expected in cases:
    hits = index.search(question, audience="all_ai_bots")
    assert hits and hits[0][0] == expected, (question, hits[:2])
assert len({exact_phrase(question) for question, _ in cases}) == 6
print("Six unique paraphrases resolve to three reviewed answers for all AI bots")
