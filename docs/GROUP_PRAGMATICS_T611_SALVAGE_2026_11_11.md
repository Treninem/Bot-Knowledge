# Salvage of superseded group-pragmatics PR #611 — 2026-11-11

## Why this exists
PR [#611](https://github.com/Treninem/Bot-Knowledge/pull/611) contains five historical JSON stages (T604–T608). Their 500 original synthetic replies reuse the same 500 reply IDs as stages T604–T608 already merged into main via [#610](https://github.com/Treninem/Bot-Knowledge/pull/610). A direct merge would overwrite good published candidate wording; closing #611 without preserving its distinct material would silently lose useful work.

Verified against exact old head `d234d00fc0405015100b78ebba4b953e0df91907` and current staging main snapshot `3967f534a805d3546b790cd855f369714fa08611`: **500/500 distinct** normalized texts, IDs and context notes in old T604–T608; 500 colliding original IDs with already published candidates; **0 identical normalized texts** among those 500 and main's 1000 T600–T609 replies. Highest token-Jaccard across old500 × main1000 was `0.473684` (no pairs >= 0.60), a lexical check only.

This PR adds a **review-only, unregistered archive** `staging/ru/group_pragmatics_t611_alternatives_review_only.json`, preserving the 500 original texts and context conditions, with a noncolliding `t611_alt_` prefix for the new `id` and the original ID in `original_id`. The stable intent is retained. The new archive is NOT the active 100/100 main pool, is not a source for automatic consumer selection, and is not counted as **500 newly authored** answers. Its sole purpose is safe preservation and later editorial selection.

Metadata records all five source Git blob SHAs and exact old PR head. Scope remains `all_ai_bots`, read-only, direct-address and context-match only; no sanctions, real conversations, secrets or consumer integration. Published manifest `2026.11.09.003` and source `packs/ru/social_dialogues.json` SHA-256 `0cfedc133354a69522fecc3cda6bc21533c66005f0dc207050075f787dc977a8` remain unchanged.

QA `python -m unittest scripts.test_group_pragmatics_t611_salvage -v` checks total counts, exact old-ID correspondence, global ID/text collisions with 1000 existing entries, SHA provenance and privacy. GitHub workflow checks exact checkout SHA with `contents: read` and no persisted credentials.

## Gate / next action
Review this PR and complete all exact-head CI, source/content integrity and current-main compatibility before any merge; after merge verify actual post-main CI. **Only after verified preservation** can original #611 be closed as superseded with a link to this PR and a clear reason. Do not claim that review-only archival candidates are new skills or that they have reached any deployed bot.
