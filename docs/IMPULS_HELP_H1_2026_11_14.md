# ImPULS user-facing H1 — 14 November 2026

Source: registered `packs/ru/impuls_help_qa.json` on main `6c9f430da47f137d39a72bbd28c057cfb8f6be96`, actual source blob `430f78f7bf43940b112978bc5087b5cb6002eabe`, manifest SHA-256 `50edd41dc0c6a868577433944e0ff0b2a36c2c9ebe53d587e5cbb4692185bbc9`.
ImPULS read-only source `Treninem/Impuls` main `60f08d93c6f0268d63d1c06dc364287d0b18c183`, README and `docs/RELEASE_VERIFICATION_2026-11-14.md`. The document confirms runtime **1.6.247** in Telegram on 14 November; 1.6.248 remains an uninstalled candidate. New replies avoid candidate-only features.

## H1 checkpoint

**15 existing canonical intentions**, **45 new synthetic Russian contextual reply candidates** (three per intent). No old published answer was counted as new. No new canonical intent was claimed. The baseline for each is the one registered answer plus its actual variants; the JSON records exact per-intent published + staged counts and remaining numerical slots excluding other open PRs. **0 independent editorial approvals and 0 approved 100/100 sets**; all 15 remain partial. Check each against concurrent Draft PRs before treating its count as full cross-repository coverage.

Domains: direct/group address, topic correction, chosen group, confirmed settings, game troubleshooting, Pulse rewards, false moderation alarms, publication-vs-live knowledge, role/version visibility, conversation scope, DM/group navigation, family-tree relationships, explicit wedding consent, and complaint status.

Each variant specifies a distinct observed situation, allowed context, intended audience `impuls`, and read-only/no-sanction boundaries. None claims to observe a user's account, change settings, apply penalties, or read a private conversation. No private code was copied.

Source-published total snapshot is near the 8 MiB consumer limit; **consumer_registered=false**, no manifest/cache change. The stage is a candidate pool, not an installed consumer capability.

## Preflight and next

Code-mode readback of the exact published source and the 45 new authored replies passed normalized exact uniqueness. Maximum token Jaccard against every published help answer/variant: 0.250 (closest impuls_help_selected_chat_h1_01 / help_t41_007); 0 pairs >= 0.70. These checks do **not** prove full semantic uniqueness. Independent manual review, cross-PR semantic overlap, actual consumer contextual selection, and exact-head CI remain required. GitHub checkout via local container DNS was unavailable, so no local Python PASS is claimed.

Before merge: recheck latest main/head SHA, actual exact-head and full quality CI, current manifest+snapshot budget, and consumer behavior; only then consider staged promotion. No ImPULS, BotHost, live bot, or paid changes.
