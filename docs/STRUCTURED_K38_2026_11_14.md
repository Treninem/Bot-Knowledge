# Structured K38 · 14 November 2026 · staged only

Source main verified via live Git ref: `6c9f430da47f137d39a72bbd28c057cfb8f6be96`. Continued existing Draft PR #661 from K37 at `cb465dd9dfea51a6541396b66e7aee4965f73ca4` (K37: 4,748 raw K-series candidates, 52/54 numerically complete). Source published pack `packs/ru/structured_information_qa.json` remains consumer-registered and unchanged.

## K38 delta

Created `staging/ru/structured_information_20261114_delta_k38.json`: **11 new synthetic, context-scoped Russian reply candidates for seven stable intents**. All entries remain unapproved and `consumer_registered=false`.

| Intent | Before raw | New | Previously disqualified | Raw after | Potential numerically eligible after replacements* |
| --- | ---: | ---: | ---: | ---: | ---: |
| `struct_t93_001` zero baseline growth | 100 | 2 | 2 | 102 | 100 |
| `struct_t93_002` sequential percentages | 100 | 1 | 1 | 101 | 100 |
| `struct_t93_005` overnight shift | 100 | 2 | 2 | 102 | 100 |
| `struct_t93_018` seasonal trend | 100 | 1 | 1 | 101 | 100 |
| `struct_t90_003` route speed | 100 | 1 | 1 | 101 | 100 |
| `struct_t93_015` temperature conversion | 98 | 2 | 0 | 100 | 100 |
| `struct_t90_018` stacked bar chart | 98 | 2 | 0 | 100 | 100 |

*Potentially eligible counts are **not** independent editorial approvals. All newly added replies must pass full semantic review and proper contextual selection; other as-yet-undetected overlaps may lower these numbers. The seven older exclusions remain explicitly recorded and must never be approved or counted twice.

Raw K-series candidate total: **4,748 → 4,759**. Raw incomplete slots: **4 → 0**. Numerically, 54/54 stable intents have at least 100 *raw* records, including rejected legacy candidates. **Independently editorially accepted replies this continuation: 0; fully approved 100/100 sets: 0**.

New contexts: offsetting gross flows and net-zero grid use; same-reference percentage adjustments; both daylight-saving transitions; leap-year February comparability; mismatched time zones on a route; spreadsheet formula precedence and sensor scale for temperature; overlapping categories and hidden category gaps on stacked charts. This is a targeted attempt to avoid cosmetic variants in saturated collections.

## Safety and QA gates

- Added `scripts/test_structured_k38_20261114.py` to check accurate counts, 7 known excluded IDs (flagged in K31/K33), schema/role/context, staged isolation from manifest, source-pack actual SHA-256, uniqueness and token/context overlap across all prior K stages.
- Updated read-only `.github/workflows/structured-k-20261111.yml` to run the new tests under standard Python and `-O` and log actual K38 SHA-256. Checkout is the PR exact head; permissions remain `contents: read`; checkout credentials are not persisted.
- Locally, a GitHub clone cannot resolve `github.com` DNS in the container; do **not** claim local Python test success. Await actual exact-head CI on the final saved head. The tests alone do not detect all semantic duplicates.
- No personal data, chat transcripts, extra consumer permissions, moderation sanctions, changes to ImPULS/BotHost, live caches, manifest or version.
- Main consumer snapshot at K37: 7,999,374/8,388,608 B including manifest, 389,234 B free. K38 stays unregistered and cannot be merged as published knowledge without size-safe and consumer selection checks.

## Next

Review all 54 intents against main and other open PRs (#662–#664 and earlier), prioritising repeated high-level motifs in the two saturated temperature/chart intents. Mark exact editorial eligibility and publish only size-safe, meaning-distinct, consumer-tested subsets. Any additional candidates must be contextually distinct and have their own verifiable delta; no claim that numeric 100/100 equals semantic approval.
