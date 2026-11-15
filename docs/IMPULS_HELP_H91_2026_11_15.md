# ImPULS H91 — contextual Russian answer candidates (15 November 2026)

Continues [Draft PR #666](https://github.com/Treninem/Bot-Knowledge/pull/666) from exact parent `906fa51163cadb19a66a2b1a16051d7f4a29f99a`.
Published source Bot-Knowledge main `6c9f430da47f137d39a72bbd28c057cfb8f6be96`; read-only ImPULS source `54b8a3a813fec82c1f953408942ba327eb181c37` (`README.md`).

This checkpoint adds **66 original synthetic candidates** across **60 previously tracked canonical intents**, with a first return to **greeting** (two distinct private/group contexts) and subsequent coverage of conversation repair, roles, moderation fairness, privacy, games, rewards and troubleshooting. All examples are conditional, read-only and scoped to `impuls`; a context note is **not** proof that the deployed consumer evaluates it correctly.

H1–H90: 3,571 staged answers. H91: +66; **3637 staged** in total across 100 partial intents, with 275 source-published answers. **6088 numeric gaps**, zero certified 100/100 sets and zero newly registered or independently editorially approved answers. The stage is deliberately excluded from `manifest.json`.

Raw H91 JSON SHA-256: `8df83f75447992af502a1d8d5376b1c9d21b410ee5514258d5808e1646b3822f`. Source pack SHA-256: `50edd41dc0c6a868577433944e0ff0b2a36c2c9ebe53d587e5cbb4692185bbc9`. Source pack blob: `430f78f7bf43940b112978bc5087b5cb6002eabe`.

Preflight checked context lengths, ID scope, sensitive-link markers and normalized/Jaccard >=0.70 lexical repeats against the published ImPULS help pack, H90 and this batch; 0 proposed texts rejected. Complete H1–H91 lineage and lexical checks run in `scripts/test_impuls_help_h91_20261115.py`, both normal Python and `-O`, on the PR's exact checkout head. Structural checks **do not establish semantic originality** or live integration.

**DRAFT/BLOCKED:** detailed semantic selection against parallel PRs #662–#665, verified end-to-end consumer role/context routing, manifest SHA/cache registration within the 8 MiB cap. No published package, private ImPULS, live bot or cache was changed.
