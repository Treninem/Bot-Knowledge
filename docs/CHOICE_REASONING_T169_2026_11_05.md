# T169 — 30 practical-choice intents: contextual continuation (2026-11-05)

## Checked source and safe scope

- Base `main` before T169: `b580c71c2b823133fae52dbb4ff949b91a1234b1`.
- Registered source: `packs/ru/choice_reasoning_qa.json`, Git blob `ae0963f5e4962ad6442678003861bea5a373eb9e`, manifest SHA-256 `6120bed161faf0d13e9b86582729cf8c13ace8b7927c5d77e3da6e8a16be8611` (verified against source by the existing test).
- Source `manifest.json` knowledge_version `2026.11.05.036`; 41 registered packs, all unchanged by this PR. `staging/ru/choice_t166_context_pool.json` is **not** in the manifest and cannot be consumed as registered `qa.v1`.
- No edits to ImPULS, live caches, BotHost, protected publisher files or other workers' branches.

## Exact delta

The 30 existing **canonical** choice intents were all at 9 registered + 3 staged = **12/100**. T169 appends **3 distinct situational replies to each of these same 30 intents**, not duplicate canonical records. **90 newly authored**, 90 accepted after preliminary normalized/lexical screening, 0 automatically rejected.

| Count | Before T169 | After T169 |
|---|---:|---:|
| Canonical intents processed | 30 | 30 |
| Registered replies (unchanged) | 270 | 270 |
| Staged replies | 90 | 180 |
| Total registered + staged candidates | 360 | **450** |
| Candidates per intent | 12/100 | **15/100** |
| Missing per intent | 88 | **85** |
| Missing across these 30 | 2640 | **2550** |
| Newly completed 100/100 sets | 0 | **0** |
| Still partial sets | 30 | **30** |

Concrete contexts include unknown installation/delivery costs, trade-offs in accuracy and safety, consent, independent evidence, portability of annotations and file attachments, maintainability, disabilities, offline conflict handling, fallbacks, vendor dependency and finite evaluation budgets. Each reply includes a stable T169 ID, explicit `context_note`, `avoid`, language/style, audience and direct/private/group-addressed context; it is read-only. The previous T166 texts and IDs have not been replaced.

## Integrity and release conditions

- Staged file, exact retrieved UTF-8 bytes: **159578 B**; SHA-256 `1122436ab249d7a3d3229704c165b65bb35f1ac059567dc2861b27b3e594df82`; Git blob `de70a2ac90c6efe7ee907b2810828e0d132b75a6`.
- In-process JavaScript checked 450/450 distinct normalized staged + registered-choice responses (NFKC, case, ё/е, Unicode punctuation and spacing) and T169 against prior staged replies with no token-Jaccard pair >=0.78. This does **not** prove full semantic originality across the entire library.
- Updated `scripts/test_choice_reasoning_t162.py` verifies registered source hash, stable IDs, 30×6 staged records, original 270 registered responses, privacy, audience, read-only restrictions, normalized exact duplicates against other registered QA packs, and lookup of registered questions. **Python execution and exact-head CI remain to be proven on this PR SHA**.
- `qa.v1` allows only 1 answer + 8 variants. Staged additions must not be registered until a separately tested backward-compatible context selector and consumer integration exists. Do not claim these replies are available to bots.
- No manually requested paid GitHub Actions; do not merge without actual exact-head PASS, current-main compatibility and subsequent post-main PASS.

## Next action

Continue incomplete choice intents from **15/100**, first checking real distinctions; also work on incomplete recovery (12/100) and boundary (12/100) intents in separate PRs. Avoid artificial text inflation. Verify the full Python CI and re-evaluate this branch against the latest main before any merge. Document exact PR head/checks separately.
