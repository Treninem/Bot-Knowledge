# Quantitative clarity — contextual Russian candidate replies (2026-11-11)

General **staging-only** synthetic replies for `all_ai_bots`; no live calculator or measurement access, no ImPULS changes, no sanctions, no automatic consumer integration. This family is distinct from mechanical numeric typo repair: it explains unknown denominators, rates, absolute vs relative change, running totals, uncertainty, missing inputs, boundary inclusiveness, incompatible units, ratios and reproducible verification.

## Exact checkpoint A
- Verified original source: `packs/ru/social_dialogues.json` at main `1bf2a82834c674a50e7c44e11a41f4fc77861f3d`, Git blob `d56ff304da7165bd63c328f3220a1f6d3d26e3ab`, registered SHA-256 `0cfedc133354a69522fecc3cda6bc21533c66005f0dc207050075f787dc977a8`.
- Ten stable `quant20261111_*` intents; ten original situational replies each, **100 new candidates**. Each **10/100**, remaining **90 per intent**, aggregate **900**. Fully completed: **0**. Counts are for this standalone family, not all Bot-Knowledge.
- 100 different exact IDs, normalized replies and situation notes in precommit JS checks; **0 exact matches inside this stage**, pairwise maximum lexical token-Jaccard 0.2174 (<0.8). Cross-corpus semantic duplication cannot be ruled out by this check. Editorial and actual Python/CI results require separate confirmation.
- `manifest.json`, published pack bytes/SHA-256, cache keys, consumers, and live bots **unchanged**. This staging file is not a registered pack; adding it does not publish functionality.
- Follow-up: continue **existing intents** from suffix **11** rather than restarting, check current main and independent open PRs, run exact-head and post-main CI under gates, and prioritize useful distinct cases instead of paraphrase padding. The following 10 intents are distinct canonical questions, not spelling variants.

1. `quant20261111_percent_basis` — От какого значения считаются проценты?
2. `quant20261111_rate_scope` — За какой период или объём указана сумма или скорость?
3. `quant20261111_delta_type` — Это изменение в единицах или в процентах?
4. `quant20261111_cumulative_vs_increment` — Это итоговое число или прибавка за период?
5. `quant20261111_precision_limits` — Насколько точным можно считать это число?
6. `quant20261111_missing_inputs` — Чего не хватает, чтобы посчитать ответ?
7. `quant20261111_boundary_scope` — Входит ли граничное значение в условие?
8. `quant20261111_unit_consistency` — Можно ли сравнивать числа в разных единицах?
9. `quant20261111_ratio_denominator` — Что означает отношение или доля?
10. `quant20261111_calculation_check` — Как проверить, что расчёт верный?

Owner's authorization to expand and merge verified Bot-Knowledge PRs is in `docs/OWNER_AUTOMATION_SCOPE_2026_11_02.md`; safeguards remain in force. Do not claim the candidate answers are active in ImPULS or AuroraFox.

## Stage B checkpoint
- **100 NEW** original context-specific candidates, suffix 11–20 per intent; ten stable intents at **20/100**, **80 missing each / 800 missing total**, zero completed. Stage A 100 are prior data and not counted as new for Stage B.
- Stage A blob `c2dd1ed56e487f20041fb99fa44f46e2184ec873` is verified as parent; both unregistered JSON stages have matching registered source SHA-256 `0cfedc133354a69522fecc3cda6bc21533c66005f0dc207050075f787dc977a8`. Combined 200 distinct IDs, normalized response texts and context notes; 0 exact duplicates, maximum token-Jaccard 0.2308 (<0.8), not a semantic uniqueness guarantee.
- Python tests extend to both stages; CI on current exact head and post-main actual merge SHA must succeed before publication. Manifest, caches and live consumers remain unchanged. Next suffix **21**.

## Stage C checkpoint
- Another **100 new synthetic** situational replies (suffix 21–30) across the same ten stable canonical intents. Total A+B+C **300/1000**, each **30/100**, **70 remaining per intent / 700 total**, zero completed 100/100.
- Prior B Git blob `9783fe46d5d07273650f8822501cff5a764ec0c1` is recorded in `parent_stage_blob_sha`. A and B are not recounted as new in C. Combined 300 unique IDs, normalized texts and context notes, 0 exact duplicates, max token-Jaccard 0.2917 (lexical only). Broader editorial/corpus and full CI remain required.
- Manifest/registered pack SHA-256 untouched, consumers not updated. Next suffix 31.

## Stage D checkpoint — 11 November 2026
- After the verified merge of #628 to main `eac2ef761fe54f4f9edb3b5fa7c8ecb35e509fe8`, added **100 new original contextual RU replies** (IDs 31–40 per stable intent), not repeating A–C. Each of ten intents: **40/100**, 60 missing, **400/1000** cumulative staging candidates.
- Stage C parent Git blob `1bfdad2d0f016427fdc832c1d3b5df08a14cd8d4`. Exact normalized IDs/texts/context notes 400/400 in connector-side precommit checks; token-Jaccard max 0.381. Counts are candidate counts, not approved consumer material.

## Stage E checkpoint — 11 November 2026
- Another **100 NEW original synthetic replies** (IDs 41–50 per intent). Total **500/1000** staging-only candidates, each of ten intents **50/100**; exactly **50 remain per intent / 500 total**, **0 completed sets 100/100**. D's 100 and pre-existing A–C's 300 are not counted again as new in E.
- Stage D parent Git blob `7b2137e8c1482a3afed6dc2b6cc8d3853809b2d9`; D and E each use consistent original source SHA-256 `0cfedc133354a69522fecc3cda6bc21533c66005f0dc207050075f787dc977a8`.
- 500/500 unique IDs, normalized answer strings and context conditions; no exact duplicates and max token-Jaccard **0.5714** among all five stages (connector-side check). This is not proof of full semantic distinctness or global corpus exclusion. New read-only Python QA and exact-head workflow validate metadata, version/source integrity, Git blob ancestry, context guards and isolation.
- Scope: two new JSON staging files, an additional deterministic Python QA file, adjusted existing read-only workflow and this checkpoint document. Registered pack, manifest, cache keys, ImPULS and live bots unchanged; no permissions or sanctions created.
- Next: run **ALL** required exact-head CI against the actual PR branch SHA; verify post-main on #628 merge SHA first, then current main and expected-head guard before any merge. Continue these stable ten intents from suffix **51** in a new independent extension; broaden to other practical intents without meaningless paraphrases.
