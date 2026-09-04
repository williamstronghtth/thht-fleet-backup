# Monday Action Items — July 13, 2026
**From:** William Strong

---

## 1. Kill the Fly In stale cron — NOW (4 weeks overdue)

The "Fly In 15-touch cadence" cron is still running daily despite being halted in May. It's in crontab as:

```
0 13 * * * cd /root/agents && source .env && bin/run-agent.sh jack-sullivan "Fly In 15-touch cadence, run cadence-runner.py"
```

This has appeared in 4 consecutive weekly reviews. Kill it. Remove from crontab.txt and reload.

---

## 2. thht-social status check

thht-social.onrender.com has been down since June 21+ (unknown status). Can you do a quick curl check and report the actual status? If it's a free-tier billing cap issue same as thht-hq, say so in your memory so William can include it in the kill/keep/pay decision Chris is making.

---

## 3. Town Origin + Market Pulse deploy — awaiting Chris green light

Chris has been asked. Once he confirms, push the `town-origin-component` branch to live WordPress. Market Pulse committed at 6b40c13 — both components ready.

---

## 4. GitHub gh token (issue-004)

Still blocked. Still 5+ weeks. If you have any way to prompt Chris directly, do it. This unblocks automated repo backups.

---

## 5. thht-hq — down again (same monthly pattern)

Instance-hour cap hit again. Chris is being asked to decide kill/keep/pay (~$7/mo). No engineering action needed until he decides — just confirming the pattern holds.

---

That's it for Monday. Fly In cron is the priority — kill it today.

— William Strong
