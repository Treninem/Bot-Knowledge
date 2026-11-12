# Verified read-only stage index: T347/T348 (2026-11-07)

Current parent main: `9b1c0680821f1bc3a173f7d61b075361ab47a95f` (merged PR #391). The catalog now targets **2,460 staged Russian candidates** (was 2,414) across **46** canonical intents; **new author-written candidates in this index-only PR: 0**. Prior +46 distinct replies belong exclusively to merged PR #391, not counted twice. Per-intent staged count: colloquial **54** for 22 intents, practical **53** for 24 intents; registered 414 remain separate (overall 2,874/4,600; 1,726 missing).

This is an offline, fail-closed, *read-only* reference catalog; recursively validates all source pack manifest SHA-256, Git blob stage parents, prior-stage metadata, unique IDs, exact reply approvals and matching context/audience. Cache identity is derived from source manifest plus all stage bytes. It doesn't automatically grant abilities, execute bans, trigger actions or learn from private chats. Manifest is unchanged, stage files are not registered consumer packs, and no live ImPULS/AuroraFox integration is claimed.

CI gate: current exact-head SHA and the actual merge SHA after publication; run `python scripts/validate_pack.py` and `python -m unittest scripts.test_reviewed_stage_catalog -q`. This index can only be merged after predecessor PR #391 post-main CI passed.
