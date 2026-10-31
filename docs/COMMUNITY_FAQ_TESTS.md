# Community-bot FAQ: three synthetic, review-only candidate skills

This is a minimal test-only addition for the existing community-bot use case, not mass vocabulary expansion. The public pack contains **three original generic Russian FAQ replies** about anti-spam settings, voluntary family-game relationships, and optional free raffles. It contains no real chat text, identities, local rules, credentials or operational instructions. No paid APIs are used.

## Why just three?

The existing `packs/ru/skills.json` already covers chat settings (`bot_help_chat_settings`), rules (`bot_help_rules`), reports (`bot_help_reports`) and general social replies (`respond_to_thanks` and others). Repeating those entries would create duplicate phrases, not capability. This addition focuses on three missing short FAQ topics.

ImPULS's repository README (consulted read-only on 2026-10-31) documents these general features. The wording here was newly authored for synthetic tests, not copied from any chat. Documentation of a feature does not prove that it is enabled in a particular chat.

## Scope and verification

- Each record is declarative `kind=bot_help`, `audiences=["community_bots"]`, with explicit when/avoid conditions. No action, sanction, API call, token or permission grant is present.
- A consumer must independently confirm the current chat, enabled settings, caller role and consent. Retrieval is only a suggestion, not authorization to act.
- `scripts/test_community_faq.py` checks 10 distinct synthetic audience/retrieval cases, duplicate IDs and phrases against the existing skill pack, no personal identifiers, unsafe fields, and deliberate SHA mismatch followed by an independently SHA-pinned fresh snapshot.
- New manifest version is `2026.10.31.4`; old package SHA-256 values are unchanged. Consumer caches must refresh only after marker/version/checksum validation and retain the last valid snapshot after rejection. This PR does not invalidate any live cache.
- A new read-only GitHub Actions workflow validates all manifest packs and runs these offline tests. Existing quality workflow is left untouched to avoid interfering with pending CI test PRs.

## Boundaries

New examples are review candidates, not enabled bot functions. Current ImPULS KnowledgeSnapshot does not automatically consume a newly added pack; a separate, tested read-only consumer integration and human approval would be required. This PR must not be merged or deployed without the owner's separate decision.

Run inside a full repository checkout: `python scripts/validate_pack.py` and `python scripts/test_community_faq.py`.
