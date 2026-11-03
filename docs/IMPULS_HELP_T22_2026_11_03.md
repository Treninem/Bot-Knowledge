# T22: natural ImPULS questions, source-confirmed limits

Base Bot-Knowledge main `f7c9fb3a4a4c5dab71660691a946361be6a9d0e0`; source ImPULS `2989cbb8cbbdf60cd43696d3fb39b5d37cb36d54` inspected **read-only**: `docs/COMMANDS_MATRIX_V30.md`, `README.md` and `AGENTS.md`. The published answers are generic user-facing guidance, not private implementation or release promises. A candidate on GitHub is **not** proof of the same version running on BotHost.

24 genuinely distinct practical situations: delayed/double game button presses, uncertain round state and participation, store preview versus confirmed payment, stale balances, effect/boost status, raffle deadlines, stale management UI and rights, unclear warning after deletion, report privacy and plain-language troubleshooting. **24 canonical questions, 48 new searchable aliases, 72 original answers.** No existing variants overwritten; normalized exact collisions and semantic lexical near matches above 0.59 screened against 660 existing ImPULS QA before acceptance. Manually separate meaning and safety clauses.

All `impuls` audience and addressed group/private/direct contexts; no commands, automatic sanctions, payments or access to other users' information are granted. Reading a description is never a successful action; status unknown remains unknown. Sources and policy: Bot-Knowledge `AGENTS.md`, `POLICY.md`, `docs/REQUIREMENTS_21.md` at base, read-only ImPULS files above.

Pack now **684 records**; bytes **780925**, SHA-256 `5dd52472003ac9254a3a92d429f3887a26cafca401788314cfeb3e4ecb99c1e9`. Manifest version `2026.11.03.101` with real content digest; 2 MiB consumer limit and stricter 1 MiB qa.v1 test preserved. New `scripts/test_impuls_help_t22.py` exercises every canonical and alias lookup, scoped rejection, hashes and privacy in quality workflow.

No new `reply_catalog` 100/100 sets created, no incomplete sets added. Before merging: exact-head CI on final SHA, fresh base and protected merge, then post-main CI. No ImPULS edits or BotHost rollout.
