# T347/T348 — further 46 original contextual replies

Base main: `96dcb7c97b6374d2cfe7b65738446b9856b734d5` (already merged #389). Separate independent new batch: T347 22 Russian conversational intent replies and T348 24 general-purpose practical recovery replies, **one each per intent**. All are unique original synthetic texts and context notes, conditioned on direct address, verified context, scope and approval; no sanctions, no private messages, no independent actions.

Historical group baseline: 22 intents ×62/100, 24 intents ×61/100 = 2,828/4,600. New: 22 ×63/100, 24 ×62/100 = **2,874/4,600**, **1,726 remaining**, **46 partial**, **0 newly completed 100/100**. Registered packages still 414; proposed staged 2,460. Do not count these 46 as consumer-ready; the current ReviewedStageCatalog (PR #390) has **2,414**, not these new 46.

Each delta references the exact source pack SHA-256 from manifest, source blob SHA and immediately prior stage Git blob. The recursive ancestry validator and tests check independent approval scope, normalized exact duplicate texts and notes, lexical near-matches vs inherited 2,828, ID consistency and tamper rejection. Full semantic uniqueness requires human review. Manifest, live bots and caches untouched.

**Merge gate:** exact-head CI passing for this PR, confirmation of post-main for predecessor, latest base/head SHA then post-main CI after merge. No write tokens to consumers; no modification of ImPULS.
