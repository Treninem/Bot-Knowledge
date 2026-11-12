# T308 — new practical recovery contexts (2026-11-07)

Parent `main` SHA `8c200332f2fac7ca1da943f8c6a51960a8d81623`. Registered source `packs/ru/practical_recovery_qa.json` SHA-256 `be8ae1408cf42816adc3f8ba818b3f004318617ba2e878e72edd85cf7eb4954e`, Git blob `21bf261970d1bdcf0f9fb8fb3383772b86b2dc2f`; preserved T306 stage blob `bdae142af834dc169f9f8c1e17256b7b249b18da`.

New work: **24 canonical intentions × 3 original Russian replies = 72 new answers** and 72 non-repeated context notes, covering diagnostics, privacy, group/DM boundaries, permissions, reporting and reversible tests. Before: 216 registered + 96 salvaged = 312. After T308: **384 / 2400 (24 × 16/100)**, **84 per intent / 2016 total remaining**, 0 new complete sets. T306 salvaged texts are historical, not counted again as newly authored.

Preflight of T308 new rows: 72 unique IDs, 72 normalized unique answers, 72 unique context notes, 0 duplicates compared with T306 + registered; no within-batch token Jaccard ≥0.78. Independent comprehensive semantic review of all unrelated packages not claimed.

New stage is **NOT** registered in manifest or loaded by bots; `scripts/practical_t308.py` pins the source and T306 bytes and denies selection unless the caller provides explicit approved reply ID, direct address, matching context, audience and local permission. No sanctions, autonomous actions, de-anonymization, or live integrations.

Tests: `python scripts/validate_pack.py` and `python -m unittest scripts.test_practical_t306 scripts.test_practical_t308 -q`; exact-head and post-main required. Manifest/cache, working bots and ImPULS unchanged. Next step: extend genuine practical scenarios from 16/100 and implement separately reviewed consumer support for bounded contextual pools.
