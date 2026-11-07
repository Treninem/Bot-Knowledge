# T361/T362 — further 92 original RU contextual replies (2026-11-07)

This stage extends [T359/T360 PR #402](https://github.com/Treninem/Bot-Knowledge/pull/402) while preserving all 46 registered canonical intent IDs and immutable previous-stage Git blob pins.

- T361 adds **44** original conversation-pragmatics replies: 22 intents × 2 new separately scoped contexts. Registered 9 + previous staged 67 + new 2 = **78/100** per intent (22 still missing); 22 partial, none complete.
- T362 adds **48** original general technical-help/recovery replies: 24 intents × 2 distinct contexts. Registered 9 + previous staged 66 + new 2 = **77/100** per intent (23 still missing); 24 partial, none complete.
- Before: **3,472/4,600** for this group (414 registered + 3,058 staging). After: **3,564/4,600** (414 registered + **3,150** staging). Increment **+92** newly written replies, not old replies counted again. **1,036** remain (484 + 552). 46 partial, 0 newly complete.
- The examples distinguish soft conversational commitments from completed work, clarify hidden assumptions, de-escalate frustration, separate diagnostics from permissions, avoid private data in screenshots and preserve precise partial statuses. All data are synthetic Russian; no personal messages, real user IDs or secret values.
- Context note, audience, channel, direct address, approved reply ID and local permissions remain required; no autonomous sanctions, application actions or publication.
- Verify all registered source SHA-256 references and parent Git blob IDs; validate exact/near lexical duplicates, privacy, per-intent counts and fail-closed selection via supplied Python tests. The tests cannot guarantee absence of all conceptual repetitions.
- **Offline staging only**; not in manifest, not automatically installed in ImPULS or other consumers. No live bot update or paid workflow dispatch.

The dependent PR must not merge until PR #402 has fully successful post-main checks and this PR has successful exact-head checkout verification on its own latest SHA. Merge with expected head guard and confirm post-main CI on actual merge SHA.