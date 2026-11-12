# T47 — plain-language dialogue help (2026-11-03)

Base main `fcc82165d2e8c5b62308e26a1f72129034aeabaa` after T46. This update adds **24 canonical questions, 48 distinct search aliases and 72 original context-specific answers** (one principal and two alternatives per record). Stable IDs `dlg_t47_001`–`dlg_t47_024`.

Topics: clear nontechnical speech, not guessing unfinished statements, consent vs consideration, cautious certainty, sensitive quoted materials, private-to-public summaries, distinguishing proposed from decided actions, respecting user wording and tone, correcting content without inventing activity. All entries target `all_ai_bots`, require direct address, allow private or addressed group contexts, are read-only and synthetic. No rights, moderator actions or ImPULS implementation claims.

Baseline qa.v1 records 388 → 412. Exact normalized question/alias collisions vs all existing universal and ImPULS QA: 0; exact answer collisions: 0. Canonical question token Jaccard maximum 0.333 (pair dlg_t47_023 / dlg_listening_not_advice), lexical only; distinct contexts also reviewed. No personal chat histories.

Pack bytes 523392 (<2 MiB), SHA-256 `7f8073b6e51f3cfe94351c5067342dd82f8346a288d350705d0bbbd8d0bab120`. Manifest `2026.11.03.126`, SHA-256 `63c80483e7354d20a3587588b48e7da4da83eb821f92dd3ff9a218fdcd1e073b`. Existing SHA entries unchanged. Cache invalidation uses version + package SHA, no live cache mutation. Validate with `python scripts/validate_pack.py`, `python scripts/validate_qa_v1.py`, `python -m scripts.test_dialogue_help_t47`, exact-head quality CI and post-main CI. The QA set is not a 100/100 reply-catalog set; no BotHost delivery or consumer integration claimed.
