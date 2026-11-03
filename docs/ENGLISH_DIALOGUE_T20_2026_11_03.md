# T20 — English natural conversation and contextual understanding (03.11.2026)

- Base content after T19 branch `46f6f7d3feaab61b43e61d4a4946f328aff191e3`, to be retargeted to main after PR #135 and post-main CI are confirmed. ImPULS and BotHost are read-only / untouched.
- 32 new original English input/response pairs with Russian explanations: conversation 5, support 5, slang 5, sarcasm 4, rules 4, deception 4, creative 5. Existing cases 170 → 202.
- No published chats, account details, identifiers or executable commands. Similarity check found no existing inputs with token-Jaccard ≥ 0.65 for new questions; 0 normalized duplicates.
- English package size 107244 UTF-8 bytes; SHA-256 `dacfbf49b0e688091fb70e02e37e8b7eb38bcc1b8221d1b71cf6f221c8cac25f`; manifest `2026.11.03.99`, SHA-256 `7e213d222e988b5bfa2856a9d0822ba351773503dcfc2d47fba886222d211657`. Each pack is under 2 MiB.
- T20 quality test covers pack SHA, ID/input/response uniqueness, intended language and audience, privacy and 32 local retrieval queries. PR exact-head and post-main checks require actual GitHub outcomes; no consumer delivery claim.
- `reply_catalog` and ImPULS files remain unchanged. This package does not add 100/100 reply sets.
