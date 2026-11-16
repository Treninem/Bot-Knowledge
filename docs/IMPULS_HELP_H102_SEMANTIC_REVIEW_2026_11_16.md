# H102 semantic overlap triage (16 November 2026)

The H102 stage was compared intent-by-intent with staged H1–H101 for **token Jaccard ≥ 0.33**, in eleven read-only batches. This covered **all 101 earlier stage files** and the 102 H102 candidate replies. It is a screening threshold, not proof of semantic uniqueness.

**13 overlaps prompted manual rewriting in place**: `telegram_bot_rights`, `appeal`, `reply_more`, `pulses`, `explain_previous_step`, `greeting`, `conflicting_chat_rules`, `other_chat_access`, `moderation_caps`, `quoted_setting`, `game_start_diagnosis`, `ask_for_source`, `purpose`. Original H102 candidates were replaced with more situation-specific replies; the count stays **102**, with **0 extra** credited for edits.

Differences now include distinguishing a human review from an actual moderation action, quotes in appeals, ambiguous table continuations, game balances versus administrative rights, inaccessible controls, interruptions during a game, topic-specific rules, stale forwarded controls, uppercase acronyms, hypothetical commands, obsolete game messages, fact-checking a local state, and user-versus-admin authority.

Author-only editorial triage is **not independent acceptance**. Lexical screening cannot prove all candidates are genuinely novel in meaning. Pending: compare H102 with staged PRs #661–#665, review all 4,300 H1–H102 responses for factual precision, verify consumer routing by context and role, then register only reviewed candidates within 8 MiB with manifest/SHA/cache safeguards. No live bot or consumer code was modified.

Published main remains `6c9f430da47f137d39a72bbd28c057cfb8f6be96`; current task writes only the H102 stage, its validation, read-only workflow and tracking documents in PR #666.
