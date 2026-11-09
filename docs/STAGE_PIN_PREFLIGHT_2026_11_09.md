# Stage catalog fast-fail integrity preflight — 2026-11-09

Starting main: `46333f093a677848d214be7850bc3e7ca17b93e4`.

## Problem
`scripts/test_followthrough_stage_catalog.py::test_mutation_of_any_stage_or_source_rejected` intentionally mutates each reviewed stage in turn and reconstructs the whole catalog. Before this patch, a modified stage could trigger many `StagedContextSelector` constructions and historical checks before its blob-pin mismatch was reached. The main quality `validate` job was still running that step at the time of diagnosis; no benchmark or performance claim is made.

## Change
Run a simple Git blob SHA-1 pin preflight for every listed stage **before** constructing selectors. A missing pin or mismatch raises `ValueError` immediately. For valid snapshots, leave the existing selector, parent-chain, audience, SHA-256 manifest, deduplication and privacy checks in place. The entire mutation regression is preserved.

`scripts/test_followthrough_stage_preflight.py` asserts all stages have immutable pins, tampering with the first/middle/last stage is refused before selector construction, and removing the pin fails closed. Registered packs, `manifest.json`, source data, consumer behavior, private ImPULS, live caches and deployment are unchanged.

## Gates
New regression is registered in `.github/workflows/quality.yml` after the pre-existing catalog test. No local full-repository Python test was possible in this connector-only environment. Require completed exact-head CI (actual SHA, not a merge-ref), latest-main compatibility, then post-main validation before merge. Do not bypass pending parent PR #545/#546 gates or count candidate replies as published.
