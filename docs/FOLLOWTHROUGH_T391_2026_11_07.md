# Followthrough T391 — девять этапов ответов для 82 намерений (07.11.2026)

Новая партия **82 оригинальных синтетических русских ответа** для 82 существующих канонических intent-ID `follow_t86_*`, `follow_t88_*`, `follow_t90_*`. Новых вопросов 0, новых завершённых 100/100 — 0. После T390 ранее: 246 registered + 738 staged = 984/8200. T391 добавляет только +82, теперь **246 registered + 820 staged = 1066/8200**, по **13/100** на намерение, остаток **7134**.

- Stage `staging/ru/followthrough_t391_context_pool.json` Git blob `66157082f9e60937f513f3e6bf9c5b6c1e0f99c5`. Предыдущий T390 Git blob `41bc57dbcc429f2bfeaa68ef28ca77450748f963`. Source `packs/ru/conversation_followthrough_qa.json`, manifest SHA-256 `0862daf244df650bfd85217df3bedb9f2373a6e63dbabfa8d0c831a6fb289ff7`, source Git blob `707fcaa6440d398a730840362602d4532ab92036`. Родительские Git blob T383–T390 зафиксированы на чтение.
- Данные синтетические, контекстно ограниченные, с read-only opt-in, явными `approved_reply_ids`, адресацией и локальными разрешениями. Без права санкций, персональных чатов или записи в GitHub. Соответствие `all_ai_bots`.
- JS preflight: 82 уникальных reply-ID, нормализованных текстов и `context_note`. Ноль точных повторов относительно зарегистрированных исходных ответов и всех восьми прежних стадий. Максимальный token-Jaccard 0.348 (<0.78). Данный лексический фильтр не равен полной ручной смысловой экспертизе.
- Обновлены `StagedContextSelector`, `FollowthroughStageCatalog`, Python-обратные тесты с ожидаемыми 820 staged, read-only `quality.yml` с `scripts.test_followthrough_t391`, `scripts.test_followthrough_stage_catalog`, `validate_pack.py`. Версия `manifest.json`, зарегистрированные SHA, рабочий cache, ImPULS и прочие живые боты не менялись.

**Gate:** Draft до успешного exact-head CI с реальным checkout SHA, затем ready и защищённый merge, после — post-main CI по фактическому SHA. Никаких вручную оплачиваемых Actions.

Следующий содержательный набор: новые разные контексты для этих 82 намерений с 13/100; не перефразировать механически.
