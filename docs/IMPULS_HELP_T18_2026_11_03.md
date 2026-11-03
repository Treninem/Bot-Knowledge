# T18 — understandable explanations of ImPULS functions (03.11.2026)

- Starting Bot-Knowledge main `c494879d0c7a76bc8b14a27fef60b7ef1e87d90b` and manifest `2026.11.03.96` after post-main CI PASS for #133.
- ImPULS read-only source `0979092ea6fdf9787ed02c40a88ed4e2a437edf1`: `docs/FEATURE_MAP_V30.md`, `docs/COMMANDS_MATRIX_V30.md`, `docs/BOT_KNOWLEDGE_SKILLS_INTEGRATION.md` (v30 source describes categories; no claim about live BotHost).
- 26 new questions, 52 distinct search aliases and 78 original scoped answers. Exactly 0 rejected normalized duplicates. `impuls_help_qa` 634 -> 660 records.
- Topics: conflict signal, hotspot, shield and retrospective review; local learning categories and corrections; initial setup vs release and diagnostics; season/rating, weekly gifts, boosts, inventory; privacy and separation of explanation from action.
- Pack 750132 bytes, SHA-256 `2ebca5bb5959fbe937f293f452d89032f3c39371541d16b783f377e76c26df29` and manifest `2026.11.03.97` SHA-256 `a5cce082ea17e267bfc19d7e0780b737df0b6b01164168275f24182aada5b3e6`. All qa.v1 entries are read-only, no personal data, require direct address, audience `impuls` only.
- `scripts/test_impuls_help_t18.py` checks integrity, index lookup by all 78 questions/aliases and audience isolation. Exact-head GitHub CI and post-main must be separately verified before claiming publication.
- No reply_catalog changes: 119 completed 100/100 sets; no new partial sets. No ImPULS source changes, no deployments, no GitHub tokens supplied to bots.
