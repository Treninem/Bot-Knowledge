# RU communication integrity, Stages A+B — 2026-11-11

This is **staging-only**, not a deployed assistant feature. It continues systematic RU dialogue-skill development after the prior support-triage series (PR #616).

## New canonical intents and strict scope

| Intent suffix | Canonical question | Starting | New A+B | Unique staged | Still needed |
|---|---|---:|---:|---:|---:|
| quote_integrity | Как цитировать часть сообщения, не искажая смысл? | 0 | 22 | 22/100 | 78 |
| speaker_attribution | Как пересказать обсуждение, не перепутав авторов мнений? | 0 | 22 | 22/100 | 78 |
| translation_register | Как перевести сообщение, сохранив его вежливость и тон? | 0 | 22 | 22/100 | 78 |
| incident_report | Как описать сбой для поддержки без лишних данных? | 0 | 22 | 22/100 | 78 |
| decision_record | Как записать итог обсуждения, отделив решения от предложений? | 0 | 22 | 22/100 | 78 |
| correction_ack | Как принять исправление собеседника и не повторить прежнюю ошибку? | 0 | 22 | 22/100 | 78 |
| polite_request | Как попросить о действии без давления и приказного тона? | 0 | 22 | 22/100 | 78 |
| topic_return | Как вернуться к исходному вопросу после долгого отступления? | 0 | 22 | 22/100 | 78 |
| uncertain_claim | Как обсуждать непроверенную версию, не превращая её в факт? | 0 | 22 | 22/100 | 78 |
| forward_consent | Как вежливо спросить разрешение переслать чужое сообщение? | 0 | 22 | 22/100 | 78 |

**Verified staged inventory A+B:** 10 canonical intents, 220 new synthetic context-bound replies (A: 120, B: 100), 0 finished 100/100, 10 partial 22/100, 780 remaining. No intentional formulaic synonym inflation. Every response has its own use condition and disallows automated sanctions or actions. Editorial review is still required for semantic overlap and situational appropriateness. No consumer claims, ImPULS/private-code excerpts or private conversation data.

Stable IDs: `comm20261111_<intent>_<01..22>`; subsequent stage must begin at `23` for these same intents, not reset them.

## Source, lineage, validation

- Initial main: `9ad8a748dd1df873920f68334ec5430d71115b7c` (post-merge PR #616).
- Source registered pack: `packs/ru/social_dialogues.json`, manifest `2026.11.09.003`, actual source SHA-256 `0cfedc133354a69522fecc3cda6bc21533c66005f0dc207050075f787dc977a8`, source Git blob `d56ff304da7165bd63c328f3220a1f6d3d26e3ab`.
- New data: `staging/ru/communication_integrity_20261111_context_pool.json` and `staging/ru/communication_integrity_20261111_context_delta_b.json`, `consumer_registered=false`; manifest/registered pack/cache unchanged.
- Before publication, local JavaScript validation: 220/220 unique IDs, normalized texts and context notes, no exact duplicates against 1,920 responses across ten adjacent staging pools; max observed cross-pool/earlier-stage token-Jaccard **0.3334**, zero >=0.80. No claim of exhaustive full-corpus semantic uniqueness.
- Python suite: `python -m unittest scripts.test_communication_integrity_20261111 -v` (source SHA, manifest lineage, privacy/scope metadata, counts, lexical duplicates). The workflow pins the real PR head and uses read-only permissions. CI result must be checked for the final head after every edit; do not count an earlier green run.
- User-authorized maintainer can merge only after full exact-head CI and compatibility checks; post-main CI on the merge SHA must be verified separately. Public staging is not live learning.

**Next:** after green exact-head and post-main checks, fill indices 13 onward across multiple intents, compare meanings against other related packs/PRs, and only register a vetted compatible package in a separately tested consumer-aware change. Do not alter ImPULS or launch a live deployment.

## Stage B checkpoint (2026-11-11)

- A Git blob: `c11b260e24c0571b342e3371f1107194e5063a22`; B Git blob: `53029246981df5bc58afd8099ff348ca72acc675`. Parent identity is checked by SHA-1 over the actual Git blob bytes, not via string formatting.
- B contributes 100 new responses across the same ten stable intents, indices 13–22. For every intent: old 12 + new 10 = **22/100**, remaining **78**. Cross-stage totals: 220 unique accepted staging candidates; 780 remaining. There are no completed 100/100 sets.
- 220/220 unique normalized answers, response IDs, and context notes; zero exact duplicates across A+B; against 1,920 related existing responses, no exact repeats. Highest observed lexical token Jaccard for B against A+related was **0.3333**. These are programmatic checks, not semantic editorial proof.
- Data, Python tests, read-only workflow and checkpoint document are the only changed file categories. A and B remain **unregistered staging**. Consumer integration, live response quality, and user-specific applicability have **not** been tested.
- Next: start C at index 23 for every intent after current PR head tests and review; prioritize different contexts instead of paraphrased fillers. Do not count A+B replies as new next run.
