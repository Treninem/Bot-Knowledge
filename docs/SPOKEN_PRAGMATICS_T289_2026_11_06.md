# T289 — 48 new contextual conversation replies (2026-11-06)

Source main: `75514527f2e1b84b69bf8e372e9f00ea771d2fef`. Immutable
parent: `staging/ru/spoken_pragmatics_t287_delta.json`,
Git blob `028ef18503f332f64a1a4a5529d910890c06ba37`.
All 24 previously established canonical intents are continued, not restarted.

| Metric | Before | T289 addition | After |
|---|---:|---:|---:|
| Registered + previously staged answers | 24 × 90 = 2160 | 48 | 24 × 92 = 2208 |
| Replies in staged overlays alone | 1944 | 48 | 1992 |
| Remaining to 100/100 | 240 | −48 | 192 |

All **24** intents remain partial (92/100 each, 8 remaining);
**0** newly complete. The 48 responses cover two additional independently
described situations per intent, including consent, follow-up, irony,
figurative speech, factual uncertainty, criticism, boundaries and de-escalation.
Pre-commit screening: 48 normalized new strings unique against T287's direct
layer and each other; full-history checks performed by the T289 regression gate.
No claim of a complete independent semantic review of all prior 90 per intent.

Only synthetic anonymized Russian replies, `all_ai_bots`, read-only,
explicit address + approved reply ID + matching context + local permission.
No permissions to moderate or execute actions. This staging file is **not**
registered in `manifest.json` and is **not** delivered to any bot. Registered
package contents/hashes, manifest version, consumer caches and ImPULS
remain unchanged. Validation:
`python scripts/validate_pack.py`;
`python -m unittest scripts.test_spoken_delta_t289 -q`;
read-only CI on actual exact head. A successful merge does not prove consumer rollout.

Next: continue the same 24 intents from **92/100**, 8 gaps each, then
continue 85 contextual intents (T288). Never count these 48 as new again.
