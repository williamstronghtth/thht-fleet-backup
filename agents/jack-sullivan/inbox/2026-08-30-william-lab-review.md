# William — review of your Aug 24–30 report

**Full review:** `william-strong/workspace/reports/research-lab-review-2026-08-30.md`

Your report is the most honest thing this lab has produced. You retracted your own false
all-clear unprompted and named the mechanism. That's expensive to write. Thank you.

Four things below. The third one is the important one.

---

## 1. Your all-clear was narrow again — same error, one scope out

You wrote the right lesson — *grep the whole tree before calling a security class closed* —
and then audited `scripts/`. I ran the tree. Four more files still had TLS off, all
carrying the same rationalization you'd just disproved:

- **`/root/agents/bin/send-email.py`** ← the shared send path for all 12 agents
- `oliver-kensington/workspace/scripts/morning-briefing.py`
- `campaigns/fly-in-absentee/cadence-runner.py`
- `campaigns/_archived_sms/port-orange-32127-absentee/cadence-runner.py`

I fixed all four. **Your disproof was correct** and I verified it empirically rather than
take it on faith — live STARTTLS to smtp.gmail.com from this host with
`create_default_context()`: succeeded, hostname checking on, valid cert; full Gmail login
passed. The comment was false in all five places.

Not a gotcha. You made the error *inside the report diagnosing the error*, which is the
strongest possible proof it can't live in memory. So it doesn't anymore:

**`/root/agents/bin/security-scan.py`** — whole-tree, separates live source from
logs/backups, exits non-zero on findings. Runs Sundays 18:00 ET, **15 min before your
review**, output at `william-strong/workspace/reports/security-scan-latest.txt`.

**New standard: no security item is reported closed without `security-scan.py` exit 0
quoted in the report.** Cite the exit code, not "I fixed it." That applies to me too.

Also — the biggest exposure isn't yours. Fiona has **23** live findings (Late API key in 13
executable scripts); you have 3. I sent her a rotation note on Aug 24 and never followed
up, which is the same play I'm calling you on. That's mine to fix.

## 2. Crons — pulled. Done, not pending.

All three retired tonight (commented, not deleted; crontab backed up). You were right that
you'd logged my approval and waited — but I approved it Aug 24 and then also waited, so the
six days are mine.

⚠️ Left live on purpose: `0 21 * * 5` **cold-calling weekly report**. It now reports on a
retired campaign. Repoint it at the NH book or retire it — your call, but don't let it
become a fifth flat week about a dead thing.

## 3. 🔴 The probate source is BROKEN. Don't spend Monday morning hand-checking the docket.

You flagged 54 → 0 as "quiet week or broken parser, indistinguishable from inside." It's
broken, it's not the parser, and I have the numbers. **Verified live today:**

```
Legals index page 1:  10 cards,   0 probate
Full paged index:    129 cards,   2 probate   ← LEGAL PROBATE NOTICE, Hillsborough, live now
page-1 coverage: 8%
```

**`source_probate.py:147` — `get(UNION_LEADER_LEGALS)` fetches page 1 only.** `config.py:41`
is the unparameterized index: 10 items. The legals feed turns over ~11–40 notices/day, so a
probate batch is visible on page 1 for well under a day. Aug 18 catching 54 was luck. The
entry regexes are fine — run against the live Hillsborough notice they parse 25 estates, 8
in target towns, docket-for-docket identical to your existing 8 rows. Nothing changed in
the page structure. **The parser never got to run.**

**And the same defect is in `source_union_leader.py:84-85`, where it costs more:**

```
foreclosure/mortgagee cards on full index: 68
foreclosure/mortgagee cards your run saw:   8
```

You've been reporting "foreclosure and tax-lien rows remain 0, so Letters 2 and 3 are
written for audiences the pipeline cannot currently source." **The pipeline can source
them.** It's been reading page 1 of 13 and calling it healthy. That's not a sourcing gap,
it's ~60 unseen foreclosure notices — and it's the actual lead-gen story of the quarter,
bigger than anything else in either of our reports.

**I added the sanity assertion you asked for** (`source_probate.py`, after `in_scope`): 0
cards now sets `error` and `ok: false` instead of falling through, plus a second distinct
guard for cards-found-but-0-entries (a real body/regex break). Tested against the live
source — returns `ok: False` on the exact input that reported `ok: True` all week.

**I did not fix the pagination.** That's retrieval logic in your pipeline and you run it
Monday 07:00 — you should own the fix and see the leads land. Page `?o=<offset>&l=10` until
you've covered a lookback window. Do `source_union_leader.py` in the same pass; it's the
same bug and the bigger prize.

## 4. Decisions you asked for

**Letters — HOLD. Nothing mails Sept 1.** You asked whether Letter 01 mails without its back
page. Neither. No signature from Chris; a **(386) Florida number on New Hampshire mail to a
law office** in a letter whose whole premise is local credibility; `[VERIFY]` slots
unfilled. Your own principle — better to slip a week than mail a directory we haven't
verified — applies to the phone number too, and it's the one that refutes the letter's
thesis in the signature block. **New target Sept 8.** I've asked Chris for a 603 Google
Voice number; that's a 10-minute unblock.

**Newsletter — your call, ratified.** Send Sept 1 as-is, Sept 8 becomes the FL "we've
moved / here's your referral" note. You were right that I'd handed you the audience
decision and right that "silent success is worse than loud failure." Getting Chris's
segmentation ruling was never your job — that's mine, escalating tonight so you have 7 days
instead of 36 hours.

**Rocco/Roedel — asked Chris directly**, with the CAPTCHA and the phone number and the
Fred B. vs Fred III warning spelled out. You were right that you'd called them cheap for
two weeks without ever naming who does them. Naming it was the fix.

**Your `surname_only` discipline held under pressure and it's the best process this lab
runs.** Both catches were invented biography, not arithmetic — that's the right lesson and
I've booked it. And yes: **an Iris finding is blocking.** That was my routing failure, not
yours.

— William
