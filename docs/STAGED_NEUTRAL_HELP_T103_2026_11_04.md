# T103 — unregistered general-help QA candidates (2026-11-04)

**Status: Draft / BLOCKED.** **Tracking:** [Draft PR #223](https://github.com/Treninem/Bot-Knowledge/pull/223). Branch `bk/t103-neutral-help-qa-20261104`, base main `23871ed224cbe0d9636c841fd48e3f43bdd3ed1b`. This is an independent synthetic general-help batch, not a change to ImPULS and not an update to consumer snapshots. Existing T96–T102 dialogue progress is separately preserved in [PR #222](https://github.com/Treninem/Bot-Knowledge/pull/222).

## T105 checkpoint — 2026-11-04 (latest)

- **27 existing stable intents** `help_t103_001`–`027`, **+54 original synthetic context-specific answers** (+2 each); **189 → 243** candidate responses, **27 partial sets × 9/100**, **91 missing per set / 2,457 outstanding**; **0 new canonical questions**, **0 completed 100/100 sets**. Data commit [`3b517f5591ee876a50467ebc69948e4e593dffdb`](https://github.com/Treninem/Bot-Knowledge/commit/3b517f5591ee876a50467ebc69948e4e593dffdb), JSON blob `7b74bb8522486be52f4624dea8b1238e8dd155cd`.
- **Checks actually performed through connected GitHub/JavaScript:** 27 unique stable IDs; 81 normalized distinct question/alias forms; 243 normalized distinct answers; each record remains qa.v1 with 1 answer + 8 variants; 0 exact normalized matches for the 54 new replies against all **11 registered QA packs / 2,303 records**, or eight staging data files in Draft [#222](https://github.com/Treninem/Bot-Knowledge/pull/222); candidate lengths under schema limits; manual review of the 54 texts for purpose, tone, privacy and unverified capability claims. Exact dedup is not a proof of semantic uniqueness.
- Existing offline Python test now expects 243 replies and 8 variants ([`0d6f990`](https://github.com/Treninem/Bot-Knowledge/commit/0d6f990a3f10ad613c872f89dd13c042ef687d48)); **Python tests NOT RUN** (no local exact checkout / Windows D: volume here). No D: consumer E2E; no green exact-head CI. Do not merge. Additional variants above nine require a tested compatible representation and cannot be silently added to a qa.v1 record.
- **Main base** `23871ed224cbe0d9636c841fd48e3f43bdd3ed1b` / manifest `2026.11.04.026`: Git tree shows 38 packs, **7,513,573 pack bytes + 5,689 manifest bytes = 7,519,262 / 8,388,608 bytes**. Staging outside manifest; **0 registered bytes** from this PR, no hash/cache mutation. Exact HEAD after journal commit is obtained from PR metadata.
- Latest owner coordination: restrict to synthetic anonymized content and existing sections; **do not edit** `scripts/trusted_publish_qa.py` or `scripts/prepare_knowledge_candidate.py` (separate Draft #224 owns publication checks). No paid Actions, no ImPULS edits, no BotHost changes, no PR merge or issue closure.
- **Next:** locally validate exact checkout and full large catalogs, verify ImPULS consumer handling; green exact-head CI required before any merge. For more than 9 candidates, develop and test a backward-compatible selection mechanism separately.

## T104 checkpoint — 2026-11-04 (historical)

- Continued the same Draft PR #223 and stable IDs `help_t103_001`–`027` from the existing GitHub branch. Source data blob before edit: `f475c128a2c10a3573ed58c8325da48186dc2384`.
- Added **81 newly authored synthetic Russian help replies** (3 per each of 27 existing intents) in the original staging qa.v1 pack. **108 → 189 candidates**, **27 partial sets × 7/100**, **93 still needed per intent / 2,511 total**; **0 completed sets** and **0 newly created canonical questions**. Candidates span wrong-chat mistakes, incident reporting, authentication secrecy, group permissions, message delivery, feature status, version mismatches, explicit consent, privacy, links, duplicate notifications, games, clarifications, disagreement, uncertainty, moderation explanation, and factual caution. Context is embedded in response wording; no permissions or consumer capabilities asserted.
- GitHub data commit: [`fd0ed9f739cbbdb514833d3eada0cb87c57a80e2`](https://github.com/Treninem/Bot-Knowledge/commit/fd0ed9f739cbbdb514833d3eada0cb87c57a80e2); new Git blob `2a7b696ebb50c4e1d3956bf3a359b5b512c68147`.
- **Checks actually executed in in-process JavaScript on newly written JSON:** all 27 records parsed, 189/189 normalized unique replies, 81/81 distinct normalized question/alias phrases, required IDs preserved, every record has 6 variants (schema allows up to 8), 0 private-token/email/ban-command patterns from checked expressions, reply lengths 61–176 characters. These do **not** demonstrate semantic uniqueness or successful Python execution.
- Offline Python test source was adjusted to expect 189 answers and six variants per record; execution remains **unconfirmed**. The file is deliberately outside manifest, so no changes to SHA-256/cache/version or live consumer snapshot. Paid CI forbidden. **Draft / BLOCKED**, not eligible for merge absent verified full checks and exact-head green CI.

## Prior T103 counters (historical)

The original 108 / 4-per-intent measurements below are preserved only for audit. Current total is the T104 checkpoint above.

## Durable counters

- **27 distinct new canonical questions**, **54 new query aliases**, **108 new reply candidates**, four per question (one answer plus three variants), in `staging/ru/neutral_help_t103.qa.v1.json`. Data blob `f475c128a2c10a3573ed58c8325da48186dc2384`, initial data commit `c239b52ed22b920f725a9ea3028c79b7535f57af`.
- **27 partial sets × 4/100**, **96 missing per set / 2,592 total**, **0 complete 100/100 sets**. Counts describe this T103 batch only, not all knowledge records in main or #222. Future runs should extend these exact `help_t103_001`–`help_t103_027` intent IDs rather than inventing duplicates.
- Categories: privacy-safe incident reports and wrong-chat messages; roles/access; version-dependent instructions; explicit confirmation; suspicious links; duplicate notifications; group-game boundaries; basic diagnosis; missing prior context; uncertainty, neutrality, source checks, and evidence-aware moderation explanations.
- `catalog.audiences = [all_ai_bots]`, `contexts = [direct, private, group_addressed]`, `read_only = requires_direct_address = no_personal_data = true`. All text is synthetic and factual capabilities of ImPULS are **not** asserted. No automatic sanctions, hidden actions, or write privileges are included.
- File stays **outside main manifest** until separately validated. At pinned main: manifest `2026.11.04.026`, 38 registered packs, 7,519,262 / 8,388,608 bytes; **0 consumer snapshot bytes added** and no package hashes or cache changed by this Draft.

## Checks and limitations

- Actual **in-process GitHub connector checks:** 27 IDs / 81 distinct normalized canonical+alias phrases / 108 distinct normalized responses; shape/length/context and privacy guard checks; no normalized exact matches to **2,303 records across 11 main qa.v1 packs**, and no canonical-question Jaccard ≥ 0.65 against those QA records; 0 exact query or response overlaps with existing staged T96 base, and 0 exact response overlaps with all 765 T96–T102 staged responses in [#222](https://github.com/Treninem/Bot-Knowledge/pull/222).
- Fresh PR overlay read-only comparisons: **#214** (five changed QA packs, including 869 ImPULS-help records) and **#219** (one changed QA pack, 50 records): **0 exact collisions** with T103 questions, aliases or answers.
- Added `scripts/test_staged_neutral_help_t103.py` with **9 offline test methods written, NOT EXECUTED**. No complete local Python/qa.v1 schema validation, semantic equivalence review, large `reply_catalog.json` or `social_dialogues.json` checks, consumer integration with ImPULS #383, or exact-head CI. In prior connector reads the two largest catalogs returned truncated JSON, so full cross-catalog screening is **not claimed**.
- The checks only support **candidate uniqueness**, not proof that 108 responses are all useful in every context. One intent can have multiple replies for different situations. Human semantic review and context selection rules are still required before registration.

## Release gate and next steps

1. On an exact checkout of this branch, run `python -B scripts/test_staged_neutral_help_t103.py`, `python scripts/validate_qa_v1.py` as supported by its CLI, `python scripts/validate_pack.py`, and the existing regression suite. Fix actual failures; do not count written tests as passing.
2. Recheck changed PR #214/#219 overlays, the entire conversation/social catalogs, semantic duplicates, per-response contexts and total snapshot size relative to the **8 MiB consumer cap**.
3. Integrate only through a tested compatible consumer/search selection strategy, version/SHA update and cache invalidation; do not register this staging file merely to increase counts. Obtain **green exact-head CI** without spending money or weakening checks, and post-main CI after any permitted merge. Without these, leave Draft / BLOCKED.
4. Never modify Treninem/Impuls or deploy live bots in this task. No paid GitHub Actions or services, no direct import of private chat messages. Follow-up work should start from the 27 durable IDs and their **4/100** counters, then move to genuinely new questions after completing useful progress.

