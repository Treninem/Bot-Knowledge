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
