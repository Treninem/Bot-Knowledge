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


## Stage C–D checkpoint — continuation after #627 merge (2026-11-11)

This is the current checkpoint; the earlier "next suffix 21" instruction above is superseded. PR #627 has been merged at actual main SHA `fbf23438790f33f767e8890dd14fd9fde5bd20c3`. The current branch `bk/temporal-language-20261111-c-d` began at that exact SHA. Do **not** count the 200 replies from stages A–B again as newly authored.

- **C:** 100 genuinely new synthetic responses, IDs **21–30** for each of the ten original `temporal20261111_*` intents. 200 previous → **300/1000** (ten sets 30/100).
- **D:** 100 additional contextual responses, IDs **31–40** on those same ten intents. 300 previous → **400/1000** (ten sets **40/100**, exactly **60 remaining per intent**, 600 total, zero finished 100/100).
- This continuation adds **200 new candidate replies** across **two JSON files**. No additional canonical intents are invented. Answers include relative time anchoring, source time zones, open and intersecting intervals, tentative promises, conversational clock expressions, exceptions in recurrence, temporal status, scheduling collisions, ambiguous date formats and dependency order.
- Source stays `packs/ru/social_dialogues.json` with registered SHA-256 `0cfedc133354a69522fecc3cda6bc21533c66005f0dc207050075f787dc977a8`, Git blob `d56ff304da7165bd63c328f3220a1f6d3d26e3ab`. Registered manifest, index and live caches were **not** changed: `consumer_registered=false`.
- C checks its parent B blob `1872f48b24d0bbbdfbe023ab464f24cf93d6cf6d`; D checks its parent C blob `1f773829644bdb61e2366ab7bb4d3a89ba032700`. The updated read-only Python unittest verifies both links, original SHA-256, ten stable intents, 400 unique IDs/texts/context notes, target counts and action/privacy guards.
- In connector-side normalized/text token checks across all 400 candidates: **400 unique texts/IDs**, no exact repeats and maximal token-Jaccard **0.33333**; this metric does **not** prove full semantic uniqueness across all Bot-Knowledge files or open PRs. Meaning/context requires editorial review.
- No personal conversations, real identities, authoritative commands, moderation sanctions, live bot changes or new knowledge-consumer integration.
- Before merge: run local or actual GitHub Python validation, verify **all** exact-head CI on final commit and actual post-main #627 success on its merge SHA, re-check main and PR for conflicts, then expected-head guarded merge. After merge verify actual post-main CI before the next merge.
- **Next unique replies:** suffix **41–50** for each stable temporal intent. Preserve current 400 and continue; do not reset to Stage A.


## Stage E–F checkpoint — latest progress on PR #632

After stages A–B (200, merged #627) and C–D (200 new in this PR), two additional sets were written on **the same branch and same ten stable intents**:
- Stage E: 100 new replies **41–50** in `staging/ru/temporal_language_20261111_context_delta_e.json`.
- Stage F: 100 new replies **51–60** in `staging/ru/temporal_language_20261111_context_delta_f.json`.
- **New delta in PR #632: 400** (C–F); **whole staging series: 600/1000**, ten partial sets **60/100**, 40 remaining for each, 400 total; **zero completed**.
- Parent links: E → D blob `d72558db7e1e631d10b3f1f4602b5ab1c6305197`, F → E blob `90b8ee2846dab66ca322c4766f94cfa14cefd7d9`. Python QA now asserts the whole A–F chain and 600 unique normalized texts, IDs and contexts.
- Before commit, exact normalized duplicates among 600: **0**; max pairwise token-Jaccard **0.38889** (lexical only). Broader semantic/cross-corpus originality must still be reviewed, particularly against related staging files and concurrent PRs.
- No pack registration, manifest version bump, SHA-256 change, cache, consumer or ImPULS modification. Same original source pack SHA-256 from Stage A; these are **unregistered candidates** only.
- The old "next suffix 41" above is superseded: **next continuation suffix 61**. Do not recount A–F or reset intent IDs.
- Latest branch head and CI must be re-read before any merge. Current PR is DRAFT/BLOCKED until final-head full actual-checkout CI and previous merge post-main verification. After guarded merge, post-main CI on actual merge SHA is mandatory.

### Exact-head QA correction
The first actual GitHub exact-head Python run found one duplicated normalized context note across 600 candidates (original `sequence_04`, Stage D `sequence_35`). **One context note was rewritten** to preserve a distinct applicability condition, and the parent Git blob hashes were recomputed in stages E and F; response texts and IDs were not altered. Distinguish this rejected duplicate from the **400 newly accepted reply texts**. Initial specialized run: [failure](https://github.com/Treninem/Bot-Knowledge/actions/runs/42973255169); a new exact-head run must pass before merge.
