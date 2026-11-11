# Temporal language stages I–J — verified draft checkpoint (2026-11-11)

This is a **dependent** continuation of the same ten `temporal20261111_*` intents, not a new set and not a rewrite of concurrently edited #632.

- Parent: [#632](https://github.com/Treninem/Bot-Knowledge/pull/632) at exact head `fff3f7b40c116db76c65e0e6979a727b58e15005`, which already includes stages A–H (**800 candidate replies**).
- Stage I: `staging/ru/temporal_language_20261111_context_delta_i.json`, IDs **81–90** per intent, **100 newly authored** responses, 900 total, ten partial sets at 90/100.
- Stage J: `staging/ru/temporal_language_20261111_context_delta_j.json`, IDs **91–100** per intent, **100 further new** responses, 1000 total, ten sets at 100/100.
- **New delta in this branch: 200**, not the historical 800. They are unregistered, synthetic, directly addressed, context-conditioned and strictly read-only.
- Pin: Stage I parent H Git blob `e231ad4ed94594d0bcefaa6496a70c6bee2aed22`; Stage J parent I Git blob `aa4de446f98bfc766bb90d571ff7403ed3e261b2`.
- Source: `packs/ru/social_dialogues.json` with unchanged registered SHA-256 `0cfedc133354a69522fecc3cda6bc21533c66005f0dc207050075f787dc977a8`; `manifest.json` version `2026.11.09.003`, index and all consumer caches unchanged.
- Connector-side programmatic comparison of each new stage to preceding staged responses found **1000 distinct IDs, normalized texts and context notes** overall and no text-pair token-Jaccard >= 0.8. This is a *lexical* check, not proof of global semantic uniqueness.
- The new Python test `scripts/test_temporal_language_20261111_i_j.py` performs chain/SHA, schema, uniqueness, lexical, privacy and read-only checks for all ten stages; the separate read-only workflow checks exact checkout head. Actual CI outcome must be verified, never presumed.
- Important: do not merge into `main` ahead of #632. Recheck all of #632's latest changes/CI and its actual post-main CI, rebase or retarget safely without force-push, then verify this PR's exact-head CI, guarded merge and actual post-main CI. No live BotHost/ImPULS changes.

**Next task:** inspect *new* missing canonical topics, instead of generating another 100 answers for these completed IDs; editorially review coverage across all related source/staging packages before consumer registration.
