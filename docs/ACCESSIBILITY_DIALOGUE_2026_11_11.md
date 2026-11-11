# Accessibility-aware Russian dialogue — 11 November 2026

## Scope and provenance
This series contains **original synthetic Russian-language read-only answer candidates** for all compatible AI consumers under `all_ai_bots`. It does not grant new capabilities, sanctions or tool access and is **not registered in manifest.json**. No ImPULS, BotHost, deployed bot, private conversation, runtime cache or consumer was changed.

The verified source pack is `packs/ru/social_dialogues.json`, whose registered SHA-256 is `0cfedc133354a69522fecc3cda6bc21533c66005f0dc207050075f787dc977a8`. Base main at start: `06c329b25db1219cf70ddec4843d2d8468abff1d`; branch created on that base, and PR should be compared with current main when reviewed.

## Ten stable canonical intents
1. `access20261111_reader_order` — screen-reader-friendly answer order
2. `access20261111_chart_description` — verbal chart interpretation without imagined measurements
3. `access20261111_color_independence` — instructions not solely dependent on color
4. `access20261111_dictation_repair` — ambiguous voice transcription and careful clarification
5. `access20261111_link_labels` — descriptive link labels and verified destinations
6. `access20261111_math_speech` — mathematical symbols and spoken relationships
7. `access20261111_linear_table` — sequential, labeled table descriptions
8. `access20261111_single_step` — manageable instruction sequencing without falsely claiming completion
9. `access20261111_video_captions` — audiovisual captions and truthful observation
10. `access20261111_accessibility_preferences` — respectful format preferences without guessing personal traits

## Verified staging checkpoint
- Stage A: existing 100 candidate replies (IDs 01–10 per intent), branch commit `5818b4d3623f6d11ec9433e45c883357116a35d2`; this is prior work, **not newly authored in the present cycle**.
- Stage B: **100 newly authored** candidates (11–20 per intent), commit `586f7c6656819cc5d3426705a87753c5c8e44780`.
- Stage C: **100 newly authored** candidates (21–30 per intent), commit `62b8a973444bad0e5cec2d4c256871ef840b2bad`.
- Combined: **300/1000**, 10 partial stable sets at **30/100** each; **70 missing per intent, 700 missing in total**. 0 sets at 100/100. Count of new material in this cycle: **200** (B+C).
- Exact normalized ID, text and context-note checks A–C in a connector read found 300 unique of each. Maximum pairwise token-Jaccard seen among 300 responses was 0.285714; there were no pairs at or above 0.80. This lexical check **does not prove semantic uniqueness**, and editorial review remains required.
- Source SHA-256, Git blob lineage, schema, isolation, privacy and duplicate guards are asserted in `scripts/test_accessibility_dialogue_20261111.py`. Tests, exact-head CI and post-main CI must be verified from the real runner and commit; no unrun test is counted as passed.

## Next steps
Continue these **same** ten intent IDs from answer 31, without regenerating or recounting A–C. Before a merge, verify exact current main/head SHAs, all required exact-head workflow results, publication guards and consumer isolation. After a merge, confirm post-main on the actual merge SHA. A staged dataset is not a consumer release: registration, manifest SHA-256/version, index and consumer integration require a separately tested release.

## Stage D checkpoint (same 11 November cycle)
- **100 additional original contextual replies**, suffix 31–40 per intent; staged **400/1000**, all ten at **40/100**, **60 missing each / 600 total**, zero completed. This stage is **new** in the current cycle; total new B+C+D is **300** (prior A100 excluded).
- Parent C blob `480352a5eb5af86406c8aa1aae5ddb89dc4cb983`; stages A–D have **400 unique** IDs, normalized responses and context conditions, zero exact duplicates; max token Jaccard 0.2857 (lexical only, human editorial check still required). Changes do not register this staging pack.
- Next suffix **41**. Run Python suite and exact-head CI after final changes before merging; no ImPULS, BotHost or cache changes.

## Stage E on dependent continuation branch
- After prior A–D 400 staged candidates, **100 newly authored** contextual replies, IDs **41–50** per ten stable intents. Across A–E **500/1000**, ten partial sets at **50/100**, **50 remaining each / 500 total**, zero completed 100/100.
- Source data and QA remain unregistered and read-only, without private chat data, consumer integration or live bot changes. Parent stage D blob `6f8f5c8fb3cf192b366b8f2e700b436e3827de26`. Full A–E connector-side count: **500 unique IDs/texts/context notes**, no lexical Jaccard >= 0.8, max 0.2857. Semantic editorial and exact-head/full CI are still mandatory.
- Dependent on PR #620 and must be rebased/retargeted against main after #620 merges and its post-main CI succeeds. Next suffix **51**.
