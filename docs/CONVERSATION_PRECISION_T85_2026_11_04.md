# T85 — точный разговор и границы контекста (2026-11-04)

- Verified starting main: `fbfd7ba48d2368fc0d9bdf40b226d3bca777778f`; consumer-specific claims deliberately excluded.
- Existing records: 84; added 48 canonical situations, 96 search aliases, 144 original answers; total 132 records.
- All answers synthetic and read-only, suitable for `all_ai_bots` only on direct/private/group-addressed utterances. No chat data, identifiers, actions, sanctions or capability claims.
- Coverage: ambiguity of consent, short follow-ups, missing attachments, source uncertainty, bounded humor, accessibility, privacy and honest capability reporting.
- SHA-256 of actual UTF-8 pack bytes: `cfa59cbab852ec8f4042f4d7c2e53918716aa3b7c91447f1b4d44bd2fc255b15`; manifest version `2026.11.04.018`. Normalized cross-pack query and response duplicates checked before commit; high-Jaccard canonical overlap rejected.
- The qa.v1 triples are **not** represented as 100/100 reply-catalog sets. Existing 119 complete reply-catalog sets are unchanged. No incomplete set is created in that separate catalog.
- Verification: `python scripts/validate_pack.py`, `python -m scripts.test_conversation_precision_t85`, local search and exact-head GitHub Actions; publication requires green checks and post-main validation.
