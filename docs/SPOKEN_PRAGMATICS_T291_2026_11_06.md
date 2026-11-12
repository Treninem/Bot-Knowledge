# T291 — 24 spoken-pragmatics intents reach 100/100 in offline staging (2026-11-06)

Continuation of T290 within the same Draft PR, based on exact prior commit `7be0192eccc692abbd7147a25bef254c79d8aade`. Parent file `staging/ru/spoken_pragmatics_t290_delta.json` Git blob `4aa0b2a7bca658151ebf6b245288c47068c2e77f`. Original main base for the proposed PR: `4c7d4914103fcad999f5465561f23c044fa712d5`.

| Measurement | T290 | T291 addition | T291 total |
|---|---:|---:|---:|
| Registered answers | 216 | 0 | 216 |
| Supplemental staged answers | 2088 | **96** | **2184** |
| Registered + supplemental | 2304 | **96** | **2400** |
| Answers per intent | 96/100 | +4 | **100/100** |
| Fully populated intents | 0 | +24 | **24** |
| Remaining gaps for these intents | 96 | -96 | **0** |

The two checkpoints add **192 original synthetic Russian replies (96 + 96)**, across 24 pre-existing canonical questions. Each response describes a distinct use-case, has explicit contextual scope, reads as a suggestion only and never authorizes actions, sanctions or bot memory. The validator checks the complete historical chain, normalized duplicate IDs/text, context-note duplicates, token-Jaccard threshold, SHA of exact parent and source pack, and strict opt-in gates (audience, address, local approval, recent suppressions). Human evaluation is still required for nuanced semantic near-duplicates beyond this lexical screen.

**Not registered or deployed:** this is a staging-only completion. The live consumer cannot select these answers without a separate approved integration. `manifest.json`, source-pack SHA, live caches, and the private ImPULS repo are intentionally untouched. No paid workflows or writes outside this public repository.

Next independent queue: 85 existing contextual intents on T288, initially 83/81/80 per intent by subgroup, with full inventory reconciliation against current main and other PRs.
