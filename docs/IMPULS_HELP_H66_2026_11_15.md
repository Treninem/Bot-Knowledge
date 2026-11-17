# ImPULS help H66 — 15.11.2026

Continuation of Draft PR #666 after H65. Created **40 original Russian reply candidates** for **20 existing practical intents**: two distinct usage contexts per intent, covering answer repair, selected-chat boundary, Pulses, release versus live features, group/DM menus, game family consent, giveaway/complaints, permissions and cautious help requests.

H1–H65: **2,680** staged; H66: **+40**; total: **2,720** staged across **100 partial intents**. Remaining numerical positions to the 100/100 targets: **7,005** (excluding other open PRs). New 100/100 sets: **0**. H65 and H66 remain completely unapproved; newly published answers: **0**. Entries in H66 each include a stable intent/ID, response role, audience, read-only scope, explanation and separately written situational guard.

Source snapshot: Bot-Knowledge main `6c9f430da47f137d39a72bbd28c057cfb8f6be96`; source pack SHA-256 `50edd41dc0c6a868577433944e0ff0b2a36c2c9ebe53d587e5cbb4692185bbc9`. ImPULS main `4a3587db879b8f0b7868c33cd719ba039306dab0` read-only; README checked. No ImPULS, BotHost, live cache or manifest write.

QA: `scripts/test_impuls_help_h66_20261115.py` verifies cumulative counts and all stage IDs, real source SHA, privacy, context conditions, normalized duplicates and lexical near-repeats. New and previous staged packages must be tested in normal Python and `-O` by exact-head GitHub Actions, plus main quality checks.

**DRAFT/BLOCKED** until full semantic edit against parallel PRs, actual consumer contextual selection, snapshot limit at registration, exact-head CI and other merge gates. These data are candidates and not available in a deployed bot.

Next: verify the current SHA, review the least-covered remaining intents, and prepare separate validated registration only for accepted replies.
