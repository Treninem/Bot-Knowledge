# T96 — safe staged conversational QA (2026-11-04)

Status: **Draft / BLOCKED; not published to consumers**. Base main at last read:
`23871ed224cbe0d9636c841fd48e3f43bdd3ed1b` / manifest
`2026.11.04.026`. Active branch:
`bk/t96-staged-dialogue-repairs-20261104`. PR:
https://github.com/Treninem/Bot-Knowledge/pull/222

## Context and risk gates

The owner prohibits paid GitHub Actions and paid services. Parallel BK
PR #214 owns the next manifest version `.027` and three ImPULS help records;
#219 separately edits the moderation pack and manifest; #220/#221 are
independent validator/search drafts. Do not rewrite their changes or claim
that #383 or the live BotHost has consumed this data.

The staged data is in `staging/ru/dialogue_repair_t96.qa.v1.json` using
the existing `qa.v1` shape. It is **not** in `manifest.packs`: no new registered
pack, no manifest/cache/version edit, and **zero consumer snapshot-byte growth**.
This also means that **zero new answers are available from live consumers**
until explicit acceptance, packaging and consumer verification.

## Exact staged counts and durable continuation

- **45 distinct canonical intents**, **90 search aliases**, **205 original answer
  strings** (including variants). The ten newly created intent IDs are
  `dialogue_t96_036` through `dialogue_t96_045`.
- In this revision, **35 existing IDs** `001`–`035` each grew
  **3 → 5 replies**, producing **70** additional candidate replies.
  Ten new intents received **3** replies each, adding another **30**.
  **New candidate answers this run: 100**. Existing 105 are *not* counted
  again. New canonical questions this run: **10**; aliases: **20**.
- Unfinished target: `001`–`035` are **5/100** (95 remain each);
  `036`–`045` are **3/100** (97 remain each). Total missing to
  aspirational full sets: **4,295**. No new set is 100/100.
- Cases: constructive disagreement, uncertainty, social context, group
  address, joking, respecting silence, non-duplicative help, unknown
  consent, incomplete answers, clipped screenshots, disagreement without
  pressure, partial group decisions, boundaries and emotional support.
- Existing baseline `reply_catalog.json` remains untouched; earlier
  verified main tally of 119 × 100 = 11,900 belongs to other sets.
  Do not interpret staged data as an increment to those sets.
- The staged JSON is **70,687 UTF-8 bytes**. The last independently measured
  base snapshot was **7,519,262 / 8,388,608 bytes**, with **869,346 bytes**
  available. The staged file is excluded from that snapshot. Recompute
  actual bytes and manifest hashing on the latest base *before* publication.

## Tests, evidence and limitations

Connected GitHub-read preflight, pinned to the base SHA above and the
current T96 branch snapshot:

- Parsed **all 45** records; **135 distinct normalized question/alias
  strings**, **205 distinct normalized answer strings**, unique IDs.
  Read-only, no-personal-data and direct-address markers and allowed
  audience/context values checked. One new case is restricted to
  `group_addressed` explicitly; others allow all three contexts.
- Compared with **2,303 records from all 11 registered `*_qa.json` packs**
  in pinned main: **0 exact normalized question collisions**, **0 exact
  normalized response collisions**, **0 duplicate IDs**.
- Also checked current head overlays of BK #214 (help) and #219
  (moderation), and the small `dialogue.json` pack: **0 exact collisions
  observed**. No new canonical question had word-bigram Jaccard ≥ 0.30
  with main QA questions. These are lexical tests, *not* semantic proof.
- The large `reply_catalog.json` and `social_dialogues.json` were
  **not fully re-parsed in this revision**: the connected file response was
  truncated. A prior 35-intent preflight covered them, but the new
  100 candidates need the full local tests below. Do not report that
  step as complete.
- Updated `scripts/test_staged_dialogue_t96.py` with counters, schema
  scope and full-snapshot comparisons. **Python tests NOT RUN on D:** or
  on a full checkout; likewise `scripts/validate_pack.py` and #383
  consumer integration NOT RUN. GitHub exact-head CI NOT RUN: paid Actions
  are prohibited. No merge/post-main or BotHost tests.

## Required next steps

1. On a fresh local `D:` checkout with exact branch SHA, execute
   `python -B scripts/test_staged_dialogue_t96.py`,
   `python -B scripts/validate_pack.py`, and the dedicated schema checker
   for staged qa.v1. Inspect potential semantic near-duplicates manually.
2. Compare with updated main, all open PRs and exact consumer #383
   snapshot handling. Confirm sizes and all SHA-256 against file bytes.
3. When version ownership and required checks are resolved, move accepted
   records to an **existing registered qa.v1 pack**, preserve intent IDs,
   update manifest/version/hash, rerun tests, and only then consider
   a guarded ready/merge. Do not weaken required checks or pay for CI.
4. Keep partial-set counters above in the PR or replacement progress note.
   Never double-count candidates as published records.
