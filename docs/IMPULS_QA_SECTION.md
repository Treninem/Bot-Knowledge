# ImPULS qa.v1 bot-help section

Trusted producer target: `packs/ru/impuls_help_qa.json` (manifest-registered; `catalog.adapter=qa.v1`; `catalog.id=impuls_help_qa`; `catalog.audiences=["impuls"]`).

This is a **new independent data pack**, not a conversion of `reply_catalog.json` or `skills.json`. It originally included 24 synthetic, manually composed canonical questions and 24 additional answer variants about public bot-help scenarios. Its knowledge is read-only and scoped to direct address, including personal and addressed group contexts. No chat-specific rules, raw messages, usernames, secret implementation, automatic sanctions, or GitHub write token are included.

The trusted publisher requires candidate `section_path` to exactly equal `packs/ru/impuls_help_qa.json` and requires `reviewed=true`, valid source, and an already registered package. A new producer candidate is **not** a live ImPULS deployment or proof of consumption. The consumer/export workflow remains separately owned by the ImPULS maintainer.

Source review (read-only, private repository; do not export private code): `Treninem/Impuls` main `d45d6ceac889f940bc7961704cd1953f88e6872f`; inspected `docs/BOT_KNOWLEDGE_SKILLS_INTEGRATION.md`, `docs/AI_DIALOGUE_LEARNING_20261102.md`, `docs/FEATURE_MAP_V30.md`, `docs/COMMANDS_MATRIX_V30.md`. General safety rules: `POLICY.md`, `AGENTS.md`, `docs/DYNAMIC_QA_FORMAT.md`. The content does not claim that any feature is enabled on a live bot.

This pack supports approved declarative answers only, not executable commands. Each response must still pass the consumer's runtime role, address, and scope checks. New publication requires a reviewed isolated maintainer PR plus exact-head/post-main gates, and changes to the pack require matching manifest SHA-256.

## Дополнение справки 02.11.2026 — проверяемая партия

Фиксированный исходный main: `7acfe19b65c5fc168fe7a69d515777fc2311f565`, 25 имеющихся записей. Добавлены **54 независимых вопроса и 162 оригинальных ответа** (по 3 контекстно уместных формулировки на каждый). Итого **79 вопросов и 212 ответов**; это qa.v1, а не 100/100 reply_catalog — существующий формат допускает до восьми variants. Ранее существовавшие 25 записей сохранены без изменений. Условия применения сохраняются: только audience `impuls`, прямой запрос в ЛС или адресованной группе, ответ только для чтения.

Темы: адресация/молчание бота, настройка группы, права, обучение и обратная связь, типы цитат и команд, игры, Пульсы/Stars, розыгрыши, модерация без ложных санкций, апелляции, версии и приватность. Примеры синтетические и не содержат личных диалогов, ID, токенов, секретов или реализации санкций.

Сверка фактов: только чтение `Treninem/Impuls` main `50b09ee6cb249ea0b96bc3f64f8099eea9d48b78`, документы `docs/AI_DIALOGUE_LEARNING_20261102.md`, `docs/COMMANDS_MATRIX_V30.md`, `docs/FEATURE_MAP_V30.md`, `docs/BOT_KNOWLEDGE_SKILLS_INTEGRATION.md`; внутренний код сюда не переносился. Упоминания кандидата не объявлены подтверждённым live-поведением. Consumer/export принадлежит отдельному ImPULS-потоку.

Версия/cache: `2026.11.02.38`; SHA-256 изменённого пакета по окончательным UTF-8 байтам `dfcc43d75ebaaba700e242be4b72b86ffa18a13e8bd658f586bc8086b42cb1e4`. Пройти exact-head CI и post-main CI до утверждения доставки; живой BotHost не обновлялся.

## Дополнительная публичная справка и диагностика — 02.11.2026

Проверенный исходный Bot-Knowledge main: `22d3e5336aaec48ac984bdee23a303d8b24fe2ca`; источник продуктовых ограничений, только чтение: Treninem/Impuls main `50b09ee6cb249ea0b96bc3f64f8099eea9d48b78`, `docs/AI_DIALOGUE_LEARNING_20261102.md`, `docs/FEATURE_MAP_V30.md`, `docs/BOT_KNOWLEDGE_SKILLS_INTEGRATION.md`. Добавлены 45 оригинальных синтетических канонических вопросов и 135 ответов (по одному основному и двум контекстным вариантам), без замены исходных 79 вопросов/212 ответов. Итог: 124 вопроса/347 ответов, qa.v1, audience `impuls`, прямое обращение в ЛС/адресованной группе, только справка, не санкции и не действия. Это не reply_catalog 100/100: схема qa.v1 разрешает максимум восемь альтернатив одному ответу. Темы: продолжение разговора, источники, контекст правил, права, обучение, игры и розыгрыши, SHA/cache/fallback. Все сведения обезличены, записи живого чата не копировались.

Проверки на авторском head: уникальные нормализованные ID, вопросы и 347 текстов ответов — без точных дублей, 3-граммный Jaccard новых против старых и друг друга <0.68 (максимум 0.2143); полевая проверка аудитории, длины, приватности. SHA-256 конечного UTF-8 пакета: `6cd693c577a1e338cd33cc2b2cf16c7c8c8a6a726ca07b51dbb407c075b234bd`; pack/manifest `2026.11.02.41`. Реальные Python/CI и post-main отмечать отдельно. Потребитель ImPULS и BotHost не изменялись.
