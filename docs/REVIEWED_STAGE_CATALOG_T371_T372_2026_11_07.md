# ReviewedStageCatalog — T371/T372 read-only index, 3,610 staged replies

This dependent maintenance PR covers the T371/T372 data prepared in [PR #412](https://github.com/Treninem/Bot-Knowledge/pull/412). It adds **zero** answers. Prerequisite: exact-head CI of #412 and actual successful post-main CI of its merge.

- Indexed staged corpus: **3,518 → 3,610** across the same **46** stable intent IDs.
- Overall group: **414 registered + 3,610 staged = 4,024/4,600**. Conversation 22 intents at 88/100; practical help 24 at 87/100. **576** missing; 46 partial; zero new 100/100.
- New code references only pinned, approved T371/T372 stage histories, recursively checks historical blobs and registered manifest SHA, detects duplicate normalized IDs and texts, and requires explicit trusted ID/intent/audience/context/address/permission on each selection.
- `cache_identity` incorporates the verified bytes of all eligible stage files; invalid or altered input fails closed. There is no automatic consumer routing, live cache update, external network access, sanctions or write action.
- Verify with `python scripts/validate_pack.py` and `python -m unittest scripts.test_reviewed_stage_catalog -q` on exact PR head. After merge run post-main CI against the actual merge SHA. No paid manual Actions.
- Registered packages, `manifest.json` version `2026.11.07.001`, and running consumers remain unchanged. Consumer integration is a separate permissioned task.
