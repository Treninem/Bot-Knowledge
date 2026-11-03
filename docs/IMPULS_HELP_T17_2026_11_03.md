# T17 — ImPULS: natural user guidance and safe feature boundaries (03.11.2026)

- Bot-Knowledge base main: `d81e9114e526c4745e6b02a881e0d3ce765cef89` (manifest `2026.11.03.94`).
- ImPULS read-only verified main: `0979092ea6fdf9787ed02c40a88ed4e2a437edf1`, files `docs/COMMANDS_MATRIX_V30.md`, `docs/FEATURE_MAP_V30.md`, `docs/BOT_KNOWLEDGE_SKILLS_INTEGRATION.md`. No private source code or messages copied.
- Starting `impuls_help_qa.json`: 607 records. New canonical intents: 27; new natural search aliases: 54; new distinct contextual answer texts: 81. Duplicates rejected by exact normalization: 0. Proposed total: 634 records.
- Themes: safe first use, rule draft versus action, announcements, permissions versus replies, owner menu privacy, diagnostics, archive, release status, visual settings, community and weekly gift, game-role boundaries, payment uncertainty, private info, moderated disputes.
- Every item is synthetic, `impuls` audience, direct/private/group-addressed; explicit read-only, direct address and no personal data. No sanction, write token, command execution, real chat/IDs or live runtime claims.
- Pack `717292` UTF-8 bytes (<1 MiB qa.v1 and 2 MiB consumer). SHA-256 `27cd3f08e034c875f7a208d939eadc95b39c32f4c5c74d15cf4b444c3e39fac3`. Manifest version `2026.11.03.95`, SHA-256 `de98ddcc57289846ab01a2f141c7a4978b3a7f0eb9028d8a59e303d5f52bbb28`. Local cache/live bot unchanged.
- New regression: `python -m scripts.test_impuls_help_t17` checks hash, schema, 81 paraphrase searches and audience isolation; existing quality workflow still runs full regression suite. Actual exact-head and post-main statuses must be checked at real commit SHAs, not assumed.
- No new 100/100 reply_catalog sets: existing 119 completed collections are untouched. Next cycle: recheck main/open PR and continue independently confirmed questions and non-template contextual dialog.
