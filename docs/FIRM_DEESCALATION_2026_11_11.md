# Firm de-escalation — original context-specific Russian replies (11 November 2026)

## Authoring checkpoint A

- Base: `697ec80df18205027bbbf675a512bb5d1fa8f87f` (Bot-Knowledge main after #649).
- New content: `staging/ru/firm_deescalation_20261111_context_pool.json`, **100 new** synthetic RU replies across ten *stable* `firm20261111_*` intentions, **10/100 each**, **90 missing per intention**, **900 total still missing**; **0 complete 100/100 sets**. Earlier staged replies from other series are not included.
- Subjects: direct insult, mockery instead of evidence, unsubstantiated accusations, pressure for immediate conclusions, sanctions bait, third-party private data, targeted bullying, repetitive disputes, rude group dynamics and criticism of the assistant.
- Every reply has a distinct situational `context_note`; a reply is not universally applicable to every utterance under its canonical question. `read_only=true`, `consumer_registered=false`, `requires_direct_address=true`, `requires_context_match=true`, `all_ai_bots`; never assert moderator rights, perform sanctions or publish personal data.
- Registered source: `packs/ru/social_dialogues.json`, manifest SHA-256 `0cfedc133354a69522fecc3cda6bc21533c66005f0dc207050075f787dc977a8`, Git blob `d56ff304da7165bd63c328f3220a1f6d3d26e3ab`. Manifest `2026.11.09.003` and consumer cache untouched.
- Connector-side initial 100-entry audit: 100 unique IDs, 100 normalized reply texts, 100 normalized context notes; no exact duplicates; maximum intra-stage token-Jaccard **0.2778**. This lexical metric is **not** a guarantee of semantic originality against all existing staging PRs. Manual editorial selection remains necessary.
- Test locally from actual checkout: `python scripts/validate_pack.py`; `python -m unittest scripts.test_firm_deescalation_20261111 -v`. The associated read-only exact-head CI must also complete successfully.
- Stage is **review-only**. No data were appended to registered packs or connected to ImPULS/AuroraFox. Merge into main would only publish staged candidates, not enable new consumer skills.
- Next: after verifying exact-head CI, source SHA, cross-corpus overlap and main compatibility, guarded merge `expected_head_sha` followed by actual merge-SHA post-main CI. Then continue these same IDs from suffix **11**, rejecting low-value synonym padding; also proceed with other genuinely missing intentions.

## Continuation B — distinct situational answers

- New file `staging/ru/firm_deescalation_20261111_b.json`: **+100 new** original situation-specific answers, ten per existing stable intention (suffix 11–20). No A-series entries are counted twice.
- **Cumulative staged: 200 answers**, ten distinct intentions **20/100 each**; **ten partial sets**, **80 remaining per set**, **800 total remaining**, **zero completed 100/100**.
- After A+B checks in connected GitHub code, 200 distinct stable IDs, 200 normalized texts and 200 context notes; zero exact matches and zero Jaccard ≥0.8; max token-Jaccard **0.2778**. This is only a lexical duplicate screen; full cross-corpus and semantic quality must still be reviewed.
- `scripts/test_firm_deescalation_20261111.py` and the read-only workflow validate both full stages and the per-stage checkpoint. Source hashes, manifest version, registered packs, consumer cache, ImPULS and BotHost remain unchanged.
- Current branch `bk/firm-deescalation-20261111-a`, PR #650. B initial content commit `2812b30ae15468f9472e0cf50f351071ea1d1241`. New current full head must be read, not assumed from a former checkpoint.
- Follow-up: continue each stable intent with suffix **21**, reject merely cosmetic variants, require actual final-head CI success; do not claim a consumer-ready release from staging.

## Targeted cross-staging overlap check

The latest A+B authoring pass compared all **200** new answers with **1060** contextual reply texts from six relevant existing staging files: `group_pragmatics_t600_context_pool`, `interpersonal_t590_context_pool`, `communication_integrity_20261111_context_pool`, `dialogue_repair_t554_context_pool`, `optional_humor_t518_context_pool`, and `group_pragmatics_t611_alternatives_review_only`. There were **zero exact duplicates and zero token-Jaccard matches at or above 0.55** across these 212,000 pair comparisons. This deliberately limited sample is not a full cross-repository semantic audit.

The Python test now repeats this check against those six available staging files, as well as testing exact duplicates against every manifest-registered pack. Review exact final-head CI before merge; no consumer registration.

## Continuation C — ten situational answers per stable intent

- Latest content commit: `895bd7ce8d87675d2df0cb99d6c1914aeb73ea7e`, file `staging/ru/firm_deescalation_20261111_c.json`.
- **100 newly authored synthetic RU replies**, suffixes **21–30** in each of ten existing stable `firm20261111_*` intents. Earlier A+B: 200; **cumulative 300**, ten partial sets **30/100 each**, **70 missing each** / **700 missing total**, zero sets at 100/100.
- Independent connected-data preflight: all 300 IDs, normalized answer texts and context notes unique across A+B+C; zero overlaps in this sample, highest token-Jaccard **0.2941**. This is a lexical check, **not** complete editorial semantic review or all-repository screening.
- Responses explicitly limited to directly addressed, context-specific, read-only `all_ai_bots` dialogue. No sanctions, identification, personal information sharing, BotHost, ImPULS or consumer changes.
- Existing `manifest.json` and SHA of registered `packs/ru/social_dialogues.json` unchanged. The new staging file is **not registered** for consumer loading.
- Updated `scripts/test_firm_deescalation_20261111.py` checks all three stages and their exact counts, source hashes, registered-pack exact repeats, adjacent staging lexical overlap and privacy restrictions. Exact-head CI for this **new head** still required, as is post-main CI before further merges.
- Next: continue from suffix **31** per stable intent, refusing low-value synonym padding; after successful PR CI and fresh base/head check, guarded merge and actual post-main validation. Keep the recorded full count distinct from accepted consumer content.

## Continuation D — distinct contexts 31–40

- Added **100 new** synthetic contextual replies in `staging/ru/firm_deescalation_20261111_d.json`, commit `4029fd7911887904b1c12070390ba673983de14f`.
- Cumulative **400** distinct staged replies A–D for ten unchanged `firm20261111_*` intents: **40/100 per intent**, **60 missing each**, **600 still missing**, **0 completed 100/100 sets**. The +100 count is relative to C and does not include its older 300.
- Connected read-only preflight: 400 distinct IDs, normalized text responses and situational notes; for the 100 new D responses, max token-Jaccard against A–C and D was **0.3125**; zero pairs ≥0.55. No direct identifiers, no live actions, no sanctions, no consumer registration.
- Same registered source SHA-256 `0cfedc133354a69522fecc3cda6bc21533c66005f0dc207050075f787dc977a8`. Registered manifest/cache untouched.
- Script checks four files and must be run on exact final head; these lexical checks do not replace editorial review of meaning or quality. Next suffix **41** per intent. Merge only with fresh main, final exact-head CI, expected-head protection and post-main CI.

## Continuation E — context-first conversational boundaries

- File `staging/ru/firm_deescalation_20261111_e.json`, commit `91f08153903757bd2cf85f9484114afa64f61180`: **+100 new** synthetic contextual answers, stable suffixes 41–50.
- Cumulative **500/1000** staged answers A–E across ten unchanged intentions: **50/100** each, **50 missing each** / **500 missing total**. **0 completed 100/100** sets. In this continuation PR C–E contributes **300 new**, not the older 200 from main.
- Connected preflight covers all 500: normalized IDs, answer texts and context notes unique. New E vs A–D + E max token-Jaccard **0.4167**, zero pairs ≥0.55. Manual semantic quality review and exact-head CI still required.
- Safety: no personal information, sanctions, powers or consumer registration. Source pack, manifest and cache unchanged. Next suffix **51** for all ten intentions.

## Continuation F — no sanctions, safe direct replies

- File `staging/ru/firm_deescalation_20261111_f.json`, source commit `1f7442addd22601d9f39f65daf09ef403d0e360f`; **+100** newly authored, suffixes 51–60 across the same ten intents.
- A–F cumulative **600 replies**, ten partial sets **60/100** with **40 missing per set** / **400 missing total** and **zero complete sets**. Net additions in PR #651 from C–F **400**, distinct from 200 A+B already merged.
- Deterministic preflight across A–F: 600 unique normalized responses, IDs, context notes. New F max token-Jaccard **0.3182** vs previous five stages; no pair ≥0.55. Editorial semantic audit remains separate.
- No registered-pack, manifest, SHA/cache, ImPULS, BotHost or active consumer change. `scripts/test_firm_deescalation_20261111.py` updated for all six stages. Exact final-head and post-main gates still required.
- Next suffix **61** in each of ten stable intents, subject to genuinely distinct context and wording.
