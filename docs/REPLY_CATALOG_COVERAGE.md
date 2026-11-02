# Reply catalogue: synthetic RU answers (2026-11-02)

Source main for this series: `e0858cce7c819355cabbebb6da5ed74cf3a54234` (after verified PR #40).
This candidate adds a **new, separate** SHA-pinned pack. It does not rewrite the
100 greeting answers already merged. Only original synthetic examples are used.

## Measured coverage

**97 distinct canonical questions, 9700 authored answers, 27 packs total**.
All 95 earlier questions remain complete at 100/100; there are no partial sets in this snapshot. These are reply
variants, not 443 trained model skills or new executable ImPULS commands.

| Question / intent | Count / 100 | Audience |
|---|---:|---|
| О чём поговорим? (`what_discuss`) | 100 | all AI bots |
| Пошути (`tell_joke`) | 100 | all AI bots, explicit humor opt-in |
| Спасибо (`thanks_reply`) | 100 | all AI bots |
| Пока (`farewell_reply`) | 100 | all AI bots |
| Не понял (`explain_again`) | 100 | all AI bots |
| Я не согласен (`disagreement_reply`) | 100 | all AI bots |
| Мне тяжело (`need_support`) | 100 | all AI bots |
| Мне скучно (`bored`) | 100 | all AI bots |
| Помоги выбрать (`need_decision`) | 100 | all AI bots |
| Ответить на грубость (`boundaries`) | 100 | all AI bots |
| Подкинь идею (`idea_request`) | 100 | all AI bots |
| Помоги извиниться (`apology_help`) | 100 | all AI bots |
| Помнишь прошлый разговор? (`lost_context`) | 100 | all AI bots |
| Сменим тему (`change_topic`) | 100 | all AI bots |
| Чёрный юмор (`dark_humor`) | 100 | all AI bots, explicit humor opt-in |
| Объясни правила (`rules_explain`) | 100 | community bots only |
| Ты уверен? (`no_sure`) | 100 | all AI bots |
| Где настройки ImPULS? (`chat_settings`) | 100 | community bots only |
| Как пожаловаться? (`report_violations`) | 100 | community bots only |
| Где мой профиль? (`profile_access`) | 100 | community bots only |
| Где Пульсы? (`pulse_navigation`) | 100 | community bots only |
| Команды модератора (`moderator_commands`) | 100 | community bots only |
| Открыть панель (`private_panel`) | 100 | community bots only |
| Запустить Данетки (`danetka_start`) | 100 | community bots only |
| Отключить Данетки (`danetka_off`) | 100 | community bots only |
| Подколи по-доброму (`friendly_tease`) | 100 | all AI bots, explicit humor opt-in |
| Поддержать разговор (`conversation_followup`) | 100 | all AI bots |
| Почему это не работает? (`diagnose_problem`) | 100 | all AI bots |
| Как проверить достоверность? (`verify_claim`) | 100 | all AI bots |
| Помоги сформулировать цель (`goal_clarity`) | 100 | all AI bots |
| Помоги составить план (`project_plan`) | 100 | all AI bots |
| Оцени идею (`idea_review`) | 100 | all AI bots |
| Написать ясное сообщение (`message_draft`) | 100 | all AI bots |
| Освоить новый навык (`learning_path`) | 100 | all AI bots |
| Вести групповое обсуждение (`group_discussion`) | 100 | all AI bots |
| Предложи активности чата (`chat_activities`) | 100 | all AI bots |
| Разбор возможного нарушения (`moderation_reasoning`) | 100 | chat moderators only |
| Оригинальная короткая история (`micro_story`) | 100 | all AI bots |
| Разбор противоречивой ситуации (`critical_analysis`) | 100 | all AI bots |
| С чего начать пользоваться ImPULS? (`impuls_first_steps`) | 100 | community bots only |
| Как задать ImPULS обычный вопрос? (`impuls_ask_ai`) | 100 | community bots only |
| Почему ImPULS не отвечает на вопрос? (`impuls_ai_no_reply`) | 100 | community bots only |
| Где посмотреть, как играть в игры ImPULS? (`impuls_game_help`) | 100 | community bots only |
| Чем вопрос ImPULS отличается от команды? (`impuls_command_context`) | 100 | community bots only |
| Может ли ImPULS переносить правила между чатами? (`impuls_chat_isolation`) | 100 | community bots only |
| Как посмотреть версию и изменения ImPULS? (`impuls_release_info`) | 100 | community bots only |
| Как понять, какие права у меня есть в ImPULS? (`impuls_check_permissions`) | 100 | community bots only |

| Как задать хороший вопрос? (`question_crafting`) | 100 | all AI bots |
| Как вежливо отказать? (`tactful_refusal`) | 100 | all AI bots |
| Объясни сложное простыми словами. (`simple_explanation`) | 100 | all AI bots |
| Помоги задать уточняющий вопрос. (`clarifying_question`) | 100 | all AI bots |
| Как дать полезную обратную связь? (`feedback_reply`) | 100 | all AI bots |

| Как понять исключение из правила? (`rule_exception`) | 100 | all AI bots |
| Что делать, если правила противоречат друг другу? (`rule_conflict`) | 100 | all AI bots |
| Как безопасно менять настройку? (`safe_setting_change`) | 100 | all AI bots |
| Как нормально попросить о помощи? (`ask_for_help`) | 100 | all AI bots |
| Как нормально признать свою ошибку? (`admit_mistake`) | 100 | all AI bots |
| Как ответить спокойно в споре? (`calm_conflict_reply`) | 100 | all AI bots |
| Как работает антиспам ImPULS? (`impuls_antispam_help`) | 100 | community bots only |
| Как работает семья в ImPULS? (`impuls_family_help`) | 100 | community bots only |
| Как работает бесплатный розыгрыш ImPULS? (`impuls_raffle_help`) | 100 | community bots only |
| Как играть в «Цепочку слов» ImPULS? (`impuls_word_chain_help`) | 100 | community bots only |
| Как работает журнал Пульсов ImPULS? (`impuls_pulse_journal_help`) | 100 | community bots only |
| Как вернуться к разговору после паузы? (`resume_after_pause`) | 100 | all AI bots |
| Как подвести итог обсуждения? (`discussion_summary`) | 100 | all AI bots |
| Что ты умеешь и чего не можешь? (`capability_boundaries`) | 100 | all AI bots |
| Как исправить недопонимание? (`repair_misunderstanding`) | 100 | all AI bots |
| Как найти компромисс без давления? (`constructive_compromise`) | 100 | all AI bots |
| Как корректно исправить неверный факт? (`fact_correction`) | 100 | all AI bots |
| Как расставить приоритеты? (`prioritize_tasks`) | 100 | all AI bots |
| Как передать задачу другому человеку? (`handoff_task`) | 100 | all AI bots |
| Как оценить риски перед изменением? (`risk_review`) | 100 | all AI bots |
| Как составить хороший чек-лист? (`build_checklist`) | 100 | all AI bots |
| Как правильно проверить изменение? (`verify_change_result`) | 100 | all AI bots |
| Как нормально описать проблему? (`problem_report`) | 100 | all AI bots |
| Как воспроизвести ошибку для разработчика? (`reproduce_bug`) | 100 | all AI bots |
| Как честно сообщить о ходе работы? (`progress_report`) | 100 | all AI bots |
| Как безопасно обезличить материал перед публикацией? (`privacy_before_publish`) | 100 | all AI bots |
| Как тактично напомнить о сообщении без ответа? (`followup_no_reply`) | 100 | all AI bots |
| Как попросить подтверждение перед важным действием? (`confirm_before_change`) | 100 | all AI bots |
| Как подобрать подходящий тон ответа? (`tone_adaptation`) | 100 | all AI bots |
| Как понять непрямой смысл сообщения? (`indirect_meaning`) | 100 | all AI bots |
| Как уточнять детали, не собирая лишних сведений? (`ask_details_safely`) | 100 | all AI bots |
| Как оценить объём работы? (`estimate_effort`) | 100 | all AI bots |
| Как правильно зафиксировать решение? (`decision_record`) | 100 | all AI bots |
| Как работать параллельно и не мешать друг другу? (`parallel_work`) | 100 | all AI bots |
| Как не раздувать задачу по ходу работы? (`scope_control`) | 100 | all AI bots |
| Как распознать подозрительную просьбу в переписке? (`suspicious_request`) | 100 | all AI bots |
| Как объяснить, на чём основан ответ? (`source_provenance`) | 100 | all AI bots |
| Как правильно реагировать на критику? (`respond_to_criticism`) | 100 | all AI bots |
| Как уважительно принять чужой отказ? (`respect_refusal`) | 100 | all AI bots |
| Что делать с непроверенным слухом? (`rumor_handling`) | 100 | all AI bots |
| Как похвалить человека искренне, без лести? (`sincere_praise`) | 100 | all AI bots |
| Как попросить паузу в разговоре? (`pause_conversation`) | 100 | all AI bots |
| Что делать с большим объёмом информации? (`handle_info_overload`) | 100 | all AI bots |
| Каких условий не хватает для задачи? (`spot_missing_constraints`) | 100 | all AI bots |
| Как выйти из ложной дилеммы? (`false_dilemma`) | 100 | all AI bots |
## Source and factual limits

The eight ImPULS-specific question sets are abstract user-facing help, grounded
in read-only source documentation at **Treninem/Impuls**
`f535f6d27d63eae86696291a58e9cfb2062147e4`:
`docs/COMMANDS_MATRIX_V30.md`, `docs/RELEASE_NOTES_V84.md` and
`docs/RELEASE_NOTES_V85.md`. Provenance is attached to each of the eight
sets. This source snapshot documents candidates and commands; it is **not**
proof that BotHost runs the identical code or that any particular user has
permission. No private implementation, Telegram text, chat history, personal
names, identifiers or secrets have been published.

The 100 free-conversation suggestions are grouped into ten subject domains;
the 100 original light jokes are also grouped into ten themes. Each variant is
stored once, with a context-specific `when` and `avoid` condition. Other
questions have short, partial sets. Further runs must fill those partial sets,
not start new duplicate question IDs.

## Selection and safety

`scripts/reply_catalog.py` is an offline **opt-in reference selector**:
it directly indexes the pack's 83 canonical IDs and their groups. It does
**not** recognize natural-language intent, configure chats, execute commands,
read Telegram messages or remember sessions. A caller must independently
validate explicit address, local permission, audience, and chosen context group.

```python
from reply_catalog import ReplyCatalog
catalog = ReplyCatalog()
response = catalog.reply("what_discuss", group="daily",
                         addressed=True, local_permission=True, recent=())
```

More than one group means **group_required** unless the caller selects one.
Jokes require `humor_allowed=True`; all responses abstain for sensitive
contexts and requests to be silent. The caller supplies recent replies from
**one isolated conversation**, at most 128, and keeps them locally. A used
reply is skipped; an exhausted group does not repeat. ImPULS-specific help
cannot be served to the `all_ai_bots` audience. No JSON entry grants bans,
mutes, permissions or other actions.

## Integrity and verification

The manifest version for this completed catalogue is `2026.11.02.28`. The package is pinned by the current manifest SHA-256; size and digest must be checked from actual bytes; all 27 packs must be present and SHA-valid.
The selector's cache identity is `(knowledge_version, pack_sha256)`; it
does not change any running bot's cache.

`python scripts/validate_pack.py`,
`python scripts/test_reply_catalog.py --repository -v`, and the separate
exact-head workflow must complete on the actual PR head SHA before merge.
Test requirements cover all 8300 reachable responses, normalized duplicates,
cross-pack exact matches, 100/100 completeness, opt-in, audience isolation,
refusal conditions, repeat suppression and tampered SHA/cache snapshots.
A review of semantic similarity remains necessary: an exact-string test cannot
prove that every joke or conversational suggestion is equally good.

After successful post-main CI, update these coverage counts in the next
cycle. Candidate-only values must not be reported as shipped to ImPULS.
**No consumer integration or live Telegram deployment is claimed.**

## Next unfinished questions

Next extend reviewed community-specific help and missing distinct intents with useful,
context-distinct answers, then deepen the fact-checked ImPULS FAQ. Count
existing entries and active PR variants before writing. Aim for 100 each,
but do not pad with repeated paraphrases or invented functionality.

## 2026-11-02 next completed batch (candidate 2026.11.02.3)

Five existing question sets each gained **88** original, context-separated
answers without changing their canonical IDs: `explain_again`,
`need_decision`, `idea_request`, `bored`, and `boundaries`.
They moved from 12/100 to 100/100. Exact new additions: **440**;
cumulative catalogue: **883**, full sets: **7**, partial sets: **18**.
These are language examples, not operational moderation authority. The new
context groups require explicit caller selection; do not infer sensitive or
technical permissions from text. Every prior reply remains in place.

## 2026-11-02 contextual batch 2026.11.02.4

Three partial questions (`thanks_reply`, `farewell_reply`, `disagreement_reply`) received 8 distinct guarded groups and 88 original synthetic replies each. Total **+264** (883 -> **1587**). Each moved from 12/100 to 100/100; ten completed sets in main after verified merge. The original 12-item group remains the safe default via an explicit `default_group`, while additional groups require caller-known context. The opt-in selector remains read-only and its SHA/version snapshot changes. Consumer integration, live rollout and repeat policies are unverified.

## 2026-11-02 additional batch 2026.11.02.5

Three further unfinished question sets gained 8 guarded groups and 88 original examples each: `change_topic`, `no_sure`, `apology_help`. Added **264** further replies (1147 → 1587), for **528** additions in this PR relative to its initial main. Three more intents reached 100/100; **13 complete** and **12 partial** remain. All original replies are retained. `default_group` keeps existing short response behavior when the caller omits the group; contextual alternatives require a deliberate choice. Claims about ImPULS functionality were not added in this batch.

Integrity fix: an exact normalized reply collided with `dialogue.json`/`skills.json` and was replaced with a substantively distinct phrase before merge. This was detected by the real exact-head workflow; the earlier failure is not claimed as a pass.

## 2026-11-02 additional batch 2026.11.02.6

`need_support` and `lost_context` gained 8 carefully scoped groups each, **176** new original synthetic replies total (1411 → 1587). Both reached 100/100 with no claim of access to unavailable chat history, and no replacement for crisis interventions. Existing defaults remain available; other groups require local context. This brings the PR total to **704 new replies** vs its base main, **15 full** and **10 partial** sets. Sensitive contexts continue to abstain. All totals are pre-merge until actual CI and GitHub merge are confirmed.

## 2026-11-02 second verified candidate series (2026.11.02.7)

New independently useful, original, synthetic content: `dark_humor` **+88** across eight clearly opt-in fantasy categories, `friendly_tease` **+100** in ten everyday contexts targeting only benign behavior, and `conversation_followup` **+100** with ten conversation-management contexts. Total **+288** (1587 → 1875) and 27 canonical questions; 18 complete at 100/100, 9 partial. Humor has a required `humor_allowed=True` caller flag; groups explicitly state when and avoid conditions, and sensitive/silence flags suppress output. No personal chat logs, product-specific powers or live bot integration were added. This is a separate PR based on the exact merged main after #43.

## 2026-11-02 new multi-question batch (2026.11.02.9)

Verified source base `36e7d985f0504323c474d2e52b763f99a4ec30d3`; scope is public synthetic language data only.
This batch contributes **290 new distinct replies across 11 canonical questions**:
**2 new completed sets** (`diagnose_problem`, `verify_claim`) containing 100 each,
and **9 existing incomplete ImPULS help sets** gaining ten contextual replies each (90 total).
The nine sets remain incomplete and must continue from their exact saved counts below.
Nothing in these replies performs actions or confers permissions. Their use requires an
independently validated intent, explicit address, local authorization and an appropriate
context group. The package has no automatic natural-language intent classifier.

| Remaining partial intent | Accepted / 100 | Remaining |
|---|---:|---:|
| `rules_explain` | 22 | 78 |
| `chat_settings` | 19 | 81 |
| `report_violations` | 19 | 81 |
| `profile_access` | 16 | 84 |
| `pulse_navigation` | 16 | 84 |
| `moderator_commands` | 19 | 81 |
| `private_panel` | 16 | 84 |
| `danetka_start` | 19 | 81 |
| `danetka_off` | 19 | 81 |

Source of existing ImPULS command spellings and high-level navigation for this batch:
read-only `Treninem/Impuls` main `95dcb0fc0773f970e162a6009a4d889e880a2d0e`,
`README.md`, `docs/COMMANDS_MATRIX_V30.md`. This source code snapshot does not establish
that BotHost is on the same version. No private source files or chat messages were copied.

Manifest snapshot `2026.11.02.9` pins the revised reply pack to SHA-256
`dc51e29425f01b96bd72d0dd63648c9ff70f37ec6155396af5808e68d6e92fa7`. Existing 25 pack digests remain unchanged. The pack is distributed
only after a completed exact-head PR workflow and merge; live consumer integration
and post-main CI are separate verification steps. Reviewer must assess meaningful
similarity beyond string-level deduplication, follow actual test results, and avoid
padding incomplete technical FAQ with cosmetic variants.

## 2026-11-02 context-aware planning and evaluation batch (2026.11.02.10)

Added **300 original replies in 3 new fully completed (100/100) canonical intents**: goal_clarity, project_plan, idea_review. Each has ten separately scoped contexts and ten authored replies per context; no template multiplication, fake product functions, or live-bot writes. Existing 29 intents and their 2165 replies are preserved. Selector still requires explicit intent, audience, local permission, and caller-validated context; no automatic NLP classifier or consumer deployment is claimed. Exact normalized deduplication was run against the existing catalogue, and the manifest SHA was recomputed over actual UTF-8 source bytes. Human semantic review and exact-head CI remain required before merge.

## Additional 2026-11-02 cross-context batch (2026.11.02.11)

Three more new canonical questions received 100 independently authored replies each: `message_draft` (writing clear requests, questions, updates, refusals, complaints, feedback, coordination, instructions, public announcements, corrections), `learning_path` (ten stages of learning), and `group_discussion` (ten non-enforcement discussion contexts). Added +300 on top of prior +300 in this PR: 35 canonical sets, 2765 total catalogue replies, 26 full and 9 partial. All 600 new replies are written as individual original strings, not generated cartesian permutations; SHA-256 is recalculated on actual UTF-8 bytes and bound to version/cache identity. No bot powers or moderation sanctions are granted; group-specific replies require caller-validated context.

## More reviewed prompts, 2026.11.02.12

Added **200 further authored answers across two completed new intents**: `chat_activities` (10 non-automated conversation activity categories) and `moderation_reasoning` (10 context-dependent moderation-analysis categories restricted to chat moderators, explicit prohibition on automatic sanctions). PR cumulative additions **800**; 37 canonical questions, 2965 total replies, 28 full and 9 partial. Existing 9 technical FAQs remain unchanged because an overlapping open PR contains their extensions; preserve those independently pending reconciliation. SHA-256/version updated with real bytes; exact-head CI and human semantic review are still required.

## 2026-11-02 short creative stories and structured reasoning (2026.11.02.13)

New completed intents: `micro_story` **100 original two-sentence miniature stories** across ten genres, and `critical_analysis` **100 context-scoped reasoning responses** across ten analytical stages. This adds +200 more, bringing this PR to **1000 newly authored, distinct synthetic replies across ten completed questions**, catalogue **3165 total** across **39 canonical questions** (30 at 100/100, 9 existing partial). No old reply overwritten, no private data, source-code claims, live moderation powers or deployment. Version/cache identity and source-byte SHA recomputed. Semantic near-duplicate review and exact-head CI still required.

## 2026-11-02 newly verified ImPULS-oriented help topics (2026.11.02.14)

Added **8 new canonical ImPULS FAQs with 20 original, audience-limited, context-scoped replies each** (+160). Their 80-response remainder per question is explicitly unfinished; 47 questions / 3325 catalogue replies overall, 30 complete and 17 partial. Source reference: read-only `Treninem/Impuls` main `95dcb0fc0773f970e162a6009a4d889e880a2d0e`, user-facing `README.md` and `docs/COMMANDS_MATRIX_V30.md`. Grounded subjects: starting with group/DM commands, asking AI questions, diagnosing silence, games help, questions vs explicit commands, per-chat isolation, release navigation, checking roles. User-facing documentation describes candidate features, not verified live BotHost behavior. No private source text, identities, tokens, or undocumented settings were copied. These community-only variants cannot be served by a generic AI audience and require local verified permission and explicit caller context. In this PR total newly authored replies **1160** across 18 new questions, ten at 100/100, eight at 20/100; pre-existing nine partial sets were not modified because overlapping extension work remains open.

## 2026-11-02 reconciliation of older response extension PR #46 (2026.11.02.15)

Older [PR #46](https://github.com/Treninem/Bot-Knowledge/pull/46), exact head `a21bfb79b50ef0804889ca662d8a285f073ac483`, contains **825 prior-authored** candidate replies for nine existing ImPULS question sets, based on an old 883-reply catalogue. Current main had independently gained 10 replies in each. To preserve the 100/100 per-question cap, we selected 10 candidates to exclude per set (90 total) using lexical-overlap scoring against existing records while retaining at least six replies in each new context group. **735 preserved original answers from that existing open PR migrated**, completing all nine sets from 22/19/16 to 100. These 735 were NOT newly authored during this run; they are new only to main after merging this candidate. Existing 3325 replies retained; resulting candidate: **47 questions, 4060 replies, 39 complete 100/100 and 8 partial**. The older extension PR and its different selector code remain open for separate compatibility review; no loss of its branches is claimed. Its eight source-bearing sets use current read-only `Treninem/Impuls` documents at `95dcb0fc0773f970e162a6009a4d889e880a2d0e`. All changes require actual exact-head CI, source SHA/cache, near-duplicate and full-repository regression checks before main merge. This is public synthetic content only, not operational bot permissions or live rollout.

## 2026-11-02 current independent batch v2026.11.02.16

Parent main: `fed2d0cf7bb66be6938c3c5d8d1326000fd0fe34` (after PR #49). **180 newly authored original Russian replies**:
- Eight unfinished ImPULS-specific questions each get one carefully guarded context group
  of 10 replies; each moves from 20/100 to 30/100. These are advice on safe use,
  not unverified new commands or claims about live BotHost.
- One new universal question `question_crafting` is complete at 100/100 with ten
  meaningful contexts. It requires independent caller-selected group and authorization.
- Total catalogue: **48 canonical questions, 4240 replies, 40 complete, 8 partial**.

The manifest SHA-256 changes with the pack bytes, as does the version-keyed cache identity.
All new replies are synthetic and use no private chat material. Merging requires real
full-repository validation, exact-head CI and post-main CI. No consumer rollout is claimed.


## 2026-11-02 reconciled completion batch 2026.11.02.18

Built from fresh main after parallel changes. Eight ImPULS-specific sets were already 30/100 in main; this candidate preserves those additions and adds exactly **70** missing replies to each (**+560**). Four new general sets add **+400** more replies: `tactful_refusal`, `simple_explanation`, `clarifying_question`, and `feedback_reply`. Net delta vs current main: **+960 replies**, catalogue **4240 → 5200**, **48 → 52 questions**, all **52/52 at 100/100**. No ImPULS code, deployment, private messages, secrets, sanctions or consumer rollout are included.


## 2026-11-02 rules/help/communication batch 2026.11.02.20

Six new independent questions were added at **100/100** each: `rule_exception`, `rule_conflict`, `safe_setting_change`, `ask_for_help`, `admit_mistake`, and `calm_conflict_reply`. Exact addition: **+600** original synthetic replies in 60 guarded context groups. Catalogue: **5200 → 5800 replies**, **52 → 58 canonical questions**, all complete at 100/100. These sets are general language/help knowledge, contain no product-specific powers, sanctions, PII, secrets or live-memory claims, and remain read-only reference responses selected by caller-provided context.


## 2026-11-02 sourced ImPULS topic batch 2026.11.02.22

Five new community-only ImPULS questions were added at **100/100** each: `impuls_antispam_help`, `impuls_family_help`, `impuls_raffle_help`, `impuls_word_chain_help`, and `impuls_pulse_journal_help`. Exact addition: **+500** original synthetic replies in 50 guarded context groups. Catalogue: **5800 → 6300 replies**, **58 → 63 questions**, all complete at 100/100. Product facts are source-pinned read-only to Treninem/Impuls `4db76f4ad682dd3bbc3da413af3fb53fd8f8a596` / `docs/RELEASES.md`; responses explicitly distinguish source candidates from unverified live BotHost rollout. No ImPULS code, private chats, tokens, sanctions, real balances or deployment actions were added.

## 2026-11-02 conversation continuity batch v2026.11.02.23

Main baseline: `26f9caaa62fc28ed81a9f93bdc89fc09e38c5cc9` (verified 63 questions / 6300 answers). Three new
independently scoped general intents, each with 10 context groups and 100 original
Russian replies: `resume_after_pause` (continuation after a break),
`discussion_summary` (evidence-aware, consent-aware summaries), and
`capability_boundaries` (truthful limits of model and application access).
Net authored additions: **+300**, all accepted after normalized exact duplicate
screening against the previous 6300 responses. The candidate is now
**66 questions / 6600 replies**, all **66/66 complete 100/100**, with **no partial**
sets. Existing texts and IDs are untouched. No new ImPULS commands or rights,
automatic sanctions, private chat material, external actions or live rollout.
Source pack SHA-256 on actual UTF-8 bytes: `c772564e8db3d05093e3abfa15a5e73a40cc80f18b595016f16f5f88629b0494`;
manifest version/cache identity is `2026.11.02.23`. Selector still needs
caller-confirmed intent, group, audience, address and local authorization;
its data alone does not imply a deployed feature. Human semantic sampling and
actual exact-head CI plus post-main CI remain publication gates.

## 2026-11-02 semantic repair batch v2026.11.02.24

Verified main baseline `8d785003be3d56c2dbd433c059903b1cec8f9bdc`: 66 canonical questions and 6600 replies. Three new complete intents gained 100 individually authored responses each with ten explicit context/avoid groups: `repair_misunderstanding`, `constructive_compromise`, and `fact_correction`. Exactly **+300** net new original synthetic responses; candidate **69 questions / 6900 replies**, all **69 complete 100/100**, **zero partial**. Prior 6600 answers kept. Across-pool three-gram Jaccard near-match sweep found no similarity at or above 0.52 for those 300 against the prior 6600 and themselves; this is not proof of semantic perfection. No ImPULS repo changes, private messages, external actions, sanctions or live consumer integration. Source data SHA-256 over UTF-8 bytes: `5d364a2925a61b852f8ffce487691b57ef5aeff8ff74e6be63537938fca41b39`; manifest/cache version `2026.11.02.24`. Only ship after actual completed exact-head QA and post-main CI.


## 2026-11-02 practical skills batch 2026.11.02.26

Six new independent questions were added at **100/100** each: `prioritize_tasks`, `handoff_task`, `risk_review`, `build_checklist`, `verify_change_result`, and `problem_report`. Exact addition: **+600** original synthetic replies in guarded context groups. Catalogue: **6900 → 7500 replies**, **69 → 75 canonical questions**, all complete at 100/100. A pre-PR self-check caught an accidental 110-reply set in `verify_change_result`; the extra 10-item group was removed before publication so the canonical 100-reply limit is preserved. No PII, secrets, sanctions, product-specific powers or live-memory claims are introduced.

## 2026-11-02 PR #59 concurrency reconciliation v2026.11.02.27

Fresh GitHub main `97d80d3181d42d94a2bae6251e146ecf0b06f8c5` after independent PR #60 was merged: **75 distinct intents, 7500 responses**, with completed `prioritize_tasks`, `handoff_task`, `risk_review`, `build_checklist`, `verify_change_result`, and `problem_report`. PR #59 already authored 600 responses at `16a063782de296e20033bfbc00b5f1b62ee76693`, but `prioritize_tasks` overlapped an already accepted canonical question after the parallel merge. **Do not count the 100 alternate `prioritize_tasks` responses twice**; they remain recoverable in the original PR #59 commit `16a063782de296e20033bfbc00b5f1b62ee76693` for later comparison, not in the active merged catalogue. No existing main set was removed or rewritten.

This reconciled proposal adds the **other five complete original intents** to fresh main: `reproduce_bug`, `progress_report`, `privacy_before_publish`, `followup_no_reply`, `confirm_before_change`. Net **+500 accepted responses**, 75→80 questions and 7500→8000 answers; each new set has ten explicit context guards and ten original responses per group. All 80 sets total 100/100, zero partial. One overlapping 100-answer candidate was deferred due exact intent collision (not included in published counts). New pack SHA-256 `c8d584056b2f748a2ab5885eadc9adc91e47a8cc244b0395aa2bb09d9fa2dfeb`, manifest `2026.11.02.27`, with actual exact-head and post-main CI still required. PR #59 branch merged main without force-push to retain ancestry and make a reviewable diff; consumer rollout not claimed.

## 2026-11-02 context-aware expression, implicit meanings and minimal-data intake v2026.11.02.28

Fresh main `e45e6ee46c32814caca9cc639e399fc6009b17f2`, existing **80 questions / 8000 answers**, zero partial. Three complete new independent general RU intents: `tone_adaptation` (register by audience and stakes), `indirect_meaning` (pragmatic hints, sarcasm, boundaries, quoted instructions), and `ask_details_safely` (minimization in support, account, location, documents and personal topics). Each has ten context groups with independently written `when`/`avoid` guards and ten candidate answers; **+300 original accepted responses**, all normalized-distinct from the previous 8000 and each other. Proposed catalogue **83 questions / 8300 answers**, all complete at 100/100 and zero partials. Cross-pool three-word Jaccard near-match sweep: max 0.250, none ≥0.58 (semantic accuracy still needs human judgement). No personal records, unconfirmed ImPULS features, executable actions or client rollout. Actual pack UTF-8 SHA-256 `f84ea33a693f105a708c4fa30a726b3ccd4cccbd488e86aeca5b8ae754719c0c`; manifest version/cache key `2026.11.02.28`; exact-head CI and post-main CI mandatory before publication.

## 2026-11-02 recovered independent work-skills v2026.11.02.29

Verified main baseline `a5ed5ed153cea7d1f4fe29bf0bb14bb057da2ba9`: 83 canonical intents / 8300 replies. Reused four original complete synthetic general skills authored earlier in commit `9cb2432663e01306618f223f8ec7992bb9054ec4` but not previously merged: `estimate_effort`, `decision_record`, `parallel_work`, and `scope_control`; each 10 guarded context groups × 10 Russian responses, **+400** new-to-main unique replies. Result **87 questions / 8700 replies**, all 87 at 100/100, zero partial. Accepted previous 8300 are unchanged. Exact normalization across 8700: no collisions; three-word Jaccard sweep against previous 8300 and between candidate replies: no pairs ≥0.58, max 0.200. This does not prove perfect semantic variety. Synthetic only; no private chats, product-specific commands, sanctions, credentials, powers or live consumer change. Actual UTF-8 SHA-256 `231586e9dd74159824d5ca9e6406ec7d963befae286e2a75e8dcb1b63b8a7ef9`; manifest version/cache identity `2026.11.02.29`. Publication still requires exact-head CI and post-main CI.

## 2026-11-02 safety and answer-source grounding v2026.11.02.30

Main `cd210f8656cff23ef5181f76e7980f889ec8147a`: 87 questions, 8700 accepted replies, no partial sets. Two genuinely new general RU intents: `suspicious_request` (urgency, secret requests, impersonation, payments, links, rewards, coercion, independent checking and response after compromise) and `source_provenance` (checkable source, freshness, numbers, technical version, quoting, reliability, contradictions, inaccessible sources and corrections). Each has 10 explicitly guarded context groups with 10 original synthetic texts. **+200** unique replies in this candidate, total **89 questions / 8900 replies**, 89/89 complete 100/100, 0 partial. Previously accepted 8700 responses were preserved. Full normalized corpus unique 8900/8900; candidate 3-word Jaccard check: 0 pairs ≥0.58, maximum 0.188. Not a guarantee of flawless meaning. No PII, personal chats, new ImPULS capabilities, sanctions or consumer rollout. Actual UTF-8 SHA-256 `3bfa161b083353bb0c38acb5983ef67165cafde0ec82e91489f488d80b628d5d`; manifest/cache key `2026.11.02.30`. Require completed exact-head CI and post-main CI before considering published.

## 2026-11-02 criticism and consent boundaries v2026.11.02.31

Fresh main `93a0c42655e2dda4ac4c3e4209a9fcbfe79c93e2`: 89 canonical questions / 8900 replies, 0 partial. Authored two independent general RU intents: `respond_to_criticism` (accurate, vague, angry, incorrect, public, private, workplace, creative, repeated and action-based feedback) and `respect_refusal` (direct no, invitation, privacy, help, work, disagreement, safety, ambiguity, group consent and repairing pressure). Each 10 guarded contexts with 10 original replies, **+200 unique candidates**, overall **91 questions / 9100 replies**, all 91/91 at 100/100 with zero partial. Previously accepted 8900 preserved. Normalized exact duplicates: 0; near 3-word Jaccard ≥0.58 among new texts and entire corpus: 0, maximum 0.214. Synthetic only; no private user messages, unverified bot powers, threats, sanctions or deployment. Pack actual UTF-8 SHA-256 `f51c780999c68a8eacfae53c36de4768970b2a5aa1aec191c9656a63142e7b95`; manifest/cache `2026.11.02.31`; require exact-head CI and post-main CI prior to fully verified publication.

## 2026-11-02 rumor checking and sincere encouragement v2026.11.02.32

Verified base main `3f295fae95dec8ecbfcb8fab2ac4799cd27a4027` contained 91 complete synthetic RU question sets / 9100 answers. Original new intents: `rumor_handling` (unverified headlines, reputation, groups, screenshots, numerical claims, safety, business, private information and corrections) and `sincere_praise` (specific achievement, effort, learning, creativity, teamwork, support, boundaries, small improvements, group recognition and avoiding manipulation). Each 10 guarded topical groups with 10 distinct authored texts. **+200 candidate responses**, 93 questions / 9300 replies, all 93/93 at 100/100, zero partial; old 9100 kept. Normalized global duplicates 0, candidate 3-gram Jaccard ≥0.58 count 0, maximum 0.188. Synthetic general wording only, no private transcripts, identified individuals, sanctions, new ImPULS features or consumer rollout. Exact UTF-8 pack SHA-256 `05b415a5b293aded4fea651caf7f6e16ee6e7284498a1f5342d9773b5a1030d4`, cache/manifest version `2026.11.02.32`. Exact-head CI and post-main gate still required.

## 2026-11-02 guarded conversation pause and information triage v2026.11.02.33

Verified baseline `6ca40c69a8ae69fcd239bc3a58a5cdaf9cd5f270` had 93 sets / 9300 answers. Two new original synthetic all-AI RU questions: `pause_conversation` and `handle_info_overload`, each with 10 independent context groups and explicit when/avoid guards. Authored 200 candidate replies; normalized and 3-word Jaccard screening (threshold 0.58) rejected 0 duplicates/near matches. **Accepted exactly 200 new-to-main candidate replies**. Proposed 95 sets / 9500 total answers, current progress: `pause_conversation` 100/100 (remaining 0); `handle_info_overload` 100/100 (remaining 0). Old 9300 retained intact. Max observed 3-gram Jaccard 0.200 before rejected candidates, no retained near pair >=0.58. This is a heuristic, not proof of full semantic distinctness.

Only generic conversation/data-triage examples; no private messages, PII, secrets, new ImPULS commands or roles, sanctions, executable actions or live rollout. Pack actual UTF-8 SHA-256 `1ca3ace37ff4940a7e339d54d3e92c1118b587b502739c58acb12ab93d523f58`, manifest/cache version `2026.11.02.33`. Require actual exact-head CI and post-main CI before publication. Finish incomplete sets first in next pass, then proceed to `spot_missing_constraints`.

## 2026-11-02 task boundaries and false-dilemma reasoning v2026.11.02.34

Base own PR branch `ac76230f11a4cbc231a459c5af225df1a83e8a5e`: 95 sets / 9500 replies (including 200 proposed in PR #66, not yet counted in main). Two new general RU canonical questions: `spot_missing_constraints` (goal, audience, deadlines, resources, inputs, format, quality, permissions, dependencies, ambiguities) and `false_dilemma` (extreme choices, speed/quality, cost, relationships, work, community, technology, safety, uncertainty, implementation). Exactly 200 manually authored candidates in 20 guarded context groups. After normalized and indexed 3-gram Jaccard duplicate filtering: **+200 accepted new**; 0 rejected near/exact candidates. Per question `spot_missing_constraints` 100/100, 0 remaining; `false_dilemma` 100/100, 0 remaining. Proposal totals **97 sets / 9700 replies**, preserving all prior 9500. Max observed Jaccard 0.333 before filtering; no retained pair >=0.58. This heuristic is not comprehensive human semantic QA. UTF-8 pack SHA-256 `00d4c0808cef90458b2344fd2fd4efbb36b13b3d7850587edeb3ba9220bd4dbf`; manifest/cache `2026.11.02.34`. Zero ImPULS changes, real chats, personal identifiers, sanctions, new consumer abilities or deployment. Check full exact-head CI and post-main before merge. Follow-up: complete any partial set, then `recover_task_context`.
