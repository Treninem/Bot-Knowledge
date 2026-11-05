# T111 — continuation of precise-dialogue QA (04.11.2026)

- Base main: `23871ed224cbe0d9636c841fd48e3f43bdd3ed1b`; prior Draft PR #227 head: `aa90e2f658f70a037ebf57c23c0460a8efa5ecba`. This is only a Draft, not published in main.
- Existing stable intents: **132**; +216 synthetically authored contextual RU responses after the 702 already in Draft => **918** replies in Draft; cumulative PR delta to main: +522 replies (396 in main). Completed 100/100: **0**.
- T77: 42 intents × **9/100**, remaining 91 per intent (3822 total). T82/T85: 90 intents × **6/100**, remaining 94 per intent (8460). Total missing = 12282.
- Original IDs, questions, aliases, audience `all_ai_bots`, scopes and read-only constraints retained; no real chat transcripts, personal data, hidden roles, sanctions, or unverified bot commands.
- Pack SHA-256 of proposed exact UTF-8 bytes: `2e4210e9e1d55ab7ad11b7f51ad60ca12ef5d68e384ca7942d208a4b76c10095`; pack bytes 279383. Manifest `2026.11.04.034`; candidate repo snapshot 7618891 of 8388608 bytes, 38 registered packs. Repository-side cap is **not** equivalent to actual ImPULS consumer acceptance.
- Executed on in-process JS: SHA-256 known vector and previous manifest hash verification; 918 unique normalized replies; new-vs-existing within same intent no token-Jaccard ≥0.75 (largest 0.375); 132 IDs and expected 8/5 variant shapes. This is a lexical check, not complete semantic evaluation.
- Local Python on exact checkout, cross-pack comparisons, exact-head CI and consumer E2E remain outstanding. Update test expectations before merging. Protected publisher scripts from #224 not touched. No paid Actions manually dispatched.
