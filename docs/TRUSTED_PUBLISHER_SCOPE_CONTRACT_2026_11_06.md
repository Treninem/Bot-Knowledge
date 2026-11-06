# Scope validation for reviewed QA publication

The trusted publisher now rejects malformed optional `audiences`, `contexts`, `language`, and `constraints` before opening a PR. It also reads the destination `qa.v1` catalog and rejects scope widening, a language mismatch, unsafe constraints, or conflicting catalog metadata in the manifest. These checks keep a reviewed candidate from creating a pack that the ImPULS catalog would later reject.

Local regression: `python -B scripts/test_trusted_publisher_scope.py` covers valid publication and invalid record/target scopes. The offline end-to-end probe runs `python -B scripts/test_trusted_publisher_consumer.py --impuls-root <local ImPULS checkout>`. It uses a reviewed synthetic candidate, generates modified pack and manifest bytes with SHA-256, then loads the result through the ImPULS catalog and verifies audience-scoped search. It sends nothing to GitHub and uses no token. On ImPULS 1.6.238 (`2af8e83c0232b0af2cd496cf5d654c0817f89787`), the local probe passed.

This change does not alter any published knowledge pack, so existing pack SHA-256 values and knowledge version remain unchanged. A real GitHub PR, exact-head CI, post-main CI, remote refresh and BotHost delivery require separate verification.
