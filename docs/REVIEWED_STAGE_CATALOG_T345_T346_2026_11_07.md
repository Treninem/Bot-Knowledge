# ReviewedStageCatalog T345/T346 — pinned read-only index

Parent main: `96dcb7c97b6374d2cfe7b65738446b9856b734d5` (PR #389, 2026-11-07).

The catalog now includes **2,414 staged replies** across **46** canonical intents, up from 2,322 (+92 already authored and merged in PR #389; **no newly authored replies in this catalog PR**). The verified per-intent staged totals are 53 in 22 colloquial intents and 52 in 24 practical intents; registered 414 are separate, combined 2,828/4,600, remaining 1,772. The catalog recomputes its cache identity using the manifest and each reviewed stage byte stream, and recursively validates history/provenance. `qa.v1` registered manifest and all package SHAs remain untouched.

Fail-closed lookup requires a trusted caller to supply an approved exact reply ID, confirmed audience and context, direct address and local permission; denies unknown, quoted, untrusted and recently used IDs. It does not automatically route questions or carry out actions or sanctions. Candidate staging **is not registered in manifest and is not deployed to ImPULS or any consumer**.

Test: `python scripts/validate_pack.py`; `python -m unittest scripts.test_reviewed_stage_catalog -q`; current exact-head CI and post-main actual SHA gate required before merge. Follow-up: continue original contexts T347/T348 after semantic review, with source and immutable-stage SHA.
