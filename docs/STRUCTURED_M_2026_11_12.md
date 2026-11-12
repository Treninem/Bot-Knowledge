# Structured-information M: continuation of 60 established intents (12 Nov 2026)

## Verified baseline and scope

- Repository: `Treninem/Bot-Knowledge`; base published `main` is `6c9f430da47f137d39a72bbd28c057cfb8f6be96`. The published source is `packs/ru/structured_information_qa.json`, manifest SHA-256 `55b3f6126d36cd92687d005b7fedf5a11df9ee61cf453103accdf1f13c8498f0`, Git blob `8b3d596b5b50d3d319ebf450c96d5623fc99d26a`.
- Continue **PR #662**, original L head `e24803c1e9e81480dfd8a8fc9d47613e31fe08a6`. L is kept byte-for-byte unchanged to preserve its existing regression tests and the conservative 2 MiB per-file planning budget.
- New independent, **unregistered** file: `staging/ru/structured_information_20261112_delta_m.json`, suffixes **52–53**. Shared canonical intent IDs, prompts, categories and selection constraints remain unchanged; there are exactly two replies per intent, each with its own explicit context note. Each reply is read-only, direct-address-only and for `all_ai_bots`.
- This content is synthetic. No quotations from private conversations, names, identifiers, credentials, sanctions, asserted actions or new ImPULS features. It cannot run moderation or modify consumer state. The existing manifest, registered pack SHA-256, live caches and bots are untouched.

## Accurate cumulative counts

| Scope | Per intent | Total for 60 intents |
| --- | ---: | ---: |
| Published source | 3 | 180 |
| Older staged A–J | 11 | 660 |
| Existing L in PR #662 | 31 | 1,860 |
| **New M (this cycle)** | **2** | **120** |
| **Combined candidate total** | **47 / 100** | **2,820 / 6,000** |
| **Still missing** | **53** | **3,180** |

There are **60 partial intent sets**, **zero new complete sets (100/100)**. The earlier 1,860 L replies and all published/older replies are not recounted as new. Stable next response ID suffix: **54** for each of the 60 intents. Continue with a separately sized delta under the same PR; do not enlarge the near-limit L blob.

## Checks and editorial changes

- Pre-write and readback structural checks: 60 stable intent IDs, 120 distinct response IDs (suffixes 52–53), 120 unique normalized responses and context notes, complete read-only/target metadata; numeric examples reviewed manually.
- Initial lexical check against 1,860 L replies: zero exact matches or token-set Jaccard >= 0.70; maximum for the second 60 was 0.4231.
- Full new set cross-checked against 1,296 K candidates, 2,000 conversation-nuance #663 candidates, 1,500 precision #664 candidates, 342 registered structured source responses, plus all A–J supplemental files. No normalized exact matches and zero pairs at Jaccard >= 0.70 were detected. This lexical screening **does not establish independent all-pack semantic review** or functioning consumer context routing.
- Manual editing found substantive overlap in five cases (measurement-unit illustration, path versus displacement, tax base, time-offset example). Reworked their text and applicability notes in `d4918497fab65a026302a71e5f7cb4edbc0a5b1a` without increasing the new-answer count.
- Dedicated regression: `scripts/test_structured_m_20261112.py`. Tests check historical registered source bytes and blob hash, complete M checkpoint, context restrictions, unique IDs, normalized duplicates against L/A–J/source, and lexical proximity. Record actual CI state only for the **latest complete head SHA**, never earlier green runs. Independent local Python with the repository files was not available in this environment.

## Publication and next actions

This is **Draft / BLOCKED** content. The published consumer snapshot is historically reported at 7,999,374 / 8,388,608 bytes; the new file is deliberately outside the consumer manifest. Do not register L/M wholesale or raise the limit without an independently tested scoped delivery plan. The pre-existing main push workflows include queued and failed runs. Merge remains gated by full current-head exact-head CI, semantic/context review, main compatibility, safe consumer budget and post-main verification. Do not override protection, use paid Actions or deploy to ImPULS/BotHost.

Next: first review these 120 examples for meaning and applicability, then continue each established intent from suffix 54 with genuinely different situations. After checks, evaluate staged separation and consumer selection without breaking the existing architecture.
