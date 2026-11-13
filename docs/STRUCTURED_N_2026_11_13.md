# Structured-information continuation N81–N82 — 13 November 2026

## Scope and actual new content

- Continue existing [PR #662](https://github.com/Treninem/Bot-Knowledge/pull/662), preserving its 60 stable canonical intent IDs and already staged answers. Latest previous source checkpoint was M80, commit `8d3b6c79a23b82358f52a12d5be6e9d7faa2922f`. Published baseline: main `6c9f430da47f137d39a72bbd28c057cfb8f6be96`.
- Two new separately authored contextual situations per intent, **120 newly saved synthetic Russian replies** (suffixes **81 and 82**) in `staging/ru/structured_information_20261113_delta_n.json`. Content IDs do not reuse previous suffixes. Applied only to an explicitly addressed question with a matching circumstance. All examples are read-only, general-audience, without personal data, sanctions, automatic consumer actions or claimed memory.
- Data commits: [N81](https://github.com/Treninem/Bot-Knowledge/commit/130af707447913fffa7ae3835732f7d0ace9c6d0) (+60), [N82](https://github.com/Treninem/Bot-Knowledge/commit/9ef26295eedf0234af7d40fd3a6579730bed11f9) (+60). Checkpoint metadata spelling corrected without increasing the count in [5e68913](https://github.com/Treninem/Bot-Knowledge/commit/5e68913b5ed86b4ee0b7638889be3b3ee589cc69).

## Exact accounting

| Source | Per intent | Total |
| --- | ---: | ---: |
| Published structured QA | 3 | 180 |
| Earlier staged A–J | 11 | 660 |
| Existing L | 31 | 1,860 |
| Existing M | 29 | 1,740 |
| **NEW N81–N82** | **2** | **120** |
| **Combined** | **76/100** | **4,560** |
| **Missing** | **24** | **1,440** |

**60 partial intents; zero newly completed 100/100.** Continue in this same PR at `<intent_id>_supp_83`. Preserve all earlier IDs and source counts. Cumulative replies *only in this PR* are L+M+N = **3,720**. The published and earlier A–J sets must not be mistaken for additions from this run.

## Preliminary validation and safety

- GitHub readback parsed the N JSON: 60 stable IDs, **120** N replies, sequential suffixes and matching context notes. All 120 reply texts and notes were authored for distinct concrete situations; 0 exact normalized collisions and 0 token-set Jaccard ≥0.70 against the published structured pack, L and M. Normalization covers case, whitespace, punctuation and е/ё. An exact normalized note comparison to L/M also found 0 matches; within-intent N notes maximum token-set Jaccard was **0.3333**.
- N JSON actual UTF-8 size: **155,746 bytes**. Git blob `eb2981d7a640505ef096ccc8f1b666f0dc0b19eb`. SHA-256 on the actual UTF-8 content: `1e641e80b9fe888d0fab8e5acb10995ea10b7b702b53909ac419eb5f62e3edbf`. The SHA-256 implementation passed the standard `abc` test vector. File remains below the 2 MiB planning limit.
- Added `scripts/test_structured_n_20261113.py`: source SHA-256/Git-blob and manifest integrity, N/L/M counts and IDs, safety metadata, normalized text/context uniqueness, privacy check, lexical proximity, note distance and file-size guard. The initial test escaping mistake was corrected in commit [749ac380](https://github.com/Treninem/Bot-Knowledge/commit/749ac3804cfcb93903d6bd60bf92512daa86f787).
- Added read-only `.github/workflows/structured-n-20261113.yml` for exact PR head checkout, source/pack validation, L/M/N tests (Python normal and N under `-O`), no secrets, no persistent checkout credentials. **No claim of Python or complete exact-head PASS until the actual GitHub run finishes.** Local Python checkout was unavailable because the local container could not resolve GitHub.
- These checks establish structural/lexical integrity only. Independent semantic, real consumer routing, cross-PR editorial scrutiny and 8 MiB snapshot-safe delivery remain necessary before merge.

## Publication and remaining gate

Current source `manifest.json` and registered pack SHA are unchanged; N is **unregistered staging**, not additional live bot capability. No edits to ImPULS, BotHost, working caches, protected GitHub settings, paid services or deployment.

Main remains `6c9f430da47f137d39a72bbd28c057cfb8f6be96` at this read. Existing #662 had diverged by 4 base commits; reconcile before merge without force-push. The last verified main snapshot budget leaves insufficient room for all pending candidate pools. Do not bypass it.

**Draft/BLOCKED:** Require real complete exact-head CI for the final PR head, independent cross-stage semantic/context review, demonstrated consumer size/selection compatibility, fresh-main reconciliation and actual post-main verification. A green run for an earlier head does not satisfy a later commit. No PR was merged or closed in this checkpoint.

**Next batch:** N83 and subsequent genuinely useful context-specific answers; update counters by delta, not by file size. Do not expand mechanically where a unique answer cannot be justified.
