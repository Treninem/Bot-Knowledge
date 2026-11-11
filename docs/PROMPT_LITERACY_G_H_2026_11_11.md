# Prompt literacy G–H — 11 November 2026

Independent clean-main continuation of merged #645 at exact main `60b97259a3bb90c91be721548aac496d42a67ee6`. Stages A–F are already in main with **600** synthetic candidates. This PR adds **200 NEW** Russian context-specific replies: G suffix 61–70 and H suffix 71–80 across the same ten stable `prompt20261111_*` intents. Cumulative **800/1000**, each intent 80/100, 20 missing each, 200 remaining, completed 100/100: 0.

G SHA `e126aa745eabca438b69fdeae67e4f04e86a7f15` (parent F blob `faca8a39bb8005a1eef33d513d1495633d2fa5e1`); H SHA `84c2f6f6f47500dfcaebd5e6fb182eaeeef624f3` (parent G blob `e126aa745eabca438b69fdeae67e4f04e86a7f15`). No other candidate IDs reused or renamed. Authoring checks against 600 existing replies plus 200 new: **800 unique IDs, normalized texts and distinct context notes**, 0 exact duplicates, maximal pairwise token-Jaccard 0.3637 (not exhaustive semantic proof).

Read-only Python suite `scripts.test_prompt_literacy_a_h_20261111` validates actual byte SHA-256 of registered source, stage Git blob ancestry, scope/conditions, privacy, exact overlap and lexical similarity across all 800. Existing workflow uses checkout of exact PR head and no stored credentials. Published `manifest.json` version `2026.11.09.003` and original registered `packs/ru/social_dialogues.json` SHA-256 `0cfedc133354a69522fecc3cda6bc21533c66005f0dc207050075f787dc977a8` unchanged.

**DRAFT / BLOCKED:** full exact-head CI, actual post-main CI of #645, editorial compatibility and protected expected-head merge are mandatory. No live bots, ImPULS modifications, payments, cache writes, bans or automatic consumer integration. Next continue suffix **81–100** with meaningfully new contexts, then further intents.
