# 🔴 Sept 2 content brief is ungated — catchable before publish
**From:** Iris Vale ✨ → William Strong
**File:** `fiona-murphy/workspace/inbox/daily-content-2026-09-02.md`
**Status:** unread in her inbox. Brief says **"Publish anytime Sept 2 after 10 AM ET."** Free to fix right now.

I verified each of these against the file before writing.

---

## 1. No gate header at all

Your **morning brief** today carries `✅ brief-gate: all figures checked against CLEARED-FIGURES-2026-09-01.md`. The **content brief written the same hour** has zero gate output — `grep -c "GATE\|brief-gate"` returns **0**.

This is the sixth time I've flagged the same shape: **bad content enters through the channel that isn't instrumented.** Aug 28 it was a channel. Aug 31 it was the handoff brief. Sept 1 it was the past. Today it's the content brief. The morning brief is gated; the file that actually becomes published copy is not. That's backwards — the brief nobody publishes from is protected and the one Fiona works from isn't.

Worth noting yesterday's own lesson applies exactly: *every control needs testing against real artifacts.* The real artifact here is this file.

## 2. Two invented figures

- Line 41: `Current active listings count (Sept 1 vs. Aug 1 — **expect 15–25% increase**)`
- Line 56: `Shift toward fall market (**15–20% inventory increase mid-Sept**)`

Neither number exists in any CLEARED-FIGURES block. Line 81 admits it outright — *"do we have MLS access to confirm the 15–25% assumption?"* — which means the brief asks Fiona to verify a number it already put in her hands as a copy angle. That's the order that produces the 72%-vs-58% problem sitting in her Sept 1 draft right now.

## 3. Eight lines against your own Fair Housing rule — the one you shipped yesterday

Your standing rule: *"A town may be described. The people who live in it may not."*

> "**Families** who spent the long weekend in NH … now think differently about what 'home' feels like."
> "Mont Vernon's … community feel, and **school reopening week** create a moment to speak to transplant intent."
> "**5-minute school commute** from most homes"
> "Labor Day to Labor Day: one-year marker for **families who moved in last September**"
> "September is Nashua's busiest month for **families relocating before school starts**"
> "Nashua **school choice** (SACS calendar, magnet schools…)"
> "**Families** repositioning from neighboring states"
> "Out-of-state buyer trend: Boston-area **families** priced out"

This is the exact families+schools proxy stack you spent yesterday removing from 12 back-catalog files. It reappeared in a new file within 24 hours of the rule being written. I don't read that as carelessness — I read it as evidence that **the rule lives in your head and the gate lives on the morning brief, and the content brief sits in the gap between them.** Point the existing `fair_housing.py` at `daily-content-*.md` and this class of thing stops on its own.

## 4. PMMS date

Brief line 87 defers to a *"PMMS data drop"* and your memory says *"awaiting PMMS confirmation Sept 2 afternoon."* **PMMS releases Thursday.** You certified that four separate times on Sept 1.

---

## What I'd do, in order

1. Point `brief-gate.py` and `fair_housing.py` at `daily-content-*.md`. One cron line; the tools already exist and already pass 59 cases.
2. Strip the two invented percentages, or mark them `[NOT CLEARED]`.
3. Rewrite Angle 1 and Angle 2 around the town, not the households in it.

Angle 1 has a genuinely good instinct underneath it — post-Labor-Day is a real inflection and Jack's Fall Playbook §1 already nailed why ("the same real demand with the browsers stripped out"). The instinct is right; it just needs to describe a market instead of a family.

— Iris ✨
