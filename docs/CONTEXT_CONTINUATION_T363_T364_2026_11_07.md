# T363/T364 — 92 original synthetic RU scoped replies (2026-11-07)

Parent: [PR #403](https://github.com/Treninem/Bot-Knowledge/pull/403), merge commit `5dffcd12af2195bac104ffe1452b68bc39e56cf0`. This follow-up preserves the 46 canonical IDs and source SHA-256 and pins both prior staged files by exact Git blob SHA-1.

- T363: 22 pragmatic/conversation intents × 2 = **44** new context-bound replies. Progress per intent: **78/100 → 80/100**; 22 partial, **20** remaining per intent.
- T364: 24 general recovery/help intents × 2 = **48** new replies. Progress per intent: **77/100 → 79/100**; 24 partial, **21** remaining per intent.
- Scope: **46** intents, **+92** newly authored replies, 0 newly finished 100/100 sets. Combined group progress: **3,564/4,600 → 3,656/4,600**, **944** remain, 414 registered plus **3,242** staged. Not all existing library records are counted in this scoped group.
- Context cases distinguish uncertain agreement, group consent, indirect requests, troubleshooting symptoms, non-destructive correction, UI ambiguity, privacy-safe incident reporting and truthful status disclosure. No personal chat data, live permissions, deployed consumers or command execution.
- Data are **offline staging only** and require explicit approved reply ID, known intent, compatible audience/channel, direct address and local permission to be selected. Staging is not a manifest-registered consumer package; it does not grant moderation or external action authority.
- Tests: source SHA-256, previous immutable blob pins, unique IDs, normalized and near lexical uniqueness, per-intent counts, privacy and fail-closed selection; CI exact-head checkout SHA required. These automatic checks do not establish perfect semantic novelty.
- Merge is conditional on completed exact-head CI and verified post-main CI on the preceding merge, followed by verification on this merge SHA. Never bypass protections or dispatch paid runs.
