# Daily Spark — Sept 3
## The town has news. It has no memory.

**From:** Iris Vale → William Strong
**This is the answer to the question you asked me yesterday**, and it means my Sept 2
Spark was half wrong.

---

## Your question

> *Assume the sourcing problem is solved by end of week. What makes the local half worth a
> resident's attention — someone who already knows the selectmen voted, because they were
> there?*

I sat with it and the honest answer is: **nothing does.** Not the top half, anyway.

News is worth approximately zero to the person who was in the room. You didn't ask a
polish question, you found the flaw in my idea. I proposed publishing the digest's top
half. But the top half is *news*, and news is the one thing our target reader already has.
A weekly Souhegan roundup competes with the Amherst Bear, Patch, the town's own
email list, and the fact that in a town of 2,584 people the news travels by parking lot.
We'd lose that race and deserve to.

So: my Sept 2 Spark was half right. The value isn't in the top half.

**It's in the diff between top halves over time.**

---

## What nobody does

A town produces decisions. **Nothing in a town produces a status.**

The minutes record that a thing was approved. The paper covers the meeting. Patch
aggregates the coverage. Then everyone moves to next week, and the thing that was approved
walks off into the dark and is never mentioned again by anyone.

A resident who sat through the March election and voted on twenty-nine warrant articles
cannot tell you, in September, which of them actually happened. **Neither can anybody
else.** That's not a gap in their attention. It's a gap in the world. Follow-through isn't
an event, and news only covers events.

That's the thing worth a resident's attention. Not "here's what happened" — they know.
**"Here's what happened to the thing that happened."**

---

## Our own archive already proves it

I didn't have to research a town to find this. I read our digests. Watch the Amherst
revaluation move through our own files:

- **May 17** — *"2026 Full Statistical Revaluation underway (contracted with Vision Government Solutions)"*
- **May 24** — *"The Town of Amherst has contracted with Vision Government Solutions… this will reassess property values across the municipality"*
- **June 21** — *"Ongoing Town Projects: 2026 Full Statistical Revaluation…"*
- **Aug 23** — gone. No mention. No outcome. Ever.

A full statistical revaluation **reassesses every property in town**. It lands on every
tax bill in Amherst. It is, without much competition, the most consequential thing that
happened to Amherst homeowners this year — and it is *exactly* the thing a real estate
agent is qualified to explain and nobody else is going to bother to. We wrote it down
three times and never once went back.

It isn't alone. Every open loop in our own archive, still open:

| Our file said | When | Still unanswered |
|---|---|---|
| Revaluation "underway" | May 17, May 24, Jun 21 | Did it land? What changed? |
| *"28 of 29 articles passed (Article 44 was rejected)"* | Jun 21 | **What was Article 44?** We never said. |
| *"$10M+ open space purchase article was voted on"* | Jun 21 | Our own file doesn't say if it passed |
| Town Planner "actively recruiting" | Jun 21 | Did they hire one? |
| Cashless transfer station "implementing" | May 24 → Jun 21 | Still "implementing" a month later. Done? |
| LaBelle Winery distillery "advancing plans" | May 17 | Advanced to where? |
| PFAS $1.7M settlement "resolved" | Aug 10 | Resolved — *and then what?* Town of private wells. |

Look at the verbs. **Underway. Advancing. Recruiting. Implementing.** Every entry is in
the present progressive and not one has ever been closed. We have spent four months
diligently writing down a town's open questions and have never answered a single one.

That list isn't a content gap. It's a content *backlog* we've been accruing since May
without noticing.

---

## The format

### **"Whatever Happened To…"**

Weekly. Short. One closed loop per issue, sometimes three.

> *Whatever happened to Article 44?*
> *Whatever happened to the revaluation?*
> *Whatever happened to the $10M open space article you voted on in March?*

Friendly, curious, faintly nosy — the register of a neighbor, not a newsletter. Every
entry is a question a resident has half-wondered and never had answered, and every entry
has a built-in sequel: when a thing finally resolves, that's the next issue.

**Why a resident who was in the room reads it:** they were in the room for the *decision*.
Nobody was in the room six months later. We're not telling them what they saw. We're
telling them how it turned out.

---

## Why this is the one that actually holds

**It's uncopyable, and the moat is time.** Any competitor can start a town newsletter
tomorrow. Nobody can start a four-month archive tomorrow. The asset here is that we have
been quietly keeping records since May — and a rival launching in September is four months
behind on day one and can never close the gap, because the gap is made of elapsed time.
That is the rarest kind of advantage available in local marketing, and we built it by
accident.

**It compounds instead of decaying.** Everything else we make loses value the moment a
figure expires. A closed loop is worth *more* later — it becomes the record. This is the
only content class we have that appreciates.

**It's stockpileable.** Seven ledger items are sitting in the table above right now. That
is seven weeks of LOCAL content available before anyone researches anything new — and it's
a real answer to the empty queue, which is now on week five.

**It earns the thing search can't buy.** You can't win 37 transactions a year with
relocation SEO. You win it by being the person who's clearly paying attention when nobody
is watching. This format *is* paying attention, performed weekly, in public.

---

## The mechanism — it attaches to the file you're building today

This is the part I most want your read on, because you're writing the sourcing gate right
now and it changes what one rule does.

You specified: **facts expire.** An event is publishable only while it's in the future; a
stale event gets blocked. Correct — and today an expired fact just gets deleted.

Don't delete it. **File it.**

> **An expired fact with no recorded resolution is not garbage. It is a ledger entry.**

That's the whole build. The gate already has to detect staleness to do its job. Have it
write what it expires into `OPEN-ITEMS.md` instead of dropping it, with its source and
date already attached — because your gate required those on the way in. Items leave the
ledger only when a sourced resolution closes them.

**The gate you're building to throw stale facts away becomes the engine that generates the
LOCAL content.** One file, two jobs, zero new production, and the sourcing discipline is
inherited rather than bolted on. The correctness machinery and the content machinery turn
out to be the same machine pointed in two directions.

---

## Guardrails, shipped with the idea

**1. Status, never verdict.** We report where a thing stands. We never say whether it
should have passed. *"Article 44 was rejected. Here is what it proposed and what the town
did instead."* Not one syllable on whether that was right. A real estate agent adjudicating
town politics is a career-ending format in a town this size — half your neighbors lose. This
is your own Fair Housing distinction (state the fact, never the verdict) applied to civics;
same rule, new domain.

**2. A town fact is a figure.** Already adopted Sept 2, and it governs here absolutely.
**Note that I have asserted no town fact in this document.** Every row above is a quotation
from our own digests plus an open question. The revaluation outcome, Article 44's content,
the open-space vote — I don't know any of them and I'm not guessing. They're research
assignments with a known source: Amherst selectmen minutes and town records, cited with
dates, per your gate.

**3. No CTA. Ever.** The moment "Whatever Happened To" ends with *"thinking of selling?"*
it stops being a service and becomes an ad, and a small town can smell that instantly.
The format's entire value is that it wants nothing.

**4. "We don't know yet" is a publishable answer.** If we can't close an item, we say so
and say what we asked. That's the loss-record principle that's already working in Jack's
newsletter — and it's what makes the loops we *do* close believable.

---

## What I'd need from you

Only a yes on the mechanism — the expiry-writes-to-ledger change, while the gate is still
soft. The first issue is already researchable from the table above; the revaluation is the
one I'd open with, because it touches every homeowner in Amherst and we've had it in our
files since May.

And credit where it's owed: this idea only exists because you pushed back instead of
accepting the Spark. "A correct-but-lifeless roundup is a zero, and it burns the slot" is
what killed my version and produced this one.

— Iris ✨
