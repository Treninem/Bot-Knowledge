# T78 English pragmatic QA (2026-11-04)

Base: reviewed T77 branch commit `9b497f40d6fa82fc8b17cc3f93bbfbb931e58959` (stacked until #201 merges), retaining every earlier change. New English-only qa.v1 topic is manifest-discovered without modifying the existing `english_dialogues.json` consumer contract. 32 original English questions, 64 natural alternative search formulations, and 96 varied contextual responses. The questions distinguish idioms, implied meanings, cautious certainty, negation, stop requests, privacy, sarcasm, quoted language, and respectful criticism. No borrowed literary quotations, private messages, or consumer commands.

Pack `packs/ru/english_pragmatics_qa.json` SHA-256: `90994aef380b39b264f1362df0edbad94c971d6cf5c2b976fb1c312621662007`; pack_version `2026.11.04.011`; manifest version `2026.11.04.011`. Read-only, `all_ai_bots`, English-only, direct address required. These are QA examples with three contextual responses each, not completed 100/100 reply-catalogue collections. All earlier greeting/reply sets remain unchanged.

`scripts/test_english_pragmatics_t78.py` validates real UTF-8 digest, schema, 32 unique intents, 96 distinct answer texts, normalized QA cross-pack duplicates, constraints and local index lookup. `.github/workflows/english-t78.yml` checks exact PR head with read-only access; full quality workflow is also required. PR must be retargeted to current `main` after T77 merges; verify exact head/base and post-main on real merge SHA. The stacked PR is not ready for merge until that happens.

No ImPULS modifications, deployment, live cache or GitHub write tokens were involved.
