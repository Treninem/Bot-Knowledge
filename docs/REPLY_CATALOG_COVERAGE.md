# Reply catalogue: synthetic RU answers (2026-11-02)

Source main for this series: `e0858cce7c819355cabbebb6da5ed74cf3a54234` (after verified PR #40).
This candidate adds a **new, separate** SHA-pinned pack. It does not rewrite the
100 greeting answers already merged. Only original synthetic examples are used.

## Measured coverage

**37 distinct canonical questions, 2965 authored answers, 26 packs total**.
Twenty-eight questions are complete at 100/100, and 9 remain partial. These are reply
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
| Объясни правила (`rules_explain`) | 22 | community bots only |
| Ты уверен? (`no_sure`) | 100 | all AI bots |
| Где настройки ImPULS? (`chat_settings`) | 19 | community bots only |
| Как пожаловаться? (`report_violations`) | 19 | community bots only |
| Где мой профиль? (`profile_access`) | 16 | community bots only |
| Где Пульсы? (`pulse_navigation`) | 16 | community bots only |
| Команды модератора (`moderator_commands`) | 19 | community bots only |
| Открыть панель (`private_panel`) | 16 | community bots only |
| Запустить Данетки (`danetka_start`) | 19 | community bots only |
| Отключить Данетки (`danetka_off`) | 19 | community bots only |
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
it directly indexes the pack's 25 canonical IDs and their groups. It does
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

The manifest version for the latest candidate is `2026.11.02.9`. The package is pinned by the current manifest SHA-256; size and digest must be checked from actual bytes; all 26 packs must be present and SHA-valid.
The selector's cache identity is `(knowledge_version, pack_sha256)`; it
does not change any running bot's cache.

`python scripts/validate_pack.py`,
`python scripts/test_reply_catalog.py --repository -v`, and the separate
exact-head workflow must complete on the actual PR head SHA before merge.
Test requirements cover all 2165 reachable responses, normalized duplicates,
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
