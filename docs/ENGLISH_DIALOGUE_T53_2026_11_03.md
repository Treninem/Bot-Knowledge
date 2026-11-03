# T53 — English nuance: dark humor, profanity and contextual corrections

Base main `2bc9d4ad0b133da508ff956d3969d37871a156f6`, manifest 2026.11.03.131. Added **36** original anonymized EN cases (`en_t53_001`–`en_t53_036`), 12 per dark_humor, profanity and context. The entire English pack moves from 522 to 558 cases. Gap-focused growth: previously 4 dark_humor, 13 profanity, 13 context cases; after addition 16, 25, 25 respectively.

Dark-humor examples are fictional and mostly explicitly requested; grief and real accident examples correctly decline a joke. Profanity cases distinguish exclamations, quoted abuse and directed insults, without applying sanctions. Context cases test referring expressions, local corrections, acknowledgments versus consent and privacy between private/group conversations. All new records are English with Russian `meaning_ru`, explicit `avoid`, audience `all_ai_bots` and no personally identifying details.

Validation at authoring: 0 exact normalized input and response duplicates against the 522 old entries, all new IDs unique, no near input overlap with existing cases at Jaccard >=0.78, original material rather than copied chats. `english_dialogues.json`: 301205 UTF-8 bytes, SHA-256 `29a03142d080188d5c808da9967938c60cc37c78daceb78fbae106bfecd8efa8`; manifest 2026.11.03.132 SHA-256 `05e06e3c1f36b9df036d7e3755fc093c59a7f6f4760e93e70984eb9a96df57a1`. New test `scripts/test_english_dialogue_t53.py` in read-only quality workflow checks SHA, size, ID/counts, privacy, duplicate normalization and actual local search.

This is portable declarative data, not new moderation powers or verified consumer behavior. Check exact-head CI on final PR SHA and post-main CI on actual merge before claiming publication complete. No ImPULS/BotHost writes.
