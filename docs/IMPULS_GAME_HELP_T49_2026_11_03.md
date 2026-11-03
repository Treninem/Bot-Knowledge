# T49 — ImPULS: natural help for real game controls (2026-11-03)

Base Bot-Knowledge `3b27e5cfc35a25658b95a0b8b63f8ca3927bfc81`. Verified source ImPULS **read-only** at `de25c08028547564e4fcf85926f1105ab74ec9f2`: `src/bot/handlers/game_controls.py`, `src/bot/services/game_recommendation.py`, `src/bot/keyboards/private_panel.py`, and `docs/MINI_GAMES_PLAN_V80.md`. The referenced private implementation itself has **not** been copied to this public repository.

New: 24 independent canonical questions, 48 search aliases, 72 context-appropriate answer variants; `impuls_help_qa` 838 → 862 records. Stable IDs `help_t49_001`–`help_t49_024`. Topics: 12 existing game settings, creator-only toggles, read-only list, stale buttons and confirmation, member-only scoped game recommendations, distinct mini-game awards, and plans versus implemented modes. Answers contain no claims about any live BotHost session and no secret data.

All rows are synthetic and declarative, `audiences=["impuls"]`; group-initiated actions are **explained**, never performed. Sources are immutable path+SHA links and are a factual snapshot, not an assertion of current BotHost deployment. The `all_ai_bots` audience must not retrieve these rows.

JS preflight against 838 existing QA rows: zero normalized duplicates across question/aliases, zero token-Jaccard candidate collisions above 0.65, highest canonical overlap 0.300. This is lexical screening, not proof of semantic uniqueness. Pack size 1032594 bytes (<2 MiB), actual UTF-8 SHA-256 `af55400bcae19291c5aaf60ef57d9b7637005ffe381687f293f2aeadf2ed457c`. Manifest `2026.11.03.128`, SHA-256 `72cc63ede26b69ec2ca98bc27af93e78223a73870e0846fe6e4a0449df54d192`. Loader must invalidate on changed version/SHA; no live cache is modified.

CI: `python scripts/validate_pack.py` and `python -m scripts.test_impuls_help_t49` plus full exact-head quality suite. Treat PR as BLOCKED until GitHub confirms **all** required exact-head checks; after any safe merge, verify real post-main SHA and Actions. No change to ImPULS or BotHost.
