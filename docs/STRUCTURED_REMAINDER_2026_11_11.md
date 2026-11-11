# Structured information: independent continuation C–D — 2026-11-11

## Pinned source and scope

- Fresh main after merge of [#653](https://github.com/Treninem/Bot-Knowledge/pull/653): `1840c3a610f9af50e234e936550054af3fb44a19`.
- Canonical registered source: `packs/ru/structured_information_qa.json`, manifest SHA-256 `55b3f6126d36cd92687d005b7fedf5a11df9ee61cf453103accdf1f13c8498f0`, Git blob `8b3d596b5b50d3d319ebf450c96d5623fc99d26a`.
- Source manifest version `2026.11.09.003`. No registered packs or manifest changed. The new files are **staging only**, `consumer_registered=false`.
- Older independent [Draft #229](https://github.com/Treninem/Bot-Knowledge/pull/229), head `2550668819d3ab229743de8c5d6ae14cc4806e16`, proposes nine replies per intent but remains **unmerged and consumer/schema blocked**. Its additional six per intent do not count as published or new here.
- This branch is intentionally independent. No ImPULS modifications, live deployments, secrets or direct consumer writes.

## Exact incremental accounting (C + D)

| Stage | Stable existing intents | Newly written | Published source per intent | Staging after this stage | Missing to 100 before #229 |
|---|---:|---:|---:|---:|---:|
| C (`struct_t93_001`–`struct_t93_025`) | 25 | **75** | 3 | +3 per intent | 94 each |
| D (`struct_t88_022`–`struct_t88_025` and `struct_t90_001`–`struct_t90_025`) | 29 | **87** | 3 | +3 per intent | 94 each |
| **New in this independent PR** | **54** | **162** | **162 prior answers, not new** | **54 partial sets at 6/100 combined** | **5,076** |

- Staging C and D add **162 genuinely new situation-specific Russian response candidates** across **54 previously untouched canonical intentions**, three per intention; no canonical questions or aliases duplicated. All are still **partial**, 0 at 100/100.
- Earlier [merged #653](https://github.com/Treninem/Bot-Knowledge/pull/653) contributed A+B = 300 distinct unregistered staging answers for *another* 60 intentions; these are **not new in this PR**.
- Across all A–D there are **114 original canonical intents, 462 unique staged replies**, and 342 registered original replies. A–B 60 intentions have 8/100 from original+new staging (92 missing), and C–D 54 intentions have 6/100 (94 missing). All remain 100/100 incomplete. These are combined content inventories only, not proof of a supported consumer choice algorithm.
- Hypothetically if the six additional alternatives per intent in #229 became compatible and merged without collisions, C–D intentions would reach 12/100 (88 remaining), A–B would reach 14/100 (86 remaining). Do not assume that integration is possible or completed.
- **0 rejected from C–D** in the write preflight: 162 distinct normalized texts, distinct contextual notes, and no exact overlap with all 1,026 old Draft #229 answers; no token Jaccard >=0.68 versus that Draft or across retained A–D. This lexical screen does not replace human semantic review.
- Direct address and matching described situation are required; these are suggestions for wording, not commands to a consumer. No sanctions, private identifiers, real chats or asserted actions.

## Tests and release gates

- `scripts/test_structured_remainder_20261111.py` verifies registered source SHA-256 and Git blob, manifest registration constraints, complete stable 114-intent inventory over A–D, exact counts 150/150/75/87, normalized uniqueness and scope, privacy guardrails, no registered exact repeats and token overlap below the review limit.
- `.github/workflows/structured-remainder-20261111.yml` uses `contents: read`, checks out the exact PR head SHA, disables persisted credentials and runs registered-pack validation plus targeted tests. **Do not infer success before actual job completion**.
- Current branch PR must stay **Draft/BLOCKED** until full exact-head checks (including quality/validate), editorial review, main compatibility, and guarded merge with expected head SHA. After merge check post-main CI against actual SHA. No paid CI was manually dispatched.
- Source/manifest SHA and consumer cache keys stay unchanged because no registered payloads changed. These answers do **not** become available to running ImPULS/AuroraFox without a separately verified consumer integration.

## Next continuation

1. Complete and review actual exact-head CI, SHA and content checks, and verify post-main CI from #653 before merging another PR.
2. Preserve current staged counts precisely. Further enrich the 114 unchanged canonical intentions only with truly distinct contexts and avoid repeating A–D and #229.
3. Separately address the incompatible older #229 representation; do not merge it merely to improve coverage counts.
