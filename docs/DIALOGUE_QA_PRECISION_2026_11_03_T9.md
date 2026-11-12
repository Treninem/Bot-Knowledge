# Universal dialogue precision QA — 2026-11-03 (.76)

Base main `c7449b8dedcc1caba16ed9a4726599028600d6b9`, manifest .75. Universal QA before: 111; new original questions: 29; new reply texts: 87 including two context variants per record; search aliases: 58. Result: 140 universal qa.v1 rows. Distinct from 100/100 reply_catalog sets (unchanged). ImPULS qa.v1 537, unchanged.

Focus on keeping already-given constraints, one-turn style, pause vs cancel, conditional exceptions, exact scope and permission, evidence provenance, privacy, careful summaries and beginner help. All entries original and synthetic, read-only all_ai_bots, no implied execution and no live ImPULS claims. Public source: AGENTS.md at base commit.

Pre-commit duplicate audit: normalized exact clashes 0, largest question-token Jaccard 0.300, none crossing threshold 0.60. Manifest SHA-256 for pack: `78530bf546a52867215aeee7bc8bef7291246ef3c8478baa9ddb7836d54ff845`; pack UTF-8 182512 bytes, below qa.v1 1 MiB and consumer 2 MiB. New exact/alias retrieval regression covers 87 queries. Local Python checkout unavailable due DNS; authoritative CI checks must run on exact PR head and after merge. No BotHost deployment.
