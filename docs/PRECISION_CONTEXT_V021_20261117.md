# Conversation precision v021 — 17.11.2026

Based on immutable main `10fc0c437639eb8ad54d58cc97d0ad6958f74800` after v020. **132 newly authored synthetic RU contextual responses** across 132 unchanged intents; baseline 8/100 → **9/100** (91 outstanding each). No 100/100 set is certified. All existing answers and IDs are preserved; each of the 132 new variants describes a different application condition, checked with a normalised Jaccard threshold of 0.56 against prior answers in its intent.

The registered `packs/ru/conversation_precision_qa.json` now uses the full existing qa.v1 ceiling of eight `variants` plus `answer`. **Do not add a ninth variant or silently widen the schema without consumer compatibility tests.** This pack remains declarative and read-only; no moderation actions or permissions. Audience `all_ai_bots`; contexts direct/private/addressed-group require explicit direct address. No public or private consumer deployment has been performed.

The `packs/ru/structured_information_qa.json` package is whitespace-minified only to free snapshot capacity. Exact parsed JSON equality against `10fc0c437639eb8ad54d58cc97d0ad6958f74800` is enforced by the dedicated test. No records or metadata are changed in this second package.

Actual UTF-8 SHA-256: precision `b37d35a98d6dd919bace2275b838f61a7973b9d3a4207b44a7a1b6040164350b`; structured `c51c28d1ed6d475b809666b3c2b23e2e6537629e85b81e463b5e0b67b20bbd9e`.
Projected current manifest+packs size: **8387442 / 8388608** bytes (1166 free). Version `2026.11.17.021`.

Safety/quality gate: `python scripts/validate_pack.py`, `python scripts/validate_qa_v1.py`, `PYTHONPATH=scripts python scripts/test_precision_context_v021_20261117.py` (normal and `-O`), historical v018-v020 immutable tests, full exact-head CI, independent meaning review, then post-main CI. Only after successful gates may this release be merged. Source candidate checkpoint: commit [ddcbae8e6261f1a0140d4139fe614e20016a4f11](https://github.com/Treninem/Bot-Knowledge/commit/ddcbae8e6261f1a0140d4139fe614e20016a4f11), staging file intentionally dropped from final PR tree. No ImPULS source, BotHost or live cache changed.
