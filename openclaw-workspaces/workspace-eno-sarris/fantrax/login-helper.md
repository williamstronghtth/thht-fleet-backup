# Fantrax Browser Automation Guide

## Session Status
**Last verified:** 2026-03-14 — Session is ACTIVE ✅

## Quick Health Check
Before starting any workflow, verify the session:
```
browser action=navigate profile=openclaw targetUrl="https://www.fantrax.com/fantasy/league/fq6li5m5mhuxa22g/home" timeoutMs=60000
browser action=snapshot profile=openclaw
```

If you see "We Got Worms the 19th" in the snapshot → session is good!
If you see "Not Member of League" → session expired, run login flow below.

## Login Flow (Only If Session Expired)

### Step 1: Navigate to Login
```
browser action=navigate profile=openclaw targetUrl="https://www.fantrax.com/login" timeoutMs=60000
browser action=snapshot profile=openclaw
```

### Step 2: Fill Credentials & Submit
Look for email/password input refs in snapshot, then:
```
browser action=act profile=openclaw request={"kind":"fill","ref":"EMAIL_REF","text":"choover323@gmail.com"}
browser action=act profile=openclaw request={"kind":"fill","ref":"PASSWORD_REF","text":"Football10!!"}
browser action=act profile=openclaw request={"kind":"click","ref":"LOGIN_BUTTON_REF"}
```

### Step 3: Verify Login
```
browser action=act profile=openclaw request={"kind":"wait","timeMs":5000}
browser action=navigate profile=openclaw targetUrl="https://www.fantrax.com/fantasy/league/fq6li5m5mhuxa22g/home" timeoutMs=60000
browser action=snapshot profile=openclaw
```

## Credentials
- **Email:** choover323@gmail.com
- **Password:** Football10!!

## Key URLs
| Page | URL |
|------|-----|
| League Home | https://www.fantrax.com/fantasy/league/fq6li5m5mhuxa22g/home |
| Team Roster | https://www.fantrax.com/fantasy/league/fq6li5m5mhuxa22g/team/roster |
| Players | https://www.fantrax.com/fantasy/league/fq6li5m5mhuxa22g/players |
| Transactions | https://www.fantrax.com/fantasy/league/fq6li5m5mhuxa22g/team/transactions |
| Draft Room | https://www.fantrax.com/fantasy/league/fq6li5m5mhuxa22g/draft |

## Critical Settings
- **ALWAYS use `timeoutMs=60000`** (60 seconds) — Fantrax is slow
- **ALWAYS use `profile=openclaw`** — keeps session persistent
- Save `targetId` from navigate response for subsequent calls

## Troubleshooting
| Issue | Fix |
|-------|-----|
| Timeout on navigate | Increase to `timeoutMs=90000` |
| "Not Member of League" | Session expired → run login flow |
| Page loads but no data | Wait longer: `request={"kind":"wait","timeMs":10000"}` |
| DNS error on m.fantrax.com | Use www.fantrax.com URLs only |
