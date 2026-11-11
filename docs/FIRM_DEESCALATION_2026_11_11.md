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
