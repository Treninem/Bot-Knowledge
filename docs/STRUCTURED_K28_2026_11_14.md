# K99 / K28 · 14 November 2026

PR #661, branch `bk/structured-information-k-20261111-2100`, source main `6c9f430da47f137d39a72bbd28c057cfb8f6be96`. Previous 54 intents each had 92/100 candidates (3 registered + 89 staged), and PR K1–K27 had 4,320 staged responses.

**This stage adds 54 original synthetic Russian replies**, one contextual variant per existing intent, making PR K1–K28 **4,374** staged replies, combined 54 × **93/100**. Zero newly completed 100/100 sets, 54 partial sets, seven missing per intent, **378 remaining**. K99 content is `consumer_registered=false`, `all_ai_bots`, direct-address and context-match only, read-only, and cannot grant sanctions.

Preliminary checks: 54 entries and replies; 54 distinct situational notes; content and context lengths above minimum; no normalized exact matches or high token-Jaccard ≥0.70 among K26–K28. Check `scripts/test_structured_k28_20261114.py` across K1–K28 plus source pack; the read-only workflow must complete for the current exact head before claiming full machine QA. No local Python run was possible because the container could not resolve github.com; GitHub-sourced tests are distinct from independent editorial approval.

**DRAFT/BLOCKED:** review all semantics and application conditions independently, prove consumer routing and snapshot delivery under the 8 MiB limit, reconcile current base/head, require complete exact-head CI. No manifest registration, live consumer change, ImPULS or BotHost edits, secrets, paid services, or cache mutation.

Next: refine overlapping contexts if found, then K100 only for truly distinct situations.
