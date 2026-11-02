# Trusted qa.v1 publisher completion (isolated maintainer only)

`scripts/trusted_publish_qa.py` creates an append-only **Draft** PR and pins package and manifest digests. Its old `--merge-if-green` path checked asynchronous CI immediately, so it is deliberately disabled before opening any new PR. Draft creation is not a merge or ImPULS rollout.

`scripts/complete_trusted_qa_pr.py` is a **separate, manually invoked maintainer stage**; it does not run in BotHost or as a GitHub Actions job. Store `GITHUB_TOKEN` only in the isolated maintainer environment. Set `BK_TRUSTED_PUBLISHER=1` there and do not provide bot runtime tokens. Never put a write token in candidate JSON, a public report, a PR or consumer configuration.

After human review of the source and contents, record the current exact 40-character PR head SHA and run:

```sh
python scripts/complete_trusted_qa_pr.py --pr NUMBER --expected-head FULL_SHA --timeout 900 --post-timeout 900 --interval 15 --merge --ready --report trusted_qa_publish_report.json
```

Without `--merge` it is a non-mutating preflight (a draft still must be made ready separately). `--ready` allows the **trusted maintainer** to mark the reviewed Draft ready only after CI; it is not a substitute for a content review. All waits are bounded. A timeout/failed workflow leaves the PR open and reports `blocked`; it does not bypass checks or merge. A post-main failure after a confirmed merge returns a nonzero exit with `merged_post_main_unconfirmed`, preserving the real merge SHA. No caller may treat a pending report as published.

Guards: correct repository and PR marker; pinned exact head; unchanged main SHA during check; exactly two modified files (one already-registered qa.v1 package plus manifest); unchanged existing rows and catalog scope; one new source-backed record; version and SHA-256 of actual byte content; successful **both** `Trusted qa.v1 publisher exact-head` (explicit head checkout/assertion) and `Bot-Knowledge quality` workflows on the same PR head; ready and mergeable PR; guarded GitHub squash merge with expected head SHA; then `Bot-Knowledge quality` **push** run on the actual merge SHA. Branch protection remains authoritative. Report is local JSON with run links, head, version, package SHA, merge SHA and post-main status, never credentials.

For ImPULS export the compatible target is `packs/ru/impuls_help_qa.json` **once its separate registration PR has merged into main**. `reply_catalog.json` and `skills.json` are not qa.v1 and must not be passed as `--section-path`. No consumer integration or BotHost update occurs in this repository.
