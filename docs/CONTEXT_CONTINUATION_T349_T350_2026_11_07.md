# T349/T350 — 92 new contextual Russian replies (2026-11-07)

Source of truth: actual main at start **9b1c0680821f1bc3a173f7d61b075361ab47a95f**, merged PR #391. The separate index-only Draft #392 remains a parallel workstream and must not be overwritten.

This release includes **44** original synthetic Russian conversational-pragmatics answers on 22 established stable intent IDs and **48** practical safety/troubleshooting answers on 24 existing IDs, two per intent. These are conditional examples, not interchangeable answers to every incoming utterance. Each has a distinct context note, audience, context label, no action or sanction, and requires a trusted consumer to confirm address, scope and explicit approval.

Baseline: colloquial 22 × 63/100 and practical 24 × 62/100 = **2,874/4,600** (414 registered and 2,460 staged). This checkpoint: colloquial 22 × **65/100**, practical 24 × **64/100**, total **2,966/4,600** and **1,634 remaining**. **46 partial**, **0 completed 100/100**. Accepted new answers 92, rejected 0 in candidate generation (lexical checks and CI pending until confirmed).

Files: two immutable supplemental pools, stage-provenance/approval validator, regression tests, exact-head read-only CI workflow, this note. The stage chains pin the registered source-pack SHA-256 and Git blob of immediately preceding stage. Neither the manifest nor live consumers or their caches are modified. The #392 catalog is intentionally not edited; it currently knows 2,460, not these 92; follow-up index work must be based on latest main after merge.

Gate: local or CI validation of all ancestors, normalized IDs/text/notes, nearest lexical duplicates, private data, fail-closed context selection, exact checkout SHA and post-main CI on actual merge commit. No private chat data or tokens; no edits to ImPULS.
