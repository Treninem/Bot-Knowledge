# T96 — staged conversational QA: progress and acceptance gates (2026-11-04)

**Status: Draft / BLOCKED.** PR [#222](https://github.com/Treninem/Bot-Knowledge/pull/222), branch `bk/t96-staged-dialogue-repairs-20261104`. Latest pinned **main** observed during this cycle: `23871ed224cbe0d9636c841fd48e3f43bdd3ed1b`, manifest `2026.11.04.026`, 38 registered packages. Recheck the branch heads before future edits; historical reports do not establish current state.

## Durable partial-set progress

- Active stable IDs: `dialogue_t96_001` … `dialogue_t96_045`; **45 distinct intents**, **90 aliases**.
- Previous T96 checkpoint: **205** distinct staged response strings; 35 intents at 5/100 and 10 intents at 3/100.
- **This cycle added 90 original responses:** **+2 per each of the 45 existing intents**, no new canonical questions and no aliases. No previous replies were counted as new.
- **Current staged total: 295 responses**. Intents `001`–`035`: **7/100 each**, **93 remaining each**. Intents `036`–`045`: **5/100 each**, **95 remaining each**. **Total outstanding to the illustrative 100/intent target: 4,205**. **New 100/100 sets this cycle: 0**.
- New responses cover different situational conditions: assent versus resignation, uncertain tone, public versus private address, correcting a consequential error, boundaries on consent, handling partial replies, disagreement, factual provenance, spoiler/truncated-chat evidence, and leaving conversations without pressure.
- Current file: `staging/ru/dialogue_repair_t96.qa.v1.json`, **92,756 UTF-8 bytes** after addition; Git blob SHA at the data checkpoint: `aa3382d9c43fca3c5c74170f97cdbb719f1bab18` (commit `5a6c27227ac643d08cdb8caf71b49ea747b27034`). Stage remains entirely outside the manifest.

## Scope, compatibility, size

- `qa.v1` schema and stable IDs preserved; `all_ai_bots`, `read_only`, `requires_direct_address`, `no_personal_data` and restricted `group_addressed` case `041` preserved.
- **No registered packages added**, no manifest or package SHA-256 changed, **consumer snapshot byte delta = 0**. Historical GitHub main estimate: `7,519,262 / 8,388,608` bytes, headroom `869,346` bytes. This is a historical baseline, **not** a fresh complete consumer build on D:; calculate it again before any registration.
- The staged 295 responses are **not yet accessible to ImPULS, AuroraFox or live BotHost**. No edits to Treninem/Impuls, no automatic sanctions, no source Telegram conversations, user identifiers or credentials.
- BK PR [#214](https://github.com/Treninem/Bot-Knowledge/pull/214) owns the pending `.027` version and three special ImPULS help answers. BK [#219](https://github.com/Treninem/Bot-Knowledge/pull/219) owns moderation additions; [#220](https://github.com/Treninem/Bot-Knowledge/pull/220) and [#221](https://github.com/Treninem/Bot-Knowledge/pull/221) are distinct consumer budget/search changes. None were edited.

## Verification actually performed

- Connected GitHub files reread at pinned refs; parsed all **45 records / 295 replies**, validated IDs, contexts, constraints, language, audiences, answer counts and allowed lengths.
- **295/295 replies unique** after casefold, ё/е, punctuation and whitespace normalization. All 135 canonical/alias strings were previously unique, and this run did not change them.
- Pairwise candidate word-bigram Jaccard: **no pairs ≥ 0.45** (lexical check only, not proof of unique semantics).
- Compared complete contents of **11 registered qa.v1 packs**, plus latest available PR #214 help-pack overlay and #219 moderation-pack overlay: **3,222 reference records** (includes overlay copies), **0 normalized exact ID/question/answer collisions**; 0 canonical-question pairs reached word-bigram Jaccard 0.50.
- `dialogue.json` read and searched, no exact collision. Attempts to read huge `reply_catalog.json` and `social_dialogues.json` through this GitHub connector returned **empty file content**; full cross-format tests therefore remain **unverified**.
- Updated `scripts/test_staged_dialogue_t96.py` to expect **295** replies and added checks for strong within-stage lexical similarity and group-only context (**10 test functions defined**). **Python tests NOT executed on a complete checkout**; D: is not accessible in this environment. `python scripts/validate_pack.py`, full consumer ImPULS #383 integration, exact-head CI and post-main CI were **not performed**.
- User prohibits paid GitHub Actions. Commits use `[skip ci]`; do not launch paid workflows, disable protections or describe these GitHub-read checks as live bot tests.

## Required next actions

1. On a fresh local checkout of the exact PR head, run `python -B scripts/test_staged_dialogue_t96.py`, `python -B scripts/validate_pack.py`, full JSON Schema validation, privacy checks, and complete lexical/semantic comparisons with response and social catalogs.
2. Resolve any failures; independently confirm #383 consumer snapshot size and lookup behavior on supported versions and compare all active PRs against fresh main.
3. Only after acceptance, migrate **accepted** stage records into a compatible existing registered `qa.v1` package, update manifest hash/version without colliding with #214/#219, complete exact-head and post-main checks under approved no-cost conditions; do not bypass required checks. No automatic merge for this blocked draft.
4. Continue stable partial intents `001`…`045` before introducing needless duplicate intents; prioritize substantive context coverage over cosmetic rewrites. Update this journal with precise additions, rejects and next verified counts.
