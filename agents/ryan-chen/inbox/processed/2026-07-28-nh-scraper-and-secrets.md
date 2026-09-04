# From William — 2 tasks, 2026-07-28

Priority order below. #1 is the unblock for the whole NH restart.

## 1. Prototype a FREE Hillsborough County lead scraper (HIGH — unblock)
The NH pipeline is stuck because we've been waiting on a RedX/Vortex (paid)
vs. build decision for weeks. Let's just build the free path and remove the
dependency on that decision.

**Goal:** a script that pulls recent property/owner records from public NH
sources so Jack has real leads to work. Candidate sources (public, free):
- Hillsborough County Registry of Deeds (recent deeds/transfers)
- Hillsborough County Superior Court (Lis Pendens / foreclosure filings)
- Town assessor databases (Mont Vernon, Amherst, Milford, Nashua, Bedford,
  Merrimack, Hollis, Brookline)

**Deliverable for today:** a working proof-of-concept that returns even
15–20 structured records (name, address, event type/date) from ONE source.
Don't build the whole thing — prove one source is scrapeable and estimate
effort for the rest. Report back what's feasible vs. gated (captcha, paywall,
ToS). If a source is truly blocked, say so plainly so we know RedX is the
only path.

**Constraint:** respect robots.txt / ToS. If a source prohibits scraping,
flag it, don't proceed on it.

## 2. Remediate hardcoded secrets (SECURITY — overdue since 7/23)
The WordPress app password is hardcoded in ~6 legacy scripts under
`jack-sullivan/workspace/scripts/` (cadence-engine.py, email-outreach.py,
send_divorce_probate_emails.py, flyin-campaign.py, mosaic-campaign.py,
load-*-to-crm.py) and in TOOLS.md.

- Move all secrets to env vars (`os.environ[...]`), reference via `.env`.
- Confirm `.env*` is gitignored.
- Report the exact list of files/secrets so Chris can ROTATE the password
  (rotation is his call — just prep the list).

Reply to my inbox or ping me when #1 has a verdict. Thanks — William
