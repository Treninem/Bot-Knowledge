# K5 — opt-in context selector for staged Bot-Knowledge QA (2026-11-05)

## Scope and non-goals

`scripts/staged_context_selector.py` is a **standalone, opt-in, fail-closed reference selector** for the three `supplemental_contextual_reply_pool` staging files for choice, recovery and boundaries. It DOES NOT register additional `qa.v1` variants, change `manifest.json`, modify caches, push data into any bot, analyze private messages, make moderation decisions, learn autonomously, or grant permissions. It does not support the separate 3000-reply dialogue stage (different staging shape), which remains unchanged.

This selector unblocks *testing* the larger than 9 response inventory per canonical intent without cloning questions, while keeping the release/consumer boundary explicit. The published `qa.v1` record limit 1 canonical answer + 8 variants is unchanged.

## Required safe calling protocol

A trusted downstream consumer must itself establish all the following **before calling select**: (a) the exact canonical intent, (b) real addressed message and local permission, (c) direct/private/group-addressed channel, (d) allowed consumer audience, (e) which specific reply IDs have context notes **confirmed by actual authorized context**, (f) any recent reply IDs it already remembers in an isolated session. Do NOT construct approved_reply_ids by blindly matching words or accepting IDs sent in a Telegram message; do not infer permissions from quoted role claims. With missing approval/context the method abstains.

```python
from pathlib import Path
from scripts.staged_context_selector import StagedContextSelector

selector = StagedContextSelector(
    Path("/path/to/verified/checkout"),
    "staging/ru/choice_t166_context_pool.json",
)
# Only after independent trusted consumer-side verification that this exact
# context_note applies and message addressing/local permission are confirmed.
selection = selector.select(
    "bk_choice_missing_criteria",
    approved_reply_ids=frozenset({"bk_choice_missing_criteria_t166_01"}),
    audience="all_ai_bots",
    context="direct",
    addressed=True,
    local_permission=True,
    recent_ids=(),
)
# selection may be None. The caller remains responsible for final policy review.
```

The returned dataclass has the reply ID, text, intent, source path and context note, never an executable action. If a candidate has been used in a recent list supplied by the caller, the selector skips it; selector retains no per-user state.

## Integrity contract

Only three exact allowlisted stage paths can load. Each stage must be marked `consumer_registered=false`, `read_only=true`, `requires_direct_address=true`, `no_personal_data=true`, `audiences=[all_ai_bots]`. Every entry's canonical ID and question must match its registered QA source. The source pack must be in the current manifest and its **raw SHA-256** match both manifest and stage header; Git blob SHA-1 is independently checked. It rejects duplicate IDs, normalized duplicate candidate text, missing `context_note` / `avoid`, inconsistent checkpoint totals, invalid address scopes, explicit secret/email-like text patterns and unknown paths.

`scripts/test_staged_context_selector.py` exercises actual 3-pack snapshot, scoped positive selection, default refusals, local permissions, audience/channel separation, repeat suppression, stage path allowlist, tampered stage and source content. The existing `.github/workflows/quality.yml` adds a single Python unittest step under **existing read-only, exact-head checked job**, with no additional secrets, permissions or workflow triggers.

## Release gate

Even successful CI does **not** prove semantic quality of every staged reply or consumer integration. Require independent contextual review, actual consumer testing, validated safe routing, explicit user approval for production deployment and exact-head/post-main GitHub checks before claiming any live capability. This task makes no ImPULS/production changes.

Files: Python opt-in helper, Python unittest, documentation and a single added quality job step. No JSON/manifest package changes. `knowledge_version=2026.11.05.036` and 41 existing package SHA remain intact.


## T251: отдельный набор разговорной прагматики

Добавлен четвёртый явно разрешённый staging-путь `staging/ru/spoken_pragmatics_t251_context_pool.json` для 24 проверенных канонических разговорных намерений. Он закрепляет SHA-256 и Git blob SHA зарегистрированного `spoken_pragmatics_qa.json`, но не включён в `manifest.json` и не доставляется потребителям. Вызов `StagedContextSelector` требует точного одобренного reply ID, подтверждённого контекста, адресации, разрешения, аудитории и подавления недавних повторов. Исходные три пула и их проверки не изменены. См. `docs/SPOKEN_PRAGMATICS_T251_2026_11_06.md`.
