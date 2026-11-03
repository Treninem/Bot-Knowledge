# T32 — English dialogue with meaning, context and safe abstention

Base: T31 verified head `539c0106d173e6b401456d2b4cb9a029eee3c163`, intended to merge after T31's post-main CI. Existing schema, languages, purposes, formats and consumer audiences preserved. Policy: `AGENTS.md`, `POLICY.md` and `docs/REQUIREMENTS_21.md`.

**42 candidate English examples** drafted; **2 rejected as duplicates or near-duplicates** on normalization/Jaccard checks: "Can we call it a day?" (already in source) and "That explanation went right over my head." (0.833 similarity). **40 new accepted situations and 40 replies**, 6 conversation, 4 slang, 6 sarcasm, 6 rules, 6 deception, 6 support, 6 creative. Includes English language, original synthetic response, Russian meaning note, explicit `avoid` caveat and `all_ai_bots` audience. Zero new sets of 100 answers: these are distinct context examples, not mechanically repeated variants.

New coverage: question versus instruction, conditional plans, consent to sending or disclosing, idioms without literal misreading, sarcasm without artificial praise, scoped moderation without sanctions, scam/code avoidance, support without certainty claims and original fantasy mini-stories. No real chat text, handles, contact details, secrets, private bot code or execution instructions.

File `packs/ru/english_dialogues.json`: **272 → 312** cases, **168272 bytes**, SHA-256 `0b5dca20bb5a60ce14560662fc90f14a12d57d556007be8f92efdd97e4be9612`; manifest `2026.11.03.111`, SHA-256 `f9ec96318b5220cb4a02ec4080c0ad9694436aa9badd314eb1f6e12c24528eac`. Both old and new data covered by manifest validation and <2 MiB consumer limit.

A dedicated `scripts/test_english_dialogue_t32.py` checks raw SHA, ID uniqueness, normalized exact duplicates, lexically near duplicates at Jaccard 0.78, metadata, privacy and local index retrieval. This screening is not a guarantee of all semantic differences; it complements editorial review.

No change to `Treninem/Impuls`, BotHost or its cache, and no claim of automatic consumer rollout. Merge only on verified exact-head CI and compatible base, followed by post-main CI on actual merge SHA. Next priority: other source-grounded practical questions without repeating these topics.
