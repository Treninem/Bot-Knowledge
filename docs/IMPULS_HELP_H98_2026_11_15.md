# H98: scoped Russian user-help candidates — 15 November 2026

Continue [PR #666](https://github.com/Treninem/Bot-Knowledge/pull/666) at source head `33d0844bad34e2c5769bc600ff5bc83831ba4430`. Main remained `6c9f430da47f137d39a72bbd28c057cfb8f6be96` when this batch was authored. The read-only ImPULS reference was `54b8a3a813fec82c1f953408942ba327eb181c37`, `README.md`: installed 1.6.262, candidate 1.6.263.

**New H98:** 50 distinct synthetic Russian context-specific reply candidates over **48 existing canonical intents**, including three additional greetings with separate private, direct and addressed-group contexts. Topics include getting started, privacy, moderation explanations, troubleshooting, settings and permissions, game help, understanding sarcasm and changing conversational tone. The answers are scoped to ImPULS and cannot carry out a settings change or sanction.

**Counters:** H1–H97: 3,966 staged; H98 +50 => **4,016 staged candidates**. Published baseline for the same 100 intents: **275**. Remaining arithmetic positions to 100/100: **5,709**, excluding concurrent PRs. **100 partial intents; 0 completed 100/100; 0 newly independently editorial-approved; 0 newly registered in manifest.** These are not whole-repository totals.

**Validation:** `scripts/test_impuls_help_h98_20261115.py` reads the full H1–H98 lineage, exact published-pack manifest digest, all IDs and counters, normalized duplicates, near-lexical repeats, scope, conservative privacy checks and per-context conditions. The read-only exact-head workflow runs validator and Python normal/`-O` suites. A passing structural test **does not** establish independent meaning review, compatibility with consumer selection by context and role, or delivery to a running bot.

**Next:** semantic review against drafts #661–#665, verify the actual consumer selection path and size-safe registration within the 8 MiB budget. Do not merge this staging PR solely on green checks. No ImPULS writes, live bot changes or working-cache updates.
