# T93: data interpretation and numeric nuance, 04 November 2026

Starting main `7e77674d356692841d898c00cc1dbd99cf1f9628`, owner scope `docs/OWNER_AUTOMATION_SCOPE_2026_11_02.md`. Existing `structured_information_qa.json` grows 89 → 114: +25 canonical questions (`struct_t93_001..025`), +50 aliases, +75 original contextual answers. New 25 intents are **3/100 partial**, 97 outstanding only if meaningfully distinct contexts can be found. Existing 119 complete reply-catalog intents untouched.

Topics: zero baseline percentages, compounding, balances vs flows, overnight shifts, buying power, unit prices, sample limitations, confidence vs predictive uncertainty, p-value interpretation, measurement outliers, dual-axis and truncated graphs, ordinal scales, seasonal variation, timestamps, repeated samples and join duplication. Synthetic, read-only `all_ai_bots` RU skills; no private data, actions, sanctions or claims of live-bot integration. Pack SHA256 `55b3f6126d36cd92687d005b7fedf5a11df9ee61cf453103accdf1f13c8498f0`, manifest `2026.11.04.026`.

Regression changes: T86 size check 114; T90 recognizes its stable original T90 IDs rather than assuming the last 25 rows, preserving old coverage; new T93 full SHA/context/cross-QA duplicate/indexed lookup test. Before merging require actual exact-head successful CI, fresh main and post-main check.
