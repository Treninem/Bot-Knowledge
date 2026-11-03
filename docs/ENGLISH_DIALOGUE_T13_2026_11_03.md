# English dialogue T13 — contextual bilingual QA

Stacked on social PR #124 head `11c1678cda3673e7e5a96ed1b86b24c6c37f1b3f`; main source snapshot `6f1c7d256a287ef5d647c01a3947b5c2a42d9677`. This PR only changes English language data, matching manifest, regression test and this note.

New synthetic language cases: **32** original English prompts and **32** English responses (original 106 → 138), 1 exact-normalized candidate duplicates rejected. Types: {"conversation":5,"slang":5,"sarcasm":4,"profanity":2,"rules":4,"deception":3,"support":3,"creative":3,"context":3}. Each record carries `language: en`, reviewed Russian meaning, audience `all_ai_bots`, and conditions limiting unsuitable use; no factual ImPULS claims, personal data, copied conversations, sanctions or active commands.

Pack SHA-256 `dc8da671431e9d0e5e0442c1360c8abbeef8b35f273082937de4dea726000372`, actual UTF-8 size 72393 bytes; manifest/cache version `2026.11.03.87`. Under the 2 MiB consumer download limit. Expanded existing Python test to require all new exact-input local search hits and retain earlier T11/T12 coverage. Exact-head CI and post-main CI remain mandatory, plus re-target onto fresh main after #123 and #124 merge. No BotHost rollout.
