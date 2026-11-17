# Context precision v020 — 2026-11-17

Source: published main `0f7ab816903132ed9d499b257f1cce44a9226993`, v019. One additional original Russian context-conditioned answer per existing precision intent: **132 new replies across 132 canonical intents**. All 132 groups advance from 7/100 to **8/100** (92 missing per group); none is complete. Source 924 responses retained unchanged. QA candidate staging was used for review and is removed from final diff.

Context: `all_ai_bots`, direct/private/group_addressed only on direct address; advisory/read-only, no moderation sanctions, unauthorized writes, private details or asserted external capabilities. Consumer must select by current context. This publication does not prove delivery to ImPULS or AuroraFox.

Pack is reserialized from two-space JSON to **one-space-indented JSON**, with byte-for-byte identical old record values and original order, to stay within consumer 8 MiB budget without removing knowledge. Historical v019 test now reads the immutable published commit. New test checks all 132 exact diffs, SHA, privacy, normalized uniqueness, qa.v1 validation and snapshot. PR exact-head workflow runs normal and `python -O` tests.

New actual-byte SHA-256: `55204fa5f9109c1446a00e65beaa726b92d2848f285fd8e04d247cd8063bb66f`; v019 SHA-256: `de8a9735838a31d13dc9702c691a4feda32cbea9f81aed748922366c2cda274f`. Pack size: 294139 bytes; projected manifest+packs snapshot: **8387975/8388608** bytes (633 remaining). Publication gate: successful full exact-head GitHub Actions, independent QA, current main/base compatibility, and successful post-main CI. Do not deploy live bots or mutate their caches.
