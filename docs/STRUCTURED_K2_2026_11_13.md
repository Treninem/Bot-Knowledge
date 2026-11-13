# Structured K2 — staged continuation (13.11.2026)

**Owner authorization:** `docs/OWNER_AUTOMATION_SCOPE_2026_11_02.md`. This is candidate-only material for `Treninem/Bot-Knowledge`; no permission to alter live bots or private repositories.

## Baseline and exact counters

- Main checked before work: `6c9f430da47f137d39a72bbd28c057cfb8f6be96`.
- Continuing PR: [#661](https://github.com/Treninem/Bot-Knowledge/pull/661), branch `bk/structured-information-k-20261111-2100`, previous head `d781ee654ca6601c43a3734019255551ef5a5f53`.
- Original pack: `packs/ru/structured_information_qa.json`, SHA-256 `55b3f6126d36cd92687d005b7fedf5a11df9ee61cf453103accdf1f13c8498f0`, blob `8b3d596b5b50d3d319ebf450c96d5623fc99d26a`.
- Before K2: **54 stable intents × 45/100** (3 registered + 9 old staged + 33 K candidates). K held 1,782 entries and was close to 2 MiB.
- Added in this checkpoint: **108 new synthetic answers**, two independently written context-specific scenarios for each of those 54 intents, suffixes `52` and `53`. Original wording of the questions and the intent IDs remain unchanged.
- After K2: **54 × 47/100**; **54 partial**, **0 new complete sets**, **53 remaining per intent**, **2,862 in total**. K2 holds 108 replies. K and all earlier staging remain unchanged.
- Next stable suffix: **54** for the same 54 intent IDs. Do not recreate K2 answers on another run.

## Application and QA

K2 is `consumer_registered=false`, `all_ai_bots`, Russian, `direct` and `read_only`, requiring an explicit matching context. Every reply has a context note and an avoidance rule. No moderation sanctions, identities, tokens, private messages, commands or fabricated ImPULS features are included. Registered manifest and consumer caches are untouched.

Before writing, generated entries were matched against the 54 existing stable questions, checked for unique IDs, normalized answer/context texts, and screened lexically against the older J stage and registered source pack with a token-Jaccard cutoff of 0.70. **This preliminary screen does not constitute independent semantic approval across all open PRs.**

Dedicated regression: `scripts/test_structured_k2_20261113.py`, wired into `.github/workflows/structured-k-20261111.yml` with read-only permissions and exact PR head checkout. Its tests verify registered source hash/manifest isolation, 54-intent counters, conditions and safety, and textual overlap against every available earlier structured staging file plus the registered source. The actual result of GitHub CI must be read for the final head; test creation alone is not a PASS.

## Publication blockers

The existing consumer snapshot is close to **8 MiB**. K2 is only an unregistered staging candidate file and does not solve the snapshot limit. Full independent semantic/context evaluation, tested consumer selection/delivery, current-main reconciliation, exact-head CI and eventual post-main CI remain required. Do not merge or claim a live-bot capability until those gates pass. No paid CI or bot deployment.
