# Правило для всех ИИ-ботов Treninem — Bot-Knowledge

**Treninem/Bot-Knowledge — единый исходный репозиторий переносимых языковых знаний и умений для всех наших ботов с ИИ.** Это долгосрочное архитектурное решение владельца от 29.10.2026. Новый бот не должен заново собирать общие базовые умения: он подключает **утверждённые универсальные пакеты** отсюда и добавляет только собственный локальный контекст.

## Для разработчика каждого бота
1. Проверить версию и содержимое публичного Bot-Knowledge: `manifest.json`, `packs/ru/*.json`, `POLICY.md`; использовать **чтение по HTTPS** с SHA-256 пакетов и проверкой схемы.
2. При первом запуске можно загрузить snapshot, но **никогда не делать сетевой запрос GitHub на каждое сообщение**: горячие знания — в памяти, подтверждённая копия — локально. Обновления фоновые, с таймаутом и последней исправной версией на случай проблем с GitHub.
3. Прежде чем говорить, сверять уместность с правилами и полномочиями **конкретного сообщества**. Общие подсказки не разрешают модерацию, баны, платежи, выдачу ролей, вмешательство в личный разговор.
4. Выученные в чате **частные** данные (история, цитаты, местные правила, имена, идентификаторы, жалобы, наказания, секреты) хранить исключительно в изолированной локальной базе с TTL и удалением. Никогда не выгружать их в этот **публичный** репозиторий.
5. Для нового универсального навыка: короткая абстракция без исходной цитаты → проверка персональных данных и качества → PR в Bot-Knowledge → CI → утверждение → версия/хэш → фоновое обновление потребителей. Не давать живому боту или BotHost токен записи в GitHub.
6. Держать базу узкоспециализированной: естественные диалоги, внимание к контексту, поддержка, уместный юмор, понимание сленга, уточнение правил, объяснение функций бота. Не добавлять энциклопедии и тяжёлые модели, если они не нужны.
7. Разделять **распространение знаний** (GitHub) и **оперативную БД** (SQLite/другое локальное хранилище). GitHub не предназначен для транзакционных обновлений и мгновенной записи каждого события.
8. Каждое изменение: обновить manifest SHA-256 и версию, прогнать `python scripts/validate_pack.py`, тесты чтения и совместимости. Отдельно подтверждать доставку в конкретный запущенный бот.

## Проверка скорости
Цель «1–3 секунды» относится прежде всего к **первому чтению обновления** при нормальной сети. Сеть GitHub не гарантирует жёсткие сроки; ответы на сообщения должны брать данные из локального снимка (миллисекунды). Измерения по GitHub Actions отражают только GitHub runner, а не реальный BotHost. Проверять холодное HTTPS-чтение и 1000 локальных обращений: `python scripts/benchmark_shared_skills.py`.

## Совместимость
Старые базовые пакеты `intents/dialogue/styles/safety` остаются. Новый `skills.json` только **декларативные знания**, а не действующие полномочия. Для каждого бота требуется собственный проверенный consumer; наличие файла в манифесте не означает, что новая функция уже включена.

## OWNER DECISION 2026-10-29: no direct cross-bot learning
- AuroraFox and ImPULS **do not connect to each other directly** for language learning; future AI bots also exchange **only via this common repository**. Existing direct routes may be deprecated **only after** call-graph audit, compatible migration, tests, and release gates; see `docs/CROSS_PRODUCT_KNOWLEDGE_EXCHANGE.md` and AuroraFox issue #122.
- The shared repository is the canonical **versioned learning library** for all Treninem AI products. Every new project must check it before building its own conversation knowledge and should use only applicable `audiences`/categories (general conversation for AuroraFox; community moderation/bot-help for ImPULS).
- Bots may *propose* learning candidates, but no raw user data or direct GitHub main writes. A publisher with isolated credentials and human-approved PRs is a **planned** feature; never claim unsupervised bot submissions already work.
- AuroraFox remains fully intelligent **offline** on its own Core/Knowledge; a GitHub outage must never disrupt it. Local model training/Evolution and the protected private memory remain AuroraFox-specific.
- When creating/reviewing another AI bot, proactively point the owner/developer to **Bot-Knowledge** and this contract, even when the owner has forgotten the repository.

## Владелец: 21 обязательная способность (30.10.2026)
- **Читать до разработки:** [docs/REQUIREMENTS_21.md](docs/REQUIREMENTS_21.md). Все AI-программы должны иметь возможность использовать библиотеку для понимания правил, обходов, ложных нарушений, английского, разговора, юмора, сарказма, мата, обмана, контекста, творчества, обучения и быстрого локального поиска.
- **Не путать понимание и полномочия:** общая библиотека даёт знания; санкции выполняет только отдельный разрешённый модерационный consumer с подтверждёнными правилами чата, защитой от ложных срабатываний и проверенными правами. Никакая запись JSON не является разрешением на мут, бан или просмотр скрытого меню.
- **Стиль:** разговаривать естественно, поддерживать и поздравлять разнообразно, а мат применять только при допустимом контексте/предпочтении, без направленных оскорблений; чёрный юмор неуместен в трауре и направленной травле. Английский язык и сленг должны пониматься по смыслу.
- **Обучение:** только локальный контур → безличный проверенный кандидат → публикация через доверенный maintainer и PR; никакого автоматического переноса приватных чатов и GitHub-токенов боту. См. [docs/LEARNING_PUBLICATION_PIPELINE.md](docs/LEARNING_PUBLICATION_PIPELINE.md).
- **Поиск:** использовать локальный валидированный индекс, а не сетевой поиск GitHub на каждое сообщение; скрипт `scripts/search_knowledge.py` — эталон, но consumer обязан подтвердить производительность на своём устройстве.
- **Отчётность и запрет фиктивной работы:** каждый завершённый цикл фиксировать конкретным diff/commit, числом новых *уникальных* единиц, проверками exact-head CI и post-main CI, честным статусом доставки. Запрещено выдавать планы или структурные тесты за уже работающее поведение модели.
