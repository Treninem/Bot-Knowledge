# T584–T585 — next natural RU social replies (2026-11-10)

Continuation of the same ten stable `t580_*` intents; source main `76d2c569a383c5f02809076bdca82962560b0631`, source `packs/ru/social_dialogues.json` SHA-256 `0cfedc133354a69522fecc3cda6bc21533c66005f0dc207050075f787dc977a8`.

T584 produced **+100** (replies 41–50, ten per intent); T585 **+100** (replies 51–60). Together with T582–T583 (+200) and pre-existing T580–T581 (200), the full six-stage chain now has **600/1000** candidates, **60/100** for each intent, **40 missing each / 400 missing overall**, **0 completed sets**. Newly authored in this PR **400**; no double counting of previous 200. All entries remain opt-in `all_ai_bots` RU `direct` read-only stage candidates, conditional on individual context; no sanctions, private chats, external actions, or unsupported bot abilities.

Confirmed GitHub read-back: all **600** IDs, normalized texts and context notes are unique; parent Git blob SHA chain is exact; 400 new responses have **zero** token-Jaccard ≥0.80 compared to earlier responses in the six-stage chain, highest observed similarity **0.4286**. Earlier T582/T583 additional cross-check against **780** responses in six related main staging files found **0 exact**, **0** token-Jaccard ≥0.80, peak 0.35. These are lexical and partial-corpus checks, not proof of full semantic distinctness.

T584 parent `3e36416906dca0a7b84d3a5594a8cabd9a14eee2` (T583 blob). T585 parent `8e894936a2f73bc990c947605b296a0300a2e92a` (T584 blob). T585 blob `c40074c27834307bb49645825611aff050cb92f4`. Original registered manifest SHA remains unchanged. Exact-head Python validation runs via read-only workflow `.github/workflows/t582-social-context.yml` with `persist-credentials: false`, which now checks all six stages. Its pass/fail is **pending at time of this checkpoint**; local Python not run because GitHub DNS unavailable.

Next step: complete full exact-head CI for current PR head, recheck base and guards, merge only on actual success, then confirm post-main CI. Continue **from reply 61** for each of the ten stable intents; do not restart or count existing 600 as new.
