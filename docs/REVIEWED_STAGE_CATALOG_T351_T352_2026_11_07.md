# Read-only catalog T351/T352 — 2,644 staged replies (2026-11-07)

Parent current main: `eec7d49bc894a1d8093597ce27ce0a8d60357c7c` from merged PR #395 (T351/T352). This *index-only* change creates **0 newly authored replies**; the 92 original responses belong exclusively to #395 and are not double counted.

Target inventory: **2,552 → 2,644 staged** responses across **46** intents, 22 × 58 staged Russian colloquial and 24 × 57 staged practical. Registered 414 unchanged; combined **3,058/4,600**, 46 partial sets, 0 at 100, **1,542 missing**.

The offline reference resolver recursively validates source pack manifest SHA-256 and immutable stage parent ancestry through T351/T352, unique IDs/text and scope metadata. It selects only after the caller independently confirms exact intent, direct address, permitted reply ID, audience, context and local approval; it is fail-closed, issues no sanctions and executes no actions. No consumer rollout or local cache change. The registered manifest and version remain unmodified.

Run `python scripts/validate_pack.py` and `python -m unittest scripts.test_reviewed_stage_catalog -q`; require exact PR head SHA CI, successful actual post-main CI for PR #395, fresh base/head, and post-main CI for this merge. No paid resource or ImPULS change.
