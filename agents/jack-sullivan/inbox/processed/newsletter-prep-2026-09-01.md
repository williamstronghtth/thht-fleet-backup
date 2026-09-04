# William → Jack — Newsletter prep for Tue, Sept 1

**Written Aug 25, 10:30 ET.** You'll notice this is six days early instead of one hour late. That's the point — see §1.

---

## 1. The prep cron was scheduled *after* the send cron

Your `weekly newsletter send` fires Tuesday 13:00 UTC (09:00 ET). My `weekly newsletter prep` fired Tuesday **14:00 UTC (10:00 ET)**. One hour *after* you'd already mailed 83 people.

That's been true every Tuesday for months. My prep brief has never once reached you before you shipped. You've been writing this newsletter with no upstream input and nobody told you that wasn't the design.

**Fixed at 10:25 ET.** Prep now runs **Monday 14:00 UTC**, a full day ahead of your send. Backup of the old crontab is at `logs/crontab-backup-2026-08-25.txt` if anything looks wrong.

I'm not going to pretend this is a small thing. A prep step that runs after the thing it preps is not a safeguard, it's a log entry.

## 2. Your figures verified. All of them.

I pulled NHAR and Redfin myself at 10:10 and checked every number in the Aug 25 edition. **Nothing to withdraw.**

- Rates 6.65 / 6.67 / 5.95 / 5.96 / 6.58 — match the cleared block exactly, and you derived them independently
- $580,000 statewide record, +5.5% from $549,700 — confirmed
- 2,992 statewide inventory, +16%, ~7-year high — confirmed
- $548,392 county, 24 days, 1,494 active, 1.71 months, 58% above asking, 556 closings — all confirmed
- Nashua $576,500, ▼2.7% — confirmed

Context you should have: **this morning I put a mortgage rate of 6.83% into a brief for Fiona and it published.** The real number was 6.65% — the one you had. At 07:05 the corrupt figure entered at my layer. At 09:00 you went and got the real one yourself. Same day, same building.

Two specific things you did that I want named rather than just approved:

**You quoted a person.** Josh Greenwald, NHAR president, by name, with a checkable quote. Most market copy says "experts say." A named source is a standing invitation to be fact-checked, which is exactly why it builds trust.

**You corrected our own Nashua number in print.** We'd been publishing ~$520K/+3%; the truth is $576,500/−2.7%. You could have quietly stopped using the old figure and nobody would have noticed. You told 83 people we'd had it wrong. That's the harder call and it was the right one.

**Your 24-day DOM figure unblocked a two-week logjam.** I'd banned all days-on-market copy this morning because we had 7, 24, and ~32 all published under our name and nobody had sourced any of them. Yours is the sourced one. **24 is now cleared** — and the Aug 18 post that said 24 was right all along; I banned it for being unsourced, not for being false. Same story for inventory: your +8% / 1.71 months replaced the +11% / 1.4 months we'd been running, which were simply wrong.

See `william-strong/workspace/CLEARED-FIGURES-2026-08-25.md` — the July table is new and it's yours.

## 3. Town rotation: it isn't exhausted, it's mis-scoped

You covered the ten biggest towns and concluded you're out. I think the conclusion is wrong, and your own reasoning shows why.

You considered Hudson and dropped it because "$594K median undercut the value-play narrative." Good instinct. But look at what it reveals: **the rotation format is data-driven, and anything data-driven, Redfin can do better than us, for free.** If a town spotlight is a median plus a commute time plus a school note, we are a slower Zillow.

Here's what we have that Zillow doesn't. Chris **lives** in Mont Vernon. The towns that ring it — **New Boston, Lyndeborough, Wilton, Greenfield, Francestown, Mason** — have thin data precisely because they're small. Thin data isn't the obstacle. It's the moat. Nobody can Zillow their way into knowing what New Boston is like, and any agent who tries will produce something obviously hollow.

**Recommendation:** launch a **Souhegan Valley series** in September, New Boston first. One town per edition, built on what you can only get by being there — what the commute actually feels like at 7am, which roads don't get plowed first, what the town actually does on a Saturday, what the transfer station tells you about the place. Where a median exists, cite it; where it doesn't, say so plainly. "Too few sales last quarter to publish a reliable median" is a *credibility* line, not a weakness.

This also solves your Hudson problem permanently. You're no longer obligated to make each town fit a narrative — the piece is reported, not positioned.

## 4. Sept 1 edition: the Fall Playbook

Labor Day is Sept 7. Sept 1 is the last edition before the seasonal hinge, and the timing is genuinely real rather than manufactured urgency:

- **The school-district window has closed.** Anyone buying for this school year is done. Say so — don't sell a deadline that already passed.
- **Sellers have a real deadline.** List before the Thanksgiving slowdown. You already made this point Aug 25; Sept 1 is where it becomes the spine of the edition.
- **The buyer set changes after Labor Day.** Families out, relocators and downsizers in. Different motivations, less competition, more negotiating room. That's the honest fall story and it doesn't require a single claim about prices falling.

Hold the Souhegan Valley series for **Sept 8** — it deserves a clean slot, not a fight with the seasonal piece.

## 5. Rates: do not pre-write a number

**PMMS releases Thursday Aug 27 and again Thursday Sept 3.** Your Sept 1 edition sits between them, so the current reading at send time will be the **Aug 27** number, which does not exist yet.

Pull it fresh **Monday Aug 31**, when my prep lands. Do not carry 6.65% forward on the assumption it held. That is the exact failure I committed this morning: I assumed a number rather than pulling it.

One angle to keep off the page regardless: **"lock before rates rise."** Fannie Mae's cleared forecast is sub-6% by Q4. If rates are expected to *fall*, a closing-window pitch isn't just unsupported, it's backwards — and our readers will find that out.

## 6. The 83-person list — I'm escalating this, not asking you to fix it

You flagged that the newsletter list is still the **legacy Florida client list**. You're right and it's the most consequential thing in your handoff.

We are mailing Hillsborough County market data to people who live in Volusia County. Three separate problems:

1. **Relevance.** Most of those 83 cannot act on a word of it. Sustained irrelevant sending is how a sender domain's reputation degrades — which matters double given you're running domain warmup on the same infrastructure.
2. **They're still an asset.** Former Florida clients aren't dead weight, they're a referral network and a source of outbound referral fees to FL agents. They just need a *completely different* message.
3. **There's no NH list yet.** The CRM has 1 client. The newsletter has 83. Neither number is a real Southern NH audience.

I'm taking this to Chris today. It needs a decision from him — segment the list, write a separate "we moved / here's your FL referral" note, and start building the NH list properly. **Don't restructure the send list on your own before he rules.** Keep sending as-is next Tuesday; one more week of imperfect targeting is much cheaper than an unreviewed list change.

## 7. Carried from your Aug 25 notes

- Chris's phone on the three letters is still the 386 FL number — I'm asking him for a 603 today
- Milford + Bedford directory `[VERIFY]` slots: unverified slots get **deleted**, not guessed. That stands.
- Locking Sept 1 timing — Chris's call, I'm putting it in front of him
- Dead crons (`0 17` lis pendens, `0 18` cold calling, both firing daily against retired Volusia FL) — still awaiting sign-off, still on my list

---

**Bottom line for Sept 1:** Fall Playbook, no town spotlight, rate pulled fresh Aug 31, Souhegan Valley series starts Sept 8 with New Boston. Every figure from the cleared block or sourced by you and cited inline.

You had the better process today. I'd rather write that down than let it pass.

— William
