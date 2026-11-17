# ImPULS contextual H74 continuation — 2026-11-15

Continues [PR #666](https://github.com/Treninem/Bot-Knowledge/pull/666) after H72–H73. **40 new synthetic Russian help candidates across 40 additional canonical intents**, separate from the 53 intents in H72–H73. This run has now handled **93 distinct canonical intents**, producing **93 new stage-only replies**. None are independently approved, and none are registered for a live consumer.

## Actual source deltas

- H74: +20 replies on the group last updated in H58 and +20 on the group last updated in H59. All are single genuinely different scenarios per stable intent; no synonym or emoji variants counted.
- H58 lineage after H74: 14 intents reach 35/100 and six reach 32/100.
- H59 lineage after H74: 11 intents reach 38/100 and nine reach 35/100.
- H72 lineage: 33 intents at 27/100; H73 lineage: 9 at 41/100, 4 at 40/100, 7 at 38/100. Seven other intents retain their previous partial counters. Every individual record has a machine-readable `remaining_to_target_excluding_other_prs`.
- Previously staged H1–H71 2,879; H72 +33, H73 +20, H74 +40. **H1–H74: 2,972 staged** across **100 partial intents**, **6,753** numeric vacancies. **0 completed 100/100 sets**, **0 editorially approved / published new answers**. All figures exclude separate unmerged PRs.

## Data and checks

- Baseline Bot-Knowledge main `6c9f430da47f137d39a72bbd28c057cfb8f6be96`.
- QA source `packs/ru/impuls_help_qa.json` manifest SHA-256 `50edd41dc0c6a868577433944e0ff0b2a36c2c9ebe53d587e5cbb4692185bbc9`; no manifest/consumer registration changes.
- ImPULS read-only: `README.md` at `a9004b2d4b8a09f5ff2866eb15cdfab14cd3c410`; candidate 1.6.257, live deployment unverified. No ImPULS source edited.
- H74 `scripts/test_impuls_help_h74_20261115.py` compares all H1–H74 numeric deltas with the published source, verifies source manifest, scope/read-only flags, IDs, text context, privacy markers, and lexical duplication. H72–H73 remain tested separately.
- Read-only [exact-head workflow](../.github/workflows/impuls-help-h72-h73-20261115.yml) verifies the actual Git checkout SHA and runs tests with and without `-O`. Check its **final SHA** before reporting success.
- H72–H73 were checked in a constrained in-run lexical comparison against 2,688 published and representative prior-stage texts: 0 normalized exact matches, maximum Jaccard 0.357. This does not cover every older staged reply, other PR, or semantic overlap; the CI checks the full local H1–H74 stage for lexical conflicts.

## Blockers and next step

**DRAFT/BLOCKED** until independent semantic editing against concurrent PRs (#662–#665), compatibility of live context-aware reply selection, completed exact-head/quality CI and a safe 8 MiB registration budget. Keep all records out of the active manifest until those release conditions are met. Do not deploy, spend money, change ImPULS/BotHost or touch running caches.

Next: check exact head results, correct any detected issues, review a manageable candidate subset for explicit context selection and registration. Remaining lowest-count sets have not been declared complete.
