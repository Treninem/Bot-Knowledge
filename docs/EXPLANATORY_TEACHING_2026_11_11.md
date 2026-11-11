# Explanatory teaching and learning by examples — 2026-11-11

## Source and scope
- Published source: `packs/ru/social_dialogues.json` on `main` 8697a9abb15380a3b25f567467d1cfddb3f5b58c; Git blob `d56ff304da7165bd63c328f3220a1f6d3d26e3ab`; SHA-256 from manifest `0cfedc133354a69522fecc3cda6bc21533c66005f0dc207050075f787dc977a8`.
- Owner permission dated 2026-11-02 is already documented in `AGENTS.md` and `docs/OWNER_AUTOMATION_SCOPE_2026_11_02.md`.
- New independent stable prefix **`teach20261111_*`**, 10 canonical intents: explain without jargon, explain by steps, correcting misconceptions, showing a concrete example, identifying exceptions, practice exercises, actionable feedback, checking understanding, comparing methods and transfer to new contexts.
- New **100** original synthetic RU contextual replies; 10 per intent (**10/100**), exactly **90 missing each, 900 total**, zero completed. 100 new only; prior Bot-Knowledge replies are not counted.
- Before commit, code-side normalized IDs, reply texts and context descriptions all unique (100/100); zero exact duplicates and max within-batch token-Jaccard **0.2857**. This is lexical not exhaustive semantic screening.
- Reply contexts are individualized; the assistant must select based on direct request and actual situation. These replies are *not* a guarantee of educational competence or a live tutoring, grading or learning system.

## Safety and publication
`staging/ru/explanatory_teaching_20261111_context_pool.json` is **consumer-unregistered** (`consumer_registered=false`), `all_ai_bots`, read-only; no sanctions, private chats or permissions. Registered source and manifest `2026.11.09.003` unchanged, no cache updates or changes to ImPULS/any live bot.

Tests: `python -m unittest scripts.test_explanatory_teaching_20261111 -v`, registered source and manifest SHA, exact checkout, stage counts, ID, normalization, context selection, privacy and duplicates. Full exact-head CI/compatibility and after-merge post-main are mandatory; no bypass of required checks.

Next action: independently and carefully continue **the same ten stable intents** from suffix **11**, do not restart, use genuinely different examples and only publish after gates.

## Stages B–C checkpoint — 11 November 2026
- Source `main` commit at branch start: `1e81ec9b23a212d05ae9bdcd569c4aefc5c0699c`; stage A's **100 earlier examples** remain unchanged and are not counted as new.
- Stage B adds exactly **100 new** synthetic RU answers (suffix 11–20), Stage C adds exactly **100 new** (suffix 21–30), ten per stable intent in each stage. **New delta in this PR: 200; cumulative staging 300/1000** across ten `teach20261111_*` intentions, each **30/100**, **70 missing each** (700 total); completed **0**, partial **10**.
- Git blob ancestry: A `520a95da851a551f4b35f6f2ea6d3dd3387d4d6e` → B `548ef4ac0f0e69a1115d9fdd2d5cd778a77ccbe2` → C `7a58591d9d929e2671b5d3badc015353bad5c82a`; each child embeds the exact previous Git blob SHA. Dedicated Python test extended to all three stages, including registered source manifest SHA-256, stable IDs, context guards, duplicates, and privacy.
- Connector precommit screening: **300 distinct IDs, 300 normalized answers, 300 distinct normalized application notes**, zero exact duplicates; maximum reply token-Jaccard **0.2857** among A–C. This is not a full semantic uniqueness proof. Synthetic examples are direct-address, read-only, no sanctions or claims of tutoring, persistent memory, or real consumer capabilities.
- Registered source `packs/ru/social_dialogues.json` SHA-256 `0cfedc133354a69522fecc3cda6bc21533c66005f0dc207050075f787dc977a8`, manifest `2026.11.09.003` and consumer caches are deliberately unchanged; these files remain unregistered.
- Next: actual exact-head CI on the full current PR SHA and editorial/cross-corpus screening; compatibility with updated main, expected-head guarded merge, actual post-main checks. If still blocked, preserve B/C in the Draft rather than recount them. The following set starts at suffix **31**, not 01.

## Stage D checkpoint — 11 November 2026
- Parent: merged PR #638, main `daa81c091497735dd0754ecffead5aac9b234e3f`; parent C exact Git blob `7a58591d9d929e2671b5d3badc015353bad5c82a`.
- Added exactly **100 new original synthetic responses**, 10 per each of ten stable `teach20261111_*` intents, suffixes **31–40**. Prior A–C 300 not recounted; **cumulative 400/1000**, each intent **40/100**, **60 remaining each / 600 total**, zero completed 100/100.
- Precommit normalization QA A–D: **400 distinct IDs, 400 normalized texts, 400 normalized context notes**; zero normalized duplicates, maximal token-Jaccard **0.2857** (< 0.80). This is lexical screening, not a full semantic guarantee. Independent situations cover data migration, verification, source reliability, reversible steps, teaching exercises, safety, measurement and evidence.
- Stage D JSON remains **unregistered read-only staging**; no permission to change user state, moderate, make claims of live tutoring or copy personal correspondence. Registered pack and manifest remain unchanged (`2026.11.09.003`; source SHA-256 `0cfedc133354a69522fecc3cda6bc21533c66005f0dc207050075f787dc977a8`). No ImPULS/consumer/cache deployment.
- Verification command: `python -m unittest scripts.test_explanatory_teaching_20261111 -v` with four-stage parent SHA, schema, source SHA, IDs, lexical scope, registered exact answers, privacy constraints. GitHub exact-head and post-main are mandatory before publication; no bypass.
- Next: complete exact-head tests for stage D, merge only after verified current main and guarded head; then continue **suffix 41**, not a new series.

## Stage E checkpoint — 11 November 2026
- New **100** original Russian contextual replies, suffix 41–50, ten for each of the same ten stable `teach20261111_*` intentions. Previous 400 not counted again; **total 500/1000**, each intent **50/100**, 50 remaining each / 500 total, completed 100/100 **0**.
- Parent D exact Git blob `3ee07b06cddc44ce27bc635f7925c095d48f3786`. Five-stage QA input paths preserve complete ancestry A→B→C→D→E. New examples span state definitions, version checks, evidence limits, exercises, careful feedback, alternate methods and transfer of principles without claiming actual tutoring or access.
- Pre-commit normalization on A–E: 500 unique IDs, 500 unique normalized answer texts and 500 distinct normalized application notes, exact duplicates **0**; maximum pairwise token-Jaccard **0.2857**. Semantically close answers may still require editorial review.
- All stages unregistered read-only (`all_ai_bots`); published source SHA-256 `0cfedc133354a69522fecc3cda6bc21533c66005f0dc207050075f787dc977a8`, manifest `2026.11.09.003`, live caches, ImPULS and bots unchanged.
- Next: run updated `python -m unittest scripts.test_explanatory_teaching_20261111 -v` on the **final** PR head; verify full exact-head checks and post-main compatibility before merge. If blocked, preserve branch and continue suffix **51** next time, do not restart.
