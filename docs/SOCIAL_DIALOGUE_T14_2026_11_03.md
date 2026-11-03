# T14: natural turns and social boundaries

Parent PR [#126](https://github.com/Treninem/Bot-Knowledge/pull/126) head `ad32aa1ceebdf89f7f669746eeb2900ef24ab08b` (proposed manifest `2026.11.03.88`). This PR is independently reviewable but must be rebased against its merged main before merging. It does **not** modify ImPULS.

- Existing social cases: 599; accepted new 30, proposed total 629. Genres: {"conversation":14,"support":8,"profanity":4,"humor":4}.
- All examples are original synthetic text without identities or chat logs. Context and explicit avoidance flags prevent jokes in serious help, personal attacks, accidental sanction claims and fake knowledge of BotHost.
- Exact normalized input/response collisions: 0; highest new-to-existing/new input token-Jaccard: 0.429. Editorial checks preserve context differences; this automatic measure is not proof of every semantic distinction.
- Package size 427872 bytes (<2 MiB), sha256 `de9a98ae31360db4bc907aee8ea403cbaf64bc4f52db6a49ef3a6659691906ef`; manifest proposal `2026.11.03.89`, sha256 `f93398018be0bb644e8d29ee51a506820b477b0b5312e22308a97bb65fc5e02d`.
- New completed 100/100 reply-catalog sets: 0. Existing `reply_catalog.json` untouched. Test `python -m scripts.test_social_dialogue_t14` plus `scripts/validate_pack.py` and GitHub exact-head/post-main gates.
