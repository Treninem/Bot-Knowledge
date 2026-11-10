# T582–T583 — original Russian social boundary replies (2026-11-10)

Stable 10 intent IDs are taken from **T580–T581**, not recreated. Confirmed origin main `76d2c569a383c5f02809076bdca82962560b0631`, original source `packs/ru/social_dialogues.json` with manifest SHA-256 `0cfedc133354a69522fecc3cda6bc21533c66005f0dc207050075f787dc977a8` and Git blob `d56ff304da7165bd63c328f3220a1f6d3d26e3ab`.

Two independent checkpoints: T582 **+100** (ten each for replies 21–30); T583 **+100** (ten each for replies 31–40). Prior T580–T581: 200. Total **400/1000** stage-only candidates, **40/100 for every one of 10 intents**, 60 missing each / 600 remaining, completed 100/100 sets **0**. Increment this run **200**, do not recount prior work. The next sequence starts at reply **41**. Parent blob of T582: `d40ead85c21ff12d4d0f05ec0151c3e6fde17734`; parent blob of T583: `44727ac4b43f73c36c8f98ac55b098acef4de761`.

Topics: listening without advice, reducing superfluous clarifications, seriousness, consensual friendly teasing, pauses, topic changes, plain congratulations, de-escalation when angry, opt-in dark humour without victimisation, and respectful evidence-based rebuttals. Each candidate has its own specific `context_note`, read-only/direct-address gates, RU and `all_ai_bots`. They are **not** universally interchangeable even within a single intent. No real user chats, names, identifiers, private content, sanctions or execution permissions.

Actual pre-write and GitHub read-back checks: **400/400** different IDs, normalized response texts and context notes; exact parent blob chain PASS; **0 exact** new duplicates and **0 near token-Jaccard >= 0.80** in the full 400 family. Peak lexical Jaccard for T583 against previous replies **0.3125**. These checks do not prove full semantic originality or consumer behavior.

New regression test: `scripts/test_social_boundaries_t582_t583.py`; read-only exact-head workflow: `.github/workflows/t582-social-context.yml`. Test results must be reported only **after** actual GitHub CI for final head; the local Python suite was not executed (container DNS cannot resolve github.com). Pending: final exact-head quality checks, fresh base compatibility, guarded merge, then post-main CI.

`consumer_registered=false`: no manifest registration and no automatic activation in ImPULS, AuroraFox or other bots. The registered package hash, on-disk consumer caches, private ImPULS and BotHost remain untouched. GitHub is only the staging distribution point.
