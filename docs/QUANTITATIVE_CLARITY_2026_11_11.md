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
