# T86 — original structured-data reading and conversation followthrough (2026-11-04)

Starting verified main: `b3ff785098b44bc2d7d4846260a682d402dbaeb8`, manifest `2026.11.04.018`.
Owner authorization: `docs/OWNER_AUTOMATION_SCOPE_2026_11_02.md`.

Two existing-compatible `qa.v1` manifest-discovered packs:
- `structured_information_qa.json`: 39 independent canonical questions, 78 search aliases, 117 context-scoped responses. Arithmetic/format ambiguity, dates, units, tables, missing values and trustworthy comparisons.
- `conversation_followthrough_qa.json`: 32 independent canonical questions, 64 aliases, 96 responses. Listening, revised intent, addressing, group boundaries, transitions and non-assumptive conversation.

Newly accepted: 71 questions / 213 synthetic responses; rejected 0 during normalized and bigram-near dedup against 5191 existing qa.v1 search expressions. These are **not** new 100/100 reply-catalog groups; the 119 existing complete groups are untouched. Source: public `docs/REQUIREMENTS_21.md` at immutable b3ff785098b44bc2d7d4846260a682d402dbaeb8; ImPULS private source was not copied.

Privacy: no real chats or IDs; no personal memory, payments, moderation sanctions, commands or consumer deployment. Applies only to direct/private/addressed group utterances, audience `all_ai_bots`. Each example depends on the described condition and is not globally interchangeable with the other variants.

Checks: SHA-256 based on exact UTF-8 bytes; `python scripts/validate_pack.py`; `python scripts/validate_qa_v1.py`; `python -m scripts.test_new_dialogue_skills_t86` including local retrieval and audience isolation. Publication gated by actual exact-head CI and post-main CI. Live consumer caches are not touched.

- `packs/ru/structured_information_qa.json`: 51228 bytes, SHA-256 `83d755602feca69f19c44cfc6dadbf222ba7d0930c1d6dd8218b82461bbb0cae`
- `packs/ru/conversation_followthrough_qa.json`: 42075 bytes, SHA-256 `265c6e7b730996afbb2773d233f5337f0124c3dfd906eea296650875581d68a3`

Next: inspect existing language and moderation gaps; do not inflate existing 100/100 counts. ## Progress for a 100-alternatives-per-intent goal

These qa.v1 questions are **new partial 3/100 sets**, not newly completed 100/100 sets. Each stable `records[].id` is the intent identifier. As of this PR, every one of the 39 `struct_t86_001..039` records and 32 `follow_t86_001..032` records contains exactly 3 accepted responses (one `answer`, two `variants`); **97 alternatives remain per ID** if a genuine 100-alternative catalog is eventually justified. That is 71 partial sets; none of the old 119 completed `reply_catalog` sets has changed. Do not automatically turn technical facts into 97 hollow paraphrases.

Application context and audience are recorded in each row: `all_ai_bots`, `direct/private/group_addressed`, direct address, read-only, no personal data; specific conditions are stated in `question` and each distinct response. Source, baseline, current source files, initial 0, added 3 and result 3 per ID are fully recorded in the two manifests packs.

Persisted work: branch `bk/t86-structured-followthrough-20261104`, [PR #210](https://github.com/Treninem/Bot-Knowledge/pull/210). The final head SHA must be recorded from the PR itself; it can change during validation. Next run: inspect the current PR/main, preserve these exact IDs and existing alternatives, then prioritize underserved practical intents where more truly different contexts exist. When alternatives cannot differ meaningfully, retain 3/100 without padding.
