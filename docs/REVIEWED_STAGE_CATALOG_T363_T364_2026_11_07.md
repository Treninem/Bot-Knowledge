# Read-only verified index through T363/T364 — 3,242 staged replies (2026-11-07)

This follow-up depends on [PR #404](https://github.com/Treninem/Bot-Knowledge/pull/404), head `73fe584639f4c09dd792135b62b4f2d1a7013f76`. It does not introduce or alter any response text. It updates the **offline reference** `ReviewedStageCatalog` to validate and expose the two newly added histories, rather than stopping at T357/T358.

- Before: 22 conversation intents × 65 staged, 24 practical intents × 64 staged = **2,966 staged** (414 registered; 3,380/4,600 combined).
- After: 22 conversation intents × **71 staged** and 24 practical intents × **70 staged** = **3,242 staged** (414 registered; **3,656/4,600** combined). This indexes 276 previously missing staged replies, not 276 newly written replies in this PR.
- Still **944** replies to reach 46 × 100, with 46 partial and zero completed intents. Conversation 80/100; recovery 79/100.
- The index recursively validates source SHA-256, pinned parent Git blobs, identity and normalized text, expected record counts, audience and read-only flags. The cache identity hashes manifest and staged bytes but never touches live consumer caches.
- Selection remains fail-closed unless the caller supplies an **explicit authorized reply ID**, direct addressing, suitable intent/audience/context and local permission. No sanctioned actions, inferred roles, background network lookups or automatic bot integration.
- Workflow checks exact checked-out head SHA and runs manifest validation plus full catalog tests. This is a staging reference module, **not** publication of extra manifest packages or deployment to ImPULS, AuroraFox or other running programs.
- Dependent change: merge #404 only after successful exact-head and predecessor post-main CI; then retarget/recheck this PR against fresh main and merge only after its own exact-head success, followed by post-main CI.
