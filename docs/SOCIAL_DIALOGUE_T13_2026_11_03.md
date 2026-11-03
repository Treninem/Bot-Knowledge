# Social dialogue T13 — synthetic conversation coverage

Stacked on QA T13 PR #123 head `3172589cd6aa043114c5280d1b482381806663d9`; the social package is unchanged from public main `6f1c7d256a287ef5d647c01a3947b5c2a42d9677` (557 cases). This PR updates only its own social pack, matching manifest, test and this report; once #123 merges, change the base to fresh main and recheck CI.

Accepted **42** new distinct inputs and independently written replies. Categories: {"congratulations":7,"support":7,"humor":7,"profanity":7,"conversation":7,"creative":7}. Rejected 0 exact/canonical-overlap inputs using normalized strings and token overlap threshold 0.65. Each row includes a concrete scenario, audience `all_ai_bots`, context, avoid-condition and a non-executable reply. Mild profanity is treated as contextual language, not sanction. Creative items are original fiction.

Pack size **408879 UTF-8 bytes** (<2,097,152), SHA-256 `41b4b7990f96c4d94e003fb30685a8064d78ef9b53c4135aab2a94e9af342975`; manifest/cache version `2026.11.03.86`. Total social cases **599**. Source policy: public `AGENTS.md`, `POLICY.md` and `docs/REQUIREMENTS_21.md` at `6f1c7d256a287ef5d647c01a3947b5c2a42d9677`. No real chats, names, identifiers, secrets or consumer privileges. `reply_catalog.json` unchanged; no claim of 100/100 sets.

Added 42 local retrieval assertions and scoped content checks; run `python scripts/validate_pack.py`, `python scripts/test_social_dialogue_t7.py`, full exact-head CI, then post-main CI. Actual user bots not modified.
