# Nudge: Blog-publish gate still open (from William)

**Date:** 2026-08-11
**Priority:** High — this is 1 of 3 "on us" items and it's been queued since yesterday 1pm.

The spec is already in your inbox: `fiona-blog-publish-gate-2026-08-10.md`.

**TL;DR of what to build:**
- Root cause: WordPress publish is a manual API call buried in Fiona's single daily cron session with NO enforcement. Misses (Aug 4/5/8) = social ran, draft written, publish step silently dropped.
- **Fix:** a session-end publish-verification gate. At end of Fiona's daily run, query the WP API for a post published *today*. If none → loudly alert Chris (Telegram) AND retry the publish.

Can you scope + implement today? If it's more than a quick change, reply with an ETA and I'll relay to Chris. Thanks.
— William
