# T290 — 96 original spoken-context replies (2026-11-06)

Base main: `4c7d4914103fcad999f5465561f23c044fa712d5` after T289 PR #347. Parent stage `staging/ru/spoken_pragmatics_t289_delta.json` Git blob `b602a7e4cf942874c014a17f8f97bcee4dbecc3e`.

| Measurement | Previous | New | Total |
|---|---:|---:|---:|
| Registered replies in 24 established intents | 216 | 0 | 216 |
| Supplemental staged replies | 1992 | **96** | **2088** |
| Registered + staged | 2208 | **96** | **2304** |
| Per intent | 92/100 | +4 | **96/100** |
| Missing to 24 × 100 | 192 | -96 | **96** |
| Newly completed 100/100 intents | 0 | 0 | **0** |

All 24 existing canonical intents were continued with four separately described scenarios: agreement and consent, uncertainty, irony, respectful critique, support, soft endings, analogies, factual limitations and de-escalation. Each has original synthetic Russian wording, explicit context, intended audience and no sanction/action power. Mechanical synonym swaps and emoji substitution were avoided. The dedicated Python validator enforces the original 9 per-intent registered records, whole historical chain of 92 responses per intent, full normalized uniqueness, ID and note uniqueness, lexical near-duplicate screening, source/parent SHA and strict opt-in selection. Automated screening is not full independent semantic review.

**This is an unregistered staging candidate.** No changes to `manifest.json`, registered source package, live consumer cache, ImPULS or BotHost. It will not be selected by a running bot without a separately approved consumer integration and explicit local permission. CI is required on the exact PR head SHA, then post-main CI on actual merge SHA before claiming publication confirmed. No paid Actions or secrets.

Next: finish the last **4 contextually distinct responses per intent** to reach 100/100, then continue the existing 85 contextual intents from T288, verifying baseline first.
