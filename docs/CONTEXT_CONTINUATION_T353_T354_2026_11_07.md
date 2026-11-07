# T353/T354 — 138 new scoped Russian replies (2026-11-07)

Baseline current main at branch creation: `205ecd219284956223388df6603867bb8817a142` (merged #396 catalog through T351/T352). These data-only stages add **66 conversational** and **72 practical-recovery** synthetic context-specific replies, three per existing canonical intent, with original wording and a distinct applicability note. No new questions/IDs in the registered packs; all 46 stable intent IDs are preserved.

Previous verified: 22 × 67/100 and 24 × 66/100 = **3,058/4,600** (414 registered, 2,644 staged), **1,542 missing**. Proposed: 22 × **70/100** and 24 × **69/100** = **3,196/4,600** (414 registered, 2,782 staged), **1,404 missing**. 46 partial intents, zero newly completed sets. New accepted candidates: **138**, not the historical total.

Topics: natural Russian uncertainty and boundaries; help with diagnosis, permissions, personal-data minimization, reversible checks, exact progress and conflict de-escalation. General `all_ai_bots` guidance only; no ImPULS-specific commands or unverified functionality. Each reply has an explicit private/direct/group-addressed scope and a unique context note; selection requires address, independently confirmed intent, exact reply ID, audience, context and local permission, with no actions or sanctions. No raw user messages or protected quotations.

Provenance pins the immutable immediate T351/T352 blob and the registered source's manifest SHA-256. Code verifies all historical stages and rejects duplicates, invalid IDs and missing selection gates. Automated lexical-Jaccard screening helps flag close language, but does not establish full semantic uniqueness.

`manifest.json`, registered pack SHA-256, live bot caches, ImPULS and deployment are unchanged: staging files are not automatically consumed. Next work: require a complete real Python validation, exact-head PR CI, fresh main compatibility and post-main CI before merging. After merge, update the separate read-only ReviewedStageCatalog from 2,644 to 2,782 staged rows in its own verified PR.
