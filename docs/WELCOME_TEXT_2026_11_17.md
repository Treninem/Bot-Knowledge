# Welcome text and newcomer orientation — 17.11.2026

Base: `d43134b9072c7ceff44cfcf63d5d11c0d0771d7a`, manifest `2026.11.17.030`.
Source intent definitions: `packs/ru/intents.json`, Git blob `71be015a85471c22697f16f5dd3246d126be290c`, manifest SHA-256 `0bd5810de43f14e0c8cb454f71adbf11bf2e92e00477bf841bb66db477a7c39b`.

## Scope

The existing `greeting` reaction already has 100 entries, and the five T544 greeting/return/farewell/scope intents are each 100/100 in staging. The next uncovered general-language intent in `intents.json` is `welcome_text`; it is distinct from replying to a plain “привет”. A second existing intent, `newcomer_help`, covers orientation advice rather than drafting a welcome message.

This checkpoint adds **300 original Russian candidates**:

| Stable intent | Canonical question | New | Staged | Remaining |
|---|---|---:|---:|---:|
| `welcome_text` | Как написать приветственное сообщение новому участнику сообщества? | 100 | 100/100 | 0 |
| `newcomer_help` | Что новичку стоит сделать, чтобы спокойно освоиться в сообществе? | 100 | 100/100 | 0 |
| `respond_to_self_introduction` | Как ответить человеку, который впервые представился в группе? | 100 | 100/100 | 0 |

Each set has ten context families with ten individually written examples each. The third ID is a new candidate absent from the current intent registry; it remains staging-only until routing and consumer selection are designed. Contexts cover public and hobby communities, work teams, learning groups, temporary projects, quiet participation, orientation, joining an ongoing discussion, formal channels, privacy, roles/access, language accessibility, and conflict triage. Light humour appears only in the family explicitly requested by the caller. Every candidate carries language, style, audience, direct/group context, a specific context note, read-only status, and selection restrictions.

## Verification boundary

The pool is **staging only**: `consumer_registered=false`. The manifest, registered packs, SHA-256 values, search index, cache key, ImPULS, and live consumers are unchanged. The 300 candidates are not presented as deployed behaviour or as an enabled bot feature.

The exact-head workflow checks the source pack's real SHA-256 and Git blob, stable IDs, exact counts, 10×10 context-family coverage, style/audience/context constraints, privacy/sanctions boundaries, normalized exact duplicates against all registered packs and staged reply pools, and within-batch near-duplicate similarity. The repository-wide quality workflow remains an independent gate. Automated similarity checks do not prove complete semantic uniqueness; editorial review remains required.

## Next action

After exact-head and full quality CI pass, compare the two sets against any newer main/PR additions and review meaning-level overlap. Only then consider a separate registered-pack proposal with consumer compatibility checks. Do not update ImPULS or any live bot from this staging change.
