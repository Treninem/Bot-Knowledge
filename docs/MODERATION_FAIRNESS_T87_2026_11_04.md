# T87: moderation fairness language, 2026-11-04

Starting main: `e1795b9427706298e01163a40d5319b85915e281`. Direct maintainer authorization: `docs/OWNER_AUTOMATION_SCOPE_2026_11_02.md`. Public source `docs/REQUIREMENTS_21.md` pinned to `b3ff785098b44bc2d7d4846260a682d402dbaeb8`.

36 different canonical questions, 72 aliases, 108 original synthetic answers, 0 discarded candidates. New independent `qa.v1` manifest-discovered pack, purpose moderation_language; strictly `chat_moderators/community_bots`, addressed direct/private/group contexts only. No actions, bans, tokens, raw chats, user identities, or private ImPULS code.

Progress: 36 stable intent IDs `modfair_t87_001..036`, initial 0/100, added 3, now **3/100, 97 remaining per intent**. This is not 36 completed sets; do not fill the remaining slots with synonyms. Context criteria and exclusions are in the question, aliases, answer and variants; full scopes are on each record. Existing 119 completed reply-catalog intents unchanged.

Pack UTF-8 size 49797 bytes (below 1 MiB), SHA-256 `b59c00dbf7d8f3d57ee514764a731ddb5233d898bf24125c5180a8fd0dbd6fb8`; manifest/cache version `2026.11.04.020`. Live caches untouched. Test via `python scripts/validate_pack.py`, `python scripts/validate_qa_v1.py`, `python -m scripts.test_moderation_fairness_t87`; exact-head and post-main CI required before accepted merge. Next: resolve remaining public bot-help knowledge gaps independently; do not infer unverified features.