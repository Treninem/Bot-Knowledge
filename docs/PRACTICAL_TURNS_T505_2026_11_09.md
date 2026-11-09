# T505 — third practical continuation for ten stable intents (2026-11-09)

Created from exact main `d02a9a195414e66e69727ee9cacd0672b6a4b15c` after [PR #564](https://github.com/Treninem/Bot-Knowledge/pull/564) merged. **400 new independent context-specific Russian reply candidates** (thirty per stable intent). Prior T503+T504: 200; cumulative stages T503–T505: **600** across ten intents: two at **100/100**, eight at **50/100** (**400 total remaining**). Newly completed sets: **2** (candidate-only).

Stable intents: `verify_numeric_context`, `interpret_relative_time`, `conditional_steps`, `safe_bug_report`, `fact_vs_guess`, `responsibility_boundary`, `restore_missing_step`, `compare_incomplete_criteria`, `explain_known_limit`, `creative_revision_scope`.

Original scenarios include ambiguous capacity/percentages, deadlines and reporting timezones, safety-sensitive conditional instructions, minimal private bug reports, evidence limits, authority boundaries, procedural rollback checkpoints, lifetime costs, known capability gaps and style-constrained creative revisions. Replies are **synthetic only**; each contains scenario metadata, unique identifier, Russian language, neutral style, `all_ai_bots` audience, explicit context-match and read-only/no-sanctions constraints.

Source pack `packs/ru/dialogue.json` unchanged. Manifest SHA-256 `3e63012f2823ea1896e9d9612f68f19a3cf2fe6bbf2c8296fc98ac29fb18a024`; source Git blob SHA `b881d145f634b6104c8538fef708d45162ef3125`. Staging is **not consumer registered**; no change to manifest, production caches, ImPULS or any live service. This is a candidate pool, not proof that any bot can pick the answer or remember it.

Preflight: 400 distinct candidate IDs, 400 distinct normalized replies, 400 distinct context notes; no exact repeats against the previous two stages on the same intent; maximum token-set Jaccard `0.474`. This is a mechanical check, not evidence of semantic independence; quality must still be inspected. Real source integrity, structure, privacy and history validation is required by CI on the exact head SHA before merge. After merge, verify CI on the actual main SHA.

Next stage: continue same IDs from 50/100, without treating alternative spellings of a question as separate intents. 

## T505 second preserved sub-batch

The current branch contains an additional 100 newly authored scenarios for the same ten intent IDs (20 new per intent within T505). T505 total is now 300 newly added, taking T503+T504+T505 to 500 candidate replies, 50/100 per intent, 50 remaining per intent. Second sub-batch covers distinct issues such as net/gross measurement, timestamp precision, guarded updates, reproducible environment differences, sourced statistics, non-impersonation, verification after recovery, licensing and accessibility, and editing with immutable artistic constraints. The previous 100-response commit remains in branch history. Mechanical preflight checks are not equivalent to human validation; exact-head CI on the final SHA is required.

## T505 third preserved sub-batch

A further 100 original context-specific replies have been appended in this branch, another ten per stable intent. Current T505 stage is 300 responses (30/intent), cumulative T503–T505 is **500** (50/100 for each of ten intents), with **500 slots remaining**. Third-batch contexts include weighted averages, changes across calendar boundaries, idempotent actions, reproducible bug conditions, statistical evidence, consent/authority, instruction stop conditions, long-term product viability and text edits with fixed constraints. Prior T505 sub-batches remain in the Git history. No changes to registered packs or consumers. Each final exact-head CI must pass before merge.

## T505 priority completion — numeric context 100/100 candidate coverage

A fourth, checked-in incremental batch adds **50** distinct number-handling scenarios to the persistent stable intent `verify_numeric_context`. This intent now has T503 10 + T504 10 + T505 80 = **100/100 candidate replies**; it was only 50/100 immediately before this batch. Examples cover dimensional consistency, weighted and conditional rates, time units, currency vintages, uncertainty, significant figures, distributions, meaningful denominators and overlapping records. The other nine intents are still 50/100. T505 totals **350 new replies**, T503–T505 **550 across ten intents**; **1 candidate set at 100/100, 9 partial sets with 450 remaining**. This is not consumer-delivered knowledge, and semantic distinctness beyond lexical screening still requires editorial review. The previous T505 checkpoint commits remain in Git history.

## T505 priority completion — relative time 100/100 candidate coverage

Another checked-in 50 context-specific Russian temporal replies cover ambiguous dates, regional calendars, recurring schedules, changing UTC offsets, event-relative deadlines, historical messages, time format and DST risks. `interpret_relative_time` now reaches **100/100** staged candidates (T503 10 + T504 10 + T505 80), as does `verify_numeric_context`. Each of the other eight stable IDs remains at 50/100. T505 has **400 newly created candidates**, cumulative T503–T505 **600**, with **two candidate sets 100/100** and **eight partial sets (400 missing)**. No consumer was updated. The previous four partial commits remain in this PR's history.
