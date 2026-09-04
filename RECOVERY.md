# RECOVERY.md — Relaunching The Hoover Home Team from scratch

**Last updated:** 2026-09-04 · maintained by Ryan Chen
**Purpose:** If this box dies, this file plus the backup archive is everything needed to rebuild.

---

## 0. Read this first

The box holds **~4.6 GB**, but only a small slice is irreplaceable:

| Category | Size | Where it lives | Regenerable? |
|---|---|---|---|
| Application code | ~large | GitHub (13 repos) | Already safe |
| Scraped/model data | ~1.5 GB | local only | Yes — re-fetch |
| `node_modules`, logs, caches | ~2 GB | local only | Yes — reinstall |
| **Agent personas + memory** | **~35 MB** | **local only** | **NO — irreplaceable** |
| **System config (cron, openclaw)** | **<1 MB** | **local only** | **NO — irreplaceable** |
| CRM records (410+ leads) | cloud | Supabase | Safe, but export anyway |

The backup script captures the two **NO** rows plus config. Everything else is either
already on GitHub or cheaper to regenerate than to store.

---

## 1. Run the backup

```bash
bash /root/agents/ryan-chen/workspace/scripts/backup-all.sh
# → /root/agents/ryan-chen/workspace/backups/thht-backup-YYYY-MM-DD.tar.gz
```

The script **excludes all secrets** and aborts if any secret-shaped file slips into the
archive. Store the archive somewhere off this box (Google Drive, S3, or a private repo).

---

## 2. Rebuild order

### 2.1 Restore code from GitHub

All under `github.com/williamstronghtth` unless noted:

| Repo | Purpose | Deployed at |
|---|---|---|
| `thht-crm` | Client CRM (Supabase backend) | clientlist.onrender.com |
| `thht-hq` | Team HQ / virtual office | thht-hq.onrender.com |
| `thht-social` | Fiona's content pipeline | thht-social.onrender.com |
| `thht-board` | Kanban board | Render |
| `thht-sms` | SMS integration | — |
| `thht-communities` | Community pages | — |
| `Nolan-Price-BackUp` | MLB betting model | — |
| `Elliot-Crane-BackUp` | Kalshi trading | — |
| `calvin-nba-model` | NBA model | — |
| `billys-betting-board` | Betting board | — |
| `papermlb` / `papernba` | under `cuzifelt1ikeit` | — |
| `mlb-odds-scraper` | fork of `ArnavSaraogi` | — |

### 2.2 Restore agents

Unpack the archive. For each agent in `agents/<name>/`:

1. Create workspace at `/root/agents/<name>/workspace/`
2. Copy in `SOUL.md`, `IDENTITY.md`, `USER.md`, `AGENTS.md`, `MEMORY.md`, `TOOLS.md`, `HEARTBEAT.md`
3. Copy in `memory/` — this is the agent's accumulated context, ~1,200 files fleet-wide
4. Copy in `skills/` and `scripts/`

**Fleet roster (16 agents):** arthur-pembroke, calvin-king, derek-marshall, elliot-crane,
eno-sarris, fiona-murphy, iris-vale, jack-sullivan, main (William Strong), miles-redgrave,
nolan-price, oliver-kensington, ryan-chen, william-strong, willow-hayes, chris-hoover.

> Note: `iris-vale` and `miles-redgrave` run via `run-agent.sh` and are intentionally
> **not** in `openclaw.json`. That is expected, not a bug.

### 2.3 Restore system config

- `system/openclaw.sanitized.json` → `/root/.openclaw/openclaw.json` — **secrets redacted, re-supply them** (§3)
- `system/crontab.txt` → `crontab system/crontab.txt` — **92 scheduled jobs**
- `system/telegram-bots.sanitized.json` → `/root/agents/telegram-bots.json` — **bot tokens redacted**
- `system/run-agent.sh` → `/root/agents/bin/run-agent.sh`

Then: `systemctl restart thht-telegram`

### 2.4 Restore data

- **CRM:** lives in Supabase project `thht-crm` (`lkceqalryoyfxbdbmvvj.supabase.co`) — survives a box loss. Export a CSV snapshot periodically anyway.
- **Model/scraped data:** re-run each agent's fetch scripts. Not backed up by design.

---

## 3. Secrets to re-supply by hand

**None of these are in the backup — that is deliberate.** Re-issue each one:

| Secret | Used by | Source |
|---|---|---|
| `ANTHROPIC_API_KEY` | all agents | console.anthropic.com |
| Telegram bot tokens (~12) | per-agent bots | @BotFather |
| `SUPABASE_URL` / `SUPABASE_ANON_KEY` | CRM | Supabase dashboard |
| `WP_USER` / `WP_APP_PASSWORD` | WordPress publishing | thehooverhometeam.com admin |
| `LATE_API_KEY` | social auto-posting | getlate.dev |
| `CANVA_CLIENT_ID` / `CANVA_CLIENT_SECRET` | Canva | Canva developer portal |
| GitHub PAT | git push | github.com/settings/tokens |
| GA4 credentials | Fiona analytics | Google Cloud console |

Re-supply via `.env` files and `secrets_loader` — **never hardcode.**

---

## 4. ⚠️ Known security debt (fix during any relaunch)

1. **3 GitHub PATs are embedded in 11 files**, including 9 `.git/config` remote URLs.
   Anyone who gets a copy of those directories gets push access to every repo.
   → Rotate all three, then use `gh auth` or a credential helper instead of inline URLs.
2. **CRM key `sk_3957…` appears in 19 files** (tracked as a known open item).
3. **`publish-aug-15.py` hardcodes the WP password and Late API key.**

The backup script strips these, but the **live box still has them.** Rotating is the fix.

---

## 5. What is NOT yet backed up off-box

`/root/agents` is a git repo with **no remote** and ~5,200 uncommitted changes
(last commit 2026-06-27). Eight openclaw workspaces also have no remote:
`workspace`, `workspace-chriscasso`, `workspace-eno-sarris`, `workspace-jack-sullivan`,
`workspace-derek-marshall`, `workspace-billy-holland`, `workspace-william-strong`,
`workspace-ryan-chen`, `workspace-fiona-murphy`, `workspace-arthur-pembroke`,
`workspace-willow-hayes`, `workspace-oliver-kensington`.

**These exist on this box only.** The archive is currently their sole copy — which means
it must be moved off-box to count as a real backup.

---

## 6. Keeping it current

Add to crontab for a weekly snapshot:

```cron
0 3 * * 0 bash /root/agents/ryan-chen/workspace/scripts/backup-all.sh >> /root/agents/logs/backup.log 2>&1
```
