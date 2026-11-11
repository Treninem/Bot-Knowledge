# Quantitative clarity G–J — completion checkpoint (2026-11-11)

This PR continues the **same ten stable** `quant20261111_*` intents from prior merged A–F, not a parallel rewrite. Main base after verified #630 merge: `f3488be0e31356f5d34e4d575f5efe6ae14a4f60`.

## Counts and ownership

| Stages | Placement | New answers in this PR | Cumulative candidates | Per intent |
| --- | --- | ---: | ---: | --- |
| A–F | Merged via #628, #629, #630 (historical; not new here) | 0 | 600 | 60/100 |
| G | This PR | 100 | 700 | 70/100 |
| H | This PR | 100 | 800 | 80/100 |
| I | This PR | 100 | 900 | 90/100 |
| J | This PR | 100 | 1000 | 100/100 |

**New in this PR: 400**, not 1000. Ten intents processed, ten complete **as unregistered staging candidates**, zero partial in this series. The new data cover 4 JSON files; no source pack or manifest modification.

- Intent namespace: `quant20261111_percent_basis`, `rate_scope`, `delta_type`, `cumulative_vs_increment`, `precision_limits`, `missing_inputs`, `boundary_scope`, `unit_consistency`, `ratio_denominator`, `calculation_check` (all prefixed `quant20261111_`).
- New ID suffixes: **61–100**, exactly 40 per intent; no earlier responses counted as newly authored.
- All replies are original synthetic, Russian, direct-address with a distinct contextual applicability note. Audience `all_ai_bots`, no personal data or operative sanctions, read-only and not automatically selected.
- Source pack: `packs/ru/social_dialogues.json`, manifest SHA-256 `0cfedc133354a69522fecc3cda6bc21533c66005f0dc207050075f787dc977a8` (unchanged). No download of real user conversations. Git blob parent for F: `b49efb91d4516c119e04aef6974c243b19a3c4f0`. Parent ancestry for G→H→I→J is asserted on exact bytes by `scripts/test_quantitative_clarity_completion_20261111.py`.
- Pre-commit connector-side checks compared 1000 candidates across A–J: 1000 distinct IDs, normalized texts and context notes; **zero exact repeats**, and all new answer pairs had token-Jaccard below 0.80. This is a **lexical** test, not proof of semantic uniqueness against every package.
- Previous exact-head #630 passed 39/39; **post-main checks must be independently verified**. Do not merge current PR unless its own complete exact-head CI, SHA/manifest tests, compatibility check with the then-current main, and guarded expected-head merge are successful.
- **No consumer integration:** these stages are not listed in `manifest.json`, not fetched by running bots, and do not confer calculator functionality, live sensor access, account privileges or moderation rights.

## Follow-up

After full exact-head CI and guarded merge, verify actual post-main workflow checks at merge SHA before other merges. Next work should review and expand different genuinely missing intent sets rather than create duplicate G–J packages, then tackle safe consumer integration as a separate explicitly verified project. Existing PR #611 contains historically conflicting IDs and must be reconciled without discarding unique text.
