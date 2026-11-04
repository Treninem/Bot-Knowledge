# T72 — 28 universal, context-precise questions
Baseline main: `a1b37293dc3546e71864e32427476c3d3de6ab34` after T71, 721 universal qa.v1 records.
T72 adds **28 distinct canonical questions** with exactly **3 useful,
context-dependent replies each (84 new answer variants)** and 56 new
search aliases. The existing 721 records are retained.
Domains: document revisions, inaccessible data, audio uncertainty,
structured data, screenshots, languages, schedules, accessibility,
file/account scope, finance status, privacy, percentages and software limits.
Each record is read-only, directed to `all_ai_bots`, and grounded in the
public `docs/REQUIREMENTS_21.md` at pinned commit
`fbf842da77b5e002bab7942821f33527a4638417`.
No ImPULS-specific feature claims, bot execution, sanctions or personal chat content.
Exact and normalized incoming-phrase checks: 0 duplicates before commit.
Answer texts also checked against the baseline and within each new record.
New total: **749 records**, not 749 newly authored; old 119/100/100
`reply_catalog` intents are unchanged. None of the T72 QA questions
should be declared complete 100/100 sets: each has exactly 3 responses.

Pack size **971644 UTF-8 bytes** (<1 MiB qa.v1 cap).
SHA-256 **51e9d96f9892202cdeb0284a034becd4295767822644b8eba763046b4cb58012**. Manifest/cache version **2026.11.04.006**.
Tests: `scripts/validate_pack.py`, `scripts/validate_qa_v1.py`,
`python -m scripts.test_dialogue_help_t72`, existing regression suite,
exact-head six CI then post-main CI. Consumer integration and BotHost deployment
were not performed. Stop/repair if any test or privacy gate fails.
