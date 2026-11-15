# ImPULS H89 — 100 context-specific Russian candidate replies (15 November 2026)

## Baseline and scope

Continues [PR #666](https://github.com/Treninem/Bot-Knowledge/pull/666)
from exact H1–H88 head `df490439234e94a01004f08c7285b9e68cc2836d`.
The published Bot-Knowledge `main` remained
`6c9f430da47f137d39a72bbd28c057cfb8f6be96`.
Source catalog: `packs/ru/impuls_help_qa.json`; original manifest
SHA-256 `50edd41dc0c6a868577433944e0ff0b2a36c2c9ebe53d587e5cbb4692185bbc9`;
Git blob `430f78f7bf43940b112978bc5087b5cb6002eabe`.

ImPULS was **read only** at main `54b8a3a813fec82c1f953408942ba327eb181c37`,
`README.md`: 1.6.263 is a candidate, 1.6.262 installed, AI quality
not accepted. No modification or live integration occurred.

## What changed

`staging/ru/impuls_help_context_h89_20261115.json` adds **100 synthetic
candidate replies to 100 distinct existing canonical intents**, one per intent.
Existing responses are retained. Each new candidate supplies a distinct
situational note, a declared delivery context, read-only and audience scope,
and an explicit restriction on changing settings or punishing people.
Examples cover greeting without unrelated rules, technical fault reports
without secrets, quoted commands, moderation appeals, local-vs-general rules,
outdated game buttons, permissions, indirect sarcasm, training revocation,
Pulses, and family-game consent.

Each answer is **a pending candidate**; candidate count is not an editorial
acceptance or a delivered response. 100 intents remain partial; no set is
certified as genuinely complete or independently reviewed. There is no
guarantee that all 100 candidates are fit for one single chat situation.

| Main + H1–H89 answers per intent | Intents | Missing to 100 |
|---:|---:|---:|
| 24 | 1 | 76 |
| 25 | 6 | 450 |
| 32 | 33 | 2,244 |
| 37 | 6 | 378 |
| 40 | 23 | 1,380 |
| 43 | 18 | 1,026 |
| 45 | 4 | 220 |
| 46 | 9 | 486 |
| **Total** | **100** | **6,260** |

H1–H88 previously staged **3,365** candidates; H89 adds **100**;
total staged **3,465**. Main source has 869 records; this checkpoint
tracks only the same 100 named intents, not a count of the entire library.
Published source answers within these intents: **275**.
Total main + staged in this tracked subset: **3,740**.
Accepted independent editorial approvals: **0**.
Registered H89 answers: **0**. Certified sets 100/100: **0**.

## Required verification and publication gates

Run `python -B scripts/test_impuls_help_h89_20261115.py`,
`python -O -B scripts/test_impuls_help_h89_20261115.py`,
and `python -B scripts/validate_pack.py`. The new read-only
`.github/workflows/impuls-help-h89-20261115.yml` checks out the exact
PR head with credentials disabled. It reconstructs all H1–H89 staged
counts and checks IDs, candidate context, normalized exact repetition,
coarse token-overlap signals and privacy restrictions. Semantic review
of H1–H89 and parallel PRs #662–#665 is still necessary: token
overlap is only a proxy and cannot establish meaning or factual validity.

Published snapshot last measured at **7,999,374 / 8,388,608 bytes**.
No stage files were added to manifest; no current consumer's cache or
deployment was touched. Publishing H89 requires a genuinely selected
subset, accurate manifest/version/actual-byte SHA and a proven safe
consumer context/permissions route. Do not claim availability in live
ImPULS, or merge draft staging as a delivered feature.

## Next

Editorially review candidates against prior stages and concurrent PRs,
including examples with hidden assumptions. Confirm the consumer's
read-only response routing, direct-address constraints and role
isolation on tested inputs. Only after those gates, register a
size-safe selection with exact-head CI and post-main validation.
Continue the lowest-count useful intents without cosmetic padding.
