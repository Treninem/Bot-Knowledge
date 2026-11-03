# T64 — English situational dialogue and meanings (2026-11-03)

Stacked on T63 PR #186 exact head `21b66c9cecb13367bfda1c45cf8c4f83137af7e7`; the T63 branch will be merged using a merge commit, after which this PR can be checked against the new main.

Original English cases: **58**, one unique answer for each distinct English utterance; baseline 814 → proposed 872. Categories: {"conversation":10,"support":8,"slang":7,"sarcasm":7,"context":8,"rules":5,"deception":5,"creative":8}. Rejected candidates: 1. This is not a new 100/100 reply-catalog group. No raw chats, user data, sanctions, product-specific features or proprietary text.

Pack version 2026.11.03.150. Pack SHA-256 `6950a9974c3b49ae59848fcbf0380e7489a2d7a9fb7e33535dbb915fc5a56c14`; manifest SHA-256 `159e38c6f3ac68c7f101826d2295ce2060b6bf58e9937e1f5a4db027a82e2828`; UTF-8 pack bytes 467454. Sources are newly authored synthetic utterances; language notes and explicit avoid constraints distinguish sarcasm, idioms, group policies and quoted instructions. All consumers are `all_ai_bots`, with local rules taking precedence.

Tests: `python -m scripts.test_english_dialogue_t64`, `python scripts/validate_pack.py`, `python scripts/validate_qa_v1.py`, real complete exact-head CI and post-main CI. No live bot deployment is part of this change.
