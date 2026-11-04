# T74 — Universal RU QA precision and context
Base main `a214f949ef5830167e348b2ce2de774b6ead0d11`, manifest version `2026.11.04.008`.
Before 749 universal qa.v1 records; added 41 distinct canonical questions, 123 original answers, 82 search aliases. 0 exact normalized collisions rejected.
Topics: search and evidence, files, testing, uncertain diagnostics, privacy, chat rights, rule interpretations, tone, reporting, uncertainty and changing requirements.
All synthetic original cases; no raw chats, private identifiers, live actions or sanctions. Audience `all_ai_bots`, direct/private/group_addressed, read-only. Factual contract from public pinned `docs/REQUIREMENTS_21.md`.
Now 790 records, 1025143 UTF-8 bytes (<1 MiB), SHA-256 `6c46d16212014cc8e30ffbc9c5ba28d58dc83387bf160f2c2184da9a53ef1ee6`. Manifest and cache version `2026.11.04.008`.
Pre-commit JS checks: UTF-8 SHA test vectors, normalized queries and answer dedup, three distinct per question, JSON, size. CI gate: `validate_pack.py`, original T72 test, new `test_dialogue_help_t74.py` and six exact-head workflows, followed by post-main.
This is 123 **new QA answer variants**, not 41 completed 100/100 catalog intents. Prior 119 complete intent sets untouched. No consumers modified.
