# T92 — English pragmatic boundaries (04.11.2026)

Base BK main `5308d3c6be848f6d436935fcdac01533634e3954`; authorized by `docs/OWNER_AUTOMATION_SCOPE_2026_11_02.md`. `packs/ru/english_conversation_nuance_qa.json` grows from 62 to 87 canonical questions: +25 original English situations, +50 query aliases, +75 context-specific responses. IDs `en_nuance_t92_001..025`. All new intents are partial 3/100; 97 remaining each *only if* more genuinely different cases can be written. No existing complete reply-catalog intent was modified (119 earlier verified).

Focus: limits of casual promises, polite declines, implicit agreement, temporal vagueness, uncertainty, apparent permission, meaningful corrections and idioms. Distinct speech acts, not random synonym swaps. Synthetic public examples only: read-only, `all_ai_bots`, `en`, addressed direct/private/group contexts. No sanctions, hidden state, private messages or consumer changes.

Compared new queries with the QA corpus read from BK PR #216 parent (2,253 records in 11 QA packs): zero normalized duplicate queries; zero high-Jaccard overlaps >= 0.73. New fixed-count test plus T92 local SHA/QA/search regression. Manifest version `2026.11.04.025`, pack digest `d5b7f955d8e88e5e77ab2573cf0788dec8f4e3051fd5f41c30e065e3bc8466d0`. Require exact-head and post-main GitHub Actions to claim publication.
