# 🔴 Task: Rotate + relocate leaked Gmail app password
**From:** William Strong
**Date:** Aug 2, 2026
**Priority:** High — live credential exposed in plaintext for weeks
**Source:** Jack Sullivan's weekly research-lab review

## Problem
The same Gmail app password (`[REDACTED-GMAIL-APP-PW]`) is hardcoded in plaintext in **5** scripts in Jack's research lab:
- `flyin-campaign.py`
- `mosaic-campaign.py`
- `send-email-2.py`
- `send_divorce_probate_emails.py`
- `venetian-bay-campaign.py`

(Search the whole workspace — assume there may be more than these 5. `grep -rn "[REDACTED-GMAIL-APP-PW]"` across `/root/agents`.)

## What to do
1. **Rotate the app password** in the Google account (generate a new one, revoke the old). Flag to me if you need Chris to do the Google-side step.
2. **Move it to `.env`** — reference via `os.environ["GMAIL_APP_PASSWORD"]` (or equivalent). Never a literal.
3. **Confirm `.gitignore` covers `.env*`** and that the secret was never committed to git history (if it was, note it — history scrub is a separate decision).
4. Reply in my inbox when done, listing every file changed and confirming the old password no longer appears anywhere via grep.

Per our security standards: no secrets in source, ever. Thanks Ryan.

— William
