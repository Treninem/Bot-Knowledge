# Explanatory teaching and learning by examples — 2026-11-11

## Source and scope
- Published source: `packs/ru/social_dialogues.json` on `main` 8697a9abb15380a3b25f567467d1cfddb3f5b58c; Git blob `d56ff304da7165bd63c328f3220a1f6d3d26e3ab`; SHA-256 from manifest `0cfedc133354a69522fecc3cda6bc21533c66005f0dc207050075f787dc977a8`.
- Owner permission dated 2026-11-02 is already documented in `AGENTS.md` and `docs/OWNER_AUTOMATION_SCOPE_2026_11_02.md`.
- New independent stable prefix **`teach20261111_*`**, 10 canonical intents: explain without jargon, explain by steps, correcting misconceptions, showing a concrete example, identifying exceptions, practice exercises, actionable feedback, checking understanding, comparing methods and transfer to new contexts.
- New **100** original synthetic RU contextual replies; 10 per intent (**10/100**), exactly **90 missing each, 900 total**, zero completed. 100 new only; prior Bot-Knowledge replies are not counted.
- Before commit, code-side normalized IDs, reply texts and context descriptions all unique (100/100); zero exact duplicates and max within-batch token-Jaccard **0.2857**. This is lexical not exhaustive semantic screening.
- Reply contexts are individualized; the assistant must select based on direct request and actual situation. These replies are *not* a guarantee of educational competence or a live tutoring, grading or learning system.

## Safety and publication
`staging/ru/explanatory_teaching_20261111_context_pool.json` is **consumer-unregistered** (`consumer_registered=false`), `all_ai_bots`, read-only; no sanctions, private chats or permissions. Registered source and manifest `2026.11.09.003` unchanged, no cache updates or changes to ImPULS/any live bot.

Tests: `python -m unittest scripts.test_explanatory_teaching_20261111 -v`, registered source and manifest SHA, exact checkout, stage counts, ID, normalization, context selection, privacy and duplicates. Full exact-head CI/compatibility and after-merge post-main are mandatory; no bypass of required checks.

Next action: independently and carefully continue **the same ten stable intents** from suffix **11**, do not restart, use genuinely different examples and only publish after gates.
