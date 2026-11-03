# T71 — English natural conversation and contextual meaning
Base main: `fbf842da77b5e002bab7942821f33527a4638417`. English pack `2026.11.04.002` contained 968 cases.
Added **62** original context-dependent EN cases across eight classes
(context, conversation, support, slang, sarcasm, rules, deception, creative);
2 candidates rejected at normalized-input/response or 3-gram 0.80 threshold.
All cases are synthetic and available to `all_ai_bots` only through permitted
local knowledge readers; `avoid` and RU meaning fields constrain selection.
No private chat excerpts, user IDs, sanctions, bot actions or live claims.

After: **1030** English cases. New pack size **547362 UTF-8 bytes**,
SHA-256 `92bf39a4353240cbd4c22027182fe391afe789806de97974ffa97b7063cb54df` in manifest/cache version `2026.11.04.005`.
The earlier 968 items are preserved; new accepted answers count is 62,
not the full size. Greeting `reply_catalog` remains 119 complete 100/100
intents, not touched. This batch does not falsely claim new complete sets.
Validation must run: `python scripts/validate_pack.py`,
`python -m scripts.test_english_dialogue_t71`, exact PR head six CI,
then post-main CI after guarded merge. Human checks remain necessary for
semantic near duplicates; lexical filters do not prove meaning uniqueness.
Do not update ImPULS, AuroraFox or live bots as part of this PR.
