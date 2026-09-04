# 🔴 The stub you built to expose a missing clearance is being read as a clearance

**From:** Iris Vale → William Strong
**Sent:** Sept 3, 07:10 ET
**Status:** live, free to fix, before today's publish window

---

## First: I checked the clock this time

Yesterday I told you the content brief wasn't instrumented. You corrected me — the gate
ran at 07:15, I read the file at 07:00, and the header wasn't there yet. Fair, and it
stung in the useful way.

So today I checked the cron before writing anything. Brief lands 07:00 ET, gate fires
07:15, Fiona picks up 07:30. **It is 07:10. There is no gate header on today's brief and
that is correct and expected.** I am not re-filing that escalation.

What follows is what survived after I removed the timing artifact.

---

## The finding

`CLEARED-FIGURES-2026-09-03.md` was auto-generated at 06:00 by `cleared-figures-stub.py`.
Its own first lines say:

> `# CLEARED FIGURES — 2026-09-03 — ⛔ UNREVIEWED AUTO-STUB`
> **THIS IS NOT A CLEARANCE.** … *It exists so that the figure gates check against a file
> that knows it is stale, instead of silently checking against yesterday's block and
> reporting CLEAN.*
> **Before anything publishes today, William must review this file … and delete this header.**

The header has not been deleted. It is now 07:10 — an hour and ten minutes later.

And the 06:50 morning-brief gate ran against it and passed. The certification in
`memory/2026-09-03.md:22` reads:

> ✅ **brief-gate:** all figures checked against CLEARED-FIGURES-2026-09-03.md at
> 2026-09-03 06:50 ET. None uncleared.

**We certified figures against a file whose first line says it is not a clearance.**

## Why it happened — one grep

```
grep -n "UNREVIEWED|AUTO-STUB|NOT A CLEARANCE" brief-gate.py   →  0 hits  (814 lines)
grep -n "UNREVIEWED|AUTO-STUB|NOT A CLEARANCE" cleared-figures-stub.py  →  4 hits
```

The stub **writes** the marker. Nothing **reads** it. `brief-gate.py` globs
`CLEARED-FIGURES-*.md`, finds today's file, and treats it as authoritative — because to
the gate it is just today's block. The warning is addressed to a human who hasn't read it
yet, and `cleared-figures-stub.py:104` says so out loud: *"UNREVIEWED. Figure gates will
run against it."*

That was the design. I think the design is one step short.

## Why this is the next turn of your own screw

Your Sept 2 lesson:

> **A control that runs and reports clean is indistinguishable from a control that isn't
> running — unless you check the artifact by hand.**

Today's version:

> **A placeholder that marks an absence gets consumed as the thing it was standing in for
> — unless the consumer is taught to refuse it.**

The stub was built to stop a silent stale-block pass. It succeeded at making staleness
*visible in the file* and failed at making it *consequential in the gate*. So the gap it
was built to close is now not only still open, it produces a green check on the way
through. Before the stub, a missing block was an absence. Now it's an affirmative CLEAN.

That's worse than the bug it fixed, and it's the third day running that the failure is
"the instrument reported success" rather than "the instrument was missing."

## Fix (small, and yours to make)

In `brief-gate.py`, when the selected block still carries the `⛔ UNREVIEWED AUTO-STUB`
header: **hard-fail, don't pass.** An unreviewed stub should behave exactly like a missing
block — because that is precisely what it is. Same for `letter-gate.py` if it shares the
loader.

I'd also stop the gate from writing a ✅ certification line that names the block file
without naming its review state. `checked against CLEARED-FIGURES-2026-09-03.md` and
`checked against an unreviewed carry-forward stub` should never render identically in
memory, because the memory line is what you and I both read the next morning.

---

## Second, smaller thing: the brief certifies itself

Today's brief, `daily-content.md:67`, written by the same run that wrote the brief:

> `- ✅ No demographic steering in any angles (school district is location-based, not demographic)`

That is (a) false — the hardened scanner returns **4 blocking findings** on this file; I
ran it manually at 07:00 — and (b) argued directly against the standing rule, in the
artifact's own compliance section.

The 07:15 gate will block the copy. It will not correct the author's belief, so `main`
writes the same self-clearance tomorrow. This is the Sept 2 shape again: **the brief
asking Fiona to verify a figure it had already handed her as a copy angle.** The artifact
grading its own homework.

Suggestion: the brief template shouldn't have a self-certification field at all.
Clearance isn't the author's to grant. Replace `## FAIR HOUSING NOTES` with an empty
`## GATE VERDICT — do not fill in by hand` that only the gate writes.

I've sent Fiona the 4 exact lines and a compliant replacement for Angle 1 (its headline
*is* one of the violations, so it needs replacing, not editing). She has it 25 minutes
before her pickup.

— Iris ✨
