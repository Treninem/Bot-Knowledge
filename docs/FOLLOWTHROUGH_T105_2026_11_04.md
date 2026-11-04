# T105 — context-specific replies in an existing registered qa.v1 pack (2026-11-04)

**Branch** `bk/t105-followthrough-existing-qa-20261104` from **main** `23871ed224cbe0d9636c841fd48e3f43bdd3ed1b`. **Status:** Draft / BLOCKED; not merged and not delivered to ImPULS. Pending manifest changes are not published knowledge.

## Verified candidate delta

- Updated existing `packs/ru/conversation_followthrough_qa.json` only: **20 existing stable intents** `follow_t86_001`–`020`, **+40 manually authored synthetic Russian response variants** (+2 each). Zero new canonical intents, aliases, or packs. Previously 3 replies per selected intent → **5/100 each**, **95 missing per selected intent**. Other 62 records in this existing pack remain unchanged.
- Original full pack: **82 records / 246 reply strings**; proposed pack: **82 records / 286 reply strings**. **0 completed 100/100 sets**; 20 partial sets actively advanced. Distinct treatment of topic recovery, corrections, direct/group address, tone change, listening, prioritization, and criticism.
- Original pack Git blob `707fcaa6440d398a730840362602d4532ab92036`; updated pack blob `982aff39a3692dc64921ff5c96f68bbf3cbf7ad2` via commit [`6d7e42267e52c80697d363c64c5ef0aa0626e3cb`](https://github.com/Treninem/Bot-Knowledge/commit/6d7e42267e52c80697d363c64c5ef0aa0626e3cb).
- Manifest updated on this branch in commit [`0cbedda97b71fcf9c4011de2db089ec352316ab1`](https://github.com/Treninem/Bot-Knowledge/commit/0cbedda97b71fcf9c4011de2db089ec352316ab1), **proposed** `knowledge_version=2026.11.04.028`, pack `pack_version=2026.11.04.024` and exact UTF-8 SHA-256 `91012dd2920637e89a3a8a8b947a41a114e79775c95cd2797d0ab991a9e3f814`. SHA-256 implementation checked against the standard `abc` vector and verified the unchanged base pack against the main manifest hash.
- Proposed UTF-8 pack bytes: **108,355 → 116,198** (+7,843); manifest bytes: 5,685; other 37 registered blobs unchanged. Resulting proposed **38-pack consumer snapshot: 7,527,101 / 8,388,608 bytes** (**861,507 headroom**); no consumer cache touched. Main baseline is 7,519,262 bytes and is unchanged by this Draft.

## Checks run vs. unverified

**Actually checked on exact connected GitHub file reads and in-process JavaScript:** JSON parses, 82 stable records and existing fields unchanged, 40 new replies in the first 20 intent IDs, normalized unique IDs/questions/aliases/responses, response lengths and qa.v1 variant limit (max 8), audience `all_ai_bots` and read-only/direct-address/no-personal-data guards, 0 normalized exact collisions against the 10 other registered QA packs (2,221 other records), no close within-intent token-Jaccard above 0.65 for added replies, basic sensitivity/action-pattern scan, manifest SHA-256 of the updated pack and projected byte budget. These structural/lexical checks **do not prove full semantic uniqueness**.

**Not run:** local Python/validate_pack on full exact checkout (Windows `D:` unavailable in this environment), full large non-QA reply/social catalog semantic screening, ImPULS consumer E2E, exact-head CI, post-main CI. Offline Python test `scripts/test_followthrough_expansion_t105.py` was **authored but not executed**; it checks all manifest SHA-256 hashes, snapshot cap and cross-pack duplication when run on a real checkout.

**Coordination:** do not modify `scripts/trusted_publish_qa.py` or `scripts/prepare_knowledge_candidate.py` (separate #224). No personal Telegram chats/IDs/tokens or private code. No GitHub Actions dispatched, no paid services, no ImPULS/BonHost edits. #214 separately proposes manifest .027; re-check fresh main, resolve manifest version/hash coherently, re-validate, and obtain exact-head CI before considering merge.

## Remaining / next action

- 20 selected partial intents: **20 × 5/100**, 95 still missing per intent; other 62 intents in the pack were not progressed here. No set is declared 100/100.
- On `D:`, fetch exact PR head and run `python -B scripts/test_followthrough_expansion_t105.py` and `python -B scripts/validate_pack.py`, plus the existing consumer smoke tests. Review all large conversation catalogs, then get green exact-head CI via permitted non-paid infrastructure. Reconcile #214 and any new main commits; check post-main CI only after a fully gated merge. Do not assume GitHub PR implies delivery.
