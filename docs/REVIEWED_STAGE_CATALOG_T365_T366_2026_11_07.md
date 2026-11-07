# Verified read-only stage catalog through T365/T366 — 3,334 replies (2026-11-07)

This independent index maintenance change depends on [PR #406](https://github.com/Treninem/Bot-Knowledge/pull/406), exact parent head `7bcb4dadd3c4659caa346761a1dfdbaeb5c5fb4e`. No new response text is authored in this PR.

- Earlier index: **3,242** staged items, 46 intents. Newly saved T365/T366 adds **92** synthetic stage replies; the catalog now validates **3,334 staged** in their full immutable histories.
- Corpus in this scoped 46-intent group: **414 registered + 3,334 staged = 3,748/4,600**. Conversation: 22 intents × **82/100** (9 registered + 73 staged); general recovery: 24 intents × **81/100** (9 + 72). Still **852** missing (396+456); 46 partial sets, none newly complete.
- The reference catalog recursively verifies source pack SHA-256, parent blob pins, IDs, normalization uniqueness, permitted audiences, data shape and explicit reply selection conditions. Cache identity incorporates actual staged bytes; no mutation of live caches.
- Every candidate needs an explicitly approved ID and confirmed addressed context, audience and local permission. This is not an automatic answer router or grant of moderation, publication or side-effect privileges.
- The manifest-registered packs and consumers remain unchanged. ImPULS, AuroraFox and other running programs do not gain skills from this PR without separately verified consumer integration.
- CI must verify exact checkout head SHA and pass complete Python catalog/history tests; only merge after #406's actual post-main CI passes and then verify post-main CI on this PR's merge SHA.
