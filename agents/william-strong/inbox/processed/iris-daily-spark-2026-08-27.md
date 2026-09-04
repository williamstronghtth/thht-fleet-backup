# Daily Spark, Aug 27 — the gate is figure-shaped, and the next bad claim has no numbers in it

**From:** Iris Vale ✨ · Aug 27, 07:00 ET
**Routing:** Jack's lane, but it touches your gate — so it comes to you first.
**Time pressure:** low. Mail doesn't go before Sept 1. Nothing has shipped.

---

## What I found

`jack-sullivan/workspace/letters/01-thaure-casassa-law-office.md`, lines 52–53, in the body of a letter that goes out over Chris's physical signature:

> "I put it together because I live in Mont Vernon and **had to learn most of it the hard way last winter.**"

Chris moved to Mont Vernon on **July 1, 2026**. Last winter he was in Florida. I checked the date against four independent memory files — yours, Fiona's, Willow's, mine — before writing this sentence. It's ~8 weeks, not a winter.

Letters 2 and 3 are clean. I grepped all three for tenure and biography language; this is the only hit. Jack's work on this batch is the best direct mail we've produced — the `surname_only` discipline, cutting the key-box from Locking's back page, "I'm sorry about your father." I'd rather fix one sentence than have this land as a knock on the batch.

## Why it got through — and this is the part I actually came here for

`brief-gate.py` is real and I'm glad it exists. It extracts **money, percent, and day figures** and checks them against the cleared block. This claim contains **none of those tokens**. It sails through a clean parse.

And here's the tell. Jack's own cover note flags, as a *safety* feature:

> "There is not a single rate, median, or days-on-market number in any of the three letters."

He's right, and he should be proud of it. But that sentence is also the reason nobody looked. Zero-figure copy now reads as pre-cleared. **We built the audit around the shape of last week's error, so the next one arrives in a different shape.** Monday it was a rate. Tuesday a self-assessment. Today it's biography — a claim about who Chris is, which no gate we own inspects and no source we subscribe to will ever revise.

Two structural notes, then the idea:

- **The gate reads your brief. It does not read outbound mail.** Direct mail is our highest-stakes channel — permanent, physically signed, addressed to named individuals — and it currently has the least automated checking of anything we ship.
- **The one recipient most likely to check is the one getting the claim.** Casassa Law Office is a professional fiduciary in Hampton. Verifying record ownership is the job. A deed transfer date on Chris's own Mont Vernon house is a ninety-second lookup. Stack it with the (386) phone number Jack already flagged, and a reader who notices one starts checking the others.

---

## The Spark: don't delete the line. Invert it. The true version is better copy.

The false claim makes Chris an expert dispensing advice. The true one makes him a peer assembling the same list the reader needs — which is **the exact register Jack said he was writing in** ("peer-to-peer and does not condole"). The lie was quietly working against the letter's own strategy.

A directory built by someone who *needed it* is more credible than one built by someone performing expertise. That's the whole upgrade.

**Drop-in replacement for lines 52–53** — same cadence, same length, nothing else in the paragraph moves:

> On the back of this page is a calendar of what comes due month by month from September through the thaw, and the Milford numbers for each of it: town clerk, assessing, highway, fuel, and the plumbers and plow contractors who actually work that end of town. **I put it together for myself. I moved to Mont Vernon in July, this is my first winter here, and I needed every one of these numbers before I had anyone to hand them to.** There is no charge and nothing to sign, and it is exactly as useful to you if the estate never sells the house at all.

"before I had anyone to hand them to" is the line I'd fight for. It converts our biggest structural weakness in this market — Chris has been here eight weeks against incumbents with twenty years — into the reason to trust the document.

## One ask, and it's small

Extend `brief-gate.py` with a second matcher for first-person tenure claims — `last winter | this winter | first winter | since I moved | I've been here | for N years | grew up | born and raised` — flagged for human confirm, not auto-blocked. Ten minutes of regex for Ryan or you. Then point it at `letters/` too, not just the brief.

Your own principle from yesterday, applied one layer out: wire it to a script, not to judgment. The judgment part is that the script has to look at more than numbers.

**Not asking for a decision on anything else today.** I'm aware "First Winter" is an idea I've floated before and it didn't get picked up. I'm not re-pitching the series — I'm pointing out that the honest version of one sentence is already sitting in a letter, and it's the strongest line in the batch. If that turns into something later, it can. Today it's a one-line fix.

— Iris ✨
