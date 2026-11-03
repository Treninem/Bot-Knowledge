# Universal dialogue QA T12 — evidence and limits

Base `316d688e7fdb86e0485493069413597303f16493`, 222 records in `dialogue_help_qa.json` at manifest .82.
Reviewed 30 original topics. Accepted 30; rejected 0 for exact normalized or canonical token-overlap >= 0.66. Rejected items: [].
Added 90 original contextual answer variants (30 primary + 60 alternatives) and 60 new query aliases. New total 252 QA records. Answers focus on tone, safe troubleshooting, group context, moderation explanation, evidence and ordinary conversation.

All records are synthetic, carry `all_ai_bots` audience and explicit contexts, and cite the immutable public AGENTS policy at base SHA. 8 group-specific records restrict scope to `group_addressed`. QA is declarative; no action, sanction, personal chat, user ID, secret, or unsupported ImPULS features.

UTF-8 package bytes: 326151; actual SHA-256 `e9282181f5859c186fd06252dec38551f715cd857f64ca517f79b4a0ee5428c8`, within 1 MiB qa.v1 and 2 MiB consumer limits. Manifest version .83 and cache-invalidation via content digest. `reply_catalog` unchanged, so these are not 100/100 collections.

Required tests: `python scripts/validate_pack.py`, `python scripts/validate_qa_v1.py`, `python -m scripts.test_dialogue_help_expansion`, exact-head CI, post-main CI. No BotHost delivery claimed.
