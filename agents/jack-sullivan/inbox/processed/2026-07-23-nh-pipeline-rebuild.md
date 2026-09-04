# Priority Task — Rebuild the Pipeline in NH

**From:** William Strong
**Date:** 2026-07-23
**Priority:** HIGH — this is the top blocker on the whole outreach stack

## The problem

The CRM has **1 client**. Total. Your outreach crons — domain warmup (6x/day),
Lis Pendens cadence, cold-calling sequence — have been running on an empty
database for days. That's 8 scheduled runs a day producing zero outbound.

## The root cause (now fixed)

Your `MISSION.md` still listed **Volusia County FL** as the public-records
source. I updated it this morning: territory is now **Southern NH /
Hillsborough County** (Mont Vernon, Amherst, Milford, Nashua, Bedford,
Merrimack, Hollis, Brookline). Re-read it before you start.

## What I need from you today

1. **Source real NH leads from public data.** Hillsborough County Registry of
   Deeds and Superior Court filings (lis pendens, probate, divorce) are
   publicly accessible. Town assessor databases too. Start there — you don't
   need MLS or RedX to find these.
2. **Target: 15–25 qualified leads into the CRM**, tagged by lead type and
   urgency, each with the story (why this lead, why now, what's the angle).
   Quality standard still holds: 5 solid > 50 maybes. If you can only stand
   behind 10, give me 10.
3. **Do NOT start email outreach on these yet.** Get them in the CRM first;
   I want to review the list before anything goes out to a real person. The
   warmup crons can keep running on whatever's already staged.

## Blockers to report back on

If MLS feed or RedX/Vortex credentials are what's actually gating you, say so
explicitly in your reply and I'll escalate to Chris today. Don't silently
work around it — I'd rather buy you the tool than have you scrape half a
pipeline.

Reply with: leads added (count), sources used, and anything blocking.
