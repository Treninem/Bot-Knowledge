# Practical recovery R4 — 120 contextual candidates / 24 intents

Continuation of [PR #665](https://github.com/Treninem/Bot-Knowledge/pull/665), branch `bk/practical-recovery-context-r1-20261114`.

## Delta

- R1–R3: **192 staged candidates** across 24 stable canonical intents.
- R4: **120 new replies**, five per each of the same 24 intents.
- Cumulative: **312 staged candidates / 24 intents**.
- Published baseline: 9 answers per intent. If all staged candidates pass independent editorial and consumer review, the numerical position becomes **22/100 per intent**, with **78 remaining**.
- Newly editorially accepted: **0**. Complete 100/100 sets: **0**. Newly registered in main: **0**.

R4 covers new cases for diagnosis without logs, privacy-safe screenshots, authority claims, permissions, reversible tests, unverified completion, trade-offs, small edits, terminology, rollback, disagreement, progress reporting and stopping unwanted advice. Every response is synthetic, Russian, direct-context, read-only and pending full semantic review.

## Source and boundaries

Source pack: `packs/ru/practical_recovery_qa.json`; SHA-256 `be8ae1408cf42816adc3f8ba818b3f004318617ba2e878e72edd85cf7eb4954e`; Git blob `21bf261970d1bdcf0f9fb8fb3383772b86b2dc2f`. Current main reverified at `d43134b9072c7ceff44cfcf63d5d11c0d0771d7a`, manifest `2026.11.17.030`. The branch copy and current main source pack have the same blob SHA. The R4 file is unregistered staging only; no manifest, cache, consumer, ImPULS or live bot is changed.

## QA

The R4 test verifies the 192→312 lineage, stable IDs, exact delta, source SHA/blob, all registered packages and main staging for exact duplicates, 15 related QA packages for near-duplicates, within-intent lexical distance, privacy, direct-address scope and the prohibition on sanctions. The read-only exact-head workflow checks the actual PR checkout SHA and runs normal Python and `-O`.

No local test is claimed. The current branch remains Draft pending independent editorial acceptance and verified consumer-selection compatibility.

