# RU communication integrity, Stages A+B+C — 2026-11-11

This is **staging-only**, not a deployed assistant feature. It continues systematic RU dialogue-skill development after the prior support-triage series (PR #616).

## New canonical intents and strict scope

| Intent suffix | Canonical question | Starting | New A+B+C | Unique staged | Still needed |
|---|---|---:|---:|---:|---:|
| quote_integrity | Как цитировать часть сообщения, не искажая смысл? | 0 | 32 | 32/100 | 68 |
| speaker_attribution | Как пересказать обсуждение, не перепутав авторов мнений? | 0 | 32 | 32/100 | 68 |
| translation_register | Как перевести сообщение, сохранив его вежливость и тон? | 0 | 32 | 32/100 | 68 |
| incident_report | Как описать сбой для поддержки без лишних данных? | 0 | 32 | 32/100 | 68 |
| decision_record | Как записать итог обсуждения, отделив решения от предложений? | 0 | 32 | 32/100 | 68 |
| correction_ack | Как принять исправление собеседника и не повторить прежнюю ошибку? | 0 | 32 | 32/100 | 68 |
| polite_request | Как попросить о действии без давления и приказного тона? | 0 | 32 | 32/100 | 68 |
| topic_return | Как вернуться к исходному вопросу после долгого отступления? | 0 | 32 | 32/100 | 68 |
| uncertain_claim | Как обсуждать непроверенную версию, не превращая её в факт? | 0 | 32 | 32/100 | 68 |
| forward_consent | Как вежливо спросить разрешение переслать чужое сообщение? | 0 | 32 | 32/100 | 68 |

**Verified staged inventory A+B+C:** 10 canonical intents, 320 new synthetic context-bound replies (A: 120, B: 100, C: 100), 0 finished 100/100, 10 partial 32/100, 680 remaining. No intentional formulaic synonym inflation. Every response has its own use condition and disallows automated sanctions or actions. Editorial review is still required for semantic overlap and situational appropriateness. No consumer claims, ImPULS/private-code excerpts or private conversation data.

Stable IDs: `comm20261111_<intent>_<01..32>`; subsequent stage must begin at `33` for these same intents, not reset them.

## Source, lineage, validation

- Initial main: `9ad8a748dd1df873920f68334ec5430d71115b7c` (post-merge PR #616).
- Source registered pack: `packs/ru/social_dialogues.json`, manifest `2026.11.09.003`, actual source SHA-256 `0cfedc133354a69522fecc3cda6bc21533c66005f0dc207050075f787dc977a8`, source Git blob `d56ff304da7165bd63c328f3220a1f6d3d26e3ab`.
- New data: `staging/ru/communication_integrity_20261111_context_pool.json` and `staging/ru/communication_integrity_20261111_context_delta_b.json`, `consumer_registered=false`; manifest/registered pack/cache unchanged.
- Before publication, local JavaScript validation: 320/320 unique IDs, normalized texts and context notes, no exact duplicates against 1,920 responses across ten adjacent staging pools; max observed cross-pool/earlier-stage token-Jaccard **0.3334**, zero >=0.80. No claim of exhaustive full-corpus semantic uniqueness.
- Python suite: `python -m unittest scripts.test_communication_integrity_20261111 -v` (source SHA, manifest lineage, privacy/scope metadata, counts, lexical duplicates). The workflow pins the real PR head and uses read-only permissions. CI result must be checked for the final head after every edit; do not count an earlier green run.
- User-authorized maintainer can merge only after full exact-head CI and compatibility checks; post-main CI on the merge SHA must be verified separately. Public staging is not live learning.

**Next:** after green exact-head and post-main checks, fill indices 13 onward across multiple intents, compare meanings against other related packs/PRs, and only register a vetted compatible package in a separately tested consumer-aware change. Do not alter ImPULS or launch a live deployment.

## Stage B checkpoint (2026-11-11)

- A Git blob: `c11b260e24c0571b342e3371f1107194e5063a22`; B Git blob: `53029246981df5bc58afd8099ff348ca72acc675`. Parent identity is checked by SHA-1 over the actual Git blob bytes, not via string formatting.
- B contributes 100 new responses across the same ten stable intents, indices 13–22. For every intent: old 12 + new 10 = **22/100**, remaining **78**. Cross-stage totals: 220 unique accepted staging candidates; 780 remaining. There are no completed 100/100 sets.
- 220/220 unique normalized answers, response IDs, and context notes; zero exact duplicates across A+B; against 1,920 related existing responses, no exact repeats. Highest observed lexical token Jaccard for B against A+related was **0.3333**. These are programmatic checks, not semantic editorial proof.
- Data, Python tests, read-only workflow and checkpoint document are the only changed file categories. A and B remain **unregistered staging**. Consumer integration, live response quality, and user-specific applicability have **not** been tested.
- Next: start C at index 23 for every intent after current PR head tests and review; prioritize different contexts instead of paraphrased fillers. Do not count A+B replies as new next run.

## Stage C checkpoint (2026-11-11)

- Stage C file `staging/ru/communication_integrity_20261111_context_delta_c.json`: Git blob `8d63c28f05760b09a934953fade4b9314022f904`; parent B blob `53029246981df5bc58afd8099ff348ca72acc675`.
- C is +100 unique synthetic RU replies, 10 per existing intent, IDs 23–32. A+B+C: **320/1000** total candidate responses, **10 partial intentions 32/100**; **68 missing per intent**. Only staged data; no registered consumer release.
- Rechecked 320 IDs, 320 normalized responses and 320 normalized context notes, with zero repeats. All new C replies compared with 1920 other relevant replies plus A+B: no exact repeats, highest token Jaccard **0.2728**, no pairs >= 0.8. This lexical check does not prove full semantic independence.
- The Python unittest now verifies all 3 stages, exact Git parent chain, existing source manifest checksum, unique counts and read-only scopes. CI exact head and post-main results must be rechecked after the last commit, and the dataset remains blocked from release/merging until they pass.
- Next unfilled reply number is **33** per intent. Do not count previous 320 as newly written on future runs.

## Stage D checkpoint — 11 November 2026

- Exactly **120 new** synthetic Russian contextual replies across the **same ten stable intents**, suffixes `33–44` per intent. Previous 320 A–C candidates remain counted only once; cumulative **440/1000**, ten partial sets **44/100**, **56 missing per intent / 560 total**, zero 100/100.
- Unregistered `staging/ru/communication_integrity_20261111_context_delta_d.json`, parent C blob `8d63c28f05760b09a934953fade4b9314022f904`, source manifest unchanged. Each candidate has distinct context condition, `all_ai_bots`, direct and read-only scopes, no sanctions, no actual chat data.
- Pre-commit JS on connector-read original: 440/440 unique IDs, normalized responses and notes; zero exact duplicates; max lexical Jaccard against the existing A–C and other new D candidates 0.3333 (<0.80). Editorial semantic review is separate from lexical checks.
- Python suite expanded to include D; exact-head CI and post-main CI must be checked on their final actual SHAs. No changes to ImPULS, consumers, registered packs, manifest or live cache.
- Next index for each intent: **45**; complete pending quality review before merge.

## Stage E checkpoint — 11 November 2026

- Starting point: merged PR #617 at `85f684592c0aa80c336725acba460ecfc08c7b2f`; A–D already contained **440** candidates. Stage E adds **120 NEW** original RU answers (12 per existing canonical intent), suffixes **45–56**; cumulative **560/1000**, ten partial sets **56/100**, **44 remaining per intent / 440 total**, no 100/100 set claimed.
- New file `staging/ru/communication_integrity_20261111_context_delta_e.json` is unregistered staging, parent D Git blob `9662c8ec779f5daf021f739fa4ddcc314d8bd14c`. All replies are synthetic, apply only to their explicit context, require a direct request, are read-only, and do not authorize sanctions or transferring private chat data.
- JS pre-commit normalization found zero exact duplicate texts, IDs or context notes against A–D; observed max within A–E token-Jaccard **0.3500** (not a substitute for semantic editorial review). The Python suite is expanded to E, with source SHA-256, ancestry, manifest and related-pool checks. Actual CI for final head must pass before merge, followed by post-main CI.
- The manifest and registered packs remain unchanged; consumer deployment and ImPULS were not touched. Next suffix is **57** for every intent.

## Stage F checkpoint — 11 November 2026

- F adds **100 NEW** hand-authored contextual replies, 10 per existing intent, suffixes **57–66**. E already held 560 across A–E. Cumulative **660/1000** candidates, 10 partial sets at **66/100**, remaining 34 per intent / 340 total, 0 complete.
- Staging `staging/ru/communication_integrity_20261111_context_delta_f.json` has parent E blob `62417965f34e3608ec850d76ee14b7b53e4d4818` and explicit context conditions. No registered pack, cache, private chats, consumer capabilities or ImPULS modifications.
- JS exact normalization finds no repeated IDs/texts/context notes against A–E and the 100 new F candidates; maximum observed A–F token Jaccard **0.3750**, no pair >=0.80. Semantic editor review remains required. Python unittest expanded to include stage F; exact-head and post-main checks remain gates.
- Next response suffix **67** per intent; do not recount earlier 660 as newly authored.

## Stage G checkpoint — 11 November 2026

- G adds **100 NEW** original synthetic RU contextual answers, suffixes **67–76** for ten existing intent IDs; prior A–F 660 kept intact. Cumulative **760/1000**, ten partial **76/100**, **24 missing per intent** / 240 remaining, 0 sets marked complete.
- Source ancestry: parent F Git blob `3e6fe4d9ddbd0cd160f07f9651d4035963440a56`. New stage `staging/ru/communication_integrity_20261111_context_delta_g.json` is unregistered, direct/context-guarded and read-only. Registered source manifest, consumers, ImPULS, live caches and private materials unchanged.
- Pre-commit JS found zero repeated normalized replies, IDs or context notes across A–G, with maximum observed token Jaccard **0.3333** (no pair >=0.80); human semantic review still required. Python suite updated for G and must pass on actual final PR head. After any merge, check actual post-main SHA before more merges.
- Next suffix **77**. Earlier 760 are cumulative, not new in a subsequent run.

## Stage H checkpoint — 11 November 2026

- +**80 NEW** authored synthetic RU responses, 8 per stable intent, ID suffixes **77–84**. Prior A–G 760 retained, cumulative **840/1000**, ten partial sets **84/100**, 16 remaining per intent (160 total); no 100/100 claim.
- File `staging/ru/communication_integrity_20261111_context_delta_h.json`, parent G blob `4158e136ec800cb0187dabc27b1f7a016a43ba80`. Public staging only, with direct/context match, no personal chat data, no sanctions, no actual consumer feature claims.
- On A–H, pre-commit JS found 840 unique normalized texts, IDs and context notes; maximum observed token-Jaccard **0.3571**, no pair >=0.80. Full semantic editorial proof not claimed. Python tests updated for H. Exact-head CI and post-main gates apply; manifest, source pack, ImPULS and caches unchanged.
- Next suffix **85** per intent; 160 remains.
