# K16 / K81–K82 — 14 ноября 2026

Continues [PR #661](https://github.com/Treninem/Bot-Knowledge/pull/661), 54 canonical RU intents. Registered source pack at main `6c9f430da47f137d39a72bbd28c057cfb8f6be96`; SHA-256 `55b3f6126d36cd92687d005b7fedf5a11df9ee61cf453103accdf1f13c8498f0`.

Before: 3,348 staged; 3 published + 71 staged = 74/100 numerical candidates per intent. Added **108 synthetic RU context-specific replies**. Now **3,456 staged**, 3 published + 73 staged = **76/100** per intent. Completed: **0**; partial: **54**; remaining: **24 each / 1,296 total**; next suffix K83.

Preliminary connector-side check: all 108 replies and context notes distinct; compared against K14/K15 with no exact or token-Jaccard ≥0.70 matches (max 0.2903). Earlier stages, including the very large K file, and the registered source are covered by `scripts/test_structured_k16_20261114.py` on exact-head CI. These are lexical tests only; independent semantic/context routing review has not passed.

All new responses are synthetic, `all_ai_bots`, read-only and context-gated. `consumer_registered=false`. BLOCKED until complete exact-head CI, editorial review, delivery within consumer 8 MiB, compatibility with main and eventual post-main CI. Manifest, ImPULS, BotHost and running caches unchanged.
