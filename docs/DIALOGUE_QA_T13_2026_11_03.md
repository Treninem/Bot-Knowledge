# Universal dialogue QA T13 — verified candidate

Base GitHub main: `6f1c7d256a287ef5d647c01a3947b5c2a42d9677` (manifest .84); existing universal QA: 252.

New synthetic universal topics: 32 distinct questions, 96 authored answer texts, 64 search aliases. 0 candidates rejected by the normalized/existing-canonical overlap preflight. Result: 284 records in `dialogue_help_qa.json`.

Focus: respectful turn-taking, stated conversation boundaries, interpretation of corrections, figurative and mixed-language speech, preserving authorial voice, opinion versus evidence, non-punitive group discussions. Group-specific cases are scoped to `group_addressed`. Every record is read-only, synthetic and for `all_ai_bots`, with an immutable source to `AGENTS.md` at the exact starting commit. No chat excerpts, IDs, personal data, consumer actions or live feature promises.

File: `packs/ru/dialogue_help_qa.json`, UTF-8 365689 bytes; SHA-256 `3abfad517bfa6ff0b6e47a2b63f2a78f4fcc7a188dff056903479455b34e89b1`; manifest/cache version `2026.11.03.85`. The original `reply_catalog.json` is untouched (near the 2 MiB consumer cap). The qa.v1 file remains below the 1 MiB schema cap and the 2 MiB consumer cap.

Checks: normalized questions and aliases compared with both the existing universal and ImPULS QA package; conservative canonical token-Jaccard screen threshold 0.68; 96 exact search assertions added to the current Python test. These preflight checks do not prove complete semantic nonoverlap. Run GitHub quality CI on the actual PR head and post-main CI after any merge; never claim live BotHost delivery from publication.
