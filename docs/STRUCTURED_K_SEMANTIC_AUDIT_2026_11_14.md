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


## Editorial decisions and K33 continuation (14 Nov, additional pass)

Seven flagged pairs reviewed against the cited older texts. **Five newer entries are rejected as meaning-equivalent**: `struct_t93_001_supp_102`, `struct_t93_001_supp_104`, `struct_t93_002_supp_103`, `struct_t93_005_supp_102`, `struct_t93_005_supp_104`. They remain visible for audit, flagged `editorial_eligible=false`, but must be excluded from any future approved or consumer set. **Two retained as context-distinct candidates**, not fully approved: `struct_t93_001_supp_105` (worked numerical rounding example) and `struct_t93_001_supp_106` (complaint count plus differing denominator).

The K31/K32 reported 10 provisional 100/100 sets were raw counts. Excluding these five confirmed duplicates, only **7** of those sets still reach numerical 100. Editorially accepted 100/100 sets remain **zero**. No file is consumer-registered; the independent all-stage semantic review is outstanding.

K33 prepared 44 proposals; after extended editorial comparison, 2 clear meaning duplicates were excluded and 42 new unapproved candidates remain. The K-series raw cumulative is 4662; subtract the 5 known rejected K31 candidates before any *potentially eligible* count, and do not call the remainder approved. No manifest/cache/live bot changes. Details: `docs/STRUCTURED_K33_2026_11_14.md`.


### K33 wider-stage audit correction

Two drafted K33 candidates were removed before this checkpoint: `struct_t93_015_supp_104` repeats the Celsius-difference case `_supp_38`; `struct_t90_018_supp_104` repeats the signed stacked-bar case `_supp_98`. The saved K33 file holds **42** new candidates. Whole-stage test checks exact and high lexical/context overlap against all 32 K ancestor files; fully independent semantic QA remains outstanding.


## K34 check · 14.11.2026

Two **additional** K33 semantic duplicates are excluded from future approval: `struct_t93_018_supp_104` duplicates K32 `struct_t93_018_supp_103` (movable holiday shifts calendar-week demand), and `struct_t90_003_supp_104` duplicates K32 `struct_t90_003_supp_103` (stops ignored in travel-speed measurement). Both are flagged `editorial_eligible=false` in K33; they remain visible in git for auditing. Known disqualified staged entries now **7** (5 K31 + 2 K33). K34 adds **24** *pending*, non-certified contexts. Raw staging **4686**, raw incomplete slots **66**, editorially complete sets **0**. See `docs/STRUCTURED_K34_2026_11_14.md`. This is not evidence that other candidates have passed independent review.
