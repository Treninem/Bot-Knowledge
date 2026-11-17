# ImPULS contextual help H9–H10 · 14 November 2026

Continuation of PR #666 from verified H8 workflow head `e756b3ed6532b936affb517c09da065af2631651`.

## New data

- H9: 45 original Russian contextual replies to the 45 stable questions from H1–H4; data commit `bd463902b688f2e5d3f06520f17935424266c38c`.
- H10: 55 original Russian contextual replies to the remaining 55 stable questions from H5–H6; data commit `de35f7d0a66701d317220fa633a0e8783d08882b`.
- H9+H10 **100 new responses for 100 different canonical intents**, without duplicating old responses in the new count. Including H7+H8 earlier this same cycle, **200 new candidates for the 100 existing intents**.
- H1–H10 cumulative staging **535** candidates for **100** distinct published FAQ intents. Total numeric remaining to 100 per intent **9,190**, other PR candidates excluded. All 100 sets still incomplete.
- Editorially approved new responses **0**, independently certified complete 100/100 sets **0**; the raw 535 do not imply independent meaning-level approval or consumer deployment.

Each answer has explicit context (direct/private/group_addressed), distinct scenario note, `audiences=["impuls"]`, `read_only=true`, and no right to enact moderation, setting changes or disclose private information. All cases are synthetic; no Telegram correspondence was copied.

Pre-write in-memory checks read actual published `packs/ru/impuls_help_qa.json` and H1–H9 responses, normalizing case, punctuation, whitespace and ё/е. H9: no exact normalized duplicates, maximum reply token-set Jaccard **0.286**; H10: no exact normalized duplicates, maximum **0.320**; both below the 0.70 lexical threshold. This does **not** certify semantic uniqueness, particularly against every open PR. `scripts/test_impuls_help_h9_h10_20261114.py` rechecks counts, hashes, IDs, scope and normalized/lexical duplications for all H1–H10.

Source Bot-Knowledge main `6c9f430da47f137d39a72bbd28c057cfb8f6be96`, published FAQ SHA-256 `50edd41dc0c6a868577433944e0ff0b2a36c2c9ebe53d587e5cbb4692185bbc9`. Source private ImPULS main verified in read-only mode `60f08d93c6f0268d63d1c06dc364287d0b18c183`.

**Stage-only / consumer_registered=false**: manifest, published pack, operating bot caches and runtime were not changed. Publishing all staging is blocked by existing 8 MiB registered consumer snapshot budget. PR stays Draft/BLOCKED until exact-head CI, independent meaning/context review (including other PRs), actual consumer selection with role/access enforcement and a compatible size-safe release plan. Any merge requires post-main CI on its actual resulting SHA.

Next: verify H9/H10 and full quality CI for final branch head; review semantically similar contexts across open PRs; only then select candidates for bounded registration/delivery.

## Editorial correction after lexical and same-intent review

After H10 staging, a same-intent comparison found several response situations too close to earlier H1–H4 examples. Reworked **four existing** H8/H9 responses (game wedding pending consent, ambiguous continuation after switching chats, consumer search-index update, and distinction between chat rules and contest terms). **0 additional replies counted**. Commits: H8 `53d3968b7ef7bb6f9fa45173f5cfa98e75f6af9e`, H9 `e00c7c11c8b2015cb420cd76557235b5473e8193`.

Rechecked published responses plus *all* H1–H10 records on that precise revision: **535 staged replies, 0 normalized exact duplicates, 0 token-Jaccard >= 0.70**; latest stage maxima H7 0.250, H8 **0.233**, H9 0.286, H10 0.320. This does not substitute for a human review of all similar meanings. PR #665 practical recovery R1 was compared with the original H7/H8 and showed no exact duplicates (max token-Jaccard 0.167); larger PR #663/#664 blobs could not be completely fetched for independent cross-PR review and are still an unresolved gate.
