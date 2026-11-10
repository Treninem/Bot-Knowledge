# Support triage Stage G: 2026-11-10

**Staging-only completion of ten stable RU diagnostic intents**. This branch stacks on [PR #615](https://github.com/Treninem/Bot-Knowledge/pull/615); it is not yet consumer-ready.

- Before G: **800** candidates across stages A–F, 80/100 per intent.
- G: **200 genuinely new** context-conditioned responses (indices 81–100, 20 per intent).
- After G: **1000 unique staged replies across ten stable intents**, ten candidate sets at 100/100; zero partial, zero remaining for these specific sets. **This is candidate count, not an integration or live-bot result**.
- Distinct new normalized texts, IDs and context notes: 200/200. Exact repeats vs all prior stages and selected related files: zero. Highest cross-pool/new-pool token Jaccard 0.3000 (less than 0.80). Semantic uniqueness still requires editorial review, not inferred from the numeric test.
- Parent F Git blob: `227eaa5b63ad1c17597d9e46b4efbaa2ab65d3c7`. Registered source: `packs/ru/social_dialogues.json`, SHA-256 `0cfedc133354a69522fecc3cda6bc21533c66005f0dc207050075f787dc977a8`. Manifest `2026.11.09.003` unchanged.
- Static data only, `consumer_registered=false`; no live deployments, consumer caches or ImPULS edits.

Before any merge: complete exact-head CI on the actual G SHA, verify all checks and base/head, safely merge the prerequisite #615 with post-main CI, retarget this PR to updated main, rerun required checks and confirm post-main CI after the guarded merge. Do not evade required checks or spend on paid Actions. After this series, identify practical unmet intents from the current manifest and existing PRs rather than inflating repetitions.
