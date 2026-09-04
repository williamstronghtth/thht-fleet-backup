# Research Lab Weekly (Aug 24–30) — and a correction to last week's report

**From:** Jack Sullivan · Sun Aug 30, 18:15 ET
**Full report:** `jack-sullivan/workspace/briefs/research-lab-weekly-2026-08-24-30.md`

---

## The thing you should read first

**Last week's report contained a false all-clear that I wrote.**

On Aug 24 you told me to fix `cadence-engine.py` — hardcoded CRM key, TLS verification
disabled — under default-to-action. I fixed that file and `email-outreach.py`, and reported
the security items closed.

I audited the whole `scripts/` tree today for this review. The same live CRM key was still
hardcoded in **five** files, and TLS verification was still disabled in **three**:

- `load-port-orange-absentee-to-crm.py`, `load-lis-pendens-to-crm.py`,
  `send_divorce_probate_emails.py`, `flyin-campaign.py`, `mosaic-campaign.py` — key
- `flyin-campaign.py`, `mosaic-campaign.py`, **`cold-calling-sequence.py`** — TLS

`cold-calling-sequence.py` runs daily on cron. It also carried a comment rationalizing the
disable: *"Hostname check trips on this server's OpenSSL 3.0 … disabling is acceptable
here."* That's false — `cadence-engine.py` has used `create_default_context()` against the
same `smtp.gmail.com` from this host since Aug 24 with zero auth failures. I replaced the
comment with the disproof so it doesn't get re-added.

**All eight fixed this session** via `secrets_loader.require()` + `ssl.create_default_context()`,
re-scanned clean, syntax-checked, and `cold-calling-sequence.py` smoke-tested live.

I fixed the two files the ticket named and reported the *category* solved. It sat six days
behind a green check mark. My rule going forward: grep the whole tree for the pattern before
calling a security class closed, and report file counts rather than "fixed."

**🔴 Still needs someone with admin: rotate the key at `clientlist.onrender.com`.** Day 9.
The source tree is clean now but the key is still burned — it appears verbatim in 8
non-source files across four agents' workspaces (memory logs, your `TOOLS.md`, inbox notes).
Scrubbing those is theater; rotation is the fix.

---

## The newsletter list — I had your instruction backwards, and you were waiting on me

My daily log has been repeating "William says keep sending as-is, don't restructure the
list." That's your Aug **25** note (§6). Your Aug **28** note supersedes it: *"picking the
audience for outbound mail is your call, not mine. Tell me the source and I will wire it."*

You've been waiting two days for an answer from me. Here it is.

**I verified the file today: 296 rows, 94 unique emails, last modified June 3, addresses in
New Smyrna Beach / DeLand / Edgewater / Lake Mary.** Confirmed legacy Florida.

**There is no NH list to point at.** The CRM has 1 client and is auth-gated. So:

- **Sept 1: send as-is.** Your Aug 25 call was right and it's 48 hours out — an unreviewed
  list change now is worse than one more week of bad targeting.
- **Sept 8 is the last one that goes to this list.** Either Chris rules on segmentation this
  week, or I write the FL contacts a separate "we moved / here's your FL referral" note and
  take them off the NH rotation. I'll wire it; I'm not letting it reach week 8 as a bullet.

---

## Letters — delivered, clean, and two catches that weren't mine

3 mailable letters + cover note, 4 templates, `MATCHING-RULES.md`. `letter-gate.py` verified
today: **3 letters, 8 source records, CLEAN.**

Your Letter 02 kinship catch and Iris's Letter 01 residency catch were both right, and I'm
booking the pattern: **both errors were invented biography, not bad arithmetic.** My cover
note offered "not a single rate or median in these letters" as a safety feature — it was,
against last month's failure. Both of these would have passed at full confidence.

And your routing note landed. **Iris flagged Letter 01 on Aug 25; I revised Letter 02 the
same afternoon for a finding of yours and left hers.** Treating her findings as blocking
from here.

---

## 🔴 Sept 1 is Tuesday. Three things block the mail.

1. **Chris's signoff** — not received.
2. **A 603 phone number** — all three letters carry (386) 273-3460. Florida area code, New
   Hampshire mail, and Letter 01's recipient is a law office whose whole job is checking
   that kind of thing.
3. **Milford + Bedford `[VERIFY]` directory slots** — still unfilled. Standard stands:
   unverified slots get deleted, not guessed.

**My call: if 2 and 3 aren't resolved Monday, Letter 01 mails without its back page or it
doesn't mail.** The back page is the entire reason the letter survives contact with a
wastebasket. I'd rather slip a week than mail a directory we haven't verified.

---

## Two asks, both small

1. **A human for ~15 minutes.** ROCCO (Lyndeborough Avitar kiosk — free guest login behind
   an image CAPTCHA, ~2 min in a browser) and ROEDEL (call Wilton assessing, 603-654-9451;
   ⚠️ verify Fred B. vs son Fred III). Takes confirmed addresses from **2/8 to 4/8** before
   mail date. I've called these "cheap wins" two weeks running without ever naming who does
   them. Naming it now — I can't get past the CAPTCHA and I shouldn't be cold-calling a town
   office as Chris.
2. **One line on the crons.** Pull `0 12,14,16,18,20,22` (domain warmup — you approved
   retirement Aug 24, it fired ~42 more times this week), `0 17` (lis pendens, day 188), `0
   18` (cold calling, day 143). Escalation is live with Chris from the Aug 28 report;
   re-raise trigger is Sept 4. Not asking again before then — flagging that I logged your
   approval and then waited, which was my error, not a queue problem.

---

## Two things I did rather than recommend for a third week

- **exp-004 registered** in `experiments.jsonl` — hypothesis, controls, success metric
  (replies per letter mailed), blocking items.
- **`current-config.json` rewritten for NH.** It wasn't just stale, it was actively wrong:
  `primary_channel` was email, and `never_mention` listed `["divorce","probate","death"]` —
  a rule forbidding the exact campaign we're about to mail. FL version backed up.

exp-002 and exp-003 both ran and lost their outcome data. exp-004 shouldn't make three.

---

## One number I don't like

The Hillsborough probate source returned **54 docket entries on Aug 18** and **0 on Aug 24**,
reporting `ok: true` both times. Monday and Thursday runs both fired clean; 0 new leads,
still 8 rows.

A quiet week is plausible. A parser that silently started returning empty is also plausible,
and they're indistinguishable from inside the pipeline. **I'm checking the docket by hand
before Monday's 07:00 run**, and adding a sanity assertion — a source returning 0 twice
running should raise, not report healthy. Otherwise we report "no new leads" for a month and
it's actually a broken feed.

— Jack
