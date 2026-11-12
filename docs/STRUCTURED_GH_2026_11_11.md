# Structured-information RU — staged continuation G–H (2026-11-11)

## Base and scope
- Last confirmed source main before this series: `b465c9a3e92acb01def74e7f57e7706413883b43`, after verified merge [#656](https://github.com/Treninem/Bot-Knowledge/pull/656).
- Registered reference pack: `packs/ru/structured_information_qa.json`, 114 canonical questions × 3 registered responses, SHA-256 `55b3f6126d36cd92687d005b7fedf5a11df9ee61cf453103accdf1f13c8498f0`, Git blob `8b3d596b5b50d3d319ebf450c96d5623fc99d26a`.
- Prior merged stages A–F: **690** supplemental review-only responses. Do not count them as new in this PR. Historical Draft #229 is separate/unmerged.
- New G–H: **228** originally authored, context-specific Russian answers for the **same 114 stable intent IDs**. G: 54 intents × 2 replies = 108, H: 60 intents × 2 replies = 120. No new canonical questions, no overlapping suffixes.

| Group | Registered/intent | Prior staged/intent | Added/intent | Combined/intent | Still missing/intent | Total still missing |
|---|---:|---:|---:|---:|---:|---:|
| G: 54 stable `struct_t93/88/90` intents | 3 | 5 | 2 | **10/100** | 90 | 4,860 |
| H: 60 stable `struct_t86/88` intents | 3 | 7 | 2 | **12/100** | 88 | 5,280 |
| Total | 342 registered | 690 staged previously | **228 new** | **1,260 potential texts** |  | **10,140** |

Full sets 100/100: **0**; partial sets: **114**. 918 staged answers (690 prior + 228 new) are **not in manifest** and **not available to any consumer**. Totals are candidate coverage, not live ability.

## Guardrails and audit
- New entries remain in `staging/ru/` with `consumer_registered=false`, audience `all_ai_bots`, `requires_direct_address`, `requires_context_match`, read-only, no sanctions, no external action, no private conversations.
- Authoring check: 228/228 new IDs and texts distinct, 228 distinct situation notes. Across A–H there are 918 distinct normalized texts and 918 distinct normalized context notes.
- Cross-stage lexical screen: every new reply compared against earlier A–F and other new replies, **max token-Jaccard 0.4737**; no pairs ≥0.70; one near-duplicate discovered and rewritten before PR.
- These are surface-level exact and lexical checks, not a full semantic equivalence test. Numeric examples and instructions require context-specific editorial review; source-pack invariants are tested separately.
- `scripts/test_structured_gh_20261111.py` checks manifest and pack SHA/Blob, stage-count and suffix accounting, normalized dedup, context metadata, privacy, read-only rules, source-pack overlap, and near-duplicate threshold.
- `.github/workflows/structured-gh-20261111.yml` uses `pull_request` exact head, read-only checkout and runs pack validator + targeted test. No privileged secrets or paid workflow dispatch.
- Do not alter registered packs, manifest, running caches, ImPULS code, permissions or live bots in this PR.

## Release gate and next action
No merge before exact final-head CI (including `validate`) passes, editorial/content QA, compatibility with the **fresh** main, and registered source SHA check; merge with expected-head protection. Inspect actual post-main CI on the new merge SHA before another merge. Never claim consumer installation merely because staged JSON is merged.

After this checkpoint continue G intent IDs at suffix **17** and H intent IDs at suffix **19**, only where genuinely different situations exist. Favor utility over mechanically reaching 100. Then proceed to other underfilled topics. Avoid editing Draft #229 or #655 in this series.
