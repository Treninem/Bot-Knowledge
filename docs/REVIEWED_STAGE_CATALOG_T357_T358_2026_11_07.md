# Read-only catalog through T357/T358 — 2,966 staged replies (2026-11-07)

Based on merged [PR #400](https://github.com/Treninem/Bot-Knowledge/pull/400), commit `2e6d50928a9a744c1a1a5d1fb1d68054222553e6` following PR #399. **No new answer texts** in this change. It makes the 184 replies added by #399 and #400 visible to the isolated, explicitly authorized *reference* catalog instead of leaving the index at 2,782.

The registered QA packs remain 414 replies for these 46 stable intents. After #400 there are **2,966 staged** and **3,380/4,600 combined**: 22 conversation intents × 74/100 (65 staged + 9 registered) and 24 practical intents × 73/100 (64 staged + 9 registered). There are **1,220 missing**, 46 partial, zero newly complete sets.

The implementation recursively verifies registered source SHA-256, historical Git blob ancestry, original ID and normalized-text uniqueness, required per-intent counts, audience, context and read-only restrictions. Selection still fails closed without explicit caller-approved reply ID, addressed intent, `all_ai_bots` audience, matching context and local permission. Cache identity incorporates every staged file's bytes; it does not touch live bot caches.

There is no automatic integration into ImPULS or AuroraFox and no sanctions, private chat records, bot write tokens or network lookups on each turn. Merge only with exact-head CI, source integrity and actual post-main CI; do not dispatch paid workflows.
