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
