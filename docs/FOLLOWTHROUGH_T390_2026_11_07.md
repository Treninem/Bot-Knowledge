# Followthrough T390 — новые речевые ситуации (07.11.2026)

Новая независимая партия **82 оригинальных синтетических русских контекстных ответов**, по одному для 82 уже зарегистрированных intent-ID `follow_t86_*`, `follow_t88_*` и `follow_t90_*`. Новых канонических вопросов: 0. Новых полных наборов 100/100: 0. После T389 исходный объём 246 registered + 656 staged = 902/8200. Эта партия добавляет +82, новый итог **984/8200**, каждый intent **12/100**, остаток **7216**.

- `staging/ru/followthrough_t390_context_pool.json` — Git blob `41bc57dbcc429f2bfeaa68ef28ca77450748f963`, источник `packs/ru/conversation_followthrough_qa.json`, manifest SHA-256 `0862daf244df650bfd85217df3bedb9f2373a6e63dbabfa8d0c831a6fb289ff7`, source Git blob `707fcaa6440d398a730840362602d4532ab92036`.
- Родитель T389 immutable blob `dddfc5a9612fdd889c3acf92ad6e8c1bba3d1d50`; родительская цепочка T383–T389 проверяется по точным Git blob hashes. Никаких changes to actual registered QA, manifest, knowledge_version, consumer cache.
- 82 разных ситуационных `context_note`; уникальные нормализованные тексты и reply-ID по проверенному readback. Прямых повторов с 246 source и историческими 656 staged ответами — 0; максимум token-Jaccard 0.267, порог 0.78. Лексическое сито не является исчерпывающим смысловым аудитом.
- Условия: режимы direct/private/group_addressed, только all_ai_bots, read-only, явное `approved_reply_ids`, проверка истинной адресации, контекста и разрешений, анти-повтор. Истории личных чатов, токены и санкции запрещены.
- `StagedContextSelector` pin-validate stage и предков; `FollowthroughStageCatalog` содержит восемь staged уровней (738 кандидатов) с source-derived cache identity. Регрессии `scripts.test_followthrough_t390`, `scripts.test_followthrough_stage_catalog`, `scripts.test_staged_context_selector` и `scripts/validate_pack.py` выполняются в read-only exact-head CI.
- Процесс: нельзя объявлять успешные тесты, ready, merge или доставку боту до фактических CI и post-main на актуальных SHA. Платные Actions вручную не запускать; ImPULS и live BotHost не менять.

Следующий шаг: продолжить те же intent-ID с 12/100, но отбирать только новые полезные контексты без механических перефразировок.
