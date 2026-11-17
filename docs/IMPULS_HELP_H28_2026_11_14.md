# ImPULS help H28 — staged checkpoint, 2026-11-14

Continuing [Draft PR #666](https://github.com/Treninem/Bot-Knowledge/pull/666) from H27 head `b81d041b57cc76cd9ee90a77555d504b27724268`; Bot-Knowledge published main `6c9f430da47f137d39a72bbd28c057cfb8f6be96`.

- Added **50 original synthetic RU read-only candidate replies**, one per remaining H26 intent with concrete situations. H1–H27 = 1,385 → H1–H28 = **1,435 staged** (+50). Full H27/H28 continuation = 100 candidate replies on 100 distinct intents.
- Counting registered FAQ plus this PR only: **6 intents 15/100**, **49 at 16/100**, **19 at 18/100**, **26 at 19/100**; total missing raw positions **8,290**. All 100 remain partial; 0 independently approved new replies, 0 certified 100/100 sets. Other PRs excluded.
- Source registered pack SHA-256 `50edd41dc0c6a868577433944e0ff0b2a36c2c9ebe53d587e5cbb4692185bbc9`; ImPULS README at `d815dc6338808c881c5ff613c9550dc42e74b44f` checked read only; candidate 1.6.249, installed 1.6.248 per README; no live verification.
- Deterministic partial screen vs H20/H22/H24/H26: no normalized exact or high Jaccard matches; max reply 0.190, context 0.190. Automated Python test checks all 28 stages and published FAQ in exact-head CI; this is not independent semantic review.
- All new entries `consumer_registered=false`, directly addressed, scoped to correct role/chat context, no execution of sanctions/settings. Published manifest, live bot, working caches and ImPULS unchanged.
- **Merge BLOCKED** pending full exact-head CI, cross-PR semantic review, actual consumer role/context selection and published snapshot <=8 MiB. Do not claim post-main CI or active integration.
