# Structured N — checkpoint N89–N91, 13 November 2026

## Сохранённая партия и точный прогресс

В существующем [PR #662](https://github.com/Treninem/Bot-Knowledge/pull/662) продолжены 60 устойчивых структурных намерений. За этот запуск добавлено **180 оригинальных русских ответов** (по три на намерение: N89, N90, N91). Исходные 480 ответов N81–N88 сохранены; новые тексты проверены на смысловые пересечения с N и **20** формулировок содержательно переписаны без увеличения счётчика. Условия выбора указаны в `context_note`; публикации в consumer пока нет.

Данные: [N89–N90](https://github.com/Treninem/Bot-Knowledge/commit/99112043e94b5fb7c1cda5bbf3c0d6afa793a59c), [13 смысловых исправлений](https://github.com/Treninem/Bot-Knowledge/commit/56a6bca2c5ee461ae83cf48636aae2853cfee131), [N91](https://github.com/Treninem/Bot-Knowledge/commit/3529b81597eed404efa7766e7976a3f5282ef17b), [7 смысловых исправлений](https://github.com/Treninem/Bot-Knowledge/commit/d3dfef4e24c7cb5dc7ff0b47a849d14a6b76531e). Файл N на последнем data head: **754 822 байта UTF-8**; SHA-256 содержимого **`91b4038ab691d3ce6d9a4b13538520a2424d5995075b4449504e354ec8444457`**; Git blob `7f6dc4ac84e290ab903906910d1b4abf5b74379e`. Алгоритм SHA-256 сверялся с эталонным `abc` и известным хэшем предыдущего N88.

| Источник | На одно намерение | Всего |
| --- | ---: | ---: |
| Опубликовано на main | 3 | 180 |
| Ранние staging A–J (отдельные PR) | 11 | 660 |
| L в #662 | 31 | 1 860 |
| M в #662 | 29 | 1 740 |
| N81–N88 до запуска | 8 | 480 |
| **N89–N91 за этот запуск** | **3** | **180** |
| **Суммарно опубликовано + staged** | **85/100** | **5 100/6 000** |
| **Осталось** | **15** | **900** |

**60 частичных, 0 новых завершённых наборов 100/100.** Только внутри #662 сейчас L+M+N = **4 260** кандидатов. Следующий стабильный суффикс каждого `intent_id` — **92**. Нельзя повторно считать старые записи как новые.

## Проверки и публикация

- GitHub readback подтвердил 60 записей и полный ряд N81–N91, всего 660 N ответов, уникальность нормализованных ID, текстов и условий внутри N. Для новых вариантов выполнялась лексическая проверка token-set Jaccard внутри их намерений, без случаев ≥0,70. Это предварительный автоматический фильтр, не полная независимая экспертиза всех смыслов.
- На промежуточном exact-head `56a6bca2c5ee461ae83cf48636aae2853cfee131` специализированный [N CI](https://github.com/Treninem/Bot-Knowledge/actions/runs/43406762793) завершился SUCCESS: Python L/M/N 11/11 и N под `-O` 4/4. Он не подтверждает последующую N91 и редакторские изменения; для фактического финального head обязательна повторная проверка всех CI.
- Последний проверенный main SHA: `6c9f430da47f137d39a72bbd28c057cfb8f6be96`. Manifest не изменялся, файл N не зарегистрирован, данные не доставлены потребителям. Общий размер опубликованного снимка близок к ограничению **8 МиБ**; нужна подтверждённая стратегия отбора/доставки без переполнения и реальная consumer-проверка. Ветку требуется сверить с текущим main.
- PR остаётся **DRAFT / BLOCKED** до завершения exact-head CI, независимой смысловой и контекстной проверки, решения вопроса с бюджетом снимка и согласования base/head. Post-main CI отсутствует, потому что merge не было. Не менялись ImPULS, BotHost, работающие кэши, секреты, платные сервисы и branch protection.

Следующий шаг: проверить все CI на коммите журнала, продолжить N92 только оригинальными различными ситуациями, отдельно готовить потребительски совместимый небольшой утверждённый набор, не переполняя manifest/snapshot.

---

# Structured N — checkpoint N86–N88, 13 November 2026

## Actual additions and provenance

- Continued [PR #662](https://github.com/Treninem/Bot-Knowledge/pull/662) on its existing 60 canonical structured-information intents; **180 new, authored Russian replies** (one per question in each of N86, N87 and N88). All 300 earlier N81–N85 replies were preserved. This is staged material only, not registered consumer knowledge.
- Data commits: [N86](https://github.com/Treninem/Bot-Knowledge/commit/fb3b1aeaf48791c67c78790d806c4b93a27767f8), [N87](https://github.com/Treninem/Bot-Knowledge/commit/aabae2e45a14d398a29cdf068d3ba71bb078c80d), [N88](https://github.com/Treninem/Bot-Knowledge/commit/7306e0eabc0c8936b62caff3870079fd7db7fcfc). The N regression was changed from hardcoded 300 replies to a checked dynamic checkpoint in [a5ea666](https://github.com/Treninem/Bot-Knowledge/commit/a5ea666d5fb69087c3dea4b4b8f875ede2086050).
- Topics cover precision, rounding, data provenance, missing denominators, tax and currency comparison, salary hours, date/time-zone interpretation, chart/table aggregation, overlapping groups and small-cell privacy. Each answer requires the specific context note; all are answer-only with no sanction or private-data operation.
- Direct GitHub readback verified **60 intents × 8 new N replies = 480 N candidates**, 480 distinct normalized IDs, reply texts and context notes. New N86–N88 **180** replies have 0 exact or token-set Jaccard ≥0.70 collisions against the published structured source and N81–N85 plus earlier new replies; highest observed overlap **0.39286**. This is lexical/structural screening, **not** a certificate of semantic diversity or consumer selection. L/M cross-pool tests are delegated to the existing Python regression and exact-head CI; do not claim a full independent editorial review.
- Actual N JSON Git blob **`32c7a56e89123664c27d648c2d2c7d0c50d174e9`**, **558,530 UTF-8 bytes**, SHA-256 **`f2499dbb43c45798fb835c63eac0c5dfcef6bd2a690f7e436f120c4841a63c0a`**. The byte-hash implementation verified standard SHA-256 `abc` and reproduced the previous N85 hash `eab092ab74ca92b1f668a3fdb71986f331575703e176e4f137e3fef82735881f`. Each individual stage file remains under 2 MiB.

| Source | Replies per intent | Total across 60 |
| --- | ---: | ---: |
| Published structured QA on main | 3 | 180 |
| Separate A–J staged answers | 11 | 660 |
| L staged in #662 | 31 | 1,860 |
| M staged in #662 | 29 | 1,740 |
| N81–N85 (previous) | 5 | 300 |
| **New N86–N88** | **3** | **180** |
| **All published + staged** | **82/100** | **4,920/6,000** |
| **Remaining** | **18** | **1,080** |

**60 partial, 0 newly completed 100/100 sets.** L+M+N together in #662 = **4,080 staged**. The next stable suffix for each `intent_id` is **N89**. The progress count is not a count of published consumer-ready responses.

## Quality and publication gate

- The GitHub exact-head run for data commit N88 reported specialized N SUCCESS; full quality checks were 40/41 SUCCESS and one still in progress when read. A **new exact-head CI check is mandatory for this journal commit**, and its eventual status must be reported separately. Python tests in the container were not run because `github.com` did not resolve; Python executed in the read-only workflow only when that workflow reports completion.
- Current main read: `6c9f430da47f137d39a72bbd28c057cfb8f6be96`; branch and base still diverge and must be reconciled without force-push. Published manifest remains unchanged. Last independently counted published snapshot was 7,992,490 bytes / 8,388,608 bytes; the accumulated #662 stages cannot be registered together under the 8 MiB consumer cap.
- **Draft/BLOCKED:** exact-head complete CI for the final head, independent semantic/context-routing and cross-PR review, safe consumer delivery/manifest design within the size cap, reconciliation with current main. Do not merge based only on lexical checks; do not change consumer runtime, BotHost, ImPULS, caches, payment services, branch protection or GitHub secrets.
- Next: evaluate N89 against confirmed contexts, while working separately on proof of consumer-safe selection of a smaller approved subset; preserve original stage IDs and checkpoint counts.

---

# Structured N continuation — verified candidate checkpoint N81–N85, 13 November 2026

## Latest addition N83–N85 — 180 newly authored candidate answers

- Continued the existing [PR #662](https://github.com/Treninem/Bot-Knowledge/pull/662) and its **60 stable canonical intents** in `staging/ru/structured_information_20261113_delta_n.json`. **180 new original Russian replies** (N83, N84, N85; 60 per suffix) have distinct direct-address application notes. Previously saved N81/N82 (120) were preserved. Source main read: `6c9f430da47f137d39a72bbd28c057cfb8f6be96`, with published structural pack SHA-256 `55b3f6126d36cd92687d005b7fedf5a11df9ee61cf453103accdf1f13c8498f0`.
- Data commits: [N83–N84](https://github.com/Treninem/Bot-Knowledge/commit/27963bae9f70853e390d1adf214d157b86d8fc3a) (+120), [N85](https://github.com/Treninem/Bot-Knowledge/commit/e7b53b7e39ed5665904673e3c1c0a7a0ffafb7be) (+60). Structural test commits [N84](https://github.com/Treninem/Bot-Knowledge/commit/ee3f48f98bb9969e421d89ee151c58607c4810b9), [N85](https://github.com/Treninem/Bot-Knowledge/commit/a0dad0140073cc3464b15c1d749a92a23182926d); strengthened all-pairs context-note screening. Read-only SHA-reporting workflow commit [8f236c2](https://github.com/Treninem/Bot-Knowledge/commit/8f236c25121133789b73fe30a4c594033ac1fe99).
- **Actual GitHub readback**: 60 entries and 300 N reply IDs, 300 unique normalized answers and 300 unique normalized context notes; all 60 ID sequences N81–N85 present. Automatic in-stage token-set Jaccard maximum for new material against N81–N84 was **0.2759**, with 0 values ≥0.70; context-note maximum for N81–N84 pairs was **0.4667**, 0 ≥0.70. This is a *preliminary lexical check*. Full semantic/editorial and consumer-routing review remains undone.
- **N file:** Git blob `73069920c3d192f89522dfac6410e519ebe1d247`; 351,521 UTF-8 bytes; **SHA-256 `eab092ab74ca92b1f668a3fdb71986f331575703e176e4f137e3fef82735881f`**. SHA-256 implementation passed the standard `abc` vector and reproduced the previous N81–N82 known byte hash from GitHub. File stays below the 2 MiB limit. Workflow reports its own actual byte hash for independent comparison.
- Scope remains `all_ai_bots`, Russian, answer-only, `read_only`, `requires_direct_address`, `requires_context_match`, `no_personal_data`, `no_sanctions`. No facts about unverified ImPULS commands, no user messages, live data, private identifiers or sanctions are staged.

| Accounting category | Per intent | Total across 60 intents |
| --- | ---: | ---: |
| Published baseline in main | 3 | 180 |
| Earlier independent A–J staging | 11 | 660 |
| L in #662 | 31 | 1,860 |
| M in #662 | 29 | 1,740 |
| N81–N82, previous execution | 2 | 120 |
| **N83–N85, this execution** | **3** | **180** |
| **Cumulative published + staged** | **79/100** | **4,740/6,000** |
| **Still missing** | **21** | **1,260** |

**60 partial sets; 0 newly completed sets.** Exactly **3,900** candidate replies belong to #662 (L+M+N), while the earlier A–J staging is separate. Next stable ID for every intent: `<intent_id>_supp_86`. Do not recount an old variant as new.

### Publication gate and tested limits

Manifest and published pack are unchanged; staged additions are not available to consumers. Actual published-pack payload size sum on main (46 registered files, as listed by GitHub): **7,992,490 bytes** of an **8,388,608-byte** nominal snapshot cap; free room **396,118 bytes** before other overhead. This does not safely accommodate all #662 staged replies, so no full registration or merge is claimed. Main SHA and the PR's base SHA differ; the branch needs non-destructive reconciliation before any eligible merge.

Local checkout Python tests could not run because the container could not resolve github.com. The read-only workflow `.github/workflows/structured-n-20261113.yml` now runs pack validation and L/M/N tests (regular Python plus `-O` for N) against the **actual PR head**; verify that full exact-head CI succeeds on the **latest journal commit**, not an older head. Full independent semantic review, cross-PR editorial review, consumer routing and 8 MiB-safe approved publication remain open. No merge and no post-main CI during this checkpoint; no changes to ImPULS, BotHost, live caches or paid resources.

**Next:** N86 for genuinely new contexts only, then other underserved questions; in parallel establish an approved consumer-safe selection approach rather than publishing all staged material beyond the snapshot limit.

---

# Structured-information continuation N81–N82 — 13 November 2026

## Scope and actual new content

- Continue existing [PR #662](https://github.com/Treninem/Bot-Knowledge/pull/662), preserving its 60 stable canonical intent IDs and already staged answers. Latest previous source checkpoint was M80, commit `8d3b6c79a23b82358f52a12d5be6e9d7faa2922f`. Published baseline: main `6c9f430da47f137d39a72bbd28c057cfb8f6be96`.
- Two new separately authored contextual situations per intent, **120 newly saved synthetic Russian replies** (suffixes **81 and 82**) in `staging/ru/structured_information_20261113_delta_n.json`. Content IDs do not reuse previous suffixes. Applied only to an explicitly addressed question with a matching circumstance. All examples are read-only, general-audience, without personal data, sanctions, automatic consumer actions or claimed memory.
- Data commits: [N81](https://github.com/Treninem/Bot-Knowledge/commit/130af707447913fffa7ae3835732f7d0ace9c6d0) (+60), [N82](https://github.com/Treninem/Bot-Knowledge/commit/9ef26295eedf0234af7d40fd3a6579730bed11f9) (+60). Checkpoint metadata spelling corrected without increasing the count in [5e68913](https://github.com/Treninem/Bot-Knowledge/commit/5e68913b5ed86b4ee0b7638889be3b3ee589cc69).

## Exact accounting

| Source | Per intent | Total |
| --- | ---: | ---: |
| Published structured QA | 3 | 180 |
| Earlier staged A–J | 11 | 660 |
| Existing L | 31 | 1,860 |
| Existing M | 29 | 1,740 |
| **NEW N81–N82** | **2** | **120** |
| **Combined** | **76/100** | **4,560** |
| **Missing** | **24** | **1,440** |

**60 partial intents; zero newly completed 100/100.** Continue in this same PR at `<intent_id>_supp_83`. Preserve all earlier IDs and source counts. Cumulative replies *only in this PR* are L+M+N = **3,720**. The published and earlier A–J sets must not be mistaken for additions from this run.

## Preliminary validation and safety

- GitHub readback parsed the N JSON: 60 stable IDs, **120** N replies, sequential suffixes and matching context notes. All 120 reply texts and notes were authored for distinct concrete situations; 0 exact normalized collisions and 0 token-set Jaccard ≥0.70 against the published structured pack, L and M. Normalization covers case, whitespace, punctuation and е/ё. An exact normalized note comparison to L/M also found 0 matches; within-intent N notes maximum token-set Jaccard was **0.3333**.
- N JSON actual UTF-8 size: **155,746 bytes**. Git blob `eb2981d7a640505ef096ccc8f1b666f0dc0b19eb`. SHA-256 on the actual UTF-8 content: `1e641e80b9fe888d0fab8e5acb10995ea10b7b702b53909ac419eb5f62e3edbf`. The SHA-256 implementation passed the standard `abc` test vector. File remains below the 2 MiB planning limit.
- Added `scripts/test_structured_n_20261113.py`: source SHA-256/Git-blob and manifest integrity, N/L/M counts and IDs, safety metadata, normalized text/context uniqueness, privacy check, lexical proximity, note distance and file-size guard. The initial test escaping mistake was corrected in commit [749ac380](https://github.com/Treninem/Bot-Knowledge/commit/749ac3804cfcb93903d6bd60bf92512daa86f787).
- Added read-only `.github/workflows/structured-n-20261113.yml` for exact PR head checkout, source/pack validation, L/M/N tests (Python normal and N under `-O`), no secrets, no persistent checkout credentials. **No claim of Python or complete exact-head PASS until the actual GitHub run finishes.** Local Python checkout was unavailable because the local container could not resolve GitHub.
- These checks establish structural/lexical integrity only. Independent semantic, real consumer routing, cross-PR editorial scrutiny and 8 MiB snapshot-safe delivery remain necessary before merge.

## Publication and remaining gate

Current source `manifest.json` and registered pack SHA are unchanged; N is **unregistered staging**, not additional live bot capability. No edits to ImPULS, BotHost, working caches, protected GitHub settings, paid services or deployment.

Main remains `6c9f430da47f137d39a72bbd28c057cfb8f6be96` at this read. Existing #662 had diverged by 4 base commits; reconcile before merge without force-push. The last verified main snapshot budget leaves insufficient room for all pending candidate pools. Do not bypass it.

**Draft/BLOCKED:** Require real complete exact-head CI for the final PR head, independent cross-stage semantic/context review, demonstrated consumer size/selection compatibility, fresh-main reconciliation and actual post-main verification. A green run for an earlier head does not satisfy a later commit. No PR was merged or closed in this checkpoint.

**Next batch:** N83 and subsequent genuinely useful context-specific answers; update counters by delta, not by file size. Do not expand mechanically where a unique answer cannot be justified.

## Cross-PR lexical screen — same checkpoint

Read the actual Git blobs from the other still-open PRs and compared the **120 new N replies** against their staging reply texts (not against invented summary counts):

| Other candidate pool | Existing replies | Pair comparisons | Exact normalized matches | Token-set Jaccard ≥0.70 | Largest Jaccard |
| --- | ---: | ---: | ---: | ---: | ---: |
| [PR #661 K](https://github.com/Treninem/Bot-Knowledge/pull/661) | 1,458 | 174,960 | 0 | 0 | 0.2903 |
| [PR #663 conversation](https://github.com/Treninem/Bot-Knowledge/pull/663) | 2,000 | 240,000 | 0 | 0 | 0.1935 |
| [PR #664 precision](https://github.com/Treninem/Bot-Knowledge/pull/664) | 1,500 | 180,000 | 0 | 0 | 0.2308 |

**594,960 cross-PR lexical comparisons** and no exact/high lexical collisions. This does **not** prove that the answers are semantically independent, or that live consumers will route them correctly. No unrelated PR was edited, merged or closed.
