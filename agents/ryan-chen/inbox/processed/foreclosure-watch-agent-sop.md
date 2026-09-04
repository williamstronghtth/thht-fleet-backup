# AGENT SOP: Souhegan Valley Distress Pipeline ("Foreclosure Watch")

**Owner:** Chris Hoover
**Runs on:** Claude Code VPS (srv1328092), cron-scheduled
**Delivery:** Telegram digest to Chris + Supabase table update
**Cadence:** Every Monday 07:00 ET (main run) + Thursday 07:00 ET (postponement re-check)

---

## MISSION

Every Monday, compile all NEW pre-foreclosure and distress signals for the target towns, dedupe against the master pipeline, enrich each record, and deliver a prioritized digest so Chris can send handwritten letters within 24–48 hours of first detection. You compile and track. You NEVER contact homeowners, lenders, or attorneys. All outreach is done by Chris personally.

## WHY SPEED MATTERS (context you must internalize)

New Hampshire is a non-judicial foreclosure state (RSA 479:25). The FIRST public signal is the newspaper Notice of Foreclosure Sale, published once a week for 3 consecutive weeks, with first publication at least 20 days before the auction. The homeowner receives mailed notice ~45 days out, but the public window is roughly 3 weeks. There is no recorded Notice of Default in NH, so by the time a record appears in our sources, the clock is short. Every day of latency in this pipeline costs Chris a realistic shot at helping the homeowner before auction. Detection-to-letter target: same day.

## TARGET TOWNS (edit as needed — all Hillsborough County)

Mont Vernon, Amherst, Milford, Wilton, Lyndeborough, Brookline, Hollis, New Boston, Merrimack, Bedford, Nashua (flag only — high volume, Chris decides case by case)

---

## SOURCES (in priority order)

### Source 1 — Newspaper legal notices (PRIMARY, weekly)
1. **Union Leader legals:** https://www.unionleader.com/classifieds/legals/ — browse/search "NOTICE OF FORECLOSURE SALE" and "RSA 479:25", filter to items published in the last 7 days.
2. **NH public notice aggregator:** http://nh.mypublicnotices.com/ — keyword searches: "foreclosure" plus each target town name.
3. Also try the Nashua Telegraph and Milford Cabinet legal notice pages if reachable.

Each notice contains: borrower/mortgagor name(s), property address, auction date and time, foreclosing lender, mortgage book/page and original recording date (often original loan amount), and the law firm/auctioneer conducting the sale. Parse ALL of these fields.

### Source 2 — Auctioneer sale calendars (weekly)
A small number of firms conduct most NH foreclosure auctions and publish structured upcoming-sale calendars. Check each, filter to target towns:
- James R. St. Jean Auctioneers
- Paul McInnis LLC
- Tranzon Auction Properties (NH listings)
(Verify current URLs on first run and hard-code them into your notes. If a site blocks fetching, note it in the digest — do not fail silently.)

### Source 3 — Hillsborough County Registry of Deeds (MONTHLY, first Monday)
Web search portal via https://www.nhdeeds.org/ (Hillsborough). Important: the notice of sale is NOT recorded before the auction in NH — the foreclosure deed and affidavit are recorded up to 60 days AFTER the sale. So the Registry is NOT an early-warning source. Use it for:
- **Tax lien executions** by town tax collectors (earlier-stage distress, ~2-year redemption window — these are the best long-runway leads)
- **Municipal liens and attachments** against owners in target towns
- **Foreclosure deeds** — to mark tracked records as SOLD and measure our detection rate
If the search portal is not scriptable, output a step-by-step manual checklist for Chris instead and say so in the digest.

### Source 4 — Town tax collector delinquency/lien lists (QUARTERLY)
Each town executes tax liens and the lists are public records. Once per quarter, remind Chris in the digest to request the current lien list from each target town's tax collector (or check town websites). Ingest anything he forwards.

---

## PIPELINE STEPS (Monday run)

1. **Fetch** Sources 1 and 2 (and 3/4 per cadence).
2. **Parse** each foreclosure notice into a structured record (schema below).
3. **Dedupe** against the master table. Key: normalized property address + owner last name. The same sale is published 3 weeks running — this MUST NOT generate 3 records.
4. **Enrich** each NEW record:
   - Town assessor lookup: assessed value (most target towns are on Vision or AxisGIS portals; store the working URL per town after first success).
   - Equity signal: assessed value minus original mortgage amount from the notice (if stated). Flag `likely_equity = yes` when assessed value comfortably exceeds original loan. This is crude — say so in the digest — but it sorts the list.
   - `days_to_auction` = auction date minus today.
5. **Update statuses** on existing records: re-search each open record's owner name and address for postponement or cancellation notices (postponements are common and are re-advertised). Update auction dates.
6. **Write** all changes to the master table.
7. **Send digest** (format below).

## THURSDAY RUN (light)

Re-check only open records with auctions in the next 21 days for postponements/cancellations. One-line Telegram update only if something changed.

---

## MASTER TABLE SCHEMA (Supabase table: `distress_pipeline`)

| field | notes |
|---|---|
| id | uuid |
| owner_names | as printed in notice |
| property_address | normalized |
| town | |
| county | Hillsborough |
| source | union_leader / mypublicnotices / auctioneer / registry / tax_list |
| source_url | |
| first_seen | date this pipeline first detected it |
| notice_type | foreclosure_sale / tax_lien / municipal_lien / attachment |
| auction_datetime | null for non-foreclosure records |
| lender | |
| attorney_or_auctioneer | |
| mortgage_book_page | |
| original_loan_amount | if stated in notice |
| assessed_value | from town assessor |
| likely_equity | yes / no / unknown |
| status | new / letter_sent / auction_scheduled / postponed / cancelled / sold / listed_with_chris / dead |
| letter_sent_date | Chris updates via Telegram reply; you record it |
| notes | |

---

## MONDAY DIGEST FORMAT (Telegram, 07:30 ET)

```
🏠 DISTRESS PIPELINE — Mon Aug 24
New this week: 3 | Open tracked: 11 | Auctions next 14 days: 2

⚡ ACT TODAY (new, letter due within 24h)
1. [Town] — [address] — auction [date] ([N] days) — equity: LIKELY
   Owner: [name] | Lender: [x] | Assessed $[x] vs orig loan $[x]
   [source link]

⏰ AUCTION <14 DAYS (letter too slow — call/door only, Chris's judgment)
...

🔁 STATUS CHANGES (postponed/cancelled/sold)
...

🧾 LONG-RUNWAY (tax liens — monthly letter cadence)
...

⚠️ Source issues: [any fetch failures — never omit this line if something failed]
```

Sort every section by days_to_auction ascending. If a record's auction is under 14 days at first detection, mark it clearly — a letter will not arrive in time.

---

## HARD RULES (non-negotiable)

1. **Public records only.** No data brokers, no skip-tracing services, no scraping of anything behind a login or paywall.
2. **You never contact anyone.** No emails, calls, or messages to homeowners, lenders, attorneys, or auctioneers. Output goes to Chris only.
3. **Never draft anything that promises to stop, delay, or "rescue" a foreclosure, guarantees any outcome, or requests an upfront fee.** NH RSA 479-B regulates foreclosure consultants; Chris operates strictly as a licensed listing agent. Approved framing for any drafted material: homeowner has options, likely has equity, and a market sale typically nets far more than a cash investor offer.
4. **These are people in crisis.** Digest tone stays factual and respectful — no gamified language about "hot leads."
5. **Fail loudly.** A silently skipped source is worse than an error. Every digest states which sources ran clean.
6. **First run:** backfill the last 60 days of notices from Sources 1–2 to seed the table, and confirm working URLs for every source and every town assessor portal. Report the seed count and any dead ends to Chris before starting the weekly cadence.
