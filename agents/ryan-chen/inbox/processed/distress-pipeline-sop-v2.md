# AGENT SOP v2: Souhegan Valley Distress Pipeline

**Owner:** Chris Hoover
**Agent:** Jack Sullivan (Claude Code VPS srv1328092, cron-scheduled)
**Delivery:** Telegram digest (dedicated bot) + Monday email to Chris + Supabase table
**Cadence:** Monday 07:00 ET (main run) + Thursday 07:00 ET (postponement re-check)

---

## MISSION

Every Monday, compile all NEW distress signals across three tracks — pre-foreclosure, tax-delinquent, and probate — for the target towns, dedupe against the master pipeline, enrich each record, and deliver a prioritized digest and email so Chris can act on the right cadence for each track. Jack compiles and tracks. Jack NEVER contacts homeowners, fiduciaries, lenders, attorneys, or town offices. All outreach is done by Chris personally.

## THE THREE TRACKS AND THEIR CLOCKS

| Track | First public signal | Runway | Chris's cadence |
|---|---|---|---|
| Foreclosure | Newspaper notice of sale | ~3 weeks to auction | Letter same day as detection |
| Tax lien | Registry lien execution / town lien list | ~2-year redemption window before tax deed | Monthly letter cadence |
| Probate | Court-published fiduciary appointment notice | Months (6-month creditor period, 90-day inventory) | Measured; see hold rule below |

**Why foreclosure speed matters:** NH is non-judicial (RSA 479:25). Notice is mailed to the homeowner ~45 days before sale, but the public window opens with newspaper publication — once a week for 3 weeks, first publication ≥20 days pre-auction. There is no recorded notice of default in NH. Detection-to-letter target: same day.

**Why the other two tracks matter:** tax-delinquent owners usually have real equity, a solvable problem, and almost no investor competition; probate fiduciaries (often out of state) are motivated, not desperate, and carrying costs work in favor of a timely conversation.

## TARGET TOWNS (edit as needed — all Hillsborough County)

Mont Vernon, Amherst, Milford, Wilton, Lyndeborough, Brookline, Hollis, New Boston, Merrimack, Bedford, Nashua (flag only — high volume, Chris decides case by case)

---

## SOURCES

### Source 1 — Union Leader legals (PRIMARY, weekly) ✅ verified scriptable
https://www.unionleader.com/classifieds/legals/ — server-rendered, no JS wall.
Parse TWO notice types from the same section:

**1a. Foreclosure:** blocks matching "NOTICE OF FORECLOSURE SALE" / "RSA 479:25" / "MORTGAGEE". Extract: borrower name(s), property address, auction date/time, lender, mortgage book/page (often original loan amount), law firm/auctioneer.

**1b. Probate:** blocks matching "LEGAL PROBATE NOTICE" / "APPOINTMENT OF FIDUCIARIES". These are batch listings from the Circuit Court probate division covering ~2-week windows. Each entry: decedent name, "late of [town]", fiduciary name + full mailing address, court docket number (#316-YYYY-ET-#####). Filter to entries where the decedent is "late of" a target town. **Flag out-of-state fiduciary addresses — strongest signal in this track.**

### Source 1c — Nashua Telegraph legals (weekly, redundancy)
Some Hillsborough notices run here instead of the Union Leader. Same parse logic. (Substitute for nh.mypublicnotices.com, confirmed dead — retry https/UA variants once before final removal.)

### Source 2 — Auctioneer sale calendars (weekly) ✅ verified up
James R. St. Jean Auctioneers (WordPress, scriptable), Paul McInnis LLC, Tranzon Auction Properties (NH). Filter to target towns. **Monthly QC job:** diff auctioneer calendars against parsed newspaper notices — any auction on a calendar that never hit the table is a named coverage gap; report it.

### Source 3 — Hillsborough County Registry of Deeds (MONTHLY, first Monday)
Via https://www.nhdeeds.org/ (Hillsborough). The notice of sale is NOT recorded pre-auction (foreclosure deed + affidavit record up to 60 days AFTER sale), so the Registry is not early warning. Use it for:
- **Tax lien executions** by town tax collectors → these create/refresh TAX LIEN track records
- Municipal liens and attachments against owners in target towns
- Foreclosure deeds → mark tracked records SOLD; measure detection rate
If the portal won't script, output a manual checklist for Chris and say so in the digest.

### Source 4 — Estate appointment lists, courts.nh.gov (MONTHLY, cross-check)
The NH Judicial Branch publishes executor/administrator appointment lists by county and year (Probate Division → Estate Appointments). Cross-check Hillsborough entries against Source 1b. Note: estates under $10,000 don't appear on these lists.

### Source 5 — Town tax collector lien/delinquency lists (QUARTERLY, human-in-loop)
No central online source; lists are public records held by each town's tax collector. Quarterly, Jack DRAFTS a records request per target town; **Chris sends them from his own email** (agent-signed requests to small-town offices are an optics risk). Jack ingests whatever Chris forwards back. Digest includes a quarterly reminder with the drafts attached.

---

## PIPELINE STEPS (Monday run)

1. **Fetch** Sources 1, 1c, 2 (plus 3/4 monthly, 5 quarterly).
2. **Parse** into structured records (schema below), tagged by `pipeline_track`.
3. **Dedupe** against master table. Foreclosure/tax key: normalized address + owner last name (same sale publishes 3 weeks running — must not triplicate). Probate key: docket number.
4. **Enrich:**
   - *All tracks:* town assessor lookup → assessed value (store working portal URL per town after first success).
   - *Foreclosure:* equity signal = assessed value vs original loan amount from notice → `likely_equity` yes/no/unknown (crude — say so); `days_to_auction`.
   - *Probate (REQUIRED GATE):* match decedent name against town assessor owner records. **No property match in a target town → no pipeline record.** A probate notice proves a death, not a house. On match: property address, assessed value, out-of-state fiduciary flag.
   - *Tax lien:* record lien execution date; estimate `redemption_deadline` (~2 years out) — label it an estimate; the town's records govern.
5. **Update statuses:** re-search open foreclosure records for postponements/cancellations (common; re-advertised). **Append to `postponement_history` — never overwrite `auction_datetime` history.** Multi-postponement records are high-signal (owner is fighting or negotiating) and get flagged.
6. **Write** all changes to Supabase.
7. **Send digest** (Telegram) and **email** (format below).

## THURSDAY RUN (light)

Re-check open foreclosure records with auctions in the next 21 days. One-line Telegram update only if something changed.

---

## MASTER TABLE SCHEMA (Supabase: `distress_pipeline`)

| field | notes |
|---|---|
| id | uuid |
| pipeline_track | foreclosure / tax_lien / probate |
| owner_names | as printed (for probate: estate owner of record) |
| decedent_name | probate only |
| fiduciary_name | probate only |
| fiduciary_address | probate only — the mailing target |
| out_of_state_fiduciary | boolean |
| docket_number | probate only |
| property_address | normalized |
| town / county | Hillsborough |
| source / source_url | union_leader / telegraph / auctioneer / registry / courts_nh / tax_list |
| first_seen | |
| notice_type | foreclosure_sale / tax_lien / municipal_lien / attachment / probate_appointment |
| auction_datetime | current scheduled date |
| postponement_history | append-only list of {old_date, new_date, seen_date} |
| lender / attorney_or_auctioneer / mortgage_book_page / original_loan_amount | foreclosure |
| lien_execution_date / redemption_deadline | tax lien (deadline = estimate) |
| assessed_value | |
| likely_equity | yes / no / unknown |
| status | new / letter_sent / auction_scheduled / postponed / cancelled / sold / redeemed / listed_with_chris / dead |
| letter_sent_date | Chris updates via Telegram reply; Jack records |
| notes | |

**HARD WALL:** this table is isolated from ALL of Jack's drip/sequence/CRM outreach logic. Built as a constraint, not a convention. Nothing in this table is ever a send target. Jack's SMTP is used for exactly one thing here: the Monday email to Chris.

---

## MONDAY DELIVERY

### Telegram digest (07:30 ET, dedicated bot)
```
🏠 DISTRESS PIPELINE — Mon Aug 24
New: 3 foreclosure | 1 tax lien | 2 probate | Open tracked: 17

⚡ FORECLOSURE — ACT TODAY (letter due within 24h)
1. [Town] — [address] — auction [date] ([N] days) — equity: LIKELY
   Owner | Lender | Assessed vs orig loan | [link]

⏰ AUCTION <14 DAYS (letter too slow — call/door, Chris's judgment)

🔁 STATUS CHANGES (postponed [count in history] / cancelled / sold)

🧾 TAX LIEN — LONG RUNWAY (monthly letter cadence)
   [address] — lien executed [date] — est. redemption deadline [date] — equity signal

🕊 PROBATE — NEW MATCHES (hold rule applies — see below)
   [decedent], late of [town] — property [address] — fiduciary [name], [city, ST] ⚑OOS
   Docket # | first letter eligible [date]

⚠️ Sources: [ran clean / failures — never omit]
```

### Email (Monday, after digest)
To Chris via existing Workspace SMTP. Body: digest summary. Attachment: **CSV of all open records** sorted by track then urgency (days_to_auction / redemption_deadline / first-letter-eligible date) — column layout matched to the Twriter mail-merge input.

---

## HARD RULES (non-negotiable)

1. **Public records only.** No data brokers, no skip-tracing, nothing behind logins or paywalls.
2. **Jack never contacts anyone** — homeowners, fiduciaries, lenders, attorneys, auctioneers, or town offices. Records requests are drafted by Jack, sent by Chris.
3. **Never draft anything that promises to stop, delay, or "rescue" a foreclosure, guarantees outcomes, or requests upfront fees** (NH RSA 479-B foreclosure-consultant territory). Chris operates strictly as a licensed listing agent. Approved framing: options, equity, market sale nets more than an investor cash offer.
4. **Probate hold rule:** no probate record is letter-eligible until at least 14 days after its notice first appears (the notice itself already lags death by weeks). Digest shows the eligibility date. Tone of anything drafted for this track: condolence-first, practical, zero urgency language.
5. **These are people in crisis or grief.** Digest tone stays factual and respectful — no gamified language.
6. **Fail loudly.** Every digest states which sources ran clean. A silently skipped source is worse than an error.
7. **First run:** backfill 60 days of Union Leader notices (both types) to seed the table; confirm working URLs for every source and every town assessor portal; report seed counts and dead ends to Chris before starting weekly cadence.
