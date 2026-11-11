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

## Stage B checkpoint — same ten stable intents
- New B: `staging/ru/media_interpretation_20261111_context_delta_b.json`, exactly **100** additional synthetic contextual replies (suffixes 11–20, 10 per same intent). These are **new for this continuation**, not the previous A set.
- Stage A Git blob parent SHA: `2d146659a81f932f5d933452cc0dee7fc9ee77c2` (after fixing a short context note). Stage B references that exact blob and the original source pack.
- Cumulative proposed **200/1000**; each of 10 intents **20/100**, 80 missing, 800 total remaining. **0** finished sets. No new canonicals, no published consumer package changes.
- Precommit connector-side verification for A+B: **200/200 distinct IDs, normalized reply text and context notes**, 0 exact collisions; highest token Jaccard **0.3333** (lexical only). New B content length ≥45 characters and notes ≥18; 100 B replies are fresh relative to A.
- Required Python, exact-head CI and complete cross-corpus semantic review must be checked **on the new head**; any prior CI is obsolete. Next B→C continuation from suffix **21** after QA, do not restart IDs or create duplicate PRs.

## Stage C checkpoint — continued exact same ten intents
- New 100 original situational Russian replies in `staging/ru/media_interpretation_20261111_context_delta_c.json`, suffixes 21–30. Earlier stages A+B (**200**) unchanged and excluded from this new count.
- Parent B Git blob `9dcf8ec62ed1129596d1a797a00dadd250d0f7a2`; C checkpoint inherits source manifest SHA-256, audience and safety limits.
- Cumulative staged **300/1000**; 10 partial sets **30/100 each**, 70 missing each, 700 total remaining, complete 0. No changes to registered pack, manifest, live consumer or ImPULS.
- Precommit connector-side checks over stages A–C: 300 unique IDs, normalized replies and application notes; no exact duplicates, max token-Jaccard **0.3333** (<0.80). Semantic uniqueness beyond lexical checks remains subject to editorial review. All C replies have distinct scenario conditions and are read-only.
- Python/quality checks for the latest head, expected-head guarded merge and actual post-main required. Prior head CI is obsolete after C commit. Next suffix: **31**.

## Stage D checkpoint — continued ten stable intents, 31–40
- Based on confirmed main `8697a9abb15380a3b25f567467d1cfddb3f5b58c` after merged #634; earlier stages A–C unchanged. New stage `staging/ru/media_interpretation_20261111_context_delta_d.json` contains **100 original synthetic contextual Russian candidates**, ten per existing `media20261111_*` intent, ID suffixes 31–40. This is the **new delta**, not a recount of the preceding 300.
- Exact parent C Git blob: `d2ba043797124cbf8758c9756a85bbf7b054f6ea`. Source registered pack remains `packs/ru/social_dialogues.json` with SHA-256 `0cfedc133354a69522fecc3cda6bc21533c66005f0dc207050075f787dc977a8`; staging is not registered and no consumer cache is modified.
- Pre-commit connector-side read of A–C plus D: **400/400 distinct IDs, normalized reply texts, application context notes**; 0 exact repeats; maximum pairwise token-Jaccard **0.3333**, less than 0.80. This is a lexical screen, not exhaustive proof of semantic uniqueness. All new answers are conditional and read-only; no invented media access, actions, sanctions, or personal data.
- Cumulative staging **400/1000**; ten partial intents at **40/100**, 60 missing each (600 total), completed 100/100: **0**. Continuing source is D, next unused suffix **41**. Keep the same intent IDs and do not regenerate the first 400.
- Existing dedicated Python suite extended to include D; require actual exact-head CI and post-main checks for the merge SHA before release claims. To publish to consumers, a separate manifest/SHA/version/compatibility review and consumer integration is necessary. No ImPULS or BotHost writes.

## Stage E checkpoint — stable intent suffixes 41–50
- Fresh **100 original RU candidates** in `staging/ru/media_interpretation_20261111_context_delta_e.json`. Parent D Git blob `da529d0b2a95e5efcacd92f105625e1d4f558916`. Previous 400 replies unchanged; stage checkpoint 500/1000, each of 10 intents **50/100**, remaining 500 total; completed 0.
- Lexical check over A–E: 500 unique ID, normalized text, and context notes; no exact repeat; max pairwise token-Jaccard 0.3333. Semantic cross-corpus originality is not established by this number alone.

## Stage F checkpoint — stable intent suffixes 51–60
- Fresh **100 original RU candidates** in `staging/ru/media_interpretation_20261111_context_delta_f.json`. Parent E Git blob `386c26370a0e692ed110fe4cc8ff4031e6d9f723`. Earlier 500 unchanged, excluding their counts from this newly added 100.
- A–F now **600/1000**: ten existing intents each **60/100**, 40 missing each (400 total), complete 0. Connector-side comparison: 600/600 unique ID, normalized text and application notes; no exact collisions; highest token-Jaccard 0.4286. This does not replace editorial, privacy, JSON/schema or exact-head CI.
- Six-stage Python unittest in `scripts/test_media_interpretation_20261111.py` and read-only workflow must pass on actual PR head; merge only with guarded SHA and confirmed post-main checks. Staging is unregistered: manifest, source SHA, consumer caches and ImPULS unchanged. **Next unused suffix 61** in each of ten `media20261111_*` intents.
