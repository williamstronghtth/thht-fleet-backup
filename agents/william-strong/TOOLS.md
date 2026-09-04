# TOOLS.md - Local Notes

Skills define _how_ tools work. This file is for _your_ specifics — the stuff that's unique to your setup.

## What Goes Here

Things like:

- Camera names and locations
- SSH hosts and aliases
- Preferred voices for TTS
- Speaker/room names
- Device nicknames
- Anything environment-specific

## Examples

```markdown
### Cameras

- living-room → Main area, 180° wide angle
- front-door → Entrance, motion-triggered

### SSH

- home-server → 192.168.1.100, user: admin

### TTS

- Preferred voice: "Nova" (warm, slightly British)
- Default speaker: Kitchen HomePod
```

## Why Separate?

Skills are shared. Your setup is yours. Keeping them apart means you can update skills without losing your notes, and share skills without leaking your infrastructure.

---

Add whatever helps you do your job. This is your cheat sheet.

## Google Cloud Project
- **Project:** thehooverhometeam.com → My First Project
- **Project Number:** 746664107005
- **Project ID:** delta-carving-486821-c3
- **Google Search API Key:** `$GOOGLE_SEARCH_API_KEY` — value in `/root/agents/.env` (gitignored). Moved out of this file 2026-08-30.
  - Used for: Prospect Intelligence — LinkedIn URL lookup via Custom Search API
  - Also needs: `GOOGLE_SEARCH_CX` (Custom Search Engine ID) — lives on Render only
  - **Status: Both keys live on Render — Prospect Intelligence fully operational**


---

## CRM API Access
- **Base URL:** https://clientlist.onrender.com
- **Agent Key (William Strong, admin):** `$CRM_API_KEY` — value in `/root/agents/.env` (gitignored)
  - Use this for all programmatic CRM calls from any agent
  - Load with `source /root/agents/.env`, or `secrets_loader.require("CRM_API_KEY")` in Python
- **Auth header:** `Authorization: Bearer $CRM_API_KEY` or `x-api-key: $CRM_API_KEY`

> **🔒 RULE (2026-08-30): never paste a key literal into this file or any `.md`.**
> Record the *env var name*, never the value. Key literals were removed from this file on
> 2026-08-30 after an audit found the live admin key committed to git history
> (commit `696a2db`, 2 tracked files). No remote is configured, so it was never pushed —
> exposure is local-only — but it cannot be removed from history without a rewrite.
> That is why the fix is **rotation, not scrubbing**. Chris/Jack keys were removed here
> for the same reason; reissue them post-rotation into `.env`, not into markdown.

---

## ⚠️ Email — Do NOT use MCP or Gmail Auth

Never ask Chris (or anyone) to connect MCP or authenticate Gmail.
Use the local email script instead:
```bash
python3 /root/agents/bin/send-email.py --to "recipient@example.com" --subject "Subject" --body "Body text"
```
