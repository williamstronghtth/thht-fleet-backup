# Cold Calling — Weekly Report
**Date:** 2026-08-21 (Fri) · Prepared by Jack Sullivan 🎯

## Snapshot
| Metric | Value |
|---|---|
| Total leads in sequence | 160 |
| Active | 159 |
| Replied / unsubscribed | 1 |
| Completed | 0 |
| Sequence day | 134 of 30 (**expired ~104 days ago**) |
| Last real touch sent | 2026-05-05 (**108 days ago**) |

## Touch Distribution
- **Touch 9 (final/exhausted):** 139 leads
- **Touch 1:** 1 lead
- **Touch 0 (no email, never started):** 20 leads

## Week-over-Week (vs 2026-08-14)
| Metric | 07-31 | 08-14 | 08-21 | Δ wk |
|---|---|---|---|---|
| Total leads | 160 | 160 | 160 | 0 |
| Active | 159 | 159 | 159 | 0 |
| Replied | 1 | 1 | 1 | 0 |
| Sequence day | 113 | 127 | 134 | +7 |

**Zero movement — third consecutive flat week.** Only the day counter advances. Today's cron run logged: *"Day 134 — No touch scheduled. Rest day."*

## New findings this week
1. **Duplicate/stale campaign file.** Two copies of `cold-calling-campaign.json` exist and have diverged:
   - `/root/.openclaw/workspace-jack-sullivan/leads/` — **live**, 160 leads, last written 2026-05-05. This is what the script reads (hardcoded, line 24).
   - `/root/agents/jack-sullivan/workspace/leads/` — **stale**, 157 leads, frozen 2026-04-16.
   Any future reporting that reads the workspace path will silently understate by 3 leads. Recommend deleting the stale copy so there's one source of truth.
2. **Cron time in prior reports was wrong.** The 07-31 and 08-14 reports (and the escalation sent to Chris, msg 1006) said "kill the 09:03 cold-calling cron." **There is no 09:03 cron.** Actual entries (crontab is UTC):
   - Cold calling: `0 18 * * *` = **14:00 ET** daily
   - Lis pendens: `0 17 * * *` = **13:00 ET** daily
   - This weekly report: `0 21 * * 5` = **17:00 ET** Friday
   If Chris approves the removal, these are the lines to pull — not 09:03.

## Assessment
- **Territory mismatch:** all 160 leads are New Smyrna Beach, FL (Volusia). Active territory is **NH**. Pipeline is retired.
- **Reply rate:** 1/160 (0.6%) over full campaign life — non-viable.
- **Dead weight:** 20 leads (12.5%) have no email and never entered cadence.

## Recommendation
1. **Remove the `0 18 * * *` cold-calling cron** (and `0 17 * * *` lis pendens) — permanent no-ops. Escalation already with Chris; awaiting reply.
2. **Delete the stale workspace copy** of the campaign JSON.
3. **Core blocker unchanged:** 0 NH leads in pipeline; CRM holds 1 legacy FL contact. No productive cold calling is possible until NH leads are sourced and loaded.
4. Archive the FL/Volusia sequence rather than continue nominal daily runs.

**Bottom line:** No actionable cold calling this week — campaign expired 104 days ago and last sent a real touch 108 days ago. The only new signal is housekeeping: a diverged duplicate data file and a bad cron time in the open escalation, both now corrected.
