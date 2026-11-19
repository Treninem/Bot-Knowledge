# Contextual clarity editorial review — 2026-11-19

Reviewed two staging files at PR #707 previous head `f2464802b33fe889eec7dbfed2efebde1275dad5`: 101 + 55 = 156 synthetic records and 152 distinct intent labels. All remain unregistered candidates, not accepted answers.

Four canonical intent labels occur twice:

| Intent | Record IDs | Review |
| --- | --- | --- |
| `missing_denominator` | `clarity_20261118_38`, `clarity_extra_20261119_20` | Different tasks: compute a percentage versus evaluate survey results. Retain context distinction; one canonical intent family. |
| `unconfirmed_delivery` | `clarity_20261118_48`, `clarity_extra_20261119_48` | Near-semantic duplicates about sent versus read status. Compare with registered packs before accepting both. |
| `duplicate_submission` | `clarity_20261118_56`, `clarity_extra_20261119_33` | Overlapping duplicate-send caution. One canonical intent; keep two variants only if distinct context routing is demonstrated. |
| `ambiguous_timezone` | `clarity_20261118_63`, `clarity_extra_20261119_16` | Same timezone ambiguity; second adds multi-country/date context. Count as one question family. |

Additional editorial flags: `clarity_extra_20261119_05` requires verified task dependencies before partial processing; `clarity_20261118_14` must not route crisis content into humor; `clarity_extra_20261119_55` does not authorize deletion of photographs. Generic `avoid` metadata in the extra file needs more specific contraindications before promotion.

Pending: compare all 156 records against registered packs and open PRs, verify consumer routing/schema, run local regression and privacy checks, update manifest with actual SHA-256 only for accepted packs, verify exact-head CI on the final commit and post-main CI after any merge. This review itself accepts **zero** new answers and completes **zero** 100/100 sets. Do not merge this staging PR as published knowledge.

## Full staging structural recount — 2026-11-19

At head `c83cf78edc193eeac094305e08a8ff6526595d13`, all three candidate files contain **101 + 55 + 9 = 165 records**. Normalizing case, `ё/е`, punctuation, symbols and whitespace yields **165 distinct IDs, 165 distinct input strings, and 165 distinct answer strings**. There are **160 distinct intent labels**, not 165 distinct canonical questions. This is a structural check of staging only; no cross-pack semantic acceptance is implied.

Five repeated intent families require context-aware editorial routing:

- `ambiguous_timezone` (3): `clarity_20261118_21`, `clarity_20261118_63`, `clarity_extra_20261119_16`. The previous two-file review missed the first record in this family.
- `missing_denominator` (2): `clarity_20261118_38`, `clarity_extra_20261119_20`.
- `unconfirmed_delivery` (2): `clarity_20261118_48`, `clarity_extra_20261119_48`.
- `duplicate_submission` (2): `clarity_20261118_56`, `clarity_extra_20261119_33`.
- `silent_failure` (2): `clarity_20261118_85`, `clarity_extension_20261119_03`. This family crosses into the third staging file.

The count of five duplicated *families* and five extra records over unique intents is not a count of rejected answers. Decide which variants are useful only after inspecting their triggering context and comparing published packs and other open PRs. **Accepted: 0; registered: 0; completed 100/100 sets: 0.**
