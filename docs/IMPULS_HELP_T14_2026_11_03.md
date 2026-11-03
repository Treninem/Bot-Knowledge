# T14: ImPULS user help without internal terminology

Snapshot: Bot-Knowledge main `3b3880c31c0054a02b203972a2945fc5e49f1b74` / manifest `2026.11.03.87`. Read-only verified ImPULS main `c45a47fb558451680db11806e36d4e356ef61947`, docs/FEATURE_MAP_V30.md blob `14f8db1d7dd0855821bf995b6170288add197c12`, docs/COMMANDS_MATRIX_V30.md blob `557aee6b97dc8f2c9a406bb7ff4907a52ebb5527`. No ImPULS files modified. Only document-confirmed menu names are mentioned, never guaranteed as active live functions.

- Existing ImPULS QA: 537. Added 41 canonical natural questions, 123 approved answer strings and 82 question aliases. Proposed total 578. Existing records not removed or rewritten.
- Topics: profile, card, passport, showcase, contribution, leaders, rhythm, community hub, shop/treasury/gifts/boost, explicit slash names, private management menu, and natural questions without BK section knowledge.
- Question/alias exact normalized collisions across both product and universal QA: 0. Maximum token-Jaccard between new canonical and prior/new canonical questions: 0.750 (not a guarantee of semantic uniqueness; checked editorially).
- Added variants use existing qa.v1 with scope `impuls`, explicit group/private addressing, three truth-preserving answers per question; never permissions, actions or sanctions.
- Package bytes: 641092; SHA-256: `49c13a3a0722084527eeabe437bb9ff3aaeb9af702150ca049e9aa534df0b93f`; manifest `2026.11.03.88` SHA-256 `f78c12e48e3546afb3f3a1784c5c003a528a8c2532e89f26c442bd621f8486b0`. Each pack below 2 MiB; this qa.v1 pack below 1 MiB.
- Test: `python -m scripts.test_impuls_help_t14`, `python scripts/validate_pack.py`, all relevant CI on exact head, post-main CI after merge. A green build does **not** prove live BotHost delivery.
- 100/100 family count: 0 new (these are qa.v1 records with 3 distinct answer renderings, not reply_catalog sets).
