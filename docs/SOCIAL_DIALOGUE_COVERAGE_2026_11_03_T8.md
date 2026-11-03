# Social contextual replies — 2026-11-03 (.75)

Exact source main: `1993070317a0b33b63fd6f2011a284b58ad60615` (manifest .74). Baseline: 377 social cases. This PR adds 36 original, explicitly contextual, synthetic cases across congratulations, support, humor, profanity, conversation and creative stories. Final: 413; no changes to the canonical 100/100 reply_catalog counts.

Contexts identify opt-in humor, directness and boundaries; no sanctions, real private chats, IDs, borrowed jokes, real identities or unverifiable consumer functions. All audiences: `all_ai_bots`. Counts by kind: {"congratulations":6,"support":6,"humor":6,"profanity":6,"conversation":6,"creative":6}.

Pre-commit normalized exact input/response collisions vs existing cases: 0. Question-like input token-set similarity threshold 0.58: no rejections; largest observed Jaccard 0.500. UTF-8 pack bytes 281339, under the 2 MiB contract. SHA-256: `5e571b44a3b5c3c73ddb313c4a9a2e31558122a896918f5caab71fe36cc1ae61`. QA regression tests find every new scene via the local verified search and keep the previous T7 test intact. Full validation and exact-head CI must run on the actual PR head, post-main on actual merge commit.

This is a public library expansion only, not a BotHost deployment or live consumer proof.
