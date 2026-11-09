# T505 — third practical continuation for ten stable intents (2026-11-09)

Created from exact main `d02a9a195414e66e69727ee9cacd0672b6a4b15c` after [PR #564](https://github.com/Treninem/Bot-Knowledge/pull/564) merged. **100 new independent context-specific Russian reply candidates** (ten per stable intent). Prior T503+T504: 200; cumulative stages T503–T505: **300** across ten intents, each **30/100**, remaining **70** per intent (**700 total**). Newly completed sets: **0**.

Stable intents: `verify_numeric_context`, `interpret_relative_time`, `conditional_steps`, `safe_bug_report`, `fact_vs_guess`, `responsibility_boundary`, `restore_missing_step`, `compare_incomplete_criteria`, `explain_known_limit`, `creative_revision_scope`.

Original scenarios include ambiguous capacity/percentages, deadlines and reporting timezones, safety-sensitive conditional instructions, minimal private bug reports, evidence limits, authority boundaries, procedural rollback checkpoints, lifetime costs, known capability gaps and style-constrained creative revisions. Replies are **synthetic only**; each contains scenario metadata, unique identifier, Russian language, neutral style, `all_ai_bots` audience, explicit context-match and read-only/no-sanctions constraints.

Source pack `packs/ru/dialogue.json` unchanged. Manifest SHA-256 `3e63012f2823ea1896e9d9612f68f19a3cf2fe6bbf2c8296fc98ac29fb18a024`; source Git blob SHA `b881d145f634b6104c8538fef708d45162ef3125`. Staging is **not consumer registered**; no change to manifest, production caches, ImPULS or any live service. This is a candidate pool, not proof that any bot can pick the answer or remember it.

Preflight: 100 distinct candidate IDs, 100 distinct normalized replies, 100 distinct context notes; no exact repeats against the previous two stages on the same intent; maximum token-set Jaccard `0.474`. This is a mechanical check, not evidence of semantic independence; quality must still be inspected. Real source integrity, structure, privacy and history validation is required by CI on the exact head SHA before merge. After merge, verify CI on the actual main SHA.

Next stage: continue same IDs from 30/100, without treating alternative spellings of a question as separate intents. 
