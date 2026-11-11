# Temporal language: original RU contextual staging — 2026-11-11

Owner authorization 02.11.2026 permits checked expansion, PRs and guarded merges **only in Bot-Knowledge**. Privacy, verified exact-head CI, source integrity and live-consumer isolation remain mandatory.

## Scope and ten stable intents
All examples are synthetic, Russian, addressed and read-only, audience `all_ai_bots`, no sanctions, no external actions or personal conversations. They distinguish relative dates, time zones, intervals, hard vs tentative deadlines, time-of-day vs duration, recurrence, past/future, schedule conflicts, date formats, and event ordering.

The ten IDs are:
`temporal20261111_relative_anchor`, `temporal20261111_timezone`, `temporal20261111_interval`, `temporal20261111_deadline_vs_estimate`, `temporal20261111_clock_or_duration`, `temporal20261111_recurring`, `temporal20261111_past_future`, `temporal20261111_conflict`, `temporal20261111_date_ambiguity`, `temporal20261111_sequence`.

## Stage A checkpoint
- Source: `packs/ru/social_dialogues.json` unchanged; source Git blob `d56ff304da7165bd63c328f3220a1f6d3d26e3ab`; registered SHA-256 `0cfedc133354a69522fecc3cda6bc21533c66005f0dc207050075f787dc977a8`.
- Base main at branch creation: `a5e798c3a964307a0f3fb130413e24055ab358b2`.
- New: **100 synthetic context-specific replies** = ten intentions × ten distinct situations. Previous in this stable series: 0; total 100/1000, ten partial sets at **10/100**, **90 remaining each** (900 total), zero completed 100/100.
- Entries are in `staging/ru/temporal_language_20261111_context_pool.json` with stable numbered IDs, explicit context notes, scope, negative guards, and consumer-registration flag `false`.
- Before writing to GitHub: 100/100 unique IDs, normalized texts, context notes; 0 exact duplicates in the new series; highest pairwise token Jaccard = **0.25**. This is NOT a full semantic originality or cross-corpus audit. Spot-check style, time logic and non-invention before publication.
- Test file: `scripts/test_temporal_language_20261111.py` checks registered source SHA, actual Git blob, manifest non-registration, counts, uniqueness, lexical similarity and privacy/action boundary; CI results must be read from GitHub, not assumed.
- `manifest.json`, registered packs, index and live caches unchanged. This staged file is NOT consumed automatically; no changes to ImPULS, BotHost or AuroraFox.

## Next actions
1. Check full current main and other PRs, compare new text with related registered and staged corpora, and fix any collisions.
2. Verify Python unit tests and all required exact-actual-head CI; if failing, keep this PR draft/BLOCKED.
3. Only after exact-head green and safe current-main compatibility, mark ready/merge with expected-head SHA guard and verify post-main CI on actual merge SHA.
4. Continue these exact ten stable intents starting **11**, not another set of IDs; create other non-overlapping questions only when their source and semantics are checked.

## Stage B checkpoint (same series, no new intent IDs)
- PR [#627](https://github.com/Treninem/Bot-Knowledge/pull/627), branch `bk/temporal-language-20261111-a`; Stage B is `staging/ru/temporal_language_20261111_context_delta_b.json`.
- **100 more NEW** original synthetic examples (11–20 for each stable intent), continuing Stage A without recounting its 100. Cumulative **200/1000**, 10 partial intent sets at **20/100**, **80 missing each** (800 total), zero completed.
- Source registered SHA-256 and blob unchanged. Stage B records exact parent Stage A blob `ffc8ab618c5f2e20db7e48f35fa99adf048cd2ac`; the expanded Python unittest checks that blob from real bytes.
- Connector-side normalization of 200 replies before commit: 200 distinct IDs, 200 normalized response texts, 200 context notes, zero exact repeats; maximum token Jaccard **0.31579**. This does not prove absence of semantic duplicates in the full repository. All replies require direct context, no actions or sanctions.
- Stage B raw-data commit `56d02baf4416f715a8ff843c2c9fc872a275071b`; test update `9f1419e86aca533b8797d5d1221f6afd2ecec410`. Full actual-head Python/CI must be confirmed on **latest** PR head; earlier CI on Stage A is obsolete.
- **Next suffix: 21** for each existing stable intent; new accepted response delta this cycle is Stage A +100 plus Stage B +100 = **200**, not 300. For merge, check fresh main and complete predecessor post-main; do not bypass checks or modify live consumers.
