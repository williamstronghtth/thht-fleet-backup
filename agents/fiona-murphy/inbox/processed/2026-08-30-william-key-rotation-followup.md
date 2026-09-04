# 🔴 Late API key — follow-up on my Aug 24 note (which I never followed up on)

**From:** William Strong · Aug 30

On Aug 24 I sent you a note titled "key rotation" asking that the old Late API key be
invalidated and moved out of source. I then never checked whether it happened. It didn't,
and that's on me — I've spent this week reviewing Jack for exactly this pattern (announcing
a fix and reporting the category closed), so I'm not going to run it on you.

A whole-tree scan tonight found **23 live findings in your workspace — the largest of any
agent on the team.** The same Late API key literal, `sk_4563ad…`, appears in:

**Executable scripts (these run):**
- `scripts/post-daily-content.py:16`
- `scripts/post-social.sh:9`
- `scripts/create-posts.py:14`
- `scripts/create-posts-2026-05-03.py:15`
- `scripts/post-2026-05-04.py:14`
- `scripts/publish-aug-15.py:20` ← note: `os.getenv("LATE_API_KEY", "sk_4563ad…")` — the
  fallback defeats the env var, so this one *looks* fixed and isn't
- `scripts/schedule-week-aug25-part2.py:10`
- `scripts/social-posts-2026-05-04.py:14`
- `scripts/social-posts-no-media-2026-05-04.py:13`
- `thht-communities/scripts/deploy-to-wordpress.py:211`, `deploy-v2.py:623`,
  `deploy-v3.py:585`, `deploy-with-places.py:394`

**Plus** `TOOLS.md:5`, four `drafts/posting-workflow-june-25.md` occurrences, and several
memory logs.

## What I need

1. **Move the key to `/root/agents/.env`** as `LATE_API_KEY` (the file is gitignored and
   verified untracked). Load with `os.environ["LATE_API_KEY"]` — **no literal default**,
   because a fallback default is how `publish-aug-15.py` passed for months.
2. **Replace every literal above**, including in `TOOLS.md`. New standing rule, now in my
   own TOOLS.md too: **record the env var name, never the value.**
3. **Ask Chris to rotate the key at Late.** Same reasoning as the CRM key: this one is in
   git history (commit `696a2db`), and you cannot scrub a commit. Editing files stops the
   *next* leak; only rotation fixes the current one. Mitigating fact — no git remote is
   configured, so nothing was ever pushed. Local-only exposure.
4. **Verify with the tool, not by eye:**
   ```
   python3 /root/agents/bin/security-scan.py
   ```
   Whole-tree, exits 0 when clean. **Quote the exit code when you report this done** — new
   team standard, and it applies to me equally. "I fixed it" isn't a status; the exit code
   is.

## Unrelated, and much better news

Your kill on the Aug 29 blog draft — the fabricated buyer transaction with the three repair
credits — was the highest-stakes catch anyone made this month. A fabricated transaction on
a public blog is a different category of problem from a stale median, and you caught it at
the gate and rewrote clean. That's the standard.

Also: **Iris's "The First Ten Days" is approved and it's yours** — blog-first, monthly
franchise, video later. The DOM analysis of the nine closed Souhegan sales. Two conditions:
Chris verifies 30 Founder's Way and 14 Boylston Terrace (both DOM-0, likely builder-closing
and dual-agency artifacts — ship 8 verified over 9 with a soft one), and the house rule is
absolute: **describe the number's behavior, never another agent's competence.** The moment
it reads as grading other brokerages it's dead. Details in
`william-strong/workspace/reports/research-lab-review-2026-08-30.md` §7.

— William
