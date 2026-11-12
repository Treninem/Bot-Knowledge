# T196 — repair pre-existing staging source pointer (no new answers)

2026-11-06, base main `ba898f907be800cf0fe18f44e2ab4e3fa111c12f`.

The existing main workflow `Bot-Knowledge quality` failed on GitHub Actions run `42152303231`, and T195 Draft PR #284 exact-head run `42155586568` reproduced it. Failure: `scripts.test_staged_dialogue_t126.test_source_blob_and_manifest_unchanged`, expected `998420f9640bd24de58295aca7d2cfb4c192356e`, actual current `5ec9e134e0b70fc839eda6b23561f6c9808b8f16`.

The registered source `packs/ru/dialogue_help_qa.json` changed after the staging metadata was pinned. Connected GitHub content comparison of both exact blobs found **790 source records in each, identical IDs, answers, variants, and questions**. Only the `aliases` fields of **three unrelated records** differ: `dlg_t10_negative_no_event`, `dlg_t10_appeal_not_outcome`, `dlg_t56_024`. No record was added or removed. The staged 30 canonical intent IDs/questions and registered counts still match the current source.

Patch: update only the **source Git blob SHA** inside `staging/ru/dialogue_t125_context_pool.json` to `5ec9e134e0b70fc839eda6b23561f6c9808b8f16`. It does not add or rewrite a response, publish staging to consumers, change `manifest.json`, alter source package SHA-256 or cache, or modify ImPULS. Preserve the existing 3,000 staged replies; do not count this as new content.

Gate: run exact-head CI on the corrective PR; if green and compatible with fresh main, merge and verify post-main CI before resuming merges of new content. Any later source-package change must revalidate canonical rows and re-pin source metadata, not blindly replace a hash.
