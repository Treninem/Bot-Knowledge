# Reasoning risks: contextual RU replies — 11 November 2026

New independent review-only series on the exact Bot-Knowledge main `d3248d3279c3ca272b76ed2b89621c2577b20f6f`. Ten original stable canonical intents, each with 10 distinct replies: **100 new candidates**, **10 partial sets at 10/100**, **90 missing per intent / 900 total**, **zero sets at 100/100**. No pre-existing replies are counted as new.

Subjects: causal inference, small samples, comparable tests, competing explanations, forecasts, randomness, measurement definitions, falsification, conflicting reports and honest qualified conclusions. All 100 cases are synthetic and explicitly scoped by situation. Answers are not universal, and no statement permits action, sanctions, data access or authority. `consumer_registered=false` and `all_ai_bots`; ImPULS untouched.

Source reference: `packs/ru/social_dialogues.json`, manifest SHA-256 `0cfedc133354a69522fecc3cda6bc21533c66005f0dc207050075f787dc977a8`, blob `d56ff304da7165bd63c328f3220a1f6d3d26e3ab`. Source and registered manifest are unchanged; no consumer cache/key changes. Main snapshot used: `d3248d3279c3ca272b76ed2b89621c2577b20f6f`.

Pre-publication pure-JS authoring check: 100 unique IDs, normalized reply texts and context notes; max intra-batch token-Jaccard 0.2273, below 0.8. Semantic and cross-PR editorial uniqueness still require review. Run `python -m unittest scripts.test_reasoning_risks_20261111 -v` on the actual checkout. Workflow must use read-only permissions and verify exact PR head checkout.

Next: complete existing ten intents starting suffix **11**, add multiple context-specific batches, check exact-head CI, current main, and post-main CI before any merge. No actual consumer integration is claimed.
