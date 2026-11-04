# T73 — Context-sensitive decisions and safe boundaries (2026-11-04)

Main baseline `bb99012290beb5d3249dee07eb7ad321fe7fd9f3`, manifest `2026.11.04.006`, 140 existing cases.
**30 new distinct original synthetic cases**, 3 each in 10 established categories,
for a total of **170 cases (17/category)**. This is a set of contextual example
decisions, not 30 new reply variants and not completion of any 100/100 intent.
Topics: references, evidence strength, execution honesty, privacy, tone and
de-escalation, contextual moderation, role/access isolation, recovery, multi-intent,
and verifiable publication. All examples are original and do not quote real
private messages. Moderation-only examples use `chat_moderators` and
`human_review`, with no automatic punishment. Role-scoped examples use
`community_bots`; general cases use `all_ai_bots`.

Original 140 cases preserved, T69 cohort remains 60. Existing
`test_context_cases.py` now checks the additive 170 baseline and T69 cohort
unchanged, plus the separate T73 regression validates 30 IDs, 10 categories,
SHA/size, scope, exact and normalized input dedup, and local search.
No new permissions, chatbot state or deployment.
Manifest/cache version `2026.11.04.007`; pack UTF-8 length **112661**
and SHA-256 **f12c5d4bb355b75d78217304ee3a91b1df7982be43b6b8bd06d8696fa82db5d1**.
Check exact-head six real CI, then post-main quality on actual merge SHA.
No changes to ImPULS or live bots.
