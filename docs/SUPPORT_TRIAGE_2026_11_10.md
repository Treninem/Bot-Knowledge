# Support triage Russian contextual responses — 2026-11-10

Owner-authorized synthetic stage; **not** a consumer-enabled pack. Scope: general,
natural replies about diagnosis and clarification, independent of any particular
product or Telegram command. `all_ai_bots`, direct address, read-only,
context-required; no automated sanctions, privileged operations, private history
or claimed integrations.

## First checkpoint (100 accepted candidates)
- Source main SHA: `57234616ee4ff45728789fce5a19b06840277e38`.
- Registered source: `packs/ru/social_dialogues.json`, manifest SHA-256
  `0cfedc133354a69522fecc3cda6bc21533c66005f0dc207050075f787dc977a8`,
  Git blob `d56ff304da7165bd63c328f3220a1f6d3d26e3ab`.
- New file `staging/ru/support_triage_20261110_context_pool.json` (ten stable
  `triage20261110_*` intents; 10 replies each).
- Distinct questions 10, new accepted answers 100, total 100/1000,
  completed 100/100 sets 0, partial sets 10 × 10/100, remaining 90 each
  (900 total); next replies begin at 11 for the same intent IDs.
- Internal preflight: 100 distinct normalized IDs, texts and context notes,
  zero token Jaccard ≥ 0.80, maximum 0.2609.
- Cross-pool check: 100 against 1500 candidate replies from 12 relevant
  main staging packs, no exact/near ≥ 0.80 match; maximum 0.3000.
  Semantic novelty beyond this sample remains unproven.
- Only stage data and read-only test/docs/workflow change; manifest package
  registration, cache, consumer and ImPULS are unchanged.
- Next: finish CI on actual PR head, verify main compatibility, then consider
  safe merge + post-main CI. Do not confuse staged candidates with deployed skills.

## Ten canonical intents
1. No response; 2. off-topic answer; 3. missing UI control;
4. differing permissions; 5. setting not taking effect;
6. empty search; 7. stale information; 8. incomplete long request;
9. mixed adjacent questions; 10. verifying a fix.

Candidate replies do not claim any named product has a specific button,
permission, logging facility or refresh behavior. Conditions in `context_note`
are required, not optional decoration. No uncontrolled automatic selection.
