# T504 — practical answers across ten T503 intents (2026-11-09)

Extension of [PR #564](https://github.com/Treninem/Bot-Knowledge/pull/564), not a duplicate PR. Adds **100 newly authored context-specific Russian replies**, ten per stable intent, all synthetic and read-only. Source dialogue actual SHA-256 `3e63012f2823ea1896e9d9612f68f19a3cf2fe6bbf2c8296fc98ac29fb18a024` and blob `b881d145f634b6104c8538fef708d45162ef3125` are unchanged. This staged content is **not registered for consumers**.

| Canonical intent | Previously staged T503 | Added T504 | Total staged | Remaining to 100 |
|---|---:|---:|---:|---:|
| `verify_numeric_context` | 10 | 10 | 20 | 80 |
| `interpret_relative_time` | 10 | 10 | 20 | 80 |
| `conditional_steps` | 10 | 10 | 20 | 80 |
| `safe_bug_report` | 10 | 10 | 20 | 80 |
| `fact_vs_guess` | 10 | 10 | 20 | 80 |
| `responsibility_boundary` | 10 | 10 | 20 | 80 |
| `restore_missing_step` | 10 | 10 | 20 | 80 |
| `compare_incomplete_criteria` | 10 | 10 | 20 | 80 |
| `explain_known_limit` | 10 | 10 | 20 | 80 |
| `creative_revision_scope` | 10 | 10 | 20 | 80 |
| **Total** | **100** | **100** | **200** | **800** |

Each response has a scenario note, explicit audience, constraints, language and stable ID. Unlike synonym-swapping, scenarios include new numeric prerequisites, date interpretations, error isolation, trustworthy evidence, role boundaries, omitted instructions, decision tradeoffs, operational limits and scope-preserving revision. No personal chat excerpts, secrets, novel bot commands or action claims. Preliminary comparison with previous T503 entries per same intent: zero normalized exact matches, max local Jaccard 0.240. Full historical corpus comparison is performed by `scripts.test_practical_turns_t503` in CI; exact lexical screening does **not** prove semantic uniqueness.

The T504 regression checks source manifest SHA, stage lineage, per-intent totals, unique IDs/answers/conditions, audience, privacy and no sanctions. Exact-head CI and post-main gate apply. No manifest, current consumer, production cache or ImPULS changes.
