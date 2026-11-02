# Owner authorization — 2026-11-02 (Bot-Knowledge only)

This records the owner's later, explicit instruction for the **maintainer automation**;
it supersedes older workflow notes that prohibited mass additions and independent
merges. It is not an instruction to bypass GitHub protections.

- Resume substantial, original, synthetic, privacy-screened response and language
  dataset expansion. Target up to **100 truly distinct context-appropriate answers**
  per canonical question; count previously accepted answers, avoid duplicates.
- Maximize validated useful output **within each actual run**. Do not stop at
  an arbitrary quota such as 20 replies or one question. Finish incomplete
  sets first, then continue additional questions within the same run.
- The trusted maintainer may update branches, resolve conflicts, mark draft
  PRs ready, merge **verified** PRs into Bot-Knowledge `main`, and close
  demonstrably complete or superseded PRs/issues with evidence and an explanation.
  Separate owner confirmation for each such Bot-Knowledge merge is not needed.
- Keep the safety gate: actual content QA, policy/PII inspection, reproducible
  SHA-256 and version/cache checks, real tests, checkout and test of the
  **current exact PR head SHA**, compatible current base, then post-main CI
  on the actual merged SHA. A previous green merge-ref alone does not qualify.
- Do not secretly discard useful changes in older PRs, force-push other workers'
  branches, bypass branch protection, use paid CI or leak secrets.
- No permission to modify `Treninem/Impuls`, deploy or update live bots,
  publish private Telegram messages or private ImPULS implementation, or
  issue sanctions via public language packs.
- No claim of a consumer rollout or learned capability without tested integration.
  The maintainer must report per-run actual additions, completed/partial
  coverage, commits/PRs, CI and any blocks honestly.

This owner approval applies to work conducted by the trusted maintainer
in **Treninem/Bot-Knowledge only**, not to arbitrary consumer or GitHub write
tokens distributed to bots.
