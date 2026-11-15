# ImPULS H90 — 57 contextual Russian candidate replies (15 November 2026)

Continues [Draft PR #666](https://github.com/Treninem/Bot-Knowledge/pull/666) from exact head `e42344697b8779351d0a5ee14b0a66d81f32fb34`. Published Bot-Knowledge `main`: `6c9f430da47f137d39a72bbd28c057cfb8f6be96`. Read-only ImPULS `main`: `54b8a3a813fec82c1f953408942ba327eb181c37`, `README.md`: candidate 1.6.263, installed 1.6.262; live AI quality not accepted.

## Delta
- **57 new synthetic reply candidates** for **51 distinct existing intents**, including four additional context-dependent greeting answers, two feedback, two follow-up, and two onboarding cases.
- Coverage: greeting without unsolicited chat rules, addressing, missing context, private/group isolation, error reports, conflicting rules, game availability, roles, learning boundaries, privacy and uncertainty.
- Every record is scoped to `impuls`, Russian, direct-address requirement, declared delivery context and read-only/no-sanction behavior. Contexts intentionally differ; these are *not independently editorially accepted*.
- H1–H89: 3,465 previous candidates. H90 adds 57: **3,522 staged**; these 100 tracked intents have 275 published source answers, 6,203 numerical gaps. All 100 remain partial; certified complete 100/100: 0; newly approved/registered: 0.
- Manifest, registered source package, working consumer cache and private ImPULS were not modified.

## Tests and publication gates
Run `python -B scripts/test_impuls_help_h90_20261115.py`, repeat under `python -O -B`, and `python -B scripts/validate_pack.py`. The read-only PR workflow checks out the actual head without credentials and computes raw JSON SHA-256.

The H90 test reconstructs H1–H90 counts, checks stable IDs, normalized exact repetition against published and staged material, conservative lexical overlap, privacy constraints, and no-authority conditions. A passing lexical test cannot establish semantic originality.

**DRAFT/BLOCKED for publication:** independent semantic editing against parallel PRs #662–#665; end-to-end consumer routing and permissions; selected manifest SHA/cache registration and 8 MiB snapshot fit. Never claim these drafts are delivered skills. Confirm exact-head and post-main CI before release. No paid Actions, protection bypass or deployment.

Next: review candidate meanings and develop a small genuinely publishable subset instead of claiming the staged pool is active.
