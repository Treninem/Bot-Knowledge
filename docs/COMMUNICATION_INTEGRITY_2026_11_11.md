# RU communication integrity, Stage A — 2026-11-11

This is **staging-only**, not a deployed assistant feature. It continues systematic RU dialogue-skill development after the prior support-triage series (PR #616).

## New canonical intents and strict scope

| Intent suffix | Canonical question | Starting | New | Unique staged | Still needed |
|---|---|---:|---:|---:|---:|
| quote_integrity | Как цитировать часть сообщения, не искажая смысл? | 0 | 12 | 12/100 | 88 |
| speaker_attribution | Как пересказать обсуждение, не перепутав авторов мнений? | 0 | 12 | 12/100 | 88 |
| translation_register | Как перевести сообщение, сохранив его вежливость и тон? | 0 | 12 | 12/100 | 88 |
| incident_report | Как описать сбой для поддержки без лишних данных? | 0 | 12 | 12/100 | 88 |
| decision_record | Как записать итог обсуждения, отделив решения от предложений? | 0 | 12 | 12/100 | 88 |
| correction_ack | Как принять исправление собеседника и не повторить прежнюю ошибку? | 0 | 12 | 12/100 | 88 |
| polite_request | Как попросить о действии без давления и приказного тона? | 0 | 12 | 12/100 | 88 |
| topic_return | Как вернуться к исходному вопросу после долгого отступления? | 0 | 12 | 12/100 | 88 |
| uncertain_claim | Как обсуждать непроверенную версию, не превращая её в факт? | 0 | 12 | 12/100 | 88 |
| forward_consent | Как вежливо спросить разрешение переслать чужое сообщение? | 0 | 12 | 12/100 | 88 |

**Verified Stage A inventory:** 10 canonical intents, 120 new synthetic context-bound replies, 0 finished 100/100, 10 partial 12/100, 880 remaining. No intentional formulaic synonym inflation. Every response has its own use condition and disallows automated sanctions or actions. Editorial review is still required for semantic overlap and situational appropriateness. No consumer claims, ImPULS/private-code excerpts or private conversation data.

Stable IDs: `comm20261111_<intent>_<01..12>`; subsequent stage must begin at `13` for these same intents, not reset them.

## Source, lineage, validation

- Initial main: `9ad8a748dd1df873920f68334ec5430d71115b7c` (post-merge PR #616).
- Source registered pack: `packs/ru/social_dialogues.json`, manifest `2026.11.09.003`, actual source SHA-256 `0cfedc133354a69522fecc3cda6bc21533c66005f0dc207050075f787dc977a8`, source Git blob `d56ff304da7165bd63c328f3220a1f6d3d26e3ab`.
- New data: `staging/ru/communication_integrity_20261111_context_pool.json`, `consumer_registered=false`; manifest/registered pack/cache unchanged.
- Before publication, local JavaScript validation: 120/120 unique IDs, normalized texts and context notes, no exact duplicates against 1,920 responses across ten adjacent staging pools; max cross-pool token-Jaccard **0.28**, zero >=0.80. No claim of exhaustive full-corpus semantic uniqueness.
- Python suite: `python -m unittest scripts.test_communication_integrity_20261111 -v` (source SHA, manifest lineage, privacy/scope metadata, counts, lexical duplicates). The workflow pins the real PR head and uses read-only permissions. CI result must be checked for the final head after every edit; do not count an earlier green run.
- User-authorized maintainer can merge only after full exact-head CI and compatibility checks; post-main CI on the merge SHA must be verified separately. Public staging is not live learning.

**Next:** after green exact-head and post-main checks, fill indices 13 onward across multiple intents, compare meanings against other related packs/PRs, and only register a vetted compatible package in a separately tested consumer-aware change. Do not alter ImPULS or launch a live deployment.
