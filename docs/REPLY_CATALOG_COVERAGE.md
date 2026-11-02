# Reply catalogue: synthetic RU answers (2026-11-02)

Source main for this series: `e0858cce7c819355cabbebb6da5ed74cf3a54234` (after verified PR #40).
This candidate adds a **new, separate** SHA-pinned pack. It does not rewrite the
100 greeting answers already merged. Only original synthetic examples are used.

## Measured coverage

**25 distinct canonical questions, 443 authored answers, 26 packs total**.
Two questions are complete at 100/100, and 23 remain partial. These are reply
variants, not 443 trained model skills or new executable ImPULS commands.

| Question / intent | Count / 100 | Audience |
|---|---:|---|
| О чём поговорим? (`what_discuss`) | 100 | all AI bots |
| Пошути (`tell_joke`) | 100 | all AI bots, explicit humor opt-in |
| Спасибо (`thanks_reply`) | 12 | all AI bots |
| Пока (`farewell_reply`) | 12 | all AI bots |
| Не понял (`explain_again`) | 12 | all AI bots |
| Я не согласен (`disagreement_reply`) | 12 | all AI bots |
| Мне тяжело (`need_support`) | 12 | all AI bots |
| Мне скучно (`bored`) | 12 | all AI bots |
| Помоги выбрать (`need_decision`) | 12 | all AI bots |
| Ответить на грубость (`boundaries`) | 12 | all AI bots |
| Подкинь идею (`idea_request`) | 12 | all AI bots |
| Помоги извиниться (`apology_help`) | 12 | all AI bots |
| Помнишь прошлый разговор? (`lost_context`) | 12 | all AI bots |
| Сменим тему (`change_topic`) | 12 | all AI bots |
| Чёрный юмор (`dark_humor`) | 12 | all AI bots, explicit humor opt-in |
| Объясни правила (`rules_explain`) | 12 | community bots only |
| Ты уверен? (`no_sure`) | 12 | all AI bots |
| Где настройки ImPULS? (`chat_settings`) | 9 | community bots only |
| Как пожаловаться? (`report_violations`) | 9 | community bots only |
| Где мой профиль? (`profile_access`) | 6 | community bots only |
| Где Пульсы? (`pulse_navigation`) | 6 | community bots only |
| Команды модератора (`moderator_commands`) | 9 | community bots only |
| Открыть панель (`private_panel`) | 6 | community bots only |
| Запустить Данетки (`danetka_start`) | 9 | community bots only |
| Отключить Данетки (`danetka_off`) | 9 | community bots only |

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

The manifest version is `2026.11.02.2`. The new package SHA-256 is
`ee41882ebb7df77889a462f9d39ced9472cdef747ecb32d63ff2f4cb55d7889d`.
Source bytes are 85,910 UTF-8 bytes; all 26 packs must be present and SHA-valid.
The selector's cache identity is `(knowledge_version, pack_sha256)`; it
does not change any running bot's cache.

`python scripts/validate_pack.py`,
`python scripts/test_reply_catalog.py --repository -v`, and the separate
exact-head workflow must complete on the actual PR head SHA before merge.
Test requirements cover all 443 reachable responses, normalized duplicates,
cross-pack exact matches, 100/100 completeness, opt-in, audience isolation,
refusal conditions, repeat suppression and tampered SHA/cache snapshots.
A review of semantic similarity remains necessary: an exact-string test cannot
prove that every joke or conversational suggestion is equally good.

After successful post-main CI, update these coverage counts in the next
cycle. Candidate-only values must not be reported as shipped to ImPULS.
**No consumer integration or live Telegram deployment is claimed.**

## Next unfinished questions

First extend `thanks_reply`, `farewell_reply`, `explain_again`,
`disagreement_reply`, `need_support` and `bored` with useful,
context-distinct answers, then deepen the fact-checked ImPULS FAQ. Count
existing entries and active PR variants before writing. Aim for 100 each,
but do not pad with repeated paraphrases or invented functionality.
