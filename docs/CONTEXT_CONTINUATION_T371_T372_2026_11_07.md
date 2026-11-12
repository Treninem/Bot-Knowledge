# T371/T372 — 92 original context-specific Russian answers (2026-11-07)

Parent main: `35d3296de495e0c0ab2a2885510f7e1c621e51da` (PR #411, catalog through T369/T370). This is a **new independent proposed batch**. No prior replies are counted as new.

| Intent family | Stable intents | Earlier registered | Earlier staged | New candidates | New per intent | Total per intent | Remaining |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Colloquial meaning | 22 | 198 | 1694 | **44** | 2 | **88/100** | 264 |
| Practical help & recovery | 24 | 216 | 1824 | **48** | 2 | **87/100** | 312 |
| Total | **46** | **414** | **3518** | **92** | — | **4024/4600** | **576** |

All 46 intents remain partially filled; no new 100/100 group. Each item has a stable ID and a distinct synthetic situation; examples include consent versus completed action, scheduling, access limitations, staged diagnostics, safe rollback, privacy-safe error reports and explicit refusal of unverified facts. This is not a blind synonym generator. All examples are original, generic, non-operational and intended for read-only consumption only, after confirmed direct addressing and explicit consumer permission.

- Source packages: `packs/ru/colloquial_ru_pragmatics_qa.json` and `packs/ru/practical_recovery_qa.json`; source SHA-256 pinned from `manifest.json` version `2026.11.07.001`.
- Immediate parents: `staging/ru/colloquial_t369_context_pool.json` Git blob `3ebc7986147a63ae8f80ec63c19a6da22e24a7e9`; `staging/ru/practical_t370_context_pool.json` Git blob `cf6d7aa91df376d0eef0717a23c224f45bfabd59`.
- Validator: `scripts/context_t371_t372.py` checks all prior stage ancestry, immutable source hashes, IDs, normalized duplicates, context notes, PII patterns and read-only opt-in. Tests: `scripts/test_context_t371_t372.py` check safe selection, denials, lexical overlap and pin tampering.
- Run `python scripts/validate_pack.py`, `python -m unittest scripts.test_context_t371_t372 -q`, and `python -m scripts.context_t371_t372`. CI must use actual current PR head SHA and post-merge main SHA. No paid manual workflow dispatch.
- Automated lexical similarity tests do **not** prove semantic originality for every historical reply. Manual review of the new contextual distinctions remains part of QA.

No manifest change, registered pack modification, cache invalidation or live consumer activation: all 92 answers are **staging-only**. No ImPULS source, tokens, private conversation, moderation action, external write or deployment. The `ReviewedStageCatalog` index still stops at T369/T370 (3518 staged); catalog refresh, consumer compatibility and live integration are separately gated.
