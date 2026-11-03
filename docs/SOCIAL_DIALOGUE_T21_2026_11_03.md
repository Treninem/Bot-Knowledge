# T21: independent natural social dialogue contexts (2026-11-03)

Base main: `3339f3156f6ef3a8637a09da2534b967bf008faa`. Authoring branch: `bk/social-t21-contexts-20261103`.

Added **48 original synthetic cases**, 8 each: congratulations, support, explicit opt-in humor, contextual profanity, everyday conversation, and creative microfiction. These are not additional complete 100/100 reply-catalogue sets: they are context-scoped cases in an existing compatible pack. Existing cases: **803**; proposed: **851**. Rejected normalized/near-duplicate candidate inputs: **0** against the base corpus (threshold 0.80), with separate editorial review.

Only `all_ai_bots` read-only language examples; no user data, commands, sanctions, payments or assertions of live-bot capabilities. Every entry has `context` and `avoid` conditions. Humor requires a user invitation; profanity is interpreted rather than repeated to attack anyone. Source of purpose and boundaries: `AGENTS.md`, `POLICY.md`, `docs/REQUIREMENTS_21.md` at the above immutable base.

Pack SHA-256: `2020db073a8782d7d2e5a2df566e93961c389ac997f22d8c76bc3ace5c553929`; UTF-8 bytes: **572593** (limit 2 MiB). Manifest: `2026.11.03.100`. Added a direct retrieval and privacy regression to `.github/workflows/quality.yml`.

**Merge gate:** real exact-head CI on final head SHA; current-main compatibility; protected merge; separate post-main CI. No BotHost deployment or consumer integration asserted.

Next run: verify whether the working bot's natural-language ImPULS help has any factual gaps after #134, and add only source-verified universal QA to existing formats. Current `reply_catalog` remains unchanged (119 × 100 from earlier reviewed work; no incomplete sets in this T21 batch).
