# T170 — contextual recovery: 24 intents × 3 further replies (2026-11-05)

Base: `main b580c71c2b823133fae52dbb4ff949b91a1234b1`. Read-only registered source: `packs/ru/practical_recovery_qa.json`, Git blob `21bf261970d1bdcf0f9fb8fb3383772b86b2dc2f`, manifest SHA-256 `be8ae1408cf42816adc3f8ba818b3f004318617ba2e878e72edd85cf7eb4954e`; current `knowledge_version` `2026.11.05.036` (no change).

## Exact progress and intent counts

Prior T168: 24 stable intents × (9 registered + 3 staged) = **288** total candidates (72 staged). T170 adds **72 new contextual replies** (3 for each of those same 24 questions); **0** rejected by preliminary normalized/lexical screen. Result: 24×(9+6) = **360**, of which **216 registered** and **144 staged**. Every one of the 24 intents **12/100 → 15/100**, remaining **85/100** each (**2040 missing overall**); **0 newly completed 100/100**, **24 partial**. No new canonical questions; no old replies removed.

Contexts: symptom identification, selective failures, least-destructive checks, privacy on screenshots and group chats, unverifiable administrative claims, restoration and reversibility, separating queued/accepted/completed states, reporting bugs, group mention discipline, factual disagreement and stopping advice. All 72 entries are original synthetic RU text, with stable `_t170_` IDs, `context_note`, `avoid`, audience `all_ai_bots`, `read_only=true`, scope `direct/private/group_addressed`. No private ImPULS implementation copied.

Staging file `staging/ru/recovery_t168_context_pool.json` (not in manifest), exact UTF-8 length **131841 bytes**, SHA-256 `0508a6c7df3b0a68da82aae33d953184a2f373999e0e597b9dbdf10eceb62369`, Git blob `3b1551933ada91d32ff8fc65b7b0dae542ce4dab`. Preliminary JavaScript: **144/144 staged replies normalized-unique**, 0 new near matches ≥ 0.78 token Jaccard versus preexisting staging, maximum 0.333. Does not prove exhaustive semantic originality or cross-catalog absence of close paraphrases.

Updated existing `scripts/test_practical_recovery_t158.py` checks all 216 registered + 144 staged texts and data scope, stable IDs, source SHA, cross-pack exact duplicates, no PII patterns. Real Python and GitHub exact-head CI **must be checked before marking ready/merging**, followed by current-main and post-main verification. Staging variants are **not consumer-ready** without a new compatible selector; `qa.v1` permits at most 1+8 strings per canonical record. Registered manifest, 41 packs and cache **not changed**. No changes to private ImPULS, BotHost, user payments or production bots.

Next priority: continue recovery at 15/100, work independently on 31 boundary intents at 12/100, and validate context selection without cloning canonical questions.
