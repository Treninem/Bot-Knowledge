# Prompt literacy G–H — independent continuation of #645

Base exact head at creation `07c37afc31bdc272f823dc0e77afb3565590651c`, PR #645 contains previous A–F **600** contextual synthetic Russian candidates. Adds **200 new** original context-labeled responses: G suffix 61–70, H 71–80, ten stable `prompt20261111_*` intents. Cumulative A–H = **800/1000**, each partial **80/100**, missing **20** per intent (200 total); **0 completed 100/100**. Do not recount earlier 600 as new.

Immutable parent stage F Git blob `faca8a39bb8005a1eef33d513d1495633d2fa5e1`. New stage G Git blob `d5773ece186510194d89eba986740214685c7044`; H parent G, H blob `ec1bc042d29db62c7dc0d28188faadd53e5a95bb`. Manifest remains `2026.11.09.003`; source registered pack SHA-256 `0cfedc133354a69522fecc3cda6bc21533c66005f0dc207050075f787dc977a8`. Registered packs, manifest, live cache and consumers unchanged.

Authoring check: 800 unique IDs, normalized reply texts, normalized applicability notes; 0 exact duplicate; max token-Jaccard `0.3636` (<0.8), **not** proof of total semantic uniqueness. Python CI `scripts.test_prompt_literacy_a_h_20261111` requires actual checked-out head SHA and checks real file bytes, Git parent chain, scope, context, privacy and answer overlap. All entries require direct request with matching context; no moderation sanctions, personal chats, token writes, deployment or paid operations.

**BLOCKED** until parent #645 exact-head / post-main are confirmed, this PR exact-head CI passes, editorial and compatibility review, and guarded main merge. Before merge retarget from parent branch to latest main (or safely replace stacked PR) and compare all changed blobs. On successful merge verify actual merge SHA post-main CI. Next unused suffix **81**.
