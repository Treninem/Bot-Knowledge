# Universal conversation QA T10 — 2026.11.03.77

Base `f57d9ba21df1233233a1f2adea1d85d8c9773656` with 140 existing universal qa.v1 questions; this party adds **42 genuinely distinct intentions**, 126 original response texts (main plus two context-aware alternatives) and 84 search aliases. New total **182**.

Themes: group and private conversation boundaries; rule interpretation and false moderation positives; warnings, appeals and uncertain histories; dynamic search and bot capability scope; shared gaming buttons vs personal callbacks; privacy-safe debugging; partial/incorrect claims and appropriate repair; social empathy. All are generic, synthetic, read-only guidance for `all_ai_bots`. Mentioning game buttons and moderation does not assert any implemented ImPULS feature.

Source: `AGENTS.md` at immutable base f57d9ba21df1233233a1f2adea1d85d8c9773656; no private ImPULS implementation, personal chats, usernames, IDs or executable actions.

Changes: `packs/ru/dialogue_help_qa.json`, `manifest.json`, `scripts/test_dialogue_help_expansion.py`, this document. Manifest/cache version 2026.11.03.77. New pack SHA-256 `4e10df2c2667d75ca43fb6e5d6d8b8dc956b4afa17ff3232d6b8d6f43dd3f05d`, UTF-8 size 240039 bytes, under qa.v1 1 MiB and consumer 2 MiB.

Local JS preflight: normalized question/alias duplicate scan vs existing 140 plus new rows, 0 exact duplicates; conservative token Jaccard threshold 0.66 for canonical questions, 0 collisions. Search assertions for all 126 query forms are added to actual Python quality workflow. **CI status must be reported from the exact new head; no claim before running it.** No consumer delivery.
