# T103 — unregistered general-help QA candidates (2026-11-04)

**Status: Draft / BLOCKED.** Branch `bk/t103-neutral-help-qa-20261104`, base main `23871ed224cbe0d9636c841fd48e3f43bdd3ed1b`. This is an independent synthetic general-help batch, not a change to ImPULS and not an update to consumer snapshots. Existing T96–T102 dialogue progress is separately preserved in [PR #222](https://github.com/Treninem/Bot-Knowledge/pull/222).

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

