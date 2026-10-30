# RU/EN quote-safe style boundaries — 2026.10.30.17

This fixes a real safety issue: legacy preference matchers used to strip punctuation before lookup, so an approved style instruction enclosed in quotation marks could be mistaken for direct consent when the consumer forgot quoted=true.

## Correct behavior

The legacy and scoped handlers compare a punctuation-preserving normalized surface. They tolerate case differences, ordinary whitespace changes and ё/е, but refuse extra quotation marks, Markdown or code wrappers, question punctuation replacing an assertion, invisible controls and non-text input. Existing approved internal quotation marks (such as «ты») remain valid. The compositional matcher already has its own character guards.

The new package contains 48 original negative examples (24 RU and 24 EN), with three examples in each of eight categories: reported speech, hypothetical speech, negated instructions, quoted documents, meta-discussion, indirect preferences, instructional examples and mixed intentions. These are in adversarial_cases, never the searchable approved command index. They cannot authorize actions.

## Verification

Run python scripts/validate_pack.py and python scripts/test_style_boundaries.py. The test exercises all three matchers, 160 existing approved positive samples, 1600 injected quote/punctuation wrappers, malformed input and ten rounds over the 48 new examples. SHA-256 and negative-data uniqueness are checked.

## Consumer boundary

The caller must independently supply reliable addressed and quoted flags and isolate each chat session. A direct sentence and an identically worded sentence whose quotation marks were already removed cannot be distinguished by a local exact matcher. No moderation powers, GitHub write tokens or data exchange between chats are introduced. Integration into live ImPULS/AuroraFox is not implied by this package.
