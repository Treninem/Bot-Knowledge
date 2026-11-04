# T105 — context-specific replies in an existing registered qa.v1 pack (2026-11-04)

**Branch** `bk/t105-followthrough-existing-qa-20261104` from **main** `23871ed224cbe0d9636c841fd48e3f43bdd3ed1b`. **Status:** Draft / BLOCKED; not merged and not delivered to ImPULS. Pending manifest changes are not published knowledge.

## T105b second checkpoint — latest verified data (2026-11-04)

- Continued the **same existing registered pack**, not a new pack: **+40 additional original Russian replies** over another 20 stable questions (`follow_t86_021`–`032`, `follow_t88_001`–`008`). This run's registered-pack PR candidate total is now **+80 replies across 40 distinct existing intents**, all **40 × 5/100**, **95 missing each / 3,800 missing in these active sets**; the other **42** records in this pack remain at **3 replies each**. **0 sets completed 100/100**. Original pack 246 → proposed **326** reply strings over 82 records.
- Latest data commit [`6ef52da1fd783bf78bfe5aad1bcdcff97d2772c3`](https://github.com/Treninem/Bot-Knowledge/commit/6ef52da1fd783bf78bfe5aad1bcdcff97d2772c3); updated pack blob `d266cc252bb51d5ff81e31b589aab1330cee02bf`. Manifest repinned in [`5d8244c3062f41b0429f33330cb55c8c989e475b`](https://github.com/Treninem/Bot-Knowledge/commit/5d8244c3062f41b0429f33330cb55c8c989e475b) at **SHA-256 `a4d2e470e0eb762f5ac376133672959f6e8f90a35b6801fe8472f9f4e10b067f`**, `knowledge_version=2026.11.04.028`. Main remains at `.026`.
- Fresh connector/JS checks on exact branch: all 82 records and existing fields retained, 80 new normalized unique answer strings, 326 unique answers in the pack, 246 distinct normalized question/alias forms, 0 exact text overlap of the 80 new replies with ten other QA packs (2,221 records), 0 schema limit/context/privacy guard errors. Checks are lexical/structural, not complete semantic acceptance.
- **Proposed pack size 123,997 bytes**, compared with 108,355 bytes in main. Proposed all-38-pack snapshot **7,534,900 / 8,388,608 bytes** (**853,708 bytes headroom**, +15,638 bytes versus main including manifest difference). No live consumer/cache change; Draft PR is not published knowledge.
- Offline Python test amended for 80 new replies and first 40 records with 4 variants each; **not executed**. Full `validate_pack.py`, Windows `D:` checkout, large non-QA catalogs, exact-head CI, ImPULS consumer E2E and post-main remain unverified. No paid Actions, no merge.
- Latest owner coordination: leave #224 publisher functions `scripts/trusted_publish_qa.py` and `scripts/prepare_knowledge_candidate.py` unchanged. If #214 merges manifest .027, re-check base and reconcile version/SHA before any merge of this PR.

---

## T105a first checkpoint — historical data

- Updated existing `packs/ru/conversation_followthrough_qa.json` only: **20 existing stable intents** `follow_t86_001`–`020`, **+40 manually authored synthetic Russian response variants** (+2 each). Zero new canonical intents, aliases, or packs. Previously 3 replies per selected intent → **5/100 each**, **95 missing per selected intent**. Other 62 records in this existing pack remain unchanged.
- Original full pack: **82 records / 246 reply strings**; proposed pack: **82 records / 286 reply strings**. **0 completed 100/100 sets**; 20 partial sets actively advanced. Distinct treatment of topic recovery, corrections, direct/group address, tone change, listening, prioritization, and criticism.
- Original pack Git blob `707fcaa6440d398a730840362602d4532ab92036`; updated pack blob `982aff39a3692dc64921ff5c96f68bbf3cbf7ad2` via commit [`6d7e42267e52c80697d363c64c5ef0aa0626e3cb`](https://github.com/Treninem/Bot-Knowledge/commit/6d7e42267e52c80697d363c64c5ef0aa0626e3cb).
- Manifest updated on this branch in commit [`0cbedda97b71fcf9c4011de2db089ec352316ab1`](https://github.com/Treninem/Bot-Knowledge/commit/0cbedda97b71fcf9c4011de2db089ec352316ab1), **proposed** `knowledge_version=2026.11.04.028`, pack `pack_version=2026.11.04.024` and exact UTF-8 SHA-256 `91012dd2920637e89a3a8a8b947a41a114e79775c95cd2797d0ab991a9e3f814`. SHA-256 implementation checked against the standard `abc` vector and verified the unchanged base pack against the main manifest hash.
- Proposed UTF-8 pack bytes: **108,355 → 116,198** (+7,843); manifest bytes: 5,685; other 37 registered blobs unchanged. Resulting proposed **38-pack consumer snapshot: 7,527,101 / 8,388,608 bytes** (**861,507 headroom**); no consumer cache touched. Main baseline is 7,519,262 bytes and is unchanged by this Draft.

## Checks run vs. unverified

**Actually checked on exact connected GitHub file reads and in-process JavaScript:** JSON parses, 82 stable records and existing fields unchanged, 40 new replies in the first 20 intent IDs, normalized unique IDs/questions/aliases/responses, response lengths and qa.v1 variant limit (max 8), audience `all_ai_bots` and read-only/direct-address/no-personal-data guards, 0 normalized exact collisions against the 10 other registered QA packs (2,221 other records), no close within-intent token-Jaccard above 0.65 for added replies, basic sensitivity/action-pattern scan, manifest SHA-256 of the updated pack and projected byte budget. These structural/lexical checks **do not prove full semantic uniqueness**.

**Not run:** local Python/validate_pack on full exact checkout (Windows `D:` unavailable in this environment), full large non-QA reply/social catalog semantic screening, ImPULS consumer E2E, exact-head CI, post-main CI. Offline Python test `scripts/test_followthrough_expansion_t105.py` was **authored but not executed**; it checks all manifest SHA-256 hashes, snapshot cap and cross-pack duplication when run on a real checkout.

**Coordination:** do not modify `scripts/trusted_publish_qa.py` or `scripts/prepare_knowledge_candidate.py` (separate #224). No personal Telegram chats/IDs/tokens or private code. No GitHub Actions dispatched, no paid services, no ImPULS/BotHost edits. #214 separately proposes manifest .027; re-check fresh main, resolve manifest version/hash coherently, re-validate, and obtain exact-head CI before considering merge.

## Remaining / next action

- 20 selected partial intents: **20 × 5/100**, 95 still missing per intent; other 62 intents in the pack were not progressed here. No set is declared 100/100.
- On `D:`, fetch exact PR head and run `python -B scripts/test_followthrough_expansion_t105.py` and `python -B scripts/validate_pack.py`, plus the existing consumer smoke tests. Review all large conversation catalogs, then get green exact-head CI via permitted non-paid infrastructure. Reconcile #214 and any new main commits; check post-main CI only after a fully gated merge. Do not assume GitHub PR implies delivery.
