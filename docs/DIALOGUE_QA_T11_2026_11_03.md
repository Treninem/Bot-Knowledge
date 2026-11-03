# Universal dialogue QA T11 — evidence and boundaries

Base: `bd771d6deced8491f375332128e206736098e40b`; manifest 2026.11.03.78 → 2026.11.03.79. Existing 182 universal QA, accepted 40 original questions with 120 standalone answers and 80 aliases. Proposed total 222. No records in reply_catalog changed and no synthetic quota of 100 is claimed for qa.v1 (max 8 variants/record).

Domains: evidence quality, causal reasoning, user-imposed scope, conversational feedback, uncertainty and testing, consent for tone, individual/group moderation boundaries and version-sensitive functions. Generic all_ai_bots knowledge only: no live ImPULS feature assertion or sanction. All text is synthetic, with source AGENTS.md at immutable bd771d6deced8491f375332128e206736098e40b. No personal chats/IDs, tokens, private code or consumer writes.

Exact normalized scan across existing questions and aliases: 0 duplicates; canonical-token Jaccard threshold 0.66: 0 candidate(s) rejected, 40 accepted. Manual review required for semantic duplicates beyond lexical threshold. All new records have 2 aliases, 2 varied responses, explicit audience and contexts. UTF-8 qa.v1 package 290838 bytes (1 MiB qa.v1 and 2 MiB consumer limit). SHA-256: `7357a99afadab4a953dd12a26ea257552a4663b0c94699674b8412764ef52c03`.

`scripts/test_dialogue_help_expansion.py` adds 120 exact search assertions for new canonical questions and aliases. Run existing `scripts/validate_pack.py` / `scripts/test_dialogue_help_expansion.py` and full GitHub quality CI on exact head; do not infer CI success before its actual run. Publishing in main will not mean live BotHost delivery.

Next: select new semantically distinct conversational scenarios; leave near-full reply_catalog unchanged, and check all PRs before overlapping manifest writes.
