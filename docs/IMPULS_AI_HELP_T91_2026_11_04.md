# T91 — user-facing ImPULS AI modes and controls (04 Nov 2026)

Base: Bot-Knowledge `c7df364dbbcf95e8385276898cd3b7b4879d26c7`; verified public-facing behavior against current private ImPULS main **read only**. Never interpret repository main as a confirmed live BotHost release.

The existing `impuls_help_qa.json` is near its 1 MiB QA bound; rather than overflow or alter old answers, add one coherent `qa.v1` topic pack, discovered via the existing manifest and index. New catalog is `impuls_ai_modes_help_qa`, 25 stable canonical questions (`impuls_t91_001..025`), 50 search variants and 75 original contextual replies. All have the `impuls` audience, direct-addressed, private and addressed-group contexts, read-only constraints, and no actions or sanctions. The 25 new themes are partially developed **3/100**, remainder 97 each if authentic further contexts are found. Completed reply catalog remains unchanged.

Themes include AI on-call vs on-reply vs DM vs admin-only, settings roles, negative/quoted commands, multi-action safety, anti-spam vs quiet mode, game setup vs gameplay, game recommendations, permissions, soft shield, help for newcomers and event/award verification. Public messages and synthetic examples only. No source code, tokens, real Telegram chats, users or internal identifiers are published. Runtime permissions and installed live version must be checked by the consumer.

Pre-commit: normalised dedup across 10 current QA packs, 2228 prior QA records, within-set answer/ID uniqueness, human review of distinct question meanings. The source field references a pinned public Bot-Knowledge help document. Run `python scripts/validate_pack.py`, `python -m scripts.test_impuls_ai_help_t91`, full quality and exact-head CI; check post-main separately after merge. Zero publication or live-bot claims before these checks.

Next: verify real ImPULS Chat/DM integration, then only add genuinely missing user instructions rather than repeat the help catalog.
