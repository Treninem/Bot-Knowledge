# Support triage continuation — stages C and D (2026-11-10)

This independently reviewable branch extends the existing stable
`triage20261110_*` intents in [PR #612](https://github.com/Treninem/Bot-Knowledge/pull/612),
now merged at `4c5739320f080c6f456fcf0b0d4d4e6f5a0f9577`.
It **does not** promote data into a consumer or registered pack.

## Exact counts

| Stage | Prior | New | Cumulative | Each stable intent | Missing per intent |
| --- | ---: | ---: | ---: | ---: | ---: |
| A (merged #612) | 0 | 100 | 100 | 10/100 | 90 |
| B (merged #612) | 100 | 100 | 200 | 20/100 | 80 |
| C (this branch) | 200 | **200** | 400 | 40/100 | 60 |
| D (this branch) | 400 | **100** | 500 | 50/100 | 50 |

**New this branch: 300** original synthetic Russian replies across the same
**10** canonical intents. Completed 100/100 sets: **0**; 10 partial sets,
each precisely **50/100**, missing **50** each (500 total).
Continue from suffix `_51`, not from the beginning.
No previous A/B replies have been double-counted as new.

Canonical topics: missing response, off-topic response, invisible menu,
permission boundary, unapplied settings, empty search, stale information,
incomplete long request, two mixed questions, and verified repair.

## Provenance and compatibility

- Base main commit: `4c5739320f080c6f456fcf0b0d4d4e6f5a0f9577`.
- Registered source `packs/ru/social_dialogues.json`: manifest SHA-256
  `0cfedc133354a69522fecc3cda6bc21533c66005f0dc207050075f787dc977a8`.
- Source Git blob: `d56ff304da7165bd63c328f3220a1f6d3d26e3ab`.
- B parent Git blob for C: `14cff7cf90910e96fa9ac032a0b322af1ebae127`.
- C parent Git blob for D: `45ef21cede23f6c1bdce0f87c1acbb06aa8ca2be`.
- All stage entries: `all_ai_bots`, Russian, explicit direct address
  and context match, read-only, no sanctions, no personal data, no
  product-specific rights or UI claims. Intent IDs are stable.
- Registered manifest `2026.11.09.003`, package SHA/cache, ImPULS and
  live consumer deployments unchanged. `consumer_registered=false`.

Preflight written to GitHub: 300 new distinct normalized answer texts and
context notes; across A/B/C/D there are 500 distinct IDs/texts/context notes.
No exact or Jaccard >= .80 near duplicates against the prior 200
in A/B; maximum among new vs earlier same-series replies and preceding
new replies was **0.4118** for C and **0.2942** for D.
These are lexical metrics, not full semantic originality proofs.
`scripts/test_support_triage_continuation_20261110.py` checks exact counts,
lineage against Git blob bytes, registered source SHA-256, privacy and
cross-stage lexical near repetitions; it also samples related stage families.

## Publication gate

Run `python -m unittest scripts.test_support_triage_20261110
scripts.test_support_triage_continuation_20261110` and the repository's
standard quality checks on the **exact full PR head SHA**. CI workflow uses
read-only GitHub permissions and does not provide secrets to untrusted code.
Only after all current required tests pass, current main compatibility and
head SHA are re-verified, merge with expected-head guard and check
post-main on the actual merge SHA. Do not deploy to bots.
