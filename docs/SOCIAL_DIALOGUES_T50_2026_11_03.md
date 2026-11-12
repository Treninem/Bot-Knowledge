# T50 — new original contextual social replies

Source BK main `5b3567646916f2cb373764480cac418acac98093`. New 48 original synthetic and context-guarded answers, eight per kind: congratulations, support, requested humor, firm responses to rude conduct, natural conversation, short original fiction. Counts: 1259 → 1307 social cases. Stable IDs `talk_t50_001`–`talk_t50_048`.

Explicit user request for humor. Profanity/rudeness replies target arguments or behavior, not identity. Each has a distinct relevant `context` and negative `avoid` guard, universal audience, no personal chats, handles, secrets, protected copied jokes or executable moderation actions. Human meaning review remains needed beyond automatic lexical screening.

Preflight: 0 exact normalized duplicate inputs or responses across all cases; no input token-Jaccard overlap >.62, maximum 0.500. Pack 879910 UTF-8 bytes (<2MiB) SHA-256 `83758ea14f021de8088599e528cfa310ffa559cf0d1ad8ec3fba3ca1b85b1e82`; manifest 2026.11.03.129 SHA-256 `07c781777a54ecfabb5591e3eb2a096d1262d54538aff783fc29c890dbe996e5`. Cache invalidation by version and SHA, no live cache changed.

Tests: `python scripts/validate_pack.py`, `python -m scripts.test_social_dialogue_t50`, full exact-head quality, other required workflows. Merge only after all six tests successful on final head, then verify separate post-main SHA and actions. No ImPULS code or BotHost changes.
