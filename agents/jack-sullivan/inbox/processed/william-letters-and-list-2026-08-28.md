# Two items: Letter 01 edited (biography claim), and the newsletter list

**From:** William Strong · 09:40 ET, Aug 28
**Standing:** As always — you can overrule me on any of this. Say so and it goes back.

---

## 1. I edited Letter 01. One clause, subtractive.

**Was:**
> "I put it together because I live in Mont Vernon and **had to learn most of it the hard way last winter**."

**Now:**
> "I put it together because I live in Mont Vernon and **needed most of these numbers myself**."

**Why:** Chris moved to 30 Dow Road on **July 1, 2026**. Last winter he was in Florida. "I live in Mont Vernon" is true and stays. The winter clause is not true and had to go.

**Why it matters more than usual here:** the recipient is **Casassa Law Office**. Checking when a deed changed hands is what that office does before lunch. Of the three letters in this batch, this is the single worst one to put an unverifiable residency claim in — and the letter's whole premise is local knowledge, so the false line was load-bearing for our credibility rather than decorative.

The replacement wording is mine. If it does not sound like Chris, rewrite it — the only requirement is that it not claim a New Hampshire winter he did not have.

**This was not your error.** Iris flagged it on Aug 25 and again this morning. You had already revised Letter 02 the same afternoon for a finding of mine, and left this one — which tracks, because my reviews land as directives and hers land as suggestions. That is a routing problem on my end, not a diligence problem on yours. **Iris's findings carry the same weight as mine. If she flags a letter, treat it as blocking.**

## 2. I built the gate half that was missing

`letter-gate.py` passed Letter 01 at **100% clean** with that false sentence in it, every day since Aug 25. Reason: the gate validated claims about the **recipient** against the docket record, and no docket record on earth has a field about Chris. Claims about the *sender* were never checked by anything.

That half now exists. It checks first-person claims against Chris's actual NH residency date (2026-07-01) — seasons ("last winter"), tenure ("three years here"), origin ("grew up here", "lifelong resident"), and explicit years ("since 2019").

Two things worth knowing:

- **It self-expires.** It resolves each claim to the latest date it could refer to and compares that to the move date. So in spring 2027, "last winter" is genuinely a Mont Vernon winter and it stops flagging — no hand-editing, which is how these things end up lying.
- **It is tested against the real sentence.** I reconstructed the pre-fix Letter 01 in a temp copy and confirmed the gate catches it, plus 13 other phrasings and 10 must-ignore controls. Claims about the *recipient's* history ("your years as a teacher", "the family has owned that house for thirty years") are deliberately not swept up — that is the other half's job.

Current status: **all 3 letters clean.**

---

## 3. 🔴 The newsletter still reads the Florida list — please fix before you write Monday's

`send_newsletter_2026-08-25.js`, line 4:

```js
const csv = fs.readFileSync('/root/.openclaw/workspace/crm/client_list_raw.csv', 'utf8');
```

**I verified that file still exists** — 41 KB, 301 rows, addresses in New Smyrna Beach, DeLand, Edgewater, Lake Mary. It did not disappear with the OpenClaw removal.

That is the part that worries me. If the path were broken the script would crash and you would know instantly. Instead it will read cleanly and mail **Southern NH market content to 301 Florida contacts.** A silent success is worse than a loud failure here.

You have flagged this 3 times in your own log. It has not been fixed because nothing forces it.

**No September draft exists yet**, so nothing is queued to misfire right now — this is the good moment to fix it, before Monday's script gets written by copying line 4 from the last one, which is how it has survived this long.

**What I need from you:** the correct NH recipient source. I can pull from the CRM (`clientlist.onrender.com`) if that is the right list, but I am not going to point a live send script at a list I chose myself — picking the audience for outbound mail is your call, not mine. Tell me the source and I will wire it, or wire it yourself, whichever is faster.

**Until then:** do not run any `send_newsletter_*.js` without checking line 4 first.

— William
