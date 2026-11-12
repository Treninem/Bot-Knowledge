# T11 social dialogues — contextual speech and original stories

Stacked on PR #116 head `3390d9f152e630bb6fa8dc1faccdd32222e3e2fc`, not directly on the old main: manifest version 2026.11.03.79 → 2026.11.03.80. Base social cases 449; 48 original synthetic situations with 48 unique responses, proposed total 497. Categories: congratulations, support, opted-in humor, strong-language understanding, practical conversation, original microfiction. Each response includes explicit context and a usage boundary; audiences all_ai_bots, no automatic intervention.

Normalized exact input duplicates: 0; canonical token-Jaccard threshold 0.72 rejected 0. Manual semantic inspection complements lexical test. Pack bytes 338198 (<2 MiB), SHA-256 `44466b8ff720b32a9e3d983705ea8d9e41b3e85c1e09e37470ccb062ab19435a`. Changed pack, manifest, retrieval assertions (48 new searches), and this progress document. No private chats, IDs, live features, tokens, scripts for moderation actions or copied stories. Source: public POLICY.md and AGENTS.md at `3390d9f152e630bb6fa8dc1faccdd32222e3e2fc`.

Merge order: PR #116 must first pass all exact-head tests and post-main CI. Then retarget this PR to updated main, confirm actual head and full checks, merge guarded by expected SHA; verify post-main CI before announcing final publication. No BotHost rollout.
