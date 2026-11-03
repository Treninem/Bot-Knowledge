# qa.v1 normalized duplicate question and alias protection — 2026-11-03

Scope: code-only guard, no change to JSON packs or public manifest. Base commit `be60513082f0de17dc6d86e882bc4d86300b6621`, manifest remains 2026.11.03.80 with unchanged checksums/cache. Previously qa.v1 enforced unique record IDs, but different IDs could repeat the same question or alias with case, whitespace, punctuation, ё/е and cosmetic emoji changes.

`scripts/validate_qa_v1.py` now normalizes questions and aliases **within each pack** using NFKC, casefold, ё→е and non-alphanumeric separator removal. It rejects duplicate normalized queries as `duplicate_normalized_question_or_alias`; it does not remove legitimate cross-pack audience distinctions or pretend to detect all semantic paraphrases. No new dependencies or network actions.

`scripts/test_dialogue_help_expansion.py` adds two negative tests: a modified alias matching another record after normalization and a duplicate within the same record. It also validates the current 222-question universal pack and ё/е+emoji folding. Existing q.v1 manifest validation continues to cover 537 ImPULS QA records. Validate with the GitHub quality exact-head workflow; verify main post-merge separately. No consumer deployment.
