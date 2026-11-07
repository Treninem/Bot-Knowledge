# T359/T360 — 92 original RU scoped replies, 2026-11-07

Main base [PR #401 merge](https://github.com/Treninem/Bot-Knowledge/commit/37dc763f611b2ded86236ee23db9ebeb03a4aa9e). Both additions preserve the existing 46 stable intent IDs and supplement registered QA without modifying its schema.

- T359: **44** newly written, synthetic conversational pragmatics replies (22 intentions × 2), moving 74/100 to **76/100** per intention. Historical stages: 65 staged + 9 registered before this run; now 67 staged + 9 registered.
- T360: **48** newly written, synthetic practical-recovery replies (24 intentions × 2), moving 73/100 to **75/100** per intention. Historical stages: 64 staged + 9 registered before this run; now 66 staged + 9 registered.
- Total **92 newly authored** texts, 46 intentions touched, **0** newly complete 100/100 collections; registered **414** unchanged; staged **2,966 → 3,058**; combined **3,380 → 3,472/4,600**. Remaining **1,128** (22×24 + 24×25). No restoration or re-counting of earlier answers.
- Examples cover unspoken limits in everyday phrases, work handoffs, careful error diagnosis, non-destructive changes, provenance, safe screenshots, private vs public scope, and truthful progress. Context notes are unique, with explicit direct/private/group-addressed scope; no quote from real conversations.
- Registered manifest source SHA-256 and both parent Git blob SHA-1 pins are verified in Python tests, with exact IDs, lexical duplicate checks, ancestry validation and denial without explicit per-reply approval, address, context, audience and local permission. Lexical checks cannot replace full semantic review.
- The datasets are **offline staging only**, not in manifest or live consumers. Neither ImPULS nor AuroraFox was changed. No sanctions, external actions, paid workflow dispatch, private chat data, or runtime cache mutations.

Gate: exact-head test on full head SHA and post-main CI on actual merge SHA before publication. If CI unavailable, leave this PR open and blocked rather than bypassing protections.