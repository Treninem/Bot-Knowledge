# T96 — staged natural dialogue recovery QA (2026-11-04)

Status: **Draft candidate only; not published to consumers.** Base `main`:
`23871ed224cbe0d9636c841fd48e3f43bdd3ed1b`, manifest
`2026.11.04.026`. Staging branch:
`bk/t96-staged-dialogue-repairs-20261104`.
Draft PR: https://github.com/Treninem/Bot-Knowledge/pull/222 (BLOCKED; no CI / merge).

## Why staged, rather than added to manifest now

Bot-Knowledge #214 is an active parallel Draft with `manifest.json` and
version `.027`; #219 also changes manifest, and #220/#221 are separate
blocked validator/search Drafts. Do not overwrite their content, cache, version
or commit history. The owner also prohibits paid GitHub Actions. To avoid
a version collision and untested ImPULS #383 8 MiB consumer growth, these
synthetic examples are in a **single non-registered file**:

`staging/ru/dialogue_repair_t96.qa.v1.json`

It uses the existing `schema/qa.v1.schema.json` metadata/record shape, but
is intentionally absent from `manifest.packs` and will **not** be indexed,
downloaded or answered by running consumers. This is not a 39th package.
Do not infer a live ImPULS/BotHost capability from this PR.

## Actual content and bounded progress

- **35** different user-facing canonical questions (not spellings of one
  question), **70** searchable aliases, **105** separately written response
  strings: one answer and two context-sensitive alternatives for each.
- Coverage: mixed-message tone, tentative assent, non-duplicative bot replies,
  contested words, CAPS, acknowledging corrections, constructive criticism,
  gentle refusal, empathy without invented blame, unfamiliar audiences,
  outdated rule quotations, partial objections, divergent social reactions,
  unknown delays, emotions without questions, fabricated motive avoidance,
  absent participants, non-manipulative persuasion, intermediate group summaries,
  boundary setting and other everyday dialogue repairs.
- All 35 staged intentions have **3/100 authored candidate replies**, or 97
  remaining against the aspirational 100-per-intent target. This does not claim
  they are already accepted into a registered consumer pack. Do not generate
  97 mechanical paraphrases just to close the counter.
- `reply_catalog.json` on the pinned base contains **119 verified 100/100
  sets = 11,900 replies**; this PR does not edit it.
- No changes to existing package files, manifest, consumer cache, or ImPULS.

## Validation evidence and limits

In a connected **read-only GitHub data preflight** (not a local Windows
Python run), parsed the staged QA JSON and compared normalized question/alias
and answer strings with **3,505 QA records** read from 11 baseline QA packs
and 5 head overlays (including #214 and #219). Exact normalized collisions:
**0** questions/aliases, **0** answers. A word-bigram Jaccard screen of
candidate canonical questions against those QA questions returned **0
candidates at or above 0.22**. Independently scanned **13,106** textual
entries in `reply_catalog`, **9,862** in `social_dialogues`, and
**123** in `dialogue`; exact normalized collisions with candidate queries
and responses: **0**. A separate bigram-indexed comparison of **105 candidate response strings**
against **20,509 existing response strings** from QA, reply-catalog and
social-dialogue packages found **0 scores >= 0.50**; the greatest score was
**0.3077** (a common polite-refusal pattern). This is a lexical similarity
screen, not proof against all semantic paraphrases; editorial review remains
necessary.

The same preflight found 35 unique IDs, 105 normalized distinct questions
and aliases, 105 normalized distinct response strings, required read-only /
direct-address / no-personal-data scope markers for all records, supported
contexts and valid pinned provenance. Privacy marker screen found no candidate
emails, obvious tokens or long phone-like strings.

`scripts/test_staged_dialogue_t96.py` records eight offline tests for exact
schema/scope, JSON format, normalized uniqueness, cross-pack questions/answers,
near matches, privacy, cross-format string duplicates, and near-duplicate response screening. **Python test script
has been authored but NOT RUN on D:**; it must run on a real checkout.
Likewise `python -B scripts/validate_pack.py` and ImPULS #383 integration
have NOT run in this session. No paid Actions were launched, so exact-head
GitHub CI and post-main CI are **not verified**.

The pinned baseline Git tree (raw file sizes, 38 manifest-registered packages
plus manifest) gives **7,519,262 bytes** of consumer snapshot out of
**8,388,608 bytes**, leaving **869,346 bytes**. The staging file is not part
of this snapshot and adds **0 consumer bytes**. The staged file itself is
45,198 UTF-8 bytes. Recompute on the latest base before any migration to packs.

## Next permitted steps

1. Run on a full fresh Windows D: checkout without paid workflow:
   `python -B scripts/test_staged_dialogue_t96.py`,
   `python -B scripts/validate_pack.py`, plus current consumer #383 tests.
2. Editorially check intended tone, context, aliases and semantic overlap
   against newly merged packages and active drafts.
3. After #214/#219 version ownership is resolved, migrate accepted records
   into a suitable **existing** `qa.v1` package, update its real SHA-256,
   manifest/version/cache and progress counters and re-evaluate 8 MiB. No
   publication or merge until gates actually pass.
4. Track the staged rows by IDs `dialogue_t96_001` through
   `dialogue_t96_035`; if carried into a consuming pack, preserve or map
   these IDs and update this record. Avoid counting staged and merged copies
   as two additions.
