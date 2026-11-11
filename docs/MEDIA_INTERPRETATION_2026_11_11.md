# Media interpretation — synthetic contextual replies (2026-11-11)

Owner authorisation: `docs/OWNER_AUTOMATION_SCOPE_2026_11_02.md`. **Only Treninem/Bot-Knowledge** is modified. Work is read-only language guidance, not media processing integration.

## Stage A checkpoint
- Source main: `3b94c70763df9d2e8ef256967e25371719b1a998`; source file: `packs/ru/social_dialogues.json`, Git blob `d56ff304da7165bd63c328f3220a1f6d3d26e3ab`, manifest SHA-256 `0cfedc133354a69522fecc3cda6bc21533c66005f0dc207050075f787dc977a8`.
- Stable intent namespace `media20261111_*`. 10 intents for cropped images, screenshots versus completed actions, uncertain audio, frame-only video, missing document pages, tables, code excerpts, unavailable links, differing file versions, and input capability limits.
- Exactly **100 new original synthetic Russian candidates**, ten distinct contextual replies per intent. Each intent is **10/100**, **90 missing**, **900 total remaining**. Completed **0**, partial **10**. Do not count previous corpus examples as new.
- Pre-commit JS: 100 distinct IDs, 100 normalized texts and context notes, exact duplicates 0, highest within-stage token-Jaccard 0.2381. Automatic lexical screening is *not* an exhaustive proof of semantic uniqueness.
- File `staging/ru/media_interpretation_20261111_context_pool.json` is intentionally **unregistered** (`consumer_registered=false`); the published `manifest.json` and source SHA-256 are unchanged. No consumer is claimed to understand a file, image, audio, video or a link without independent access.
- All rows require direct addressing and a matching situation, are read-only, no sanctions or private data, no invented action/status. Any platform-specific capabilities require separate consumer verification.

## Gates and continuation
- Run `python -m unittest scripts.test_media_interpretation_20261111 -v` and existing validation on the exact checkout SHA. Check all required CI and post-main for the actual merge SHA before calling a release verified; do not bypass protections or trigger paid jobs.
- Next stage **B** must continue these exact ten IDs with reply suffixes **11–20**, *not* create new intents. Verify across the previous stage and registered packs, include precise counts and parent blob SHA before saving.
- Do not touch ImPULS, BotHost, existing caches, private messages or the protected publisher scripts.
