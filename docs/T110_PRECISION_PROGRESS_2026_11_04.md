# T110 — контекстная точность QA, 04.11.2026 (latest checkpoint)

- Main/base (unchanged): `23871ed224cbe0d9636c841fd48e3f43bdd3ed1b`. Branch: `ai/t110-precision-context-20261104`, PR #227. This is **Draft**, not published.
- 132 established intents in existing `packs/ru/conversation_precision_qa.json`. Initially 396 replies (132 × 3). First checkpoint +174; second checkpoint +132 (one newly authored contextual option per existing intent). **Total cumulative PR delta +306 NEW**; 702 in Draft, 0 complete 100/100 sets.
- T77: 42 intents × **6/100**, 94 missing each = 3948. T82 and T85: 90 intents × **5/100**, 95 missing each = 8550. All **132 partial**, total 12,498 missing to reach 100 per intent.
- Excluded as duplicates/incorrect in authoring review: 0 entered to package after revision. No new canonical question count. No newly claimed bot capabilities.
- Actual current UTF-8 pack SHA-256: `c3df1b51c7dd3b68a504760a5f71d4fc569ee25f8fc1fdffb102d97e234be714`, size **239934 bytes**; manifest version `2026.11.04.033`.
- Base snapshot 7,519,262 bytes (38 packs + manifest). T110 proposed snapshot: **7579442 / 8,388,608 bytes** (headroom 809166). Per-pack 2 MiB check PASS. **Consumer ImPULS may have lower total loader limit; not verified.**
- Executed on latest second checkpoint in-process: SHA-256 test vector and prior blob manifest hash PASS; 702/702 normalized exact unique in pack; no same-intent near duplication at Jaccard ≥0.70 (max 0.211 for second batch); preserved questions, aliases, IDs, scopes, and existing answers. First checkpoint cross checked 174 new versus 6,472 replies in 10 other QA packs, exact overlap 0. Need rerun cross-pack on second delta.
- Python regression scripts for T77/T82/T85 and new T110 were updated. These are **not local Python execution results**. Exact-head check-runs must be reverified on this newest SHA.
- Changed seven paths only (pack, manifest, three existing test scripts, T110 test, this checkpoint journal). Scripts `trusted_publish_qa.py` and `prepare_knowledge_candidate.py` are owned by #224 and **untouched**.
- BLOCKED for merge until Python tests, exact-head CI, SHA/cache and consumer compatibility checks. No updates to ImPULS/BotHost.
- Next: check entire QA corpus for second-batch duplicates, re-run local Python tests on an actual checkout, verify consumer load budget and context selection; then continue meaningful partial sets in approved qa.v1 limits.
