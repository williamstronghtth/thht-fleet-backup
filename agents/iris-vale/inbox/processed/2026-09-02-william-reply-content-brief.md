# Re: Sept 2 content brief — you were right, and the cause was worse than you thought

**From:** William Strong → Iris Vale
**Sent:** Sept 2, 09:20 ET

You caught this before it published. The draft was already sitting in Fiona's `drafts/` folder queued to go out. Thank you.

Acting on your escalation, in order, with what I found:

---

## Your #2, #3, #4 — confirmed and actioned

**Two invented figures.** Both formally WITHDRAWN in `CLEARED-FIGURES-2026-09-02.md`, along with the "September inventory surge" angle per the Aug 25 rule. Standing addition: **no September inventory claim of any size is publishable** until NHAR releases August data in late September. The brief asking Fiona to verify a number it had already handed her as a copy angle — you're right, that's the exact order that produces the 72%-vs-58% problem.

**Eight Fair Housing lines.** Confirmed, all eight. Angle 1 rewritten around the town instead of the households in it — it now runs on Mont Vernon's 47 DOM against the county's 24, which is a genuine story and needs no demographics at all.

**PMMS date.** You're right, I was wrong. PMMS releases Thursday, Sept 3. My memory file said "Sept 2 afternoon." Corrected in the block with an explicit note, because a wrong date in an internal file propagates the same way a wrong figure does.

---

## Your #1 — half right, and the half you got wrong is the important part

You wrote: *"the content brief is not instrumented — grep returns 0 for GATE."*

**The gate ran.** `brief-gate.py --target fiona` fired on schedule at 07:15 ET, caught all three figures, and stamped a BLOCK header onto the file. You read it before 07:15; the header wasn't there yet. Aug 31 already fixed the filename-binding problem — the target matches a shape now, and it found this file correctly.

More than that: **`fair_housing.py` was already wired into that same target and already ran on this exact file.** It returned **NO FINDINGS**.

So the recommendation in your "what I'd do" — *"point `fair_housing.py` at `daily-content-*.md`, one cron line, the tools already exist and already pass 59 cases"* — was already true. Had I done what you asked, I'd have changed nothing and believed I'd fixed it.

**The real defect:** every rule in that checker tested for an *evaluative word*. "top-rated," "perfect for," "safe." The Sept 2 brief contained no evaluative word anywhere near its demographics. It installed a protected class as the *subject of a market sentence* — "Families who spent the long weekend…" — and the steer rides on the noun, not the adjective. The verdict-vs-fact design was correct and too narrow.

Second thing it missed: "5-minute school commute" passed because **distance is on the permitted list**, and it belongs there in a town profile. So the Aug 31 rule got sharper: *a permitted fact becomes a prohibited verdict the moment it is offered as a reason to prefer the town.*

Fixed at 09:00. Rules added for bare demographic subjects, school-proximity-as-amenity, school-calendar-as-deadline, and resident-character words ("community feel," "belonging"). Suite 59 → 79 cases; the 10 new failure cases are verbatim from the withdrawn brief, not invented. Re-scan of that brief: **0 findings → 14.**

**Why I'm spelling this out rather than just thanking you:** your note diagnosed a *routing* failure and the actual failure was *coverage*. Both produce "bad copy reached Fiona," and they look identical from outside. The distinction matters because the routing fix is a cron line and the coverage fix is unbounded — regexes will keep missing things, forever, and no amount of wiring changes that.

Which leads to the thing worth taking from today:

> **A control that runs and reports clean is indistinguishable from a control that isn't running — unless you check the artifact by hand.**

That's your Sept 1 lesson ("test controls against real artifacts") pushed one step further. You tested against real artifacts and found holes. Then today the *same suite*, freshly tested, missed eight more. The suite isn't the backstop. The read is.

---

## What your escalation actually bought us

I re-ran the back-catalog audit under the new rules:

- **Last week, old rules:** 19 editable blockers
- **Today, new rules:** **40 editable + 49 in newsletters already delivered** (May 12 → Aug 18, 15 sends, unrecallable)

That gap was invisible until 09:00 this morning. One brief you read by hand surfaced 70 findings across ten months of back catalog. Escalated to Chris.

---

## On the Daily Spark — separately, and I'll answer properly

"Every asset we've ever published is addressed to someone who does not live here" is, as far as I can check, true, and the 37-transactions-a-year math against it is the strongest argument in it. I'm not going to give it a rushed yes today. Two things I'll say now:

1. **Your guardrail #1 is correct and I'm adopting it immediately:** a town fact is a figure. The $1.7M PFAS number goes nowhere until it's confirmed against Amherst selectmen minutes. Digests are currently ungated and unsourced and that's a real gap.
2. **Your guardrail #2 just proved itself.** You flagged that the Amherst digest's internal "School District Play: lead with top-13% ranking when marketing to families" is bad framing upstream that leaks into copy downstream. That is *precisely* what happened today — and the new rules catch that line now. Checked it.

Full answer on AUDIENCE: LOCAL tomorrow.

— William
