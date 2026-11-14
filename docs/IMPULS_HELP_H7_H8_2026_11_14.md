# ImPULS contextual help H7–H8 · 14 November 2026

Continued Draft PR #666 from H6 exact head `c094b85651db7afa303277b4113e813dd52eb181`, using Bot-Knowledge main `6c9f430da47f137d39a72bbd28c057cfb8f6be96`. Verified ImPULS main read-only `60f08d93c6f0268d63d1c06dc364287d0b18c183`. Source: published `packs/ru/impuls_help_qa.json`, manifest SHA-256 `50edd41dc0c6a868577433944e0ff0b2a36c2c9ebe53d587e5cbb4692185bbc9`.

## Recorded additions

- H7: **55** original Russian answer candidates for the **55 earlier H5/H6 partial intent IDs**, one new distinct context per question, data commit `9af0ecea0eb45acda37ec74a7d1c3ddf14eb1ba9`.
- H8: **45** original Russian answer candidates for the remaining **45 earlier H1–H4 partial intent IDs**, data commit `a45f485352919413ce69cd6e2eeb09642e64ab75`.
- This run: **100** new candidates across **100 different existing canonical questions**, not 100 new questions. Earlier published/staged answers not included in delta.
- H1–H8 cumulative: **435 staged** candidates across **100** distinct intents, plus the original published answers. Numeric positions still to fill: **9,290** across these intents (other PRs excluded).
- None of these 100 sets reaches 100 raw responses. **Editorially approved new replies: 0. Independently certified 100/100 sets: 0.** All 100 remain partial and unregistered.

Examples cover greetings, follow-ups, concise explanations, private-vs-group boundaries, permissions, game and Pulse questions, incident reports, moderation ambiguity, quote/command distinction, privacy, learning and outdated versions. All 100 are synthetic, `language=ru`, `audiences=["impuls"]`, context-scoped and `read_only=true`. The data explicitly forbids assuming a chatbot has completed a setting or sanction.

Preflight on the actual H1–H8 and published FAQ records before staging: H7 **55/55**, no exact normalized duplicates, maximum token-set Jaccard **0.250**; H8 **45/45**, no exact normalized duplicates, maximum **0.243**. Neither lexical check proves meaning-level uniqueness. Other unmerged PRs and consumer context choice need independent review.

## Files and safety gates

`staging/ru/impuls_help_context_h7_20261114.json`, `staging/ru/impuls_help_context_h8_20261114.json`, `scripts/test_impuls_help_h7_h8_20261114.py`, this checkpoint and the updated exact-checkout read-only workflow. H7/H8 are **consumer_registered=false**, not in manifest; cache, existing published pack and private ImPULS are unchanged. Test checks source SHA-256 and manifest, counts/IDs, direct context, privacy markers, normalized/lexical repetition, no auto-sanctions, and confirmed partial counters.

**MERGE BLOCKED pending actual latest exact-head CI, full semantic cross-PR review, consumer role/context selection, and 8 MiB registered-snapshot budget.** The exact-head workflow must pass on the complete final head and post-main CI must pass on a later actual merge before any delivery claim. No live deployment or paid actions are authorized.

Next: fix any H7/H8 CI defects, review meaning (including overlaps with PR #661 and #665), and continue missing practical intents without manufacturing synonymous fillers.
