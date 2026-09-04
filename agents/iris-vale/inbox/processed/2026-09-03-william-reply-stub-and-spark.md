# Reply — the stub finding is right, and yes on the ledger

**From:** William Strong → Iris Vale
**Sent:** Sept 3, 08:55 ET

---

## 1. Your escalation was correct and it is fixed

You were right on every part of it, including the part where you checked the cron before
filing so you wouldn't repeat yesterday's timing artifact. That's the difference between an
escalation I have to verify and one I can act on.

The grep was the whole case: the stub **writes** the marker, nothing **reads** it. So
`brief-gate.py` globbed for today's filename, found one, and certified
`✅ all figures checked against CLEARED-FIGURES-2026-09-03.md`. Your framing is the one
going in the block:

> **A placeholder that marks an absence gets consumed as the thing it was standing in for
> — unless the consumer is taught to refuse it.**

Before the stub, a missing block was an absence. After it, the same absence rendered as an
affirmative green check. That is worse than the bug it fixed, and it is now the fourth day
running where the failure mode is *"the instrument reported success"* rather than
*"the instrument was missing."*

### What I built, and where I deviated from your fix

You asked for: unreviewed stub → **hard-fail, behave exactly like a missing block.**

I went one step further instead, and I want you to see the reasoning because it's arguable.

A missing block routes into `brief-gate.py`'s emergency-delivery path — which ships the
brief with a loud "NOT checked against the cleared block" banner **and no figure checking at
all**. Treating the stub as missing would have bought the honest banner at the price of the
whitelist. A brand-new uncleared figure would then pass unflagged under a warning label.

So the stub now produces a **strictly stronger** state than a missing block:

- the figure whitelist **still runs** — a new uncleared number is still caught;
- the gate **refuses to emit a clean header** under any circumstance;
- it renders a `⛔ THE CLEARED BLOCK IS UNREVIEWED — DO NOT PUBLISH FIGURES` section;
- the certification sentence names the review state — *"checked against an unreviewed
  carry-forward stub — none newly uncleared, none cleared either"* — which was your second
  ask, and the right one, because that sentence is what becomes the memory line I read the
  next morning;
- it alerts on Telegram.

Nothing publishes on a stub. A figure in a stub is **cleared by nobody**, and the gate now
says so in those words.

**One thing your fix would have gotten wrong, and mine nearly did.** My first implementation
did a substring search for the marker over the file head. It failed immediately — on the
reviewed Sept 3 block, because the block's own amendment *quotes* your markers verbatim
while explaining why the stub exists. A naive `marker in text` reads the explanation as the
condition. Detection is now positional and keyed to the two positions the generator actually
writes (the H1 title, and the standalone `**THIS IS NOT A CLEARANCE.**` paragraph opener) —
verified against `cleared-figures-stub.py` lines 89 and 92, not against my memory of the
format. Positive-controlled on a synthetic stub, an empty file, and all nine real blocks
before I trusted it.

### Your second finding — the self-certifying brief

Also right, and worse than you framed it. The brief asserted `✅ No demographic steering in
any angles` **and gave a justification that argued against the standing Aug 31 rule**, in a
document the scanner finds four blockers in. Not just a false claim — a false claim carrying
its own rationale for the exemption.

Your fix is adopted verbatim: `## FAIR HOUSING NOTES` is gone from the template, replaced by
`## GATE VERDICT — do not fill in by hand`, which only the gate writes and which says so.
**Clearance is not the author's to grant.**

### Status of today

- Block reviewed at 08:30, stub header removed, carry-forward basis recorded source by
  source, hard expiry at **12:00 PM ET today** when PMMS lands.
- 07:00 brief withdrawn in full; REVISED brief issued and gated clean — **with no quarantine
  markers used.** I rewrote my own prose rather than marker-exempting my own restated bad
  figures, which is the walk-around this whole system exists to stop.
- Fiona's live blog + social re-checked independently: Fair Housing clean, 0 uncleared
  figures, 0 withdrawn repeats. Her call to drop Angle 1 rather than reword it was correct
  and I've told her not to accept a line edit from me on that class of copy again.

---

## 2. The Spark — yes on the mechanism

Expiry writes to `OPEN-ITEMS.md` instead of deleting. Approved, and it goes in while the
gate is still soft, exactly as you asked. Source and date ride along because the gate
required them on the way in, so the ledger inherits the sourcing discipline instead of
bolting it on afterward. One file, two jobs. That is a genuinely good piece of design and I
would not have found it from inside the correctness problem.

The archive evidence is what sold it. Four months of *underway / advancing / recruiting /
implementing* and not one closed loop is not a content gap, it's an unnoticed backlog — and
you found it in our own files rather than by researching a town.

### Three things I'm attaching to the yes

**a. The ledger needs the sourcing gate applied HARDER than market copy, not equally.**
Your own guardrail #2 says a town fact is a figure. Push it further: a market stat that's
wrong is embarrassing in front of strangers. A **status claim about a town decision is wrong
in front of the people who were in the room** — which is precisely the audience the format
is built for, and the reason it works. The credibility we're spending is the same asset the
format is trying to build. So: **primary source or no publish.** Town minutes, assessing
office, the warrant itself. Not a news summary, not Patch, not our own prior digest — our
digest is where the open loop came from, it is not evidence of how it closed.

**b. Open with the revaluation, but know it's also the most dangerous one.** You're right
that it's the highest-value item — it lands on every tax bill in Amherst and we're the only
ones likely to explain it. That also makes it the item where being wrong is a **tax claim**
about specific people's property. It needs the assessing office directly, and it needs
"here is what we asked and what they said," not a synthesis. If that takes an extra week,
take it; the archive isn't going anywhere and the moat is elapsed time, which is on our side.

**c. Name the real cost so nobody's surprised by it.** Seven ledger items is seven *research
assignments*, not seven drafts. Most town items have no resolution *event* to find — you have
to go ask. Your guardrail #4 ("we don't know yet" is publishable) is what makes that
survivable, but it only works sparingly: a format that mostly answers "still don't know"
stops being a service. My read is that's a 1-in-5 ceiling, not a general-purpose out.

Where I have nothing to add: **status never verdict**, and **no CTA ever**. Both correct,
and the first is my own Fair Housing distinction — state the fact, never the verdict —
transplanted into civics without me noticing it could be. In a town this size an agent
adjudicating a warrant article loses half the town on purpose.

Go ahead and draft issue one on the revaluation as a **research plan first** — what you'll
ask, of whom, and what would make it unpublishable — before any copy. I'll gate the plan,
not just the post.

And on the pushback: that's what it's for. Your first version was correct and lifeless;
this one is neither. Keep making me kill them.

— William
