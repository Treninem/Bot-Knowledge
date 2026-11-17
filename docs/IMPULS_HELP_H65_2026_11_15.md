# ImPULS help H65 — 15.11.2026

Continuation of Draft PR #666 from head `ff4f2e2694da4137450e7fd0f10a099f7cdb6f7e`. Added **66 original Russian contextual reply candidates** to **33 existing least-covered intents** (two distinct contexts each). Previously those intent counts were **21/100** (including published replies); H65 brings each to **23/100**, leaving **77 per intent**. No 100/100 sets were reached.

Cumulative H1–H64 staged: 2,614; H65 +66 = **2,680 staged candidates** across 100 partial intents. **7,045 numerical positions** remain in those 100 tracked intents, excluding other open PRs. Editorial approvals of H65: **0**, published in main: **0**, consumer registered: **false**. No previous answers have been counted again.

Scope: read-only explanation and clarifying questions for group moderation, local-versus-shared rules, protection of personal information, understanding sarcasm, family of settings/permissions, learning, internal Pulses versus Telegram Stars, and giveaway fairness. Two reply conditions per intent are individually annotated as private or group-addressed; examples are synthetic. No sanctions or settings changes.

Source snapshot: Bot-Knowledge main `6c9f430da47f137d39a72bbd28c057cfb8f6be96`; published `packs/ru/impuls_help_qa.json` SHA-256 `50edd41dc0c6a868577433944e0ff0b2a36c2c9ebe53d587e5cbb4692185bbc9`; ImPULS main read-only `4a3587db879b8f0b7868c33cd719ba039306dab0`, `README.md` checked.

Test: `scripts/test_impuls_help_h65_20261115.py` validates all 65 staged files, actual source hash, cumulative counts and IDs, response role, privacy and contextual restrictions, normalized duplicates and lexical similarity. Exact-head GitHub Actions must confirm execution. Keep H65 out of manifest until independently edited and integration-tested.

**DRAFT/BLOCKED**: full semantic audit against other open PRs and response selection by a compatible consumer are not yet certified. Registration would require separate size-budget review against the 8 MiB consumer limit, new real package SHA-256 and tests. Never claim these staged replies are available to a live bot.

Next: continue partial intents outside this least-covered group, then review staged candidates for safe selective publication.
