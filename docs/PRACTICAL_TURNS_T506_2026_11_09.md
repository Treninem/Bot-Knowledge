# T506 — 400 practical Russian replies; all ten staged sets at 100/100 (2026-11-09)

Based on exact merged main `788a125410ef5bf2f5bcdad4c3b3310e2dfc56fd` ([#565](https://github.com/Treninem/Bot-Knowledge/pull/565)). **400 newly authored synthetic, context-specific replies** in this PR, for eight existing stable intents. The two other intents were already complete before T506 and are not counted as newly completed here. **T503–T506 cumulative: 1000 candidate replies across 10 stable intents, all 100/100.**

| Canonical intent | T503–T505 baseline | New T506 | Total staged | Remaining |
|---|---:|---:|---:|---:|
| `verify_numeric_context` | 100 | 0 | 100/100 | 0 |
| `interpret_relative_time` | 100 | 0 | 100/100 | 0 |
| `conditional_steps` | 50 | 50 | 100/100 | 0 |
| `safe_bug_report` | 50 | 50 | 100/100 | 0 |
| `fact_vs_guess` | 50 | 50 | 100/100 | 0 |
| `responsibility_boundary` | 50 | 50 | 100/100 | 0 |
| `restore_missing_step` | 50 | 50 | 100/100 | 0 |
| `compare_incomplete_criteria` | 50 | 50 | 100/100 | 0 |
| `explain_known_limit` | 50 | 50 | 100/100 | 0 |
| `creative_revision_scope` | 50 | 50 | 100/100 | 0 |
| **Total** | **600** | **400** | **1000** | **0** |

Examples cover reproducible technical failures, procedural conditions, contextual evidence, authority boundaries, omitted instructions, meaningful choice criteria, honest capability limits and creative revisions within strict user constraints. Each answer has a stable ID, `ru` label, `all_ai_bots` audience, direct-address and scenario applicability notes, explicit read-only/no-sanctions guard. They are **synthetic candidates only**. Completing 100 candidates per intent does not prove all are interchangeable, semantically different or live in any AI consumer.

## Git checkpoints and verification scope

- First saved stage checkpoint: [`670d790`](https://github.com/Treninem/Bot-Knowledge/commit/670d790dc57d79fd90c43510bcef516c2a57040e) with 160 new answers, completing `conditional_steps` and `safe_bug_report`; six others reached 60/100.
- Second preserved checkpoint: [`0490a76`](https://github.com/Treninem/Bot-Knowledge/commit/0490a76e7e6cba9e3c872a30aaadd3f829b0f2a2) with 240 more answers, completing all remaining six intents to 100/100.
- Preflight from actual source stages T503, T504, T505, plus the earlier T506 checkpoint: 400 normalized unique new answers, 400 distinct context notes, zero exact duplicates. Max observed within-intent token Jaccard during the first checkpoint 0.286, second checkpoint 0.375. **Lexical tests do not establish conceptual independence**; editorial review, Python tests and exact-head CI remain required.

Source `packs/ru/dialogue.json` remains manifest SHA-256 `3e63012f2823ea1896e9d9612f68f19a3cf2fe6bbf2c8296fc98ac29fb18a024`, source Git blob `b881d145f634b6104c8538fef708d45162ef3125`. No registered manifest change, no consumer integration, no live BotHost changes, no cache writes, no sanctions. The source remains frozen and can be consumed only through an independently verified, compatible publishing mechanism.

## Next work after successful merge

Complete exact-head and post-main checks. Then address the editorial meaning-based near-duplicate review and verified consumer registration separately, with explicit schema/audience compatibility and snapshot-size checks; adding more word substitutions to already-complete intents is not useful. For new intent families, first inventory existing staged candidates and consumer support so that none are counted twice.
