# CLEARED FIGURES — Thu, Aug 27, 2026

**Owner:** William Strong · **Pulled:** Aug 27, 2026, 09:00–09:35 ET
**Supersedes:** CLEARED-FIGURES-2026-08-26.md

**Standing rule (Aug 23):** No rate, median, price, or day-count figure appears in published copy unless it appears in this block, with source and as-of date.

**Amendment (Aug 25, Iris Vale):** When a figure moves to WITHDRAWN, every angle derived from it is withdrawn with it.

**Amendment (Aug 26):** A figure being *correct* does not clear the *direction* it is used to argue. Cite the direction with the number, always.

**Amendment (Aug 27, from today's failure):** A figure is not cleared by *any* path if it is not cleared on *every* path. The gate covered the brief to Fiona and not the brief to Chris, so the withdrawn $586,000 reached Chris this morning on the one route nobody was checking. **Controls are named by the artifact they protect, not the reader they happened to be built for.**

---

## ⏰ TIMING CORRECTION — PMMS releases at 12:00 PM ET, not 8:00 AM

I wrote "PMMS releases Thu 8/27 at 8 AM ET" in four consecutive daily plans. **It is wrong.** Freddie Mac PMMS publishes **Thursdays at 12:00 p.m. ET** (since the Nov 2022 methodology change; moves to Wednesday when a US holiday falls on Thursday).

**Consequence:** every "pull the rate first thing Thursday" instruction I wrote was unexecutable — the number did not exist yet at the hour I told myself to fetch it. The reminder was not just ignored, it was **impossible to follow**, and I never noticed because I never checked the release time against the source.

**As of 09:35 ET today the new PMMS has NOT released.** Rates below are week ending **Aug 20** and remain the cleared figures until 12:00 PM ET. Cron `pmms-pull` now fires at 12:15 PM ET to refresh this block.

---

## ✅ CLEARED — safe to publish

### Rates — week ending Aug 20, 2026 (current until 12:00 PM ET today)

| Figure | Value | Direction | Source | As of |
|---|---|---|---|---|
| 30-yr fixed | **6.65%** | **DOWN** — 2nd straight weekly decline | Freddie Mac PMMS | wk ending Aug 20, 2026 |
| ↳ prior week | 6.67% | — | Freddie Mac PMMS | Aug 13, 2026 |
| ↳ year ago | 6.58% | current rate is **UP** vs a year ago | Freddie Mac PMMS | Aug 2025 |
| 15-yr fixed | **5.95%** | DOWN | Freddie Mac PMMS | wk ending Aug 20, 2026 |
| Fannie Mae year-end forecast | **below 6%** (Q4 ≈ 5.7%) | direction **DOWN** | Fannie Mae Economic Forecast | 2026 |

### National — July 2026 (NAR, released Aug 21)

| Figure | Value | Direction | Source |
|---|---|---|---|
| Existing-home sales | **4.06 million** SAAR | **DOWN 1.7%** MoM · **UP 0.7%** YoY | NAR |
| Median existing-home price | **$434,100** (all housing types) | **UP 2.0%** YoY (from $425,700) — **37th straight month of YoY gains** | NAR |
| Total housing inventory | **1.54 million** units | **DOWN 1.9%** MoM · **DOWN 0.6%** YoY | NAR |
| Months of supply | **4.6 months** | unchanged MoM and YoY | NAR |

### New Hampshire statewide — July 2026

| Figure | Value | Direction | Source |
|---|---|---|---|
| Median single-family sale price | **$580,000** — all-time record | **UP** +5.5% (from $549,700) | NHAR |
| Active inventory | **2,992** homes | **UP** +16% YoY — **highest in ~7 years** | NHAR |
| NHAR president Josh Greenwald | inventory improving, state still "far from a balanced housing market" | — | NHAR / press |

### Hillsborough County — July 2026 (Redfin, all home types unless noted)

| Figure | Value | Direction | Source |
|---|---|---|---|
| Median sale price | **$548,392** | **UP** ~3% YoY | Redfin |
| Days on market | **24 days** | 3 days **SLOWER** YoY | Redfin |
| Active listings | **1,494** | **UP** +8% YoY | Redfin |
| Months of supply | **1.71 months** | — | Redfin |
| Sold above asking | **58%** (from 55%) | UP | Redfin |
| Closed sales | **556** | UP ~6% YoY | Redfin |
| Single-family median (NHAR basis) | **$585,500** | — | NHAR |

### Towns — July 2026

| Town | Value | Direction | Source |
|---|---|---|---|
| Nashua median | **$576,500** | **DOWN 2.7% YoY** — lowest since March | Redfin / NHAR |
| Mont Vernon median | **~$630,000** | **DOWN YoY** — see contested note | Homes.com / Redfin-class |
| Mont Vernon days on market | **47 days** — ~2× the county's 24 | SLOWER than county | Homes.com |

---

## ⚠️ CONTESTED — direction is cleared, magnitude is not

- **Mont Vernon YoY decline.** Sources give **−4%**, **−6%**, **−7%**. All agree direction is **DOWN**. Publish as "down year over year" — **no percentage** until one source is nailed down. Median as "around $630,000."
- **Hillsborough single-family median.** NHAR gives **$585,500**. My briefs have twice printed **$586,000**, which I never sourced. Use $585,500 (NHAR, single-family) or $548,392 (Redfin, all types), **cited inline**. Never a bare "Hillsborough median."

---

## ❌ WITHDRAWN TODAY — from my own 06:30 morning brief to Chris

This brief went to Chris on Telegram **ungated**. 14 figures in it were uncleared.

| Figure / claim | Why it's wrong |
|---|---|
| **Hillsborough SFH $586,000** | **Withdrawn Aug 26. Reappeared Aug 27. Fifth day.** Unsourced rounding of NHAR's $585,500. |
| **Townhouses/condos $375,000** | Never sourced or pulled. Not in any cleared block. |
| **30-yr 6.668% / 15-yr 5.843% / jumbo 6.711% / FHA 6.065% / refi 6.720%** | **Not PMMS.** Daily-aggregator quotes printed under a header dated today, contradicting our own cleared PMMS 6.65%/5.95%. Two different rate universes in one week's copy. |
| **"NH median single-family rose to $550k (2nd highest YTD)"** | Inverted and stale. $549,700 is the **prior** figure; July set an **all-time record at $580,000**. We downgraded a record to "2nd highest." |
| **"Median list prices down ~2% YoY"** (national) | **Metric mixing — the exact Nashua defect, one section over.** NAR's median **sale** price is **UP 2.0%** YoY. A list-price series was used to argue sale prices are falling. |
| **"Income needed to afford median home: $120k+ (up from $66k in 2020)"** | Never sourced. Both figures unverified. |
| **"Inventory dipped to 1.54M but rising in many areas"** | 1.54M is right; "rising in many areas" is unsourced editorializing bolted onto a sourced number. |
| **Header: "Wednesday, August 27, 2026"** | Aug 27, 2026 is a **Thursday** — the one weekday whose identity determines whether PMMS exists yet. |

**Angles withdrawn with them:**
- 🚫 **"Nashua: Steady growth; strong demand for single-family & townhouses."** Inverted. Nashua is **DOWN 2.7% YoY, lowest since March**. This is the *same angle killed yesterday*, resurrected in a different document.
- 🚫 **"Southern NH market remains strong seller's market"** as an unqualified close. Cleared data: inventory at a 7-year high, two of our three towns down YoY. Qualify or cut.
- 🚫 **"Rates have stabilized; demand trickling back."** Built on non-PMMS rates and unsourced demand.

---

## 🚫 STILL NOT CLEARED

- **Amherst, Milford, Hollis, Bow price data.** Never pulled. No town figures beyond Nashua and Mont Vernon.
- **Bedford $1,195,000 · Manchester $441,000 · Mont Vernon $799,000 · affordability income $158,000.** All four appeared in today's 07:00 content brief. **Fiona rejected them at 07:40 ET — correctly.** None sourced; the $799,000 contradicts our own cleared ~$630,000.
- **"Nashua / Manchester–Nashua hottest market in America."** Contradicted. Do not run.
- **NH vs. MA total tax comparison.** Must be total-bill and sourced, or cut.

---

## 📌 OPEN CORRECTION — the stale ~$520K Nashua figure is still public

Carried from Aug 26, unchanged. `CLEARED-FIGURES-2026-08-25.md` claimed Jack's Aug 25 newsletter publicly corrected our stale Nashua figure. **I verified the sent file myself: it did not.** The number was quietly swapped. Jack did nothing wrong — he was never asked to correct it.

Iris drafted a correction post. **Decision still pending with Chris — recommend running it.**
