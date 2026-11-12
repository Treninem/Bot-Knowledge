# Reviewed paraphrases for existing answers

Six new synthetic Russian question phrasings point to three existing `qa.v1` answers. They cover whether an appeal automatically changes a decision, whether a change of tone grants powers, and whether a bot's absence proves that no event occurred. The answers and audiences stay unchanged. The last case uses the universal absence-of-evidence answer, so general AI consumers can retrieve it without receiving moderation authority.

`scripts/test_qa_paraphrase_senses.py` checks normalized uniqueness across the two relevant QA packs and confirms that all six phrases rank their intended existing answer first for `all_ai_bots`. `scripts/validate_pack.py` checks the full manifest and SHA-256. These are local retrieval checks, not evidence that any live bot learned to interpret arbitrary paraphrases.
