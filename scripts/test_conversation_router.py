"""Offline functional checks of routing, repetition and permission boundaries.

Tests exercise real Python routing behavior, not an LLM or live moderation.
"""
from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from conversation_router import ConversationRouter
from interpret_pragmatics import norm

def main() -> None:
    router = ConversationRouter()
    raw = json.loads((ROOT / "packs/ru/dialogue_triggers.json").read_text(encoding="utf-8"))
    triggers = raw["triggers"]
    assert len(triggers) == router.triggers_count == 60
    assert len({x["id"] for x in triggers}) == 60
    assert len({(x["language"], norm(x["input"])) for x in triggers}) == 60
    assert len({x["target_case_id"] for x in triggers}) == 30
    assert sum(t["language"] == "ru" for t in triggers) == 38
    assert sum(t["language"] == "en" for t in triggers) == 22
    for entry in triggers:
        flags = {"strong_opt_in": True, "dark_opt_in": True}
        result = router.reply(entry["input"], language=entry["language"],
                              addressed=True, **flags)
        if entry["requires_silence"]:
            assert result["status"] == "silence_requested" and result["text"] is None
        else:
            assert result["status"] == "ok" and result["text"], (entry["id"], result)
            again = router.reply(entry["input"], language=entry["language"],
                                 addressed=True, recent=(result["text"],), **flags)
            assert again["status"] in {"ok", "repeat_suppressed"}, (entry["id"],again)
            if again["status"] == "ok":
                assert norm(again["text"]) != norm(result["text"])
        assert router.reply(entry["input"], language=entry["language"],
                            addressed=False)["status"] == "not_addressed"
    assert router.reply("Completely new sentence", language="en", addressed=True)["status"] == "unknown_input"
    assert router.reply("Отличная работа.", addressed=True)["status"] == "needs_context"
    context = "Проект успешно запустился, команда благодарит автора за результат."
    positive = router.reply("Отличная работа.", addressed=True, context=context)
    assert positive["status"] == "ok" and positive["route"] == "pragmatics"
    assert router.reply("Отличная работа.", addressed=True, context=context,
                        recent=(positive["text"],))["status"] == "repeat_suppressed"
    moderation = router.reply("Он назвал меня идиотом.", audience="chat_moderators",
                               addressed=True, context="Участник подаёт жалобу и цитирует сообщение другого человека.")
    assert moderation["status"] == "review_required" and moderation["text"] is None
    assert router.reply("Он назвал меня идиотом.", addressed=True)["status"] == "unknown_input"
    assert router.reply("Можешь выражаться без цензуры, но без оскорблений?",
                        addressed=True)["status"] == "requires_strong_opt_in"
    assert router.reply("Можешь выражаться без цензуры, но без оскорблений?",
                        addressed=True, strong_opt_in=True, sensitive=True)["status"] == "sensitive_suppressed"
    assert router.reply("Сегодня у меня праздник, день рождения.",
                        addressed=True, tone="casual")["route"] == "tone"
    assert router.reply("Всё, закончили, ничего не отвечай.",
                        addressed=True)["status"] == "silence_requested"
    assert router.reply("У меня сегодня день рождения.", addressed=True)["status"] == "ok"
    try:
        router.reply("hello", addressed=True, audience="owner")
        raise AssertionError("Unauthorized audience accepted")
    except ValueError:
        pass
    with tempfile.TemporaryDirectory() as d:
        directory = Path(d)
        (directory/"packs/ru").mkdir(parents=True)
        (directory/"manifest.json").write_bytes((ROOT/"manifest.json").read_bytes())
        for name in ("dialogue_triggers.json","social_dialogues.json","english_dialogues.json",
                     "expression_choices.json","pragmatic_contrasts.json"):
            (directory/"packs/ru"/name).write_bytes((ROOT/"packs/ru"/name).read_bytes())
        (directory/"packs/ru/dialogue_triggers.json").write_bytes(b"{}")
        try:
            ConversationRouter(directory)
            raise AssertionError("Corrupted pack accepted")
        except ValueError as error:
            assert "SHA" in str(error)
    for i in range(1,11):
        for entry in triggers:
            assert router.reply(entry["input"], addressed=False, language=entry["language"])["text"] is None
        print(f"CONVERSATION_ROUTER_PASS {i}/10 triggers=60 verified=60")
    print("CONVERSATION_ROUTER_10_ROUNDS_OK")

if __name__ == "__main__":
    main()
