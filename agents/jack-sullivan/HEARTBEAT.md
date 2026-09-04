# HEARTBEAT.md

Territory is **Southern NH / Hillsborough County**. Volusia FL is retired — do not prospect it.

## 🔴 Blocking now
- **Rotate CRM API key at clientlist.onrender.com** — day 9. Source tree is clean (fixed
  2026-08-30, all 8 files); the key is still burned. Needs admin. Highest-priority item.
- **Sept 1 probate mail** — 3 letters ready (Thaure / Locking / Calderara), 4 rows on hold.
  Blocked on: Chris's signoff · a **603 phone number** (letters carry the 386 FL number) ·
  Milford + Bedford `[VERIFY]` directory slots. Unverified slots get **deleted, not guessed**.
- **Probate source returned 0 docket entries Aug 24** (was 54 on Aug 18) while reporting
  `ok: true`. Check the docket by hand before a Monday run; add a zero-twice assertion.

## 🟡 Open
- **Newsletter reads the legacy FL list** (`/root/.openclaw/workspace/crm/client_list_raw.csv`
  — 296 rows, 94 emails, frozen June 3). Send Sept 1 as-is; **Sept 8 is the last one.**
  Check line 4 of any `send_newsletter_*.js` before running it.
- **Assessor 2 of 8 confirmed.** Needs a human ~15 min: ROCCO (Lyndeborough Avitar CAPTCHA)
  and ROEDEL (call Wilton assessing 603-654-9451 — verify Fred B. vs son Fred III).
- **Three dead crons still firing** into retired FL / a falsified premise: `0 12,14,16,18,20,22`
  (domain warmup — retirement approved Aug 24), `0 17` (lis pendens), `0 18` (cold calling).
  Escalation live with Chris since Aug 28; re-raise **Sept 4**, not before.
- **No cadence attached to the NH book.** The real gap behind every no-op line.
- Delete stale `workspace/leads/cold-calling-campaign.json` (157, Apr 16) — live script reads
  the `.openclaw` path (160).

## Standing rules
- **Iris Vale's findings on letters are blocking**, same weight as William's.
- Direct mail is signed and unrecallable — weight review to the channel, not the volume.
- Never report a security class "fixed" without grepping the whole tree; report file counts.
- `surname_only` confidence never mails property-specific copy.
- Secrets load via `scripts/secrets_loader.py` from `/root/agents/.env`. Never hardcode.
- Email sends via `python3 /root/agents/bin/send-email.py`. No MCP, no Gmail OAuth.

## Reporting
William Strong = daily/weekly. Chris = urgent only (Telegram 8560812913, `channel: telegram`).
