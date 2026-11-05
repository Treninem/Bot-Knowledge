# Reviewed RU/EN everyday topic replies

Version `2026.11.05.037` adds a narrow, explicit binding to the existing Russian `what_discuss/daily` group and one English `everyday_topics_en/daily` group in the same `reply_catalog.v1` format. Four Russian replies replace four older variants; four original English replies are new. The old Russian set still has 100 variants. Both bindings match explicit requests for an everyday topic and include negative cues for a stated wish to avoid that topic.

The ImPULS consumer must still receive a direct address and local permission. Sensitive contexts and requests for silence remain ineligible. The binding does not grant moderation or other actions. The English group is a separate language-scoped section; adding English replies to the Russian section would make language selection unreliable.

Local checks: `python -B scripts/validate_pack.py`, `python -B scripts/test_bound_everyday_replies.py`, and the existing reply catalog suite. The ImPULS adapter was also exercised locally with both packs: RU and EN requests returned the intended group; mismatched language, missing address, sensitive context and silence returned no candidates. This is not evidence of live BotHost delivery.
