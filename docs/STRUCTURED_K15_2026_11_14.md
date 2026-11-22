# K15 / K79–K80 — 14 ноября 2026

Continuation of [PR #661](https://github.com/Treninem/Bot-Knowledge/pull/661), 54 stable canonical RU structured-information intents, general `all_ai_bots` audience. Source registered pack at `main` `6c9f430da47f137d39a72bbd28c057cfb8f6be96`, manifest SHA-256 `55b3f6126d36cd92687d005b7fedf5a11df9ee61cf453103accdf1f13c8498f0`. Each synthetic answer carries a distinct scenario note; selection requires direct addressing, matching prior context and read-only operation.

**Before:** 3,240 staged replies, 3 published + 69 staged = 72/100 per intent. **New:** 108 candidate replies K79–K80, two per intent. **After:** 3,348 staged, 3 published + 71 staged = **74/100** per intent, 54 partial sets, 0 completed, **26 missing per intent / 1,404 total**. Next stable suffix K81. All counts are numerical candidates, not independent semantic approvals.

A connector-side preliminary review checked 108 unique normalized replies and context notes; compared token overlap with 14 K stage files, max token-Jaccard **0.6400**; no exact match or ≥0.70 overlap. Registered original and full K corpus will be validated by `scripts/test_structured_k15_20261114.py` in exact-head GitHub CI. This lexical test does not guarantee distinct meanings, and editorial/context-route review remains outstanding.

No modification to `manifest.json`, live consumers, running caches, BotHost or ImPULS. `consumer_registered=false`. **BLOCKED:** independent semantic review, exact-head complete required checks, measured safe 8 MiB delivery and post-main CI after any future merge.
