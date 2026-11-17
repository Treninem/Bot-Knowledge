# H101 follow-up: semantic overlap corrections — 16 November 2026

On the already staged H100/H101 pair, editorial comparison found several cases where lexical uniqueness concealed nearly the same advice. This correction **rewrites 16 existing H101 candidates** with materially different situations, preserving their IDs, audience, restrictions, canonical intent and total counts. No new candidates are counted.

Distinctive changes include: a greeting addressed to another person versus a greeting addressed to the bot; quoted `привет` as a diagnostic example versus an actual greeting; scope of training disable across separate groups versus deletion; role revocation versus a switched-off feature; Stars purchase proof versus in-game Pulses; permission to pin versus permission to delete; restored training rights versus revival of old lessons; and post-hoc changes to giveaway rules versus verification of results.

Changed IDs:
- `impuls_help_greeting_h101_01`
- `impuls_help_greeting_h101_02`
- `impuls_help_training_disable_scope_h101_01`
- `impuls_help_return_previous_topic_h101_01`
- `impuls_help_setting_permission_change_h101_01`
- `impuls_help_pulses_vs_stars_h101_01`
- `impuls_help_other_chat_access_h101_01`
- `impuls_help_answer_limit_h101_01`
- `impuls_help_ironic_threat_h101_01`
- `impuls_help_one_turn_no_emoji_h101_01`
- `impuls_help_telegram_bot_rights_h101_01`
- `impuls_help_training_revocation_h101_01`
- `impuls_help_giveaway_terms_h101_01`
- `impuls_help_giveaway_check_h101_01`
- `impuls_help_no_public_training_logs_h101_01`
- `impuls_help_negated_prohibition_h101_01`

**Status:** Stage-only, no manifest or consumer integration. The original 50 H101 candidates remain 50; H100 remains 80. This correction requires a **new exact-head CI run** on the resulting commit. Semantic review across all H1–H101 and other PRs remains incomplete; do not mistake this focused edit for independent acceptance.

## Additional H99-versus-H101 meaning review

Compared the 22 intents newly covered by H101 with the immediately preceding H99 candidates. **11 more H101 replies** were rewritten to avoid counting a near-paraphrase as a new scenario. Examples now cover GitHub write-token separation, privilege to promote the bot, partial-response continuation, disabled group dialogue, local-memory deletion, readiness of an enabled game, fictional versus factual sources, exception to a general rule, and screenshot authenticity.

Rewritten IDs:
- `impuls_help_bot_publication_rights_h101_01`
- `impuls_help_purpose_h101_01`
- `impuls_help_group_admin_grants_bot_rights_h101_01`
- `impuls_help_feedback_h101_01`
- `impuls_help_reply_more_h101_01`
- `impuls_help_silent_group_h101_01`
- `impuls_help_privacy_h101_01`
- `impuls_help_game_help_h101_01`
- `impuls_help_ask_for_source_h101_01`
- `impuls_help_conflicting_chat_rules_h101_01`
- `impuls_help_evidence_context_h101_01`

Combined focused semantic rewrites in H101: **27**, no additional candidates claimed. Full corpus review and actual consumer routing remain outstanding.
