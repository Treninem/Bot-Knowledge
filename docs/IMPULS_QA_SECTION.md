# ImPULS qa.v1 bot-help section

Trusted producer target: `packs/ru/impuls_help_qa.json` (manifest-registered; `catalog.adapter=qa.v1`; `catalog.id=impuls_help_qa`; `catalog.audiences=["impuls"]`).

This is a **new independent data pack**, not a conversion of `reply_catalog.json` or `skills.json`. It includes 24 synthetic, manually composed canonical questions and 24 additional answer variants about public bot-help scenarios. Its knowledge is read-only and scoped to direct address, including personal and addressed group contexts. No chat-specific rules, raw messages, usernames, secret implementation, automatic sanctions, or GitHub write token are included.

The trusted publisher requires candidate `section_path` to exactly equal `packs/ru/impuls_help_qa.json` and requires `reviewed=true`, valid source, and an already registered package. A new producer candidate is **not** a live ImPULS deployment or proof of consumption. The consumer/export workflow remains separately owned by the ImPULS maintainer.

Source review (read-only, private repository; do not export private code): `Treninem/Impuls` main `d45d6ceac889f940bc7961704cd1953f88e6872f`; inspected `docs/BOT_KNOWLEDGE_SKILLS_INTEGRATION.md`, `docs/AI_DIALOGUE_LEARNING_20261102.md`, `docs/FEATURE_MAP_V30.md`, `docs/COMMANDS_MATRIX_V30.md`. General safety rules: `POLICY.md`, `AGENTS.md`, `docs/DYNAMIC_QA_FORMAT.md`. The content does not claim that any feature is enabled on a live bot.

This pack supports approved declarative answers only, not executable commands. Each response must still pass the consumer's runtime role, address, and scope checks. New publication requires a reviewed isolated maintainer PR plus exact-head/post-main gates, and changes to the pack require matching manifest SHA-256.
