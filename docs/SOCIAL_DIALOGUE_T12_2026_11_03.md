# Social dialogue T12 — 03.11.2026

Baseline: 572f9fd46ff8e50bcb3b70156ca712bff7d81ec3 (manifest .81, 497 existing synthetic situations).
Accepted: **60 newly written contexts and answers**, 10 each for congratulations, support, humor, profanity interpretation, conversation, and creative miniatures. Total proposed: **557**. Rejected exact normalized input/output matches: 0. Token-Jaccard check on inputs against earlier and new cases with threshold 0.56: 0 flagged. This lexical check cannot prove semantic uniqueness; all 60 cases underwent manual scenario-level review.

Package: `packs/ru/social_dialogues.json`. Version `2026.11.03.82`. SHA-256 of actual UTF-8 bytes: `aa645c865525a1109e51ad221b333226c38815cf7e9d4a8f486679f37d865deb`. Size: 378769 bytes (consumer cap 2,097,152). Source policy: `AGENTS.md`, `POLICY.md` and `docs/REQUIREMENTS_21.md` at baseline commit. No real chat excerpts, identifiers or logs. `audiences: ["all_ai_bots"]`; every record has a context and avoid-condition; no punitive action. Social cases are **not** 100/100 reply_catalog sets. Existing `reply_catalog.json` untouched.

Required: `python scripts/validate_pack.py`, `python scripts/test_social_dialogue_t7.py`, GitHub exact-head quality and post-main checks. Search is reference behavior only; no claim of live ImPULS/BotHost rollout.
