# T503 — practical language boundaries, 9 November 2026

Ten **new** generic canonical intents across communication, rules, help, skills, setup and creative revision. 10 original Russian replies per intent, 100 newly authored records total. These are **context-specific candidates** requiring direct address and explicit scenario matching. All are read-only and portable to `all_ai_bots`; no ImPULS capability claims, sanctions, PII or private chat excerpts.

| Intent | Section | Before (stable ID) | Added | Candidate total | Remaining to 100 |
|---|---|---:|---:|---:|---:|
| `verify_numeric_context` | навыки | 0 | 10 | 10/100 | 90 |
| `interpret_relative_time` | общение | 0 | 10 | 10/100 | 90 |
| `conditional_steps` | помощь | 0 | 10 | 10/100 | 90 |
| `safe_bug_report` | настройка | 0 | 10 | 10/100 | 90 |
| `fact_vs_guess` | навыки | 0 | 10 | 10/100 | 90 |
| `responsibility_boundary` | правила | 0 | 10 | 10/100 | 90 |
| `restore_missing_step` | умение | 0 | 10 | 10/100 | 90 |
| `compare_incomplete_criteria` | помощь | 0 | 10 | 10/100 | 90 |
| `explain_known_limit` | настройка | 0 | 10 | 10/100 | 90 |
| `creative_revision_scope` | общение | 0 | 10 | 10/100 | 90 |
| **Total** | | **0** | **100** | **100/1000** | **900** |

Main at authoring time `c87308b8c09bd7738e83674f0a4eff92ddd6e720`. Source `packs/ru/dialogue.json` actual SHA-256 `3e63012f2823ea1896e9d9612f68f19a3cf2fe6bbf2c8296fc98ac29fb18a024`, Git blob `b881d145f634b6104c8538fef708d45162ef3125`. Registered manifest and consumers unchanged. The stable IDs were searched on the main branch before creation; existing relevant semantic domains are not assumed empty. This remains staged and not a consumer-visible ability.

Preflight across this new batch: 100 different IDs, 100 distinct normalized replies, 100 distinct context notes, zero same-text matches in a local sample of 310 existing records drawn from the registered dialogue source and three latest staged families; max sampled token Jaccard 0.261. A standalone Python regression additionally examines *all* JSON files in `packs/ru` and `staging/ru` at CI checkout. Lexical screening is not proof against all semantic near-duplicates: review by context before registration.

Exact-head CI is required before merge; post-main CI must run on the actual merge SHA. No live bots, ImPULS files, spending, secrets or production caches changed. Next: curation and further contextual completion of these ten partial sets, starting with `verify_numeric_context` and `interpret_relative_time`.
