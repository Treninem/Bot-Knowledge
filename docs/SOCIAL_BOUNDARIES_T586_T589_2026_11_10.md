# T586–T589 — completion of ten contextual social reply sets (2026-11-10)

## Scope and counted delta
- Parent main (after guarded #604 merge): `94c56c148fd224e6c2aaccf3a65fcad40141257f`.
- Previous T580–T585 (already main): **600** original staged contextual RU replies, ten stable intent IDs at **60/100** each. Not counted as newly authored here.
- New T586, T587, T588, T589: **100 + 100 + 100 + 100 = 400** original synthetic replies, 40 new per existing canonical intent (items **61–100**). Stages and separate Git commits preserve each 100-item checkpoint.
- Exact combined progression: **600 → 700 → 800 → 900 → 1000**; ten stable intents at **100/100** (staging candidates only), **0 remaining**, **10 finished**; no new canonical intent IDs in this PR.
- Sections/topics: listening without advice, minimizing needless clarifications, serious mode, consent-based friendly teasing, pausing chat, changing topics without explanation, concise grounded congratulations, non-defensive response to anger, opt-in harmless dark humor, and rebuttals aimed at arguments rather than people.
- Every reply has its own `context_note`; it is **not** correct to select all 100 answers indiscriminately. `requires_context_match`, direct address, RU language, `all_ai_bots` audience, read-only, no actions/sanctions, no private identifiers.

## Source and publishing boundaries
- `packs/ru/social_dialogues.json`, registered manifest SHA-256 `0cfedc133354a69522fecc3cda6bc21533c66005f0dc207050075f787dc977a8`, Git blob `d56ff304da7165bd63c328f3220a1f6d3d26e3ab`.
- Previous T585 blob `c40074c27834307bb49645825611aff050cb92f4`; T586 `d2f75145300332dbed3704b03267f92ef156a664`; T587 `c762b964d34d7d9140ebda9abd8a3ffed5bdc2e1`; T588 `ee7bb0731d66704a994d2d1be8b6de6f2e6893dc`; T589 `429df3e9508301921b01f2ea8f305301aa52b43d`.
- `manifest.json`, registered packs, caches, ImPULS and live bots unchanged. These **staging-only candidates** do not make any consumer learn automatically.

## Validation evidence and limits
- Actual GitHub read-back of all ten stages T580–T589: **1000/1000** unique stable IDs, normalized replies and normalized contextual notes, exact parent blob SHA chain, ten unchanged canonical intents; **0** exact duplicates and **0** token-Jaccard ≥0.80; maximum internal lexical Jaccard **0.4286**.
- Additional GitHub corpus sample: **400 new** replies compared against **2419** extracted replies from nine related staged/registered files: **0 exact** and **0 Jaccard ≥0.80**, peak **0.3889**. This comparison is **partial**, not a full semantic uniqueness proof. The registered `social_dialogues.json` extraction was incomplete in the connector response; base-source integrity is checked separately through the pre-existing test suite.
- New Python regression suite `scripts/test_social_boundaries_t586_t589.py` checks ten stages, exact Git blob parent chain, immutable source/manifest SHA, scopes, safety flags, unique IDs/texts/contexts, all ten 100/100 counters and near-duplicates.
- Dedicated read-only `.github/workflows/t586-social-completion.yml` checks the **actual head SHA**, disables checkout credential persistence and runs registered source validation plus all T580–T589 Python tests. Do **not** claim Python/CI PASS until an actual run succeeds.
- Local Python tests not executed because direct container GitHub clone could not resolve `github.com`; the JS validation above is executed, but does not replace the required CI. No payments or private ImPULS changes.

## Gate and next action
- [ ] Complete full **exact-head** CI on final PR head, inspect actual checkout and all checks.
- [ ] Re-read main/head and check non-regression, base compatibility and protected merge constraints.
- [ ] Merge with head-SHA guard only after success and confirm full **post-main** CI on actual merge SHA.
- [ ] Start next independent useful topic set after the ten 100/100 social intents, without re-counting this series.
