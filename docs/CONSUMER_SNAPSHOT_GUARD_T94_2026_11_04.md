# T94 — budget guard for ImPULS consumer snapshots (2026-11-04)

## Verified repository baseline

- Base `main`: `23871ed224cbe0d9636c841fd48e3f43bdd3ed1b`.
- Manifest: `2026.11.04.026`, 38 registered packs at base.
- Related, still separate Draft PRs: [#214](https://github.com/Treninem/Bot-Knowledge/pull/214) (three source-verified ImPULS feature-help entries) and [#219](https://github.com/Treninem/Bot-Knowledge/pull/219) (20 new moderation explanation intents).
- This PR changes **no** pack, manifest, knowledge version, workflow, ImPULS file, or consumer cache. New answers: **0**; new packs: **0**.

## Guard and purpose

Draft ImPULS #383 constrains a single knowledge snapshot to **8 MiB = 8,388,608 bytes**. A pack passing the existing 2 MiB per-pack check can still make the entire snapshot exceed that cap. `scripts/validate_pack.py` therefore now measures every registered pack's raw byte length **plus the manifest's raw bytes**, reports the remaining budget, and fails on a negative remainder. Counting the manifest deliberately leaves a conservative margin beyond a packs-only budget. The guard does not establish live consumer compatibility.

The existing JSON, SHA-256, private-data and per-pack checks are retained. No added files are registered as downloadable knowledge packs.

## Verification and next steps

- Isolated Linux fixture of the exact new pure Python budget function: **6/6 unit tests PASS**; Python syntax compilation PASS.
- Full repository validation on the user's Windows `D:`, ImPULS #383 combined consumer E2E, exact-head GitHub CI and post-main CI: **NOT RUN / UNVERIFIED**.
- No paid Actions or other paid service was initiated. Commit messages use `[skip ci]`; Draft remains **BLOCKED** until the owner's required gates are evidenced.

On a fresh local checkout (preserving raw file bytes), run:

```text
python -B scripts/test_consumer_snapshot_budget.py
python -B scripts/validate_pack.py
```

Then record the exact measured snapshot/remaining bytes, pack count, head SHA, consumer #383 result and CI status before considering merge. Reconcile with concurrent #214/#219 without modifying their data or versions. Never interpret local tests as live BotHost verification.
