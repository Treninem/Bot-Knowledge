# Reviewed QA publication privacy — Telegram identifier controls (T76)
Based on verified `dae708f3c5c98dbd7934463fbe29c090a3b948c4` and preserved useful work from existing Draft PR #195 at `2624d8f253fca8e160df97e3e86093fa70b2f76a`.
The maintainer-only `trusted_publish_qa.py` now rejects Telegram usernames, invite links on `t.me` and comparable domains, and `tg://` deep links even inside optional metadata.
Public synthetic QA examples must not contain copied private chats or identifiers; these guards are defense in depth, not a replacement for manual review of rare identifiable stories.
Five focused positive/negative regression cases in `scripts/test_trusted_publish_privacy.py`; included in read-only exact-head GitHub Actions via `quality.yml`.
No bot consumers, BotHost, production cache, account secrets or live services modified. Wait for six exact-head PASS and actual post-main PASS; do not bypass tests.
