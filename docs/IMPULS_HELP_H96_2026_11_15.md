# ImPULS H96 — next 51 incomplete contexts (15 November 2026)

Continues PR #666 from exact head `00f096f8b86bd257d66e0aaf59117f373d5015c6` and unchanged published main `6c9f430da47f137d39a72bbd28c057cfb8f6be96`. ImPULS was checked read-only at `54b8a3a813fec82c1f953408942ba327eb181c37` (candidate 1.6.263, installed 1.6.262, AI quality not accepted).

**51 new original synthetic RU candidate replies for the 51 intents untouched by H95**. Topics include rules and time limits, group moderation false positives, local learning consent, privacy, game help, complaint/appeal context, and short conversation corrections. Each reply declares the situation and context; no permissions, sanctions or live actions are granted by this dataset.

Combined H95 and H96 additions this run: **101 candidates across exactly 100 tracked intents**. H1–H96 staged candidates: **3908**, previously published baseline within the same intents: **275**; remaining numeric positions: **5817**. All 100 intents remain partial, 0 completed 100/100, 0 new editorial approvals or registered replies. External PRs are not included in these counters.

Preflight checked these 51 against registered answers and H93–H95 for exact normalised reuse and conservative high lexical similarity. The exact-head CI checks every H1–H96 stage and manifests against real repository bytes in regular Python and `-O`; it does not prove semantic independence from PR #662–#665 or the behavior of the live consumer. H95 already passed [its exact-head CI](https://github.com/Treninem/Bot-Knowledge/actions/runs/43759571707).

**DRAFT/BLOCKED** for publication: independent semantic acceptance, verified consumer chat/role routing, size-safe manifest/cache integration and final CI. No ImPULS or BotHost writes, no live deployment, private data, paid services or branch-protection changes.
