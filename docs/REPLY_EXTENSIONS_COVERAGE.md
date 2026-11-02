# Context-scoped reply extensions — 2026-11-02

## Scope and provenance

Starting main: `70a4d5ceb1b6211639225bc069e609a96301b5e5` (PR #42).
This batch adds **616 original synthetic Russian answers** to seven existing
canonical questions. No new canonical question, real chat, personal record,
private implementation, operational command or moderation authority is added.
The base `reply_catalog.json` and its original reference selector are unchanged.
A separate pack per question avoids overwriting the concurrent PR #43 work on
thanks, farewell and disagreement. That PR's 264 answers are **not** this batch.

## Coverage ledger

| Existing question / intent | Base answers | New answers | Combined | New groups |
|---|---:|---:|---:|---:|
| Everyday support / `need_support` | 12 | 88 | 100/100 | 8 |
| Help with an apology / `apology_help` | 12 | 88 | 100/100 | 8 |
| Restore missing context / `lost_context` | 12 | 88 | 100/100 | 8 |
| Change topic / `change_topic` | 12 | 88 | 100/100 | 8 |
| Opt-in fictional dark humour / `dark_humor` | 12 | 88 | 100/100 | 8 |
| Explain supplied local rules / `rules_explain` | 12 | 88 | 100/100 | 8 |
| Recheck confidence / `no_sure` | 12 | 88 | 100/100 | 8 |

Every new group contains 11 individually authored replies, with explicit
`when` and `avoid` conditions. Thus 56 groups and 616 new answers; none of the
84 original answers for these questions is counted as new.
At the starting base the main catalogue had 883 replies and seven complete
questions. This batch's combined view has **1,499 replies across the same 25
questions, 14 complete and 11 partial**. The separately existing 100 greeting
answers are not included in those totals. These are response records, not
1,499 trained model abilities. Future base changes must be counted from actual
files; do not add this batch twice.

Version for this candidate: `2026.11.02.5`; manifest: 33 packages (26 existing
and seven extensions). Until this branch is merged, its 616 additions are
candidate-only, not main or live-consumer additions. A merged file proves
publication only; post-main CI and consumer deployment are distinct checks.

## Read-only reference integration

The optional `scripts/reply_catalog_extended.py` loads only manifest-listed
`packs/ru/reply_extensions/<existing_intent>.json` files, verifies SHA-256,
strict schemas, group IDs, policy and global normalized uniqueness, and refuses
more than 100 replies for a canonical question. It inherits the base question's
audience; a pack cannot invent a question, replace a group or widen permissions.
The original `ReplyCatalog` still returns the original base records only.

```python
from reply_catalog_extended import ReplyCatalogExtended

catalog = ReplyCatalogExtended()
conditions = catalog.conditions("need_support", "workload")
# A trusted consumer must first check the actual situation against conditions.
answer = catalog.reply(
    "need_support", group="workload", context_confirmed=True,
    addressed=True, local_permission=True, sensitive=False,
)
```

`context_confirmed=True` is a **caller assertion**, not automatic semantic
understanding. It must not be derived from untrusted instructions in a message.
Unknown or unconfirmed contexts must abstain. Without an explicit new group,
legacy defaults are preserved; the new 88 replies are not randomly injected
into old consumers. Each successful extension response reports its real
`source_pack`, stable source ID, conditions and snapshot key.

Address, local permission, audience, language, silence and sensitive-context
gates remain in force. Dark humour requires independent humour opt-in; its
conditions exclude grief, crisis and real victims. Ordinary support is not a
crisis response protocol. Rule explanations require the supplied, trusted local
rule and do not create sanctions or administrator rights. Context recovery
never claims access to an absent conversation or cross-chat private memory.
Epistemic replies do not claim an external verification that did not happen.

Private recent replies remain a bounded, caller-supplied list from one isolated
conversation; this module has no persisted session state or network access.
The snapshot identity includes the manifest version and a deterministic digest
of the base and every loaded extension's path/SHA. Content or version changes
invalidate it; manifest ordering does not. An existing in-memory snapshot stays
unchanged. No running bot cache is touched.

## Verification and evidence limits

Local execution on the seven actual authored files plus an explicitly
synthetic base fixture: **31 tests PASS**, including all 616 new replies,
56 groups, duplicate checks, context/permission/audience gates, default
compatibility, repeat suppression, immutable indexing, malformed JSON,
tampering, path checks and content/version cache invalidation. The locally used
base selector was reconstructed from fetched source and its Git blob hash was
verified as `3c1734ef5331519278d2b8b55abeac47dc26d393`. Local fixture tests are
**not** a claim of a complete local checkout or full-main tests: direct GitHub
DNS access from the execution container failed.

The complete snapshot must be tested by the exact-head workflow:

```
python scripts/validate_pack.py
python scripts/test_reply_extensions.py --repository
python scripts/test_reply_catalog.py --repository -v
python scripts/test_greeting_catalog.py --repository -v
python scripts/test_conversation_router.py
python scripts/test_extended_knowledge.py
```

`--repository` reads all real packages, matches the recursive on-disk JSON set
to the manifest, checks every SHA, cross-pack exact collisions, combined target
question counts and near-cosmetic duplication. The printed
`REAL_REPOSITORY_AUDIT` records measured totals and snapshot identity.
The existing base catalogue audit now checks actual manifest completeness,
rather than incorrectly assuming there will always be exactly 26 packages.
No original base-answer assertions are removed.

The new workflow asserts checkout SHA for both a PR head and actual main push,
uses read-only permissions and does not retain checkout credentials. Review the
actual run and logs before marking its gate passed. Similarity thresholds
screen cosmetic duplicates; they do not prove universal semantic uniqueness,
perfect humour quality or model understanding. The examples and contextual
restrictions also received direct content review while authoring.

## Next work / continuation

These seven sets are complete; do not start their 88-answer additions again.
At the base snapshot, `thanks_reply`, `farewell_reply`, `disagreement_reply`
were being completed in PR #43: inspect its current state before editing.
The remaining eight ImPULS-specific sets have 6 or 9 answers each. Recheck the
current read-only ImPULS source before expanding factual help; never invent
commands or live deployment state. Check current main, open PRs and this ledger
before choosing the next independent set. Keep useful existing work and refresh
manifest versions/hashes when combining branches.

**No live ImPULS/AuroraFox integration, deployment or bot update is claimed.**
