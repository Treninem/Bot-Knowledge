# T345/T346 — original RU contextual continuation

Base main: `b36999e94cec22276470174185c7066022532b22` (checked 2026-11-07).

New synthetic, non-consumer-registered candidates: T345 **22 intents × 2 = 44** (60/100 → 62/100), T346 **24 intents × 2 = 48** (59/100 → 61/100). Total **92 new** distinct reply IDs, texts and context notes, all read-only and with explicit direct-address/permission gating. Totals for this group: previous **2,736/4,600**, now **2,828/4,600**; still **46** partial intents; **1,772** remaining; **0** newly finished 100/100. Previous registered **414**, staged previously **2,322**, staged now **2,414** (not yet indexed in ReviewedStageCatalog or connected to consumer).

Preserved canonical intent IDs, source manifest version `2026.11.07.001`, pack SHA-256 and immutable preceding-stage blobs. No changes to registered pack, manifest or live cache. The code verifies parent and historical stage provenance, normalization, unique IDs/texts/context notes, privacy and read-only flags, then refuses selection without exact approved ID, direct address, matching context and local permission. New contexts address role claims, ambiguous phrases, privacy, state of unverified services, minimal recovery, irreversible operations, group/DM boundaries and partial success.

**Review caveat:** automatic lexical uniqueness tests cannot replace human semantic review across the whole library; proposed candidates are never automatically valid for all situations. No GitHub writing credentials, private chats, sanctions or actual bot actions in language packages.

Follow-up: review and explicitly extend `ReviewedStageCatalog` from T343/T344 to T345/T346 in independent PR; confirm exact-head and post-main CI, then add further nonredundant contexts. No ImPULS changes or live deployment.
