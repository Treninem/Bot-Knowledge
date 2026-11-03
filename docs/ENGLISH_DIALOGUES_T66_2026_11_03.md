# T66 — original English conversational and meaning examples

Stacked on T65 PR #188 exact head `ab91724c9a4790a79e4c067a46d3b6566a52733f` (the parent branch should merge first). Manifest `2026.11.03.151` → `2026.11.03.152`.
Initial English cases: **872**; newly accepted: **61**; total: **933**. Rejected normalized duplicates: **0**. Distinct situations across conversation, support, colloquial idioms, sarcasm, reference/context, rules, account deception and original fiction. Every entry has a natural response, Russian meaning, specific usage exclusion and audience `all_ai_bots`.

This is not a set of 100 variants for a single question. No new completed or partial 100/100 set in reply_catalog; existing 119 completed sets unchanged. No platform-specific commands, private messages or automatic sanctions.

Pack SHA-256: `c80fa8894bc8e4efe684ccefb2bb8bf513f9f38235489a5bde0c9f938decd6b3`, size **499585** UTF-8 bytes; manifest SHA-256: `5f7aec1e188ddc0776362c30189e5a63c6d262c939dac1a1677abbf31dbd1e63`. Local reading uses version+hash invalidation, live consumers untouched.
Validations: normalized input and reply uniqueness across all 933 cases, unique IDs, privacy, scope, syntax, reproducible SHA; new regression `python -m scripts.test_english_dialogue_t66`. **BLOCKED until exact-head CI** and base integration. After parent merge, retarget PR to main, repeat base+head check, and gate post-main success.
