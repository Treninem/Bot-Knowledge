# T89 — English pragmatics in real dialogue (04 Nov 2026)

Stacked on T88 head `f245978dfdfbfa07f05a9608ca45fcf6e8f9e227`, main origin `ae55e30fb9a081d26f29728f363e28c80cb1866f`. Authorized by `docs/OWNER_AUTOMATION_SCOPE_2026_11_02.md`.

Pack `packs/ru/english_conversation_nuance_qa.json`: before 32 intents, +30 new independent English questions, now 62; +60 aliases, +90 distinct context-bound replies. Stable new IDs `en_nuance_t89_001..030`, each has **3/100** unique answers and 97 remain if materially different contexts warrant it. The earlier 32 records, all 119 complete reply-catalog intents, and other packs are untouched; no new sets 100/100.

Topics: hedged requests, consent vs discussion, polite refusal, implied time and responsibility, mixed signals, idioms, nonliteral agreement, confidentiality, authority, self-correction and stopping arguments. Each entry is synthetic and intended for a specific conversational condition. No real messages, personal identifiers, ImPULS product features, sanctions, tool use or live-bot deployment.

Source: [21 general requirements](https://github.com/Treninem/Bot-Knowledge/blob/ae55e30fb9a081d26f29728f363e28c80cb1866f/docs/REQUIREMENTS_21.md); qa.v1 `all_ai_bots`, `direct/private/group_addressed`, read-only and requires-direct-address. Manifest `2026.11.04.022`; updated exact UTF-8 SHA-256. `scripts/test_english_conversation_nuance_t80.py` now checks 62 records, 186 unique queries and 186 unique replies, plus source pack integrity and cross-pack collisions. Exact-head CI and post-main status must be checked against real SHAs; local Python execution not claimed.

Do not mechanically fill the remaining 97 slots per narrow language expression. Next priority: verified practical ImPULS help gaps and context-sensitive RU replies once their current source is read.
