# Collaborative conversation T83 — 2026-11-04

Verified base `dc8f41dda1d1201fcaab99ddb9f70c5748ba934b`. New **37 original group-work questions**, **74 search aliases** and **111 original context-specific response variants** in existing `collaborative_dialogue_qa` qa.v1 pack; former 37 questions preserved. New total `74` questions and `222` answer variants.

Themes: handoffs, concurrent editing, time zones, private channels, partial agreement, budgets, decisions vs proposals, meeting summaries, cross-team dependencies and respectful conflict handling. Not product-specific; no executory rights. Audience `all_ai_bots`, contexts direct/private/group_addressed, read-only + addressed + no-personal-data constraints. Source `docs/REQUIREMENTS_21.md` at `dc8f41dda1d1201fcaab99ddb9f70c5748ba934b`.

Normalized question/alias collisions screened against all manifest qa.v1 packages and the concurrently open T82 PR; new test `scripts/test_collaboration_qa_t83.py` repeats cross-manifest checks, SHA, local index lookup, scopes and JSON schema. Existing T79 regression remains scoped to its original 37 fixtures. Workflow now compares actual checkout with expected exact head SHA.

Pack size 95915 bytes (<1 MiB), SHA-256 `21bac2e221243d11dfd11af3ea6f88b2285a05bb520a2e41e5b5be9b3626f73f`, provisional manifest version `2026.11.04.016`. Reconcile after earlier pending independent PRs; don't merge without successful exact-head and post-main verification. No ImPULS/BotHost changes or consumer delivery claimed.
