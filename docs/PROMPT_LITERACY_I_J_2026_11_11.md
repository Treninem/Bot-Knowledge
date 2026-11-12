# Prompt literacy I–J — 11 November 2026

Continuation after merged [#646](https://github.com/Treninem/Bot-Knowledge/pull/646), whose exact head `a404027c8a65acb1e3eca6315f2dfed296ee01d3` had 39/39 successful checks. Its actual merge SHA is `3967f534a805d3546b790cd855f369714fa08611`; post-main CI was still running when the I–J branch was first prepared.

Ten existing stable `prompt20261111_*` intents had 80 **previous** replies each (800 total) in stages A–H. This continuation adds **200 new original synthetic, context-bound Russian assistant replies** in stage I (suffix 81–90) and stage J (suffix 91–100), ten per intent per stage. It changes no existing reply IDs or registered pack.

| Metric | At merged #646 | New in this PR | I–J total |
| --- | ---: | ---: | ---: |
| Unique staged replies | 800 | 200 | 1000 |
| Canonical questions | 10 | 0 new (10 continued) | 10 |
| Completed sets 100/100 | 0 | 10 | 10 |
| Partial sets | 10 at 80/100 | 0 remaining | 0 |
| Missing to target | 200 | -200 | 0 |

Provenance: stage I parent H Git blob `84c2f6f6f47500dfcaebd5e6fb182eaeeef624f3`; stage J parent I Git blob `c8f1971e0e6fe646b27930516c6944d8b2083a1b`. All stages are unregistered `consumer_registered=false`, read-only `all_ai_bots`, require a directly addressed request and matching context. The published manifest stays `2026.11.09.003`; original registered source `packs/ru/social_dialogues.json` SHA-256 remains `0cfedc133354a69522fecc3cda6bc21533c66005f0dc207050075f787dc977a8`. No new bot access, moderation sanction, automation or deployed capability implied.

Authoring-side comparison of **all 1000 replies**: exactly 1000 distinct IDs, normalized reply texts and normalized context notes; zero exact collisions; maximum pair token Jaccard `0.3636`, below screening threshold `0.8`. This lexical screen does **not** establish full semantic uniqueness. Review the editorial quality of responses, especially any meaning-level proximity to other packages, before declaring full production suitability.

Read-only test: `python -m unittest scripts.test_prompt_literacy_a_j_20261111 -v`. It checks actual registered source bytes and manifest SHA, Git blob parent chain A–J, all checkpoint counters, IDs, spelling-normalized uniqueness, context scope, privacy, forbidden sanctions and exact overlap with registered QA. GitHub workflow checks actual checkout commit SHA and uses `persist-credentials: false` and `contents: read` only.

**Release gate**: draft until real exact-head CI and #646 post-main CI both pass; then editorial and current-main compatibility review, guarded merge with expected head SHA, and actual post-main CI. No live ImPULS, BotHost, consumer cache, paid services or credentials touched. Next cycle: inspect unfilled intents outside prompt literacy, and verify whether any old blocked PR can be safely salvaged without losing unique data.
