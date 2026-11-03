# Context-quality universal QA batch — 2026-11-03 (.74)

Base main: `dcce85269fdb359775d4a5b8957959371a852103` (manifest .73). Existing universal QA: 75; added 36 distinct questions with 108 answer texts and 72 search aliases. Result: 111 universal qa.v1 records. This is **not** 36 new 100/100 reply-catalog sets; those remain unchanged. Existing ImPULS qa.v1: 537 records, unchanged.

Focus: non-assumed consent, uncertainty, incomplete sources and revisions, privacy, troubleshooting, confirmation of risky actions, contextual conversation repair, honest status and evidence. Synthetic original content; read-only, all_ai_bots, no sanctions, no user records, and no claimed product functions. Source contract: `AGENTS.md` at immutable base SHA above.

Pre-commit JS audit (NFKC-like lowercase, ё/е, punctuation and spaces): exact clashes against both qa.v1 catalogs or new texts: 0; question token Jaccard threshold 0.60: none blocked, closest existing in earlier sample was 0.333. SHA-256 of the new packs/ru/dialogue_help_qa.json: `aee214e6a9f7b7f5fdc5b8f64ab0123e93f7e403a68d93dcae31eb3c0378ecb6`. UTF-8 bytes: 145590 (under 1 MiB qa.v1 and 2 MiB consumer). Manifest version .74 includes the exact new pack hash. Test script checks all 108 exact/alias retrievals and declared scopes, in addition to earlier T7 checks.

Real exact-head CI and post-main CI remain mandatory for publication. A GitHub merge does not prove live consumer delivery. Next: new independent context-sensitive social cases after checking current main and prior PRs.
