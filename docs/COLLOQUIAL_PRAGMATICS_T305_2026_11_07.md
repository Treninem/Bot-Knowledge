# T305 — 110 contextual Russian answers for T304 (stage only)

Source registered pack: `packs/ru/colloquial_ru_pragmatics_qa.json`, parent main `56e3eac09d79b12892dd7de8c9e806f0a662ce9f`, actual parent sha256 `8de38a7d2ad2ef4e90196c12cce0e36bbce36bb4636f8f011816530e202de3fe`, Git blob `ac46e5e22dbea25becebbf72984861a0573733ce`. Existing 22 independent T304 canonical IDs stay unchanged.

**New in T305**: 22 intentions × 5 originally written situation-specific replies = **110 new synthetic replies** and 110 distinct situation notes. Before: 22×9 = 198 registered. After T305: 22×14 = **308/2200 total** across this precisely scoped group, all **22 partial 14/100**, **86 per intent remain, total 1892**, **0 newly finished 100/100**. This staging collection is NOT automatically loaded by consumers, not in the manifest, and has no authorization or moderation power. The 85 historical complete intent groups are separate.

A new validator `scripts/colloquial_t305.py` pins stage bytes to actual registered parent manifest SHA-256 and exact Git blob, checks stable intent/answer IDs, normalized text and context uniqueness, restrictions and exact checkpoint. The opt-in selector requires an externally reviewed reply ID, matching context, direct address and local permission; otherwise it returns None. New tests verify 110 positive and hundreds of negative cases, and fail-closed paths.

Pre-commit checks: unique normalized 110 new texts and notes, 0 repeats vs 198 T304 registered replies, no lexical Jaccard ≥0.78 repeats inside T305. Independent linguistic review of all other packs is not claimed. `manifest.json` version `2026.11.07.001` and registered SHA/cache remain unchanged, because T305 is unregistered staging. Do not count these 110 as consumer-delivered skills. No ImPULS, live bots, GitHub token distribution or paid services involved.

Verify with `python scripts/validate_pack.py` and `python -m unittest scripts.test_colloquial_t305 -q`, exact-head CI and post-main CI on actual merge commit. Continue only after checking 14/100 and avoiding semantic repeats. Future genuine completion requires further original contexts, not mechanical synonyms.
