# Prompt-literacy dialogue for all compatible AI consumers — 2026-11-11

## Scope
A new, independent reusable Russian language skill: help a person formulate a clear AI task without inventing facts or granting the assistant extra access. These are **original synthetic contextual assistant replies**, not transcripts, model training or automatic functionality. Each reply requires a directly addressed request and a matching situation.

- Initial verified source ref: Bot-Knowledge main `daa81c091497735dd0754ecffead5aac9b234e3f`.
- Published reference `packs/ru/social_dialogues.json`: Git blob `d56ff304da7165bd63c328f3220a1f6d3d26e3ab`; actual registered SHA-256 expected `0cfedc133354a69522fecc3cda6bc21533c66005f0dc207050075f787dc977a8`; manifest version `2026.11.09.003`. Dedicated Python test checks these against **real file bytes**; do not rely on formatting alone.
- Stage A `staging/ru/prompt_literacy_20261111_context_pool.json` is `consumer_registered=false`, audience `all_ai_bots` only, no moderation power, local state writes, credentials, private message content or consumer integration.

## Canonical intents and exact checkpoint

| Stable ID | Canonical question | Existing baseline | New in A | Total staged | Missing to 100 |
| --- | --- | ---: | ---: | ---: | ---: |
| `prompt20261111_goal` | How to state the objective | 0 | 10 | 10 | 90 |
| `prompt20261111_audience` | Name the target audience | 0 | 10 | 10 | 90 |
| `prompt20261111_inputs` | Provide sufficient source data | 0 | 10 | 10 | 90 |
| `prompt20261111_limits` | Separate hard constraints and wishes | 0 | 10 | 10 | 90 |
| `prompt20261111_examples` | Use examples without copying | 0 | 10 | 10 | 90 |
| `prompt20261111_format` | Choose a useful output format | 0 | 10 | 10 | 90 |
| `prompt20261111_success` | Define an observable acceptance criterion | 0 | 10 | 10 | 90 |
| `prompt20261111_revision` | Give actionable feedback to improve a draft | 0 | 10 | 10 | 90 |
| `prompt20261111_uncertainty` | Request explicit limits and evidence | 0 | 10 | 10 | 90 |
| `prompt20261111_handoff` | Transfer project progress accurately | 0 | 10 | 10 | 90 |

**New in this PR: 100 candidate replies** across **10 canonical questions**, zero completed 100/100, ten partial sets 10/100 and exactly 900 still needed. These are a new independent series; counts from previous teaching, quantification, accessibility and other work are not added to this series.

## Quality and permission boundaries

Pre-commit connector-side audit of A: 100 unique stable response IDs, 100 distinct normalized texts and 100 distinct normalized applicability notes; zero exact duplicate, maximum pairwise token-Jaccard **0.20** (threshold 0.80). This is a lexical screening, not a guarantee against all similar meanings. Editorial review, cross-registered source comparison and GitHub exact-head Python QA are still required.

Scope is strictly natural-language coaching. Examples about software, files or messages **do not grant** write access or assert any result. They do not describe any secret implementation from ImPULS. A user asking for a private chat transcript, credentials, sanctions or uncontrolled change does not gain permission from this pack.

Python gate: `python -m unittest scripts.test_prompt_literacy_20261111 -v`. This checks real source SHA, manifest, structure, normalized IDs, context and privacy, lexical duplication and registered QA exact reply matches. Run on **the current exact PR head**; record actual result rather than claiming a local test occurred.

## Next action

First reconcile any concurrent work on the same prefix, then extend this exact series with suffix **11–20** for each intent, preserving the 100 existing responses and their contexts; repeat until reaching 100 useful choices per intent, without cosmetic paraphrases. Do not register the staging data in manifest until a compatible, reviewed consumer interface, size budget and publication gate are demonstrated. No live bot, BotHost, ImPULS or cache changes.

## Continuation B–C — 2026-11-11 (separate draft from #641)

The previous PR #641 was merged into main at `9c18349c3ad9f3305d2520e74b116c0a1109ff49`; 39/39 exact-head and 39/39 post-main checks passed. The 100 replies in stage A are **previous work**, not new in B/C.

This independent continuation contributes **200 NEW** original synthetic context-bound Russian replies, across **the same ten stable intents**: stage B IDs 11–20 and stage C IDs 21–30, ten per intent per stage. Previous 100 + new 200 = **300/1000**, ten partial intent sets **30/100**, exactly 70 missing per intent / 700 remaining, zero completed 100/100.

- Stage B `staging/ru/prompt_literacy_20261111_context_delta_b.json`, parent blob A `fad75d3166445c76dbf58a0160f65ad0aa40373a`.
- Stage C `staging/ru/prompt_literacy_20261111_context_delta_c.json`, parent blob B recorded in the C file.
- Data is **unregistered** with `consumer_registered=false`. The current manifest `2026.11.09.003` and source `packs/ru/social_dialogues.json` SHA-256 `0cfedc133354a69522fecc3cda6bc21533c66005f0dc207050075f787dc977a8` remain unchanged. No consumer update or new command is implied.
- Authoring-side GitHub connector checks: 300 different IDs, 300 normalized replies and 300 context notes; no exact duplicates; maximum pair token-Jaccard **0.2333** across A/B/C. This automated metric is not exhaustive semantic review.
- New test `python -m unittest scripts.test_prompt_literacy_b_c_20261111 -v` checks real source bytes, Git blob ancestry, all counts, uniqueness, scope, privacy and registered exact overlap. Must pass on the exact head via GitHub CI before merging. A local Python pass has not been claimed.
- Next addition should start from suffix **31**, preserving 300 existing replies. Distinct real applicability matters more than reaching 100 by superficial variations. ImPULS, BotHost, live consumers and caches are untouched.

## Continuation D — 2026-11-11

Separate dependent stage, 100 **new** original contextual RU replies, same ten canonical intents, suffix IDs **31–40**. Prior A–C count 300; cumulative staging **400/1000**, ten partial sets **40/100**, 60 missing per intent / 600 remaining, zero 100/100. Parent stage C Git blob `6016a641eea4c380773c212b5f8063d193af38e4`. Current D blob checked by repository readback before publication. No registered pack, manifest, cache, consumer, ImPULS or BotHost edits.

Connector-side verification of 400 A–D entries: 400 unique IDs, 400 normalized texts and 400 context notes, no exact duplication, maximum pair token-Jaccard **0.2800**. Tests now include four immutable stages, parent Git blob chains, byte SHA-256 source pack and scope/privacy restrictions. The lexical screen is not full semantic proof. **Do not merge D** until exact-head tests and compatibility with final merged B/C are checked. Start next suffix at 41; do not repeat old candidates.
