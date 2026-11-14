# Structured K31/K32 — semantic editorial audit (14 November 2026)

Source/main `6c9f430da47f137d39a72bbd28c057cfb8f6be96`; continuing Draft PR #661. The two stage commits added **74 + 64 = 138 synthetic RU candidates** across the same 54 stable intents. New data-only paths K31/K32 and their tests, journals and read-only CI workflow are preserved. This audit does not register them in the consumer manifest.

**Critical correction to the coverage interpretation:** raw candidate counts now reach 100 for ten intents (five in K31 and five in K32). **Zero of those sets has been cleared by a full meaning-based uniqueness review.** There are still **54 intent sets requiring independent editorial evaluation** and consumer selection checks. The unreviewed candidate count is not a count of accepted, deployable replies.

Automated exact/normalized and token Jaccard checks cannot detect every paraphrase of the same situation. An editorial spot-check against early K stages found potential meaning-equivalent pairs despite differing normalized text/context notes. Seven K31 replies are explicitly flagged with `editorial_status=possible_semantic_duplicate` and pointers to older IDs:

| New candidate | Earlier candidate | Why it needs review |
|---|---|---|
| `struct_t93_001_supp_102` | `struct_t93_001_supp_54` | transition from zero to a negative amount |
| `struct_t93_001_supp_104` | `struct_t93_001_supp_60` | missing measurement encoded as zero |
| `struct_t93_001_supp_105` | `struct_t93_001_supp_37` | rounding conceals non-zero baseline |
| `struct_t93_001_supp_106` | `struct_t93_001_supp_45` | first five events after zero baseline |
| `struct_t93_002_supp_103` | `struct_t93_002_supp_59` | identical 1.2 × 0.8 core operation |
| `struct_t93_005_supp_102` | `struct_t93_005_supp_34` | short shift crossing midnight |
| `struct_t93_005_supp_104` | `struct_t93_005_supp_24` | unpaid break within overnight shift |

These are editorial-review **flags**, not automatically proven duplicates. If their unique contextual contribution cannot be established, rewrite or drop the new entry and adjust exact cumulative counters; never move it into an approved 100/100 count. Do not simply generate cosmetic alternatives to reach 100.

Next: review each candidate against the full prior corpus, starting with these seven and the remaining K31/K32 first ten intents. Build a reviewed/rejected ledger with explicit surviving IDs, update the per-intent accepted counts after that review, then progress genuinely uncovered practical intents. Source facts, privacy, exact-head CI, consumer context gating and 8 MiB snapshot compatibility remain mandatory before merge. No changes to ImPULS, BotHost, manifest or caches.

Regression follow-up: K31/K32 test suites now assert that unreviewed candidate-complete sets cannot carry an editorial approval count, and the exact-head read-only workflow runs both new suites in standard and Python `-O` modes. These executable checks do not replace manual semantic review.
