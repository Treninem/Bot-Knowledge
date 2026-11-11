# Structured information supplemental replies — 11 November 2026

## Scope and immutable ancestry
- Worktree base (fresh main after protected #652 merge): `418d801cf037b96a9d7d5ebdfa2f563f86331344`.
- Registered source: `packs/ru/structured_information_qa.json`, **SHA-256 `55b3f6126d36cd92687d005b7fedf5a11df9ee61cf453103accdf1f13c8498f0`**, Git blob `8b3d596b5b50d3d319ebf450c96d5623fc99d26a`, from manifest `2026.11.09.003`.
- Independent existing **Draft #229**, head `2550668819d3ab229743de8c5d6ae14cc4806e16`, source Git blob `683a8e9eaa8e456bf7ddc2e18b469339177aa5ae`, contains 114 questions × 9 candidate replies. **This PR has NOT merged**; it has its own schema/consumer budget blockers. Do not treat its six additional answers per intent as published.
- Current main's first 30 `struct_t86_001`–`struct_t86_030` intents contain **3 registered answers each**. This work adds **five distinct synthetic, context-specific replies** for each of these *existing* intentions, 150 new replies total. No new canonical questions, no duplicate aliases.

## Exact accounting
- Published in main for the 30 selected intents before this change: **30 × 3 = 90** (not new).
- Additional candidates in older unmerged #229: **30 × 6 = 180** (not new here, not published).
- Newly authored here: **30 × 5 = 150** in one separate unregistered staging JSON.
- For these 30 intents, *if both independent PRs later merged and a compatible consumer representation existed*, the potential would be **14/100**, 86 missing per intent, 2,580 remaining. **Current staging independently contains 5/100 new proposed replies per intent**; published main remains 3/100. No set is 100/100 and none is consumer-enabled.
- Source intake: ambiguity of numeric separators, percentage-point comparisons, absent denominators, rounded measurements, leading zeros, hierarchical totals, road pay, partial minima, unit conversions, ambiguous dates, time zones, cropped screenshots, unlabeled graphs, multirow table headers, unexplained totals, missing values, median, unique participants, speed, monthly aggregation, exchange rates, taxes, successive discounts, length-vs-area, interval boundaries, absent-vs-zero, negative signs in OCR, sorting codes, numerical precision and correlation.
- Every entry has a stable original canonical intent ID, individual new response ID, exact situational note, read-only/direct-address scope, no sanctions and no private data. Uncertain input is explicitly handled by asking for evidence rather than assuming unsupported consumer capabilities.
- In-process connected-GitHub preflight: **150/150 distinct normalized responses and contextual notes**, 0 exact repeats against the full 1026-response head of Draft #229, no pair with Jaccard ≥ 0.68 (maximum 0.409 for comparison against that Draft). This is a lexical—not complete editorial semantic—screen.
- Package `staging/ru/structured_information_20261111_delta_a.json` has `consumer_registered=false`; registered pack, manifest hash, existing consumer caches, private ImPULS repository and BotHost remain unchanged.

## Tests and merge gates
- New read-only exact-head unittest `scripts/test_structured_context_20261111.py` checks source SHA+Git blob, counts, IDs, scope and privacy, exact duplicate comparison with registered packs, and lexical overlap. CI `.github/workflows/structured-context-20261111.yml` checks out actual PR head SHA with `persist-credentials: false`, runs `scripts/validate_pack.py` and the new tests.
- Before merge: verify fresh PR/head+base SHA, quality exact-head CI (including this special workflow), editorial quality, and all relevant conflicts. Use `expected_head_sha`; after merge verify actual post-main SHA CI. Do not bypass required checks or run paid workflows.
- **No staged reply implies live-bot delivery**. #229 remains an independent unresolved Draft. Its 9-variant ceiling requires future consumer-compatible selection/representation, not cloning canonical questions.
- Next: continue these same IDs only if genuine uncovered contexts remain; distribute effort to different incomplete practical intents, and do not count the new 150 twice.
