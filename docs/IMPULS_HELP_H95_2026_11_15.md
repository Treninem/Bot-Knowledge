# ImPULS H95 — scoped replies and follow-up failures (15 November 2026)

Continues PR #666 from exact parent `c85a01f49355372fc400002a7738f3e4b5f4272e`; source main `6c9f430da47f137d39a72bbd28c057cfb8f6be96`. Read-only ImPULS main `54b8a3a813fec82c1f953408942ba327eb181c37` (README: 1.6.263 candidate, installed 1.6.262; live AI quality not accepted).

This batch adds **50 newly written, synthetic, context-specific Russian reply candidates for 49 tracked canonical intents**. The greeting intent receives 2 distinct responses: a short private check-in and a group greeting without disrupting other speakers. Other cases address clarifying failed steps, ambiguous settings, roles, group/DM boundaries, games, privacy-safe complaints, misleading version claims and stopping unwanted humor.

Lineage in this PR: H1–H94 = 3,807 staged; H1–H95 = **3857 staged** plus 275 earlier published answers for these 100 intents. **5868 numerical slots remain**, all 100 tracked sets partial, zero certified 100/100 and zero new editorially approved or registered answers. Other open PRs are not included in this count.

A locally executed GitHub connector preflight checked all 50 entries against published records and the H93/H94 stages for normalised exact reuse and high lexical overlap. Full H1–H95 lineage, privacy, schema-like constraints and real raw file hash are checked by the exact-head CI workflow on this PR. This does **not** constitute independent semantic approval, cross-PR clearance, or live consumer integration.

**DRAFT/BLOCKED** for merge: independently review meanings against #662–#665, demonstrate consumer context/role routing, fit registered packs within 8 MiB and verify manifest/cache invalidation. No ImPULS write, deployment, live cache change, sanctions or paid service.
