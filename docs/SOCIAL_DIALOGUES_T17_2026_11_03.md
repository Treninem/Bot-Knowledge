# T17 — distinct, context-dependent social replies (03.11.2026)

- Parent commit `e0e2e5552c68534c892c0ddad48022ed3c4b1ab4` (dependent upon natural ImPULS help #132, not yet merged at creation).
- Starting `social_dialogues.json`: 707 cases; new 36 original synthetic cases; 0 rejected normalized duplicates. Proposed total 743.
- New kinds: {"conversation":6,"support":6,"humor":6,"profanity":6,"congratulations":6,"creative":6}. Cases describe when a reply is appropriate and when to avoid it. No raw conversations, names/IDs, auto-sanctions, hidden data or personal memories.
- Pack size 505684 UTF-8 bytes, SHA-256 `871c8a10fa6be8f679daa12d7fd44ba08f4c332fdff951f79326e4ec3a592d98`. Manifest version `2026.11.03.96`, SHA-256 `f2e54ebfe5d303c584d5f003bb9039ed73173c6d1bfe4a24b490d9a97df65b81`; no live cache touches.
- `scripts/test_social_dialogue_t17.py`: original inputs, local retrieval, privacy/context and manifest hash. Existing suite remains enabled. Exact-head CI and post-main CI require real outcomes, not assumptions.
- Reply_catalog remains unchanged with 119 complete 100/100 sets. These 36 contexts are not claimed as completed 100/100 sets.
- Follow-up: after #132 passes exact-head and post-main, retarget dependent PR to main, check exact current head CI and only then consider merge.
