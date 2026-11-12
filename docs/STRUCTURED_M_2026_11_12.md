# Structured-information continuation M52–M54 — 12 November 2026

## Verified source and saved data

- Repository: `Treninem/Bot-Knowledge`; source `main` `6c9f430da47f137d39a72bbd28c057cfb8f6be96`. Published `packs/ru/structured_information_qa.json`: SHA-256 `55b3f6126d36cd92687d005b7fedf5a11df9ee61cf453103accdf1f13c8498f0`, Git blob `8b3d596b5b50d3d319ebf450c96d5623fc99d26a`.
- Existing L branch/PR: [#662](https://github.com/Treninem/Bot-Knowledge/pull/662), previous head `e24803c1e9e81480dfd8a8fc9d47613e31fe08a6`. Prior L blob remains unchanged at **2,094,994 bytes**, safely below the 2 MiB per-file planning limit.
- New standalone, **unregistered** `staging/ru/structured_information_20261112_delta_m.json`: **180 synthetic Russian replies**, three distinct context-labelled responses per existing stable intent (suffixes **52, 53 and 54**), for `all_ai_bots` and explicitly addressed applicable contexts only. It does not grant actions, sanctions, memory, consumer integrations or ImPULS features.
- Readback M: **246,220 actual UTF-8 bytes**; Git blob `ec903b36d63e94cdd0112f34919cd3bc99aa4f3d`; byte-level SHA-256 **`f6af0a1af3d32508c198451956d4bd284f3bb894a6d5d19718f678054ede53c5`**. The SHA code passed the `abc` test vector and reproduced the earlier L SHA-256 before use.

## Correct cumulative counts (no double counting)

| Source | Answers per intent | Total for 60 intents |
| --- | ---: | ---: |
| Published original pack | 3 | 180 |
| Earlier staging A–J | 11 | 660 |
| Existing L in #662 | 31 | 1,860 |
| **New M in this execution** | **3** | **180** |
| **Combined** | **48 / 100** | **2,880 / 6,000** |
| **Missing** | **52** | **3,120** |

All **60 sets remain partial**, **zero sets completed to 100/100**. The 180 new records are additional to the previous L staging and were not included in any previous reported run. The next stable ID is `<intent_id>_supp_55`; preserve the current 180 and never restart at 52.

## Validation and editorial changes

- Readback confirms 60 canonical IDs, 180 response IDs, three sequential suffixes per intent, distinct normalized Russian responses and selection context notes, and the same direct-address/read-only/no-private-data/no-sanctions constraints.
- Lexical screening against L (1,860), K (1,296), conversation-nuance PR #663 (2,000), precision PR #664 (1,500), the registered structured pack (342 responses), and every A–J staging file: **1,465,920 cross-file text comparisons**, 0 exact normalized matches, 0 token-set Jaccard ≥ 0.70. This is an automatic lexical screen, *not* complete independent semantic or real consumer testing.
- Manual editorial check caught **six** context-overlapping illustrations in M (area versus length, speed versus displacement, tax base, clock offsets, inclusion of date bounds); wording and application conditions were corrected **without increasing the new-answer count**. Some broad content overlap within a canonical intent may still need independent assessment.
- Test: `scripts/test_structured_m_20261112.py` checks registered-source SHA and Git blob, M/L checkpoint counts, direct-context constraints, normalized duplicates against historical A–J/L and the registered source, and Jaccard proximity. The existing `.github/workflows/structured-l-20261111.yml` now runs **both L and M** on exact PR head using only `contents: read`, no secrets or trusted write credentials.
- Intermediate dedicated exact-head L/M job [43325706870](https://github.com/Treninem/Bot-Knowledge/actions/runs/43325706870) succeeded on commit `9f32afeed8887b69ef3cab848c84c493e79b8f56`. This is historical only; the current full head still requires its own real CI. No local repo-backed Python execution was available (the container could not resolve github.com); GitHub Actions gives the actual Python test result when complete.

## Git changes and publication gate

First two sets: [M52](https://github.com/Treninem/Bot-Knowledge/commit/2c1405d79e8ab6596d370327162c39f0c85173a2), [M53](https://github.com/Treninem/Bot-Knowledge/commit/5cdf7004061d53270f6f8b402b238035e8a9147e). Third set: [M54](https://github.com/Treninem/Bot-Knowledge/commit/716c4d21517a1ee6e555fb4866cf583a2453ce0c). Corrections include [M editorial](https://github.com/Treninem/Bot-Knowledge/commit/d4918497fab65a026302a71e5f7cb4edbc0a5b1a) and [date-boundary edit](https://github.com/Treninem/Bot-Knowledge/commit/86486b9a1536915751a75439e0a3cbccf8309d5d).

**Exactly four unique paths changed in this execution:** M JSON, dedicated Python regression, this journal, and the existing L exact-head workflow. No registered manifest/pack checksum or consumer cache was changed. No private source messages, BotHost updates, payments or real sanctions.

**Draft/BLOCKED:** snapshot historically 7,999,374 / 8,388,608 bytes, so L/M cannot be added wholesale to the registered consumer delivery. Require current full exact-head CI, independent semantic/context routing review, a validated size-compatible selection/delivery plan, safe main compatibility and post-main verification before merging. Do not raise the limit, disable safeguards or claim any live bot acquired these data.

Next: preserve all 180 newly staged records, resume the same 60 intents at suffix **55** if further genuinely different contexts are found; otherwise work on other uncovered areas while separately testing consumer selection and resolving CI/main delivery gates.


## M55 checkpoint — 13 November 2026

- Continued the same 60 intents in [PR #662](https://github.com/Treninem/Bot-Knowledge/pull/662) from head `4ce840abfa8793c1260e6227bd9d03f6c8a079bd`, source main `6c9f430da47f137d39a72bbd28c057cfb8f6be96`.
- Added **60 original synthetic Russian contextual replies**, suffix 55, one per existing intent. Preserved L=1,860 and M52–54=180. M now **240**, L+M now **2,100**. Published 3 + older staging 11 + L31 + M4 per intent = **49/100**; 60 partial, zero completed, 51 remaining per intent, 3,060 total; resume at **56**.
- Before writing, normalized exact response/context comparisons against previous M found no duplicates. Maximum token-set Jaccard against previous M was **0.3077**, none ≥0.70. Updated Python tests cover exact sequence/counts, published source SHA, A–J/L lexical comparisons, audience, context, no email and read-only safety. Broad independent semantic checks remain necessary.
- M JSON is **313479 UTF-8 bytes** (below per-file 2 MiB limit). Only this unregistered staging file, its dedicated test and journal changed. No consumer manifest, registered SHA, cache, ImPULS, BotHost, payment or live deployment changes. Exact-head CI and consumer-delivery/snapshot size must be confirmed before merge.
