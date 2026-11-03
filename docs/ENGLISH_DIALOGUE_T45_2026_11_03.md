# T45 — 28 original English contextual replies (2026-11-03)

Starting from verified main `4aa0002cfd11932c5e4e46c14ca95cd898d47ce9` after T44 merge. The existing English pack receives 28 new synthetic cases/replies across seven kinds (four each): `conversation`, `slang`, `sarcasm`, `rules`, `deception`, `support`, `creative`. Count **382 → 410**, IDs `en_t45_001`–`en_t45_028`. Each case includes precise English input and answer, a Russian meaning guard and an avoidance condition. General `all_ai_bots` audience; no live bot rights, private chats or actual sanctions.

Proposed manifest `2026.11.03.124`. English pack size **220522 bytes** < 2 MiB; SHA-256 `2b3544f8c321dbb790fb71ab1ac3112e40ec7c553c00f7213780cd756a8eabdc`. Normalized input/response uniqueness and lexical near-duplicate screen passed against all previous English cases; max Jaccard 0.462 under 0.67. CI must still verify full real manifest integrity, schemas, exact-head and indexed retrieval; post-main CI separately. No sets of 100 replies are claimed: these are separate contextual situations.

Next: reconcile any pending head with latest main, verify real checks, then only merge on exact head. Consumer integration and BotHost are separate and untouched.
