# T270 — incremental spoken-pragmatics continuation (2026-11-06)

Base main: \`48b74f4f76c6ec88b7ea7ad557197f461c203929\`.
Source: \`packs/ru/spoken_pragmatics_qa.json\`, SHA-256 \`ac379077dedbdb6202ec96d3f5d141afa017eb48a002c62c5ce2594aee7e1a85\`.
Parent: \`staging/ru/spoken_pragmatics_t251_context_pool.json\`, Git blob \`554bf93eb24f09fdaadf0cf9175997732f8158a0\`.

The existing 1.06 MiB staged pool is immutable for this PR. An additional JSON delta records **120 original Russian contextual replies to the same 24 canonical intents** (5 per intent). Existing source and prior staged material remain unchanged, avoiding a large concurrent rewrite. \`scripts/spoken_delta_overlay.py\` validates parent/source blob and SHA-256, inventory, privacy, normalized duplicates, lexical Jaccard within each intent, and exact opt-in scope before selecting an approved delta reply. It is a reference offline selector, not automatic bot integration.

| Metric | Before | After (parent + this delta) |
|---|---:|---:|
| Registered replies | 216 | 216 |
| Parent staged replies | 1224 | 1224 |
| New additive staged replies | 0 | 120 |
| Per canonical intent, including registered | 60/100 | **65/100** |
| Unfinished intents | 24 | **24** |
| Remaining | 960 | **840** |
| New completed 100/100 | 0 | **0** |

All new replies have unique stable \`_t270_01..05\` IDs per intent, explicit conversation context, intended audience, and a non-action restriction. No user chats, personal information, private ImPULS implementation, penalties, actual bot actions or published consumer version changes are included. No registered pack or \`manifest.json\` modification; no live cache touched. This delta is *not* a separately registered pack and must never be confused with 120 already deployed bot capabilities.

Verification: \`python -m unittest scripts.test_spoken_delta_t270 -v\` plus \`python scripts/validate_pack.py\` and existing regression suite in the exact-head CI. Local repository-wide Python tests were not available in the connector-only environment. Merge only with successful exact-head CI and compatible main; after merge verify post-main CI. Do not use paid Actions, bypass checks or deploy bots.

Next: continue 65/100 in this same intent set with genuinely new situations; use pinned parent/delta provenance, not a second copy of T270 data.
