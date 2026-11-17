# Consumer snapshot v030: byte-safe JSON compaction (17.11.2026)

Based on main `a975b7f6f40e32b13654edfd1f57b1574a3b08ea` and manifest `2026.11.17.029`. **No new responses were added or removed.** Four existing packages are serialized to compact JSON: the parsed JSON values before and after are strictly equal under JSON.stringify/parse. Every old byte SHA-256 matched the actual existing manifest entry before writing, and every new SHA-256 was calculated from final UTF-8 bytes. 

- `packs/ru/skills.json`: 118037 → 95175 bytes (saved 22862); new SHA-256 `202030953fb98d6397fe795407f813553298cb9e49dcbf1ee8cc4791a2328a2c`
- `packs/ru/dialogue.json`: 116547 → 99218 bytes (saved 17329); new SHA-256 `6ce8eeead4bd9213fdbc522d623c278960d313e10ed02c3048849a269072bd6c`
- `packs/ru/moderation_cases.json`: 95922 → 80592 bytes (saved 15330); new SHA-256 `5b48d80f2d425ef980e7643e2548a546c2f0c69178cd77dd51043e613e433f0f`
- `packs/ru/conversation_precision_qa.json`: 319694 → 297911 bytes (saved 21783); new SHA-256 `d45cb71eb8d028a8bc9eb88cddb56a9bef7c7e3cc693d63760b81f238383c622`

**Total saved from registered packages: 77304 bytes.** No cache, bot, ImPULS, or code of a consumer was changed. This is a capacity checkpoint, not a claim that staged replies have been delivered. Manifest candidate `2026.11.17.030`, references exact new hashes. Scripts and read-only exact-head workflow check sizes, digest, manifest linkage and 8 MiB budget. Existing validator and quality CI remain required. Review exact-head CI, source merge SHA and post-main CI before calling the candidate published.

Note: PR #699 is based on older main v029 and holds unrelated unregistered staged answers. After compaction merges, it must be revisited against new main; do not discard or double-count its candidates.
