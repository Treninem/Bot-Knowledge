# T48 — original English in context (2026-11-03)

Base main `586d4f098fbcba6c2fbc9d3179792e4a82307772`. Adds **56 distinct English situations and 56 original replies**, eight per category: conversation, idioms/slang, sarcasm, rules, deception warnings, support, and short creative fiction. Each includes its own `meaning_ru` and `avoid` conditions. Stable IDs `en_t48_001`–`en_t48_056`.

Total English cases **410 → 466**. No exact normalized duplicate input/response against entire old and new pack. Max input token Jaccard 0.417 (pair en_t48_049 / en_t45_025). Previously saturated idioms omitted; this screening supplements manual meaning review, not a claim of perfect semantic uniqueness.

Pack bytes **251656**, SHA-256 `15697b4ca995af8164b9fbb698d1b9e55488e5455548540ac91cb197d53e4943`, safely under 2 MiB. Manifest `2026.11.03.127`, SHA-256 `9177f868dfba789186fded264b792b9f8796aaf667a7c6f2c126e9590d42b681`. Existing package hashes unchanged, no live cache operations. Approved audiences `all_ai_bots`, English plus Russian context notes, no sanctions. All examples are original synthetic texts free of private chats, personal data, handles and secrets.

Validation required: `python scripts/validate_pack.py`, `python -m scripts.test_english_dialogue_t48`, full quality suite at current exact PR head and post-main suite on the real merge SHA. No consumer integrations and no live BotHost changes. Not counted as 100/100 canonical reply sets.
