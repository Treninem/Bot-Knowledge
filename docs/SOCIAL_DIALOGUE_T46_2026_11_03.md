# T46 — contextual synthetic social replies (2026-11-03)

Base main: `cb96241d2ca3ec7d8b59abb642cdffa02960d136`, post T45. New content is **48 authored social scenarios / 48 replies**, eight per kind: congratulations, support, explicitly requested humor, interpreting strong language / firm boundaries, natural conversation, and short original fiction. Stable IDs `talk_t46_001`–`talk_t46_048`. Earlier cases remain unchanged.

Pre-publish normalized exact collisions across existing social `input` and `response`: 0. Highest input token Jaccard against prior and new inputs: 0.500 (pair talk_t46_019 / talk_humor_alarm). This lexical screening is not a guarantee of semantic uniqueness; all entries have distinct circumstances and a separate `avoid` condition. No actual Telegram chats, names, user identifiers, secrets or sanctions.

Social cases: **1211 → 1259**. File bytes: **849922**, SHA-256 **`a1292d92916296df9909e75e9817ecb8f22350fdcf353f3227be03b91e2dbb08`**, within the 2 MiB consumer limit. Manifest version `2026.11.03.125`, SHA-256 `f1aa3c1fe37dde46e5cc28f537ba4f8d10b4d013f058d1606bb90e6b58acb6a7`. Existing SHA entries do not change. Snapshot invalidation uses manifest version plus content SHA; live caches were not touched.

Run `python scripts/validate_pack.py`, `python -m scripts.test_social_dialogue_t46`, and the existing GitHub quality suite on the **actual PR head SHA**. Require successful exact-head CI and post-main CI before declaring merged publication fully checked. This PR does not modify `Treninem/Impuls`, change live BotHost, or prove consumer delivery. No new 100/100 canonical reply set is claimed.
