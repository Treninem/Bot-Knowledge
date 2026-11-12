# T171 — boundaries, corrections and public-context evidence (2026-11-05)

Base: `main 6f2aa480375a21cb4d81f00a4c3ee448eda1cbfb` (after T169 merge). Registered source: `packs/ru/response_boundaries_qa.json`, Git blob `f15104dbf08d3691b198abb7f0bd52d81383b5a0`, manifest SHA-256 `e0d704a2a03d5aabb3db479eb47f07c2ba229ca76955a3cfc0f89dd5386538d9`, unchanged in this branch.

## Delta

31 already existing canonical intents: before **279 registered + 93 staged = 372** (12/100 each). Newly created **62** distinct contextual RU answers (two per intent), **0** automatically rejected for normalized/lexical duplication. After: **279 registered + 155 staged = 434 candidates**, **14/100 each**; **31 partial**, **0 newly completed 100/100**, remaining **86 each / 2666 in total**. No canonical questions copied or invented to inflate counts.

Topics: preserving tone and conditions in edits, quotes/headline corrections and uncertainty, timezones and percentage denominators, explicit consent, correct group audience, unknown prior conversation, provocation without harassment, dark humour only with fictional non-victim situations, confidentiality in examples and honest `prepared` versus `deployed` reports. Each new entry has an explicit distinct `context_note`, `avoid`, stable `_t171_` ID, `language=ru`, `style=neutral`, `audiences=[all_ai_bots]`, `read_only=true` and an allowed address context.

### Integrity

- `staging/ru/boundaries_t167_context_pool.json`, full UTF-8 **137023 bytes**, SHA-256 `967ad68b810c1df261f236edc5bb1b8b2783a1b129b22a3a4f065c9cc2c12253`, Git blob `65c11f4e938d748905f43eae4504ce87d2c91bab`.
- In-process JS: 155/155 staged normalized-unique (NFKC/case/ё-е/punctuation/whitespace); 62 new replies vs previous staged: 0 token-Jaccard >=0.78, max 0.429. Automated checks do not prove exhaustive semantic diversity.
- Updated `scripts/test_response_boundaries_t160.py` to check 31×5 staged entries, all 279 registered, original and latest IDs, source SHA, read-only audience, privacy patterns, normalized exact duplicates and existing manifest QA packs. Actual Python and exact-head CI must be confirmed before a merge.
- Staging **not** in manifest; no consumer-visible pack, `qa.v1` answer quota change, knowledge version change, runtime cache mutation, or consumer integration. Consumer selection of >9 candidates remains separately blocked.
- No edits to private ImPULS, publisher files, BotHost, paid workflows or other worker branches.

Next priority: continue 31 boundary intents from 14/100 while maintaining meaningful context diversity; independently validate consumer-side routing before any active publication.
