# T373/T374 — 92 original contextual Russian answers (2026-11-07)

Parent main `c608dcf405cb7b5cbcf523c69f34d2a6ce6e9371` includes fully reviewed T371/T372 stage and its read-only index via PR #413. This batch independently authors **92 new** synthetic replies, not counting previously existing 4,024 replies.

| Family | Intents | Registered before | Staged before | New staged | After per intent | Missing |
|---|---:|---:|---:|---:|---:|---:|
| Colloquial meanings | 22 | 198 | 1738 | **44** | **90/100** | 220 |
| General practical help | 24 | 216 | 1872 | **48** | **89/100** | 264 |
| Total | **46** | **414** | **3610** | **92** | **4116/4600** | **484** |

All 46 sets remain partial, no new 100/100. Examples are contextual, original, non-personal, non-operational, and distinguish invitations from actions, hypothetical language, uncertainty, meaningful troubleshooting, scoped permissions, no blame, safe rollback, privacy and truthful status reporting. No content from chats, private IDs, secret tokens, purchased material or sanctions.

Data lineage: `packs/ru/colloquial_ru_pragmatics_qa.json` and `packs/ru/practical_recovery_qa.json` remain registered with SHA-256 from immutable manifest version `2026.11.07.001`. T373 immediate parent `staging/ru/colloquial_t371_context_pool.json` blob `557927d8d89f1b70f5f3da6e3705331b0df09925`; T374 parent `staging/ru/practical_t372_context_pool.json` blob `e2cf8f74219a330bbd1d0b09e6c123e084e7c212`.

Validator `scripts/context_t373_t374.py` recursively verifies source SHA, parent Git blob ancestry, normalized uniqueness of text/IDs/context notes, audience, address/context and opt-in selection, fail-closed read-only semantics. Test module `scripts/test_context_t373_t374.py` also checks tampered source/parent, selection permissions and Jaccard threshold 0.78 against historical stage replies; this is **not proof of zero semantic overlap**.

Verification commands: `python scripts/validate_pack.py`, `python -m unittest scripts.test_context_t373_t374 -q`, `python -m scripts.context_t373_t374`; require current exact PR head checkout, all green CI, actual post-main CI. No paid manual GitHub Actions.

Six files in PR: two staged datasets, validator, test, workflow, this note. Registered `manifest.json`, original packages, running caches and consumers unchanged. No ImPULS/AuroraFox source, deploy, automatic learning, automatic enforcement, external action or GitHub write token in bot. The `ReviewedStageCatalog` still indexes 3,610 staged answers through T371/T372; updating it and consumer integration require independent gated checks.
