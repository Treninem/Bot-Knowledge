# Cross-stage response coverage repair T502 — 2026-11-09

Addresses [issue #558](https://github.com/Treninem/Bot-Knowledge/issues/558) without changing the already merged stage files or consumers. Prior local T493/T496/T497/T498 reports counted only `dialogue.json.reactions`, omitting 64 registered scoped responses and T486–T488 stages. This made completed stable canonical intents appear unfinished.

The new **read-only** `scripts/coverage_intent_report.py` counts the actual registered legacy and `scoped_repair_reactions` responses, then stage `entries[].replies` by the same stable `intent_id`, limited to `scoped_repair_t*` and `social_clarity_t*`. It verifies the registered pack's actual SHA-256 against manifest, stage source SHA, unpublished staging status and unique IDs. It reports counts, normalized unique texts, excess over target and each stage's contribution separately; it never rewrites stages, updates the manifest or changes consumer behavior. Exact lexical uniqueness is not equivalent to semantic quality.

## Verified structural inventory of merged stages at base main `c8a0712e2a0620bad8b9cc8eb31c6a7cab018a61`

| Intent | Registered | T486–T488 | T493 | T496+T497+T498 | Total candidate records | Above 100 |
|---|---:|---:|---:|---:|---:|---:|
| `clarify_previous` | 18 | 82 | 25 | 73 | 198 | 98 |
| `disagreement` | 17 | 83 | 25 | 74 | 199 | 99 |
| `unknown_fact` | 17 | 83 | 25 | 74 | 199 | 99 |
| `ambiguous` | 17 | 83 | 25 | 74 | 199 | 99 |
| **Итого** | **69** | **331** | **100** | **295** | **795** | **395** |

These are **candidate records**, not 795 verified semantic variations or 795 delivered consumer replies. T493's 100 entries were genuinely new candidate records but finished **zero** additional sets, because all four were already at 100/100 in T488. T496–T498 are extra candidates above target. Preserve them for later semantic curation; stop using their local `remaining` as a global count. There is no basis to generate more replies for these four until curation/registration work is done.

CLI: `python scripts/coverage_intent_report.py`; regression: `python -m unittest scripts.test_coverage_intent_report -q`. Separate minimal read-only workflow requires exact checked-out head; local Python and full CI must be reported by actual result. No ImPULS, live bot, manifest, token, privacy data, active cache or enforcement change. Other dialogue intent families are deliberately out of this report's limited scope; do **not** interpret it as all-intent global coverage.

## Reconciliation checkpoint — 2026-11-09

After T501 PR #562 merged on `c87308b8c09bd7738e83674f0a4eff92ddd6e720`, this independent T502 branch was fast-forwarded by a two-parent commit preserving the original T502 head and exact new main tree. Paths T501/T502 do not overlap. All coverage source and stage content remains unchanged; full exact-head CI must be rerun for this new head before merging.
