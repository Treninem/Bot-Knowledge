# T506 — practical RU candidate continuation (2026-11-09)

Base: exact merged [main `788a125410ef5bf2f5bcdad4c3b3310e2dfc56fd`](https://github.com/Treninem/Bot-Knowledge/commit/788a125410ef5bf2f5bcdad4c3b3310e2dfc56fd), after [PR #565](https://github.com/Treninem/Bot-Knowledge/pull/565). Do not double-count T503–T505.

**160 newly authored, synthetic Russian contextual replies** for eight existing stable intent IDs. Two 50/100 sets completed to 100/100; six 50/100 sets raised to 60/100. No new canonical questions; eight existing intents processed. Source file, registered manifest and consumers are unchanged.

| Stable intent | Before T506 | New | Total candidate replies | Remaining |
|---|---:|---:|---:|---:|
| `conditional_steps` | 50 | 50 | 100/100 | 0 |
| `safe_bug_report` | 50 | 50 | 100/100 | 0 |
| `fact_vs_guess` | 50 | 10 | 60/100 | 40 |
| `responsibility_boundary` | 50 | 10 | 60/100 | 40 |
| `restore_missing_step` | 50 | 10 | 60/100 | 40 |
| `compare_incomplete_criteria` | 50 | 10 | 60/100 | 40 |
| `explain_known_limit` | 50 | 10 | 60/100 | 40 |
| `creative_revision_scope` | 50 | 10 | 60/100 | 40 |
| **Total these 8** | **400** | **160** | **560** | **240** |

Together with the first two completed T505 intents, all ten have **760 staged candidates**, four sets at 100/100, six at 60/100 (240 remaining). Previous stages T503, T504 and T505 are already in main. These 760 are unregistered candidate counts, **not runtime bot functionality**.

All new entries carry a unique ID, context note, `ru`, `all_ai_bots`, direct-address applicability and explicit read-only/no-sanctions guard. Manual examples cover conditional changes, reversible workflows, reproducible bug reports, evidence uncertainty, permissions, procedures, comparisons, capability limits, and tightly scoped editing. No real chats, identities, secrets or unauthorized bot commands.

Source `packs/ru/dialogue.json` remains on manifest SHA-256 `3e63012f2823ea1896e9d9612f68f19a3cf2fe6bbf2c8296fc98ac29fb18a024` (Git blob `b881d145f634b6104c8538fef708d45162ef3125`). Stage T506 is **not registered** and does not mutate production cache. Initial JS preflight against all three prior stages: 160 unique normalized answers, 160 context notes, zero exact duplicates, max within-intent token Jaccard 0.286; semantic uniqueness still requires review. Python validator and exact-head CI are separate publication gates.

Next: finish `fact_vs_guess` from 60/100, then continue other five 60/100 intents without wasting cycles reauthoring existing questions.
