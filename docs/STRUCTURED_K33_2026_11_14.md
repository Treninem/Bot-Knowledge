# Structured K33 · 14 ноября 2026

Continuation of [Draft PR #661](https://github.com/Treninem/Bot-Knowledge/pull/661), original main `6c9f430da47f137d39a72bbd28c057cfb8f6be96`, parent K32 checkpoint `d70c1db5c1b3e9b92fe457cfafc0c959beb9f6fb`.

Prepared **44** original, contextual, synthetic Russian explanations for the 44 previously partial structured-information intents. All 44 passed initial lexical preflight, but a wider review found **two clear semantic duplicates**, so those are **excluded** from the staged dataset:

- `struct_t93_015_supp_104` repeated `struct_t93_015_supp_38`: translating a Celsius temperature *difference* into Fahrenheit
- `struct_t90_018_supp_104` repeated `struct_t90_018_supp_98`: positive and negative components of stacked bars

**42 new staged candidates remain**, one per other intent. All candidates are pending independent editorial review. Raw coverage: 10 candidate-complete 100/100 sets, 42 at 98/100, 2 at 97/100, 90 raw missing slots. Total K staging = 4,662 raw candidates. Five older K31 entries have also been rejected as semantic duplicates: 4,657 is only an upper bound for potentially eligible raw staging, **not an editorially certified count**. After subtracting the five K31 rejects, only 7 sets still have 100 potentially eligible numeric slots. Editorially approved sets: **0/54**.

A reproducible K33 Python test compares the new 42 to **all 32 prior K-stage JSON files**, along with the published structured QA pack, checking normalized exact duplicates and lexical token-Jaccard threshold 0.70. Context trigrams are checked within the same intent at 0.60. Even with this wider scan, conceptually equivalent situations may remain. Semantic, cross-PR, selection and consumer integration QA remain blocked. No original user messages, private chat history or sanctions are included.

All K material remains `consumer_registered=false`; original pack and manifest hashes, 8 MiB consumer snapshot, ImPULS, BotHost and working caches are unchanged. Any merge requires exact-head CI, independent review and consumer compatibility; do not import this entire staging dataset into the registered snapshot.

Next: independently compare the remaining 42 against neighboring PR #662/#663/#664, remove further semantic overlap, then finish the remaining genuinely distinct partial intents. Avoid cosmetic quota filling.
