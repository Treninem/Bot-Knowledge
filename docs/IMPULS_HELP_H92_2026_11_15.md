# ImPULS H92 — useful follow-up cases (15 November 2026)

Continues [PR #666](https://github.com/Treninem/Bot-Knowledge/pull/666) from exact parent `11980820e1b2d172c4940cf8d0f4e22ddc5d0fe7`, preserving the source baseline `6c9f430da47f137d39a72bbd28c057cfb8f6be96` and read-only ImPULS `54b8a3a813fec82c1f953408942ba327eb181c37`.

Adds **50 new synthetic Russian answer candidates** for **50 canonical intents**. All 40 intents not touched in H91 receive coverage in this run, plus contextual additions to incomplete greeting, onboarding and correction topics. Every answer is limited to a declared situation; none is a verified live bot action.

Cumulative H1–H92: **3687 staged candidates**, published baseline **275** for these 100 intents, **6038 numeric gaps**. All 100 partial; certified 100/100: zero. Approved or registered in main in this run: zero.

Preflight: verified source references, normalized duplicates and Jaccard lexical overlap below 0.70 against published help, H90, H91 and newly selected replies; 0 proposals excluded. The H92 full-lineage test checks H1–H92, context, counts, scope, privacy and misleading action claims in normal Python and `-O`. Meaning overlap against other open PRs requires separate review.

DRAFT/BLOCKED: semantic editorial check; actual consumer context/role routing; manifest and cache integration under 8 MiB. Do not merge this staging pool as a delivered language pack. No private ImPULS or BotHost changes.
