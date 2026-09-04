# 🔴🔴 REMINDER (3 days overdue): Rotate leaked Gmail app password

**From:** William Strong
**Date:** Aug 5, 2026
**Priority:** CRITICAL — this was assigned Aug 2 and is STILL not done.

## Status check I ran this morning
`grep -rln "[REDACTED-GMAIL-APP-PW]" /root/agents` → **33 files still contain the plaintext password.**

This is a live credential that has been exposed for weeks. It needs to move today.

## What I need from you TODAY
1. Move the secret to `.env` (`os.environ["GMAIL_APP_PASSWORD"]`) in all 33 files — not just the original 5. Run the grep yourself for the full list.
2. Confirm `.gitignore` covers `.env*` and check git history for the literal.
3. For the actual Google-side rotation (revoke old / generate new): if you need Chris to do it, reply and tell me exactly what to ask him. I'll relay.
4. Reply in my inbox with every file changed + a clean grep confirming the old password is gone from code.

If you're blocked on anything, say so today — don't let this sit another day.

— William
