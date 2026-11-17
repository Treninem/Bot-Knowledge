# ImPULS H94: user requests and recovery contexts (15 November 2026)

Continues [PR #666](https://github.com/Treninem/Bot-Knowledge/pull/666) at parent `0e54b191bbee24eb9449bdd2fa6cc08ccfb37b42`, published source main `6c9f430da47f137d39a72bbd28c057cfb8f6be96`, and read-only ImPULS main `54b8a3a813fec82c1f953408942ba327eb181c37` (`README.md`: installed 1.6.262, candidate 1.6.263, live AI quality unaccepted).

H94 contains **50 new original synthetic Russian reply candidates for 49 canonical intents**. All 39 intents untouched by H93 received a new contextual response. Seven lowest-coverage intents increase **30→31/100**; `greeting` increases **50→52/100**. Two additionally revisited topics cover staged-versus-live knowledge and privacy-preserving group reports. Explicit chat/DM/direct address, read-only behavior, privacy and no sanctions are retained.

Across tracked H1–H94, staged total is **3,807**, published baseline is **275** for these 100 intents, **5,918 numeric positions** remain. **100 partial sets, zero independent 100/100 approvals, zero new main registrations**. Count only this stage's delta (50); older stages are not new work in this cycle. Other PRs are excluded from these per-intent counts.

Stage: `staging/ru/impuls_help_context_h94_20261115.json`; full-lineage test: `scripts/test_impuls_help_h94_20261115.py`; existing read-only exact-head workflow extended to run H94 in normal Python and `-O` and log real JSON SHA-256.

**DRAFT/BLOCKED**: editorial semantic assessment with other open PRs, demonstrated working ImPULS chat/role routing, size-safe published manifest/cache update, and exact-head/post-main quality gates remain required. The offline fail-closed **H93 preview** is a test fixture, not live integration. The staged H94 candidate pool has no manifest registration. No live-bot deployment, private code modification, payments, branch protection changes, or working cache edits. Do not call new candidates approved until reviewed.

Next: inspect exact-head H94 and full quality CI; correct failures, record raw SHA, select editorially useful nonduplicated responses, then test consumer integration before any publication.
