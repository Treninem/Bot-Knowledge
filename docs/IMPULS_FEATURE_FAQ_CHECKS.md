# ImPULS: three narrow synthetic feature FAQ candidates

This is a review-only, minimal **three-entry** pack, not a mass language import, a deployment or proof that any feature is available on a specific live BotHost/Telegram instance.

## Verified purpose and immutable read-only references

ImPULS main inspected at commit `1b0e6a2dd3e6ece7e8b7c7fc4b983e2a3e01b2b2`. Public/repository sources (no personal messages):

- `Treninem/Impuls/docs/COMMANDS_MATRIX_V30.md`: group `пульс` and `ритм дня`, private menu roles/settings.
- `Treninem/Impuls/docs/RELEASES.md`: 1.6.33 and 1.6.37 describe the Pulse ledger UI; 1.6.16 and 1.6.62 describe a daily word-chain game; 1.6.36, 1.6.70 and 1.6.74 describe chat-specific rights checks.
- `Treninem/Impuls/docs/BOT_KNOWLEDGE_SKILLS_INTEGRATION.md`: shared skills require explicit read-only consumer integration and cannot grant rights by themselves.

Three original **synthetic** prompts/replies cover (1) opening one's Pulse journal, (2) locating the daily word-chain task, and (3) chat selection and permission re-check. Existing `packs/ru/skills.json` covers generic games, currency, moderation, chat rules and rights; the open PR #35 separately covers anti-spam, the family game and free raffles. These topics intentionally are **not** duplicated.

## Safety and testing

- `kind=bot_help`, `audiences=["community_bots"]`; response may be suggested **only after** the consumer checks the chat, membership, role, feature availability and address/intent. No moderation actions or sanctions may be taken from the FAQ.
- Public data are generated from scratch; no user IDs, names, Telegram chat content, local rules, tokens or other secrets. No paid API.
- The package is pinned to manifest version `2026.10.31.5` via SHA-256 `9664686e2a018a01d894e9100f93d928a8a388fff08b94c6daa3b23abeda030b`. Existing 25 package SHA values do not change. Any consumer must verify manifest and checksum, refuse a corrupt snapshot, and refresh its own local cache only on accepted version/SHA. This PR does not clear or deploy any live cache.
- `python scripts/validate_pack.py` checks all package hashes and safety. `python scripts/test_impuls_feature_faq.py` validates schema, policy, de-duplication against the existing skills, 10 distinct scoped probes x 10 rounds, and old/new SHA-pinned cache isolation after a forged file change.
- Legacy index tests previously used an exact baseline of 1179 records; those assertions become lower-bound checks while the new targeted test requires **exactly 1182** total records on this branch. This is not a claim of semantic accuracy of a live model.

Review-only: **no merge, no BotHost update, no changes to ImPULS**. This PR may need a manifest/workflow reconciliation with other open PRs (#30, #32, #34, #35) before owner-approved merging.
