# T49 — ImPULS: natural help for real game controls (2026-11-03)

Base Bot-Knowledge `3b27e5cfc35a25658b95a0b8b63f8ca3927bfc81`. Verified source ImPULS **read-only** at `de25c08028547564e4fcf85926f1105ab74ec9f2`: `src/bot/handlers/game_controls.py`, `src/bot/services/game_recommendation.py`, `src/bot/keyboards/private_panel.py`, and `docs/MINI_GAMES_PLAN_V80.md`. The referenced private implementation itself has **not** been copied to this public repository.

New: 24 independent canonical questions, 48 search aliases, 72 context-appropriate answer variants; `impuls_help_qa` 838 → 862 records. Stable IDs `help_t49_001`–`help_t49_024`. Topics: 12 existing game settings, creator-only toggles, read-only list, stale buttons and confirmation, member-only scoped game recommendations, distinct mini-game awards, and plans versus implemented modes. Answers contain no claims about any live BotHost session and no secret data.

All rows are synthetic and declarative, `audiences=["impuls"]`; group-initiated actions are **explained**, never performed. Sources are immutable path+SHA links and are a factual snapshot, not an assertion of current BotHost deployment. The `all_ai_bots` audience must not retrieve these rows.

JS preflight against 838 existing QA rows: zero normalized duplicates across question/aliases, zero token-Jaccard candidate collisions above 0.65, highest canonical overlap 0.300. This is lexical screening, not proof of semantic uniqueness. Pack size 1032042 bytes (<2 MiB), actual UTF-8 SHA-256 `832a6a52d849fff005315d534ebf49e0c602c3e8ffd91fd7eb2d51b7a8d0c4e1`. Manifest `2026.11.03.128`, SHA-256 `027ed898157d40a967cb51448d1daf40a98881412ac5037adf121ce145233002`. Loader must invalidate on changed version/SHA; no live cache is modified.

CI: `python scripts/validate_pack.py` and `python -m scripts.test_impuls_help_t49` plus full exact-head quality suite. Treat PR as BLOCKED until GitHub confirms **all** required exact-head checks; after any safe merge, verify real post-main SHA and Actions. No change to ImPULS or BotHost.

QA source fields point at this public fact-note file; this document retains the exact read-only private source SHA/paths without embedding private code. The change also respects the strict URL privacy validator, which intentionally does not whitelist private-repository commit URLs in public QA records.
