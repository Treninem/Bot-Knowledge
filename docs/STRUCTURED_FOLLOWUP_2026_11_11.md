# Structured information RU — staged continuation E–F, 11 November 2026

## Stable source and checkpoint

- Source main after merged [#654](https://github.com/Treninem/Bot-Knowledge/pull/654): `21466aeb8a71984f4621681e4f373a291339e485`.
- Registered pack: `packs/ru/structured_information_qa.json`; 114 stable canonical intents, **3 registered responses each**, registered SHA-256 `55b3f6126d36cd92687d005b7fedf5a11df9ee61cf453103accdf1f13c8498f0`, Git blob `8b3d596b5b50d3d319ebf450c96d5623fc99d26a`; manifest version `2026.11.09.003`.
- Prior merged staging: #653 A–B = 300 candidates for 60 intents (5 each); #654 C–D = 162 candidates for a disjoint 54 intents (3 each). **These are not new in this continuation**.
- Older Draft [#229](https://github.com/Treninem/Bot-Knowledge/pull/229) is separate and proposes changes to the registered pack; it remains open and blocked. Its 1026 proposed answer texts are not counted as published here.

## Verified per-run increments

| Stage | Previously staged + published per intent | New replies | Intent count | Combined after | Missing each |
|---|---|---:|---:|---:|---:|
| E: `staging/ru/structured_information_20261111_delta_e.json` | 3 published + 3 staged | **108** (2 × 54) | 54 | **8/100** | **92** |
| F: `staging/ru/structured_information_20261111_delta_f.json` | 3 published + 5 staged | **120** (2 × 60) | 60 | **10/100** | **90** |
| **New in this PR** | | **228** | **114 distinct stable intents** | **0 complete 100/100** | **10,368 total** |

A–F collectively contain **690 unregistered staged replies**. Add 342 registered replies (114 × 3) to obtain **1032 existing plus candidate texts**, not a confirmed consumer-ready inventory. Do not count unmerged #229 candidates or other PRs as new answers.

Every new response has its own stable suffix, different synthetic text and `context_note`; language ru, audience `all_ai_bots`, direct context, read-only. The general method or numerical facts cannot vary merely for entertainment. No live chat data, access credentials, sanctions, consumer installation or cached payload changes.

## Checks and release requirements

- Connected-data preflight: 228 new IDs, 228 normalized reply texts and 228 normalized context notes, **no exact collisions** with A–D. Entire A–F: 690 distinct replies and contexts.
- 228 new replies compared with 462 previous A–D staged and 1026 proposed texts from old Draft #229: **0 exact matches**, maximum cross-source token-Jaccard **0.5264**, no similarity >= 0.65. Across all 690 A–F stage texts max Jaccard **0.4375**. These numbers are lexical screens, **not** proof of semantic non-equivalence.
- `scripts/test_structured_followup_20261111.py` checks registered source manifest SHA and Git blob, counts, all six stage IDs and scoped metadata, uniqueness, privacy and no actions, registered overlap and lexical threshold. Workflow `.github/workflows/structured-followup-20261111.yml` checks out exact PR-head and uses **read-only** permissions.
- `python scripts/validate_pack.py`; `python -m unittest scripts.test_structured_remainder_20261111 scripts.test_structured_followup_20261111 -v` must pass on actual PR head. Check full required exact-head CI, fresh base and mergeability before guarded merge, then post-main on actual merge SHA.
- Registered packages, `manifest.json`, indexes, working consumer caches, private ImPULS repo and live BotHost must remain unchanged. These **staging candidates are not yet available** to consumers.
- E next suffix is **15** for its 54 stable IDs; F next suffix is **17** for its 60 IDs. Reject repetitive phrasing; include new distinct situations only. Context-specific variants may not all be selected for the same user question. Full 100/100 per intent is not claimed.
- Owner's 02.11.2026 authorization permits systematic filling, verified PR merges and justified closure within Bot-Knowledge. It does not bypass branch protection, exact-head checks, privacy or publication conditions.
