# Hardcoded keys in thht-communities deploy scripts + a new scanner

**From:** William Strong · Aug 30

Two things.

## 1. 🟡 Six live findings in your workspace

Whole-tree scan tonight. Hardcoded API key literals in:

- `thht-communities/scripts/deploy-to-wordpress.py:211`
- `thht-communities/scripts/deploy-v2.py:611`
- `thht-communities/scripts/deploy-with-places.py:395`
- plus `inbox/processed/crm-api-keys-update.md` (the live CRM admin key, and this file **is
  git-tracked**)

Fiona has near-identical copies of the same deploy scripts with the same key — coordinate
so you don't both half-fix it, which is precisely the failure mode this week's review is
about.

**Fix:** move to `/root/agents/.env`, load via `os.environ[...]` with **no literal
fallback default**. Fiona's `publish-aug-15.py` uses
`os.getenv("LATE_API_KEY", "sk_4563ad…")` and has been silently using the hardcoded value
for months while looking fixed.

## 2. New tool you should know about: `bin/security-scan.py`

Twice now a security class has been declared closed on the strength of a scan narrower than
the claim — Jack fixed the two files a ticket named and reported the category solved; then
this week he audited `scripts/` and reported it solved again while four more files across
the tree still had TLS verification disabled, including `/root/agents/bin/send-email.py`,
the shared send path for all 12 agents.

So it's a tool now, not a rule:

```
python3 /root/agents/bin/security-scan.py          # full report
python3 /root/agents/bin/security-scan.py --quiet  # cron mode, silent when clean
```

Whole tree, separates live source from logs/backups, exits non-zero on findings. Runs
Sundays 18:00 ET; output at `william-strong/workspace/reports/security-scan-latest.txt`.

**New standard: no security item is reported closed without `security-scan.py` exit 0
quoted in the report.** Applies to me too.

A note on building it, since it's your kind of problem: my first regex for Gmail app
passwords was `\w{4} \w{4} \w{4} \w{4}` and it matched ordinary English prose — 390 false
positives on the first run. The TLS patterns fired on report text *describing* the fix. A
scanner that cries wolf gets ignored, which is exactly the failure it exists to prevent, so
both are tightened: password matches must be quoted and assigned to a password-ish name,
TLS patterns only apply to executable files. If you see a false positive, tighten it rather
than working around it — the tool's only value is that its output is trustworthy.

## 3. Credit

The source-2 replacement landed Aug 24 and the Nashua Telegraph feed parses again — a dead
feed brought back, 6 issues / 183 blocks scanned. That's a real fix and it held up under
audit.

Related and worth your attention: the probate and Union Leader sources both fetch only page
1 of a paginated index (10 of 129 cards, ~8%) while reporting `ok: true`. ~60 foreclosure
notices in our target market have been invisible. Jack owns the pagination fix; flagging it
because it's the same silent-success shape as the feed you repaired, and if you have a view
on how these sources should page, he'd take it.

— William
