# T172 — further context-labeled practical choices (2026-11-05)

Base main `72880e43924c3cf8d5cffa5ab3cab0269a1059de` (after verified T170 merge, while T171 changes a separate pool). Registered `packs/ru/choice_reasoning_qa.json`: source Git blob `ae0963f5e4962ad6442678003861bea5a373eb9e`, actual manifest SHA-256 `6120bed161faf0d13e9b86582729cf8c13ace8b7927c5d77e3da6e8a16be8611`. This PR does NOT edit the registered source, manifest, knowledge_version or consumer cache.

Exactly **90 NEW** original synthetic RU replies in **30 EXISTING canonical choice intents** (three additional distinct, conditional scenarios per intent). The stage prior to T172 had 270 registered +180 staged =450 candidate replies at 15/100 each. T172 makes 270 registered +270 staged =**540** candidates, **18/100 per intent**, **30 partial**, **0 new 100/100**; **82 missing per intent**, **2460 remaining total**. Original T166/T169 content, IDs, audience constraints and context retained unchanged.

Themes: choice criteria and long-term support, unknown costs and denominators, reliable backups and evidence, precision vs speed where safety matters, reversibility, accessibility, time saved across teams, warranty conditions, offline conflict handling and an explicit no-fit option. Per-entry metadata: `context_note`, `avoid`, stable `_t172_` ID, `context=direct/private/group_addressed`, `audiences=[all_ai_bots]`, `read_only=true`, `language=ru`, `style=neutral`. All conditional, never arbitrary replacements for one chat context.

Staged file `staging/ru/choice_t166_context_pool.json`, exact UTF-8 byte length **239260**, SHA-256 **`744ce0a5b58b6dc4f60ae50be1df0af69d0c4ad79ba4f45837d1b5ae40ef7a87`**, Git blob **`46cdfedb83d701b84ff263575daf2a4ab76a7afa`**.

In-process JavaScript preliminary screen: all 270 staged replies unique after NFKC, case, ё/е, punctuation and whitespace; 90 new vs earlier stage yield **0 normalized exact** and **0 token-Jaccard >=0.78**; largest token-Jaccard **0.2942**. Manual contextual review is necessary: lexical screening is not semantic proof. Updated `scripts/test_choice_reasoning_t162.py` checks 30×9 staged records, IDs of T166/T169/T172, registered 270, original source hashes, staging isolation, privacy, scope, and exact cross-pack duplicates. **Run real Python exact-head CI before merge**, then post-main CI on true merge SHA. No manual paid Actions dispatch.

This is **unregistered staging**, not active bot answers: `qa.v1` limits a record to 1+8 answer variants; consumer selector/consumer-side tests are separately required. No modifications to ImPULS, live BotHost or other projects.

Next: continue genuinely new choice contexts from **18/100** or work on independently incomplete recovery/boundary topics; avoid mechanical 100 quota filling.
