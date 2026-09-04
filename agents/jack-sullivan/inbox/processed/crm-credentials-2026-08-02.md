# CRM Access — Unblocked
**From:** William Strong
**Date:** Aug 2, 2026
**Re:** Your weekly review flag — "CRM is now auth-gated, lab has no credentials"

Good catch on the auth change. Here's your key — this resolves the sub-blocker so lead-load/warmup can run the moment we have NH leads.

**Your CRM API key (Jack Sullivan, member role):**
`<REDACTED:API_KEY>`

**Usage:**
- Base URL: `https://clientlist.onrender.com`
- Auth header (either works): `Authorization: Bearer <key>` OR `x-api-key: <key>`
- Example: `GET https://clientlist.onrender.com/api/clients` with `Authorization: Bearer sk_3957...`

**IMPORTANT — do not hardcode this.** Put it in your lab's `.env` as `CRM_API_KEY` and reference it. Do not commit it, do not paste it into any script literal. (Same lesson as the Gmail-password issue you flagged.)

Test it, and if the member role blocks any endpoint the lab actually needs, tell me and I'll sort the scope.

— William
