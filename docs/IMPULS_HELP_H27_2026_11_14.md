# ImPULS help H27 — staged checkpoint, 2026-11-14

Continued [Draft PR #666](https://github.com/Treninem/Bot-Knowledge/pull/666) from head `f147684a38a0269caa4328c81dca17cba335e249` on published main `6c9f430da47f137d39a72bbd28c057cfb8f6be96`.

- New: **50 original synthetic Russian candidate replies**, one per intent from H25, each with a separate situation, direct-address/role/privacy restrictions, no executed actions.
- Count: prior H1–H26 **1,335** → H1–H27 **1,385 staged** (+50). 100 partial intents, **8,340 remaining raw numeric slots** including published FAQ and this PR only; 0 independent editorial approvals; 0 certified 100/100 sets. Other PRs excluded to avoid double counting.
- Sources: registered `packs/ru/impuls_help_qa.json` SHA-256 `50edd41dc0c6a868577433944e0ff0b2a36c2c9ebe53d587e5cbb4692185bbc9`; Bot-Knowledge main `6c9f430d...`; ImPULS `README.md` at `d815dc6338808c881c5ff613c9550dc42e74b44f`, read only (candidate 1.6.249, installed 1.6.248 per README; no live verification).
- Partial lexical preflight against H19/H21/H23/H25: zero exact/high-overlap answers or same-intent notes; maximum answer Jaccard 0.167 and context Jaccard 0.161. CI test scans all H1–H27 and published FAQ. These checks do not replace independent semantic review, cross-PR inspection or real role/context selection.
- `consumer_registered=false`; manifest, published packs, live bots, cache and ImPULS unchanged. Full publication remains BLOCKED by editorial meaning QA, consumer routing, exact-head CI and 8 MiB snapshot budget.
- Next: test H27 on actual head and continue the other 50 intents in H28, then assess safe selective publication.
