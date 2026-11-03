# T14: English natural dialogue and context boundaries

Base Bot-Knowledge `main` `b86f6cf0add0852a33f1dca6031a1ab4b04971c8`, manifest `2026.11.03.89`. Added 32 original synthetic English input/response scenarios with Russian meaning guidance and specific avoidance notes, to the existing `english_dialogues.json` pack; 138 → 170 cases. Scope remains `all_ai_bots`; moderation cases are explanatory only and no sanctions are permitted. No real chats or IDs.

New categories: {"conversation":7,"support":5,"context":6,"rules":4,"slang":4,"sarcasm":3,"creative":3}. Normalized exact duplicate inputs/responses: 0; max cross-corpus input token Jaccard 0.500. Package 89471 bytes (well below 2 MiB) SHA-256 `4eb4467dbdceaa5428d29063edf369459bf53cbcbf745f2ee06fa248b0d4290a`; proposed knowledge_version `2026.11.03.90` manifest SHA-256 `3c71cec25e8998f2eec4c3d476e71dcbcb157d93cf499e71fdd0873f11aa3cec`.

Run `python scripts/validate_pack.py`, `python -m scripts.test_english_dialogue_t14`, exact-head CI, post-main CI. Publication to GitHub does not prove live delivery to ImPULS/BotHost. The 100/100 reply catalog has not been changed; this is a separate structured dialogue pack.
