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

## Stage F checkpoint — 11 November 2026
- Added **100 NEW** synthetic RU teaching replies (51–60) across the ten unchanged intents; prior 500 retained. **Cumulative 600/1000**, each intent **60/100**, **40 missing each** (400 total), 0 complete; following suffix **61**.
- Parent E blob `d6d124bf61462b4167a9d4ff8b338adc3d13ad53`. All six source stage files remain unregistered/read-only, and test validates exact parent Git blobs, source SHA-256, stable IDs, safe scope, lexical uniqueness.
- Normalization QA on all six stages: 600 unique IDs, 600 distinct normalized replies and context notes, 0 exact duplicates; maximum token-Jaccard 0.2857. This is a lexical bound, not proof of exhaustive semantic originality. New examples cover reliability, timing, ambiguity, access, data integrity, statistics, safety, and teaching feedback.
- Manifest remains `2026.11.09.003`, source SHA-256 `0cfedc133354a69522fecc3cda6bc21533c66005f0dc207050075f787dc977a8`. Consumers, ImPULS, BotHost and caches untouched. Run all exact-head CI before merge and post-main CI after any merge; no consumer delivery asserted.

## Stage G checkpoint — 11 November 2026
- Added 100 new original replies, stable IDs suffix 61–70. Prior 600 not counted again. **Cumulative A–G 700/1000**, ten intents each **70/100**, 30 missing each, zero completed.
- Parent F blob `9ad11e9e37ace34391b742691c49ba2655943b13`; updated Python test checks exact ancestry, source manifest SHA-256 and all seven stages. Pre-commit normalized IDs/texts/context notes: **700/700** distinct, zero exact duplicates, maximal pair token-Jaccard **0.2857** (< 0.80). Semantic originality across all published corpus not proven.
- All candidates remain unregistered, contextual and read-only. Registered source pack, manifest `2026.11.09.003`, ImPULS and consumer caches unchanged. Next suffix **71**.

## Stage H checkpoint — 11 November 2026
- +100 original RU responses with suffix 71–80, continuing 10 existing stable intents, previous 700 preserved. **Total 800/1000**, each **80/100**, **20 remaining per intent** (200 total), completed 100/100 **0**.
- Parent G exact Git blob `2467feecddc609ab19e2e7fdb62094254e75d34b`, verified before commit. A–H normalization QA 800 unique IDs, 800 normalized texts, 800 normalized context notes; zero exact duplicates; maximal token-Jaccard 0.2857. Automated lexical checks are not a full semantic audit.
- Updated read-only unittest covers eight stages, parent blob ancestry, manifest/source checksums, context and privacy. All staging packages remain consumer-unregistered. No live changes or auto-delivery claims. Continue suffix **81**.

## Stage I checkpoint — 11 November 2026 (recovered)
- Stage I already existed on parent PR #639 head `e4ec206a05072f22a20fac248d92e37885b41ac1` when this independent continuation was started. It contains **100 earlier responses** (IDs 81–90), not counted as newly created by this continuation.
- Stage I Git blob `36b23de86fb21f9233c5b33d874ca899250c9165`, parent H Git blob `b7b6325745415a6e1164b7eb4da91583ed2172d9`. Parent series cumulative **900/1000**, ten stable intents at **90/100**, ten each still missing.
- Parent #639 must be merged and verified independently. The dependent completion PR does not authorize overwriting its branch.

## Stage J independent completion — 11 November 2026
- Created **100 NEW original synthetic Russian replies**, ten per stable intent with ID suffixes **91–100**. Earlier stages A–I contain 900 replies and are **not** counted as newly added. **Cumulative A–J: 1000/1000 staged candidates; 10 intentions at 100/100, no partial sets, 0 remaining.**
- Candidate file `staging/ru/explanatory_teaching_20261111_context_delta_j.json` uses exact parent stage I Git blob `36b23de86fb21f9233c5b33d874ca899250c9165`; a separate dependent branch `bk/explanatory-teaching-complete-20261111-r11` preserves parent #639 without concurrent edits.
- Connector-side normalization of A–J: **1000 unique IDs, 1000 unique normalized reply texts, 1000 unique normalized applicability notes**; zero exact duplicates; maximum token-Jaccard **0.3462** among 1000 answers (threshold 0.80). This does not prove there are no semantic near-duplicates or inaccuracies. Manual context and wording review remains required.
- The read-only Python unittest was extended from eight to all ten stages; its passing status must be confirmed by actual exact-head CI. Source and manifest remain expected at registered `2026.11.09.003` / `0cfedc133354a69522fecc3cda6bc21533c66005f0dc207050075f787dc977a8`; dedicated test independently compares source file bytes, manifest SHA and Git blob.
- All staged replies require direct address and a matching situation; they provide explanations and exercises only, no actual teaching integration, permissions, sanctions, memory, privacy extraction, or modifications to live bots.
- **Publication gate:** first verify and merge parent #639 only if its exact-head and actual post-main requirements pass. Then retarget this PR onto verified main without discarding useful changes; confirm exact-head Python plus full CI and compatible base, use guarded head merge and actual post-main CI. Do not merge this dependent candidate early.
- After the completed series: review and prioritize **existing partial** canonical intents from the backlog, not another renamed copy of this teaching set.
