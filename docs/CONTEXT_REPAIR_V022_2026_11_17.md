# v022 — context repair and optional original humor

Source main: `178a1d36062a6b77d62ad83586eb17a26bb20d5c`, manifest `2026.11.17.021`.

This candidate adds **18 conversation-repair intents × 3 original replies = 54 replies** and **10 explicit-humor intents × 3 original replies = 30 replies**. Total **28 canonical intents, 84 candidate answers**. All are synthetic, RU, read-only, no private data or sanctions, with direct-address gates; jokes additionally require explicit user request and appropriate mood.

The 100 published direct greeting responses remain in `dialogue.reactions.greeting`. The separate PR #666 explanatory `greeting` intent is about *why ordinary greetings should not trigger group rules*; its numeric quota must not be mistaken for another set of direct hello replies.

Published source `english_dialogues.json` was reserialized with JSON parsing and `JSON.stringify` only: data objects, order, and values unchanged. Source SHA-256 `4f0d9352ad8d17a34b90a6669a269390ce5d3bf526e06d142b616149ea83a786`, reserialized SHA-256 `b9a718f3815b41e67ca0a4abaec63de16cd889d1ed4b352361226b88fbbf8185`. This frees 98253 exact UTF-8 bytes without removing training examples. Work only on this feature branch, never live cache.

Snapshot estimate including manifest: **8325508 / 8388608 bytes**, free **63100**. Files changed: English JSON, two qa.v1 packs, manifest, validation test, read-only workflow, this note.

Expected tests: `python scripts/validate_pack.py`, `python scripts/validate_qa_v1.py`, `python -m unittest scripts.test_context_repair_v022 -q`, `python -O -m unittest scripts.test_context_repair_v022 -q`. New replies remain candidate content until exact-head GitHub CI and editorial/consumer checks. No ImPULS repository, BotHost, payments, or live bot changes.
