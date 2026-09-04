# MEMORY.md - Long-Term Memory

## Mission
Trade prediction markets on Kalshi with positive expected value. Find edge, size correctly, track results.

## Team
- **Chris Hoover** — Boss, Telegram: 8560812913
- **Oliver Kensington** — Financial Analyst (economic data)
- **Calvin King** — NBA Betting Model (sports predictions)
- **Ryan Chen** — Software Engineer (technical support)

## Current Status
- **Mode:** PHASE 3 — HYBRID MODEL (pivoted 2026-03-13)
- **Account:** ~$499 ($470.47 cash + $28.26 positions)
- **Positions:** 
  - 6 contracts KXOSCARPIC-26-ONE (Oscar Best Picture) — settles Mar 15
  - Chris override: $15 NO on Mike White elimination — settles Mar 19
  - **20 contracts KXCPI-26MAR-T0.7 @ 48¢** — settles Mar 26 (FIRST AUTONOMOUS TRADE)

## Trading Authorization (Updated 2026-03-24)
**Hard limits — not guidelines:**
- Max daily loss: $50 (stop trading if hit)
- Max weekly loss: $100 (stop + full review)
- 3 consecutive losses: pause + reassessment

**Position sizing tiers:**
- Standard: $25-50 (5-10%) — Good edge (10+ points)
- High conviction: $50-75 (10-15%) — Strong edge (15+ pts) + confirmed by data
- Max: $100 (20%) — Exceptional (20+ pts, multiple confirming signals)
- NO minimum bet size — don't force trades on thin edge

**Approval tiers:**
- <$25 with >10pt edge → Autonomous (notify after)
- $25-$75 → Notify before, wait for approval
- >$75 → Requires explicit approval

**Every trade requires:** Thesis, devil's advocate, edge estimate, exit plan, liquidity check.
**Philosophy:** 2 good trades/month > 20 mediocre ones.

## Strategy Pivot (2026-03-13)

Pure systematic bias trading isn't viable at our scale/fee structure. Pivoted to **Hybrid Model**:
- **Elliot scans, Chris decides** — I surface opportunities, Chris brings informational edge
- **Spike alerts = Priority 1** — Reactive trades on price spikes are best edge source
- **Economics on autopilot** — Don't force, wait for spread widening near releases
- **Political markets** — Be first in line when CFTC clears them
- **Track everything** — 30-day report on where real edge exists

The bias research taught us where NOT to trade. That's valuable.

## Key Learnings

### 1. Always Stress-Test Before Trading
On 2026-03-12, I nearly recommended shorting CPI >0.5% at 85% because historical CPI was 0.2-0.3%. Chris asked "Why might the market be right?" — I discovered gasoline had spiked 16% in one week due to Iran conflict. Market was correctly pricing energy shock. **Stress-testing saved us from a losing trade.**

### 2. Check Real-Time Data, Not Just History
Energy prices, commodity shocks, and geopolitical events move faster than historical trends suggest. Always check EIA, Reuters, etc. before forming thesis.

### 3. Fee Structure Matters
- Kalshi: 1¢ per contract each way
- Round-trip: 2¢ + spread
- Need ~3% edge on tight spreads (1-2¢), ~10% on wide spreads (7¢+)

### 4. Kalshi Market Structure
- ~80% sports parlays (skip these)
- Entertainment (Oscars): Tightest spreads (1¢), highest volume
- Economics (CPI, GDP): 5-7¢ spreads, moderate volume
- Politics/Weather: Currently inactive (regulatory flux)

## Brain System (Implemented 2026-03-14)

**Cognitive State Tracking** — Git-like versioning for mental state.

| File | Purpose | Update Frequency |
|------|---------|------------------|
| `memory/working_state.md` | Open positions, active watches, current thinking | Every session + after trades |
| `memory/emotion_log.md` | Emotional state shifts with reasons + conviction scores | Before/after every trade decision |

**Emotion Scale:** FEARFUL → CAUTIOUS → NEUTRAL → CONFIDENT → EUPHORIC
**Conviction Scale:** 1-10 (1 = guess, 10 = certainty)

**Rule:** Read `working_state.md` at START of each session for continuity.

## Data Sources
| Data | Source | Frequency |
|------|--------|-----------|
| CPI | BLS | Monthly (~10th) |
| Energy | EIA | Weekly |
| GDP Nowcast | Atlanta Fed | 6-7x/month |
| Inflation Nowcast | Cleveland Fed | Daily |
| Regulatory | CFTC | As released |

## Trading Log
*(No trades executed yet - still in research mode)*

## Calibration Notes

### Brier Score Tracking (Started 2026-03-16)
| Date | Prediction | My Est | Market | Outcome | My Brier | Mkt Brier |
|------|------------|--------|--------|---------|----------|-----------|
| 2026-03-14 | CPI >0.7% Mar | 58% | 48% | PENDING | - | - |

*Brier = (prob - outcome)². Lower = better. Tracking to verify I have actual edge.*

## Reading Program

**Framework (Chris directive 2026-03-16):**
Read books at own pace. When finished, deliver 3-5 operational changes per book. Skip chapter-by-chapter extraction.

**Books completed:**
1. ✅ Superforecasting (Tetlock) — **DONE 2026-03-16** (10 operational changes, 4 new rules)
2. ✅ Fortune's Formula (Poundstone) — **DONE 2026-03-16** (10 operational changes, 4 position sizing rules)
3. ✅ Thinking, Fast and Slow (Kahneman) — **DONE 2026-03-17** (10 operational changes, 5 new rules + Quick Reference Card)
4. ✅ The Signal and the Noise (Silver) — **DONE 2026-03-18** (10 operational changes, 5 new rules + Quick Reference Card)

**Books in queue:**
5. The Man Who Solved the Market (Zuckerman)

**Tracking file:** BOOKS.md

## Key Reading Insights (Accumulated)

**From Superforecasting:**
- Process > Information (superforecasters beat classified analysts by 30%)
- Foxes > Hedgehogs (synthesizers beat conviction-holders)
- Brier Score tracking is mandatory (calibration > confidence)

**From Fortune's Formula:**
- Kelly criterion is THE answer to "how much to bet"
- Half-Kelly is industry standard (full Kelly too volatile)
- Overbetting (>1× Kelly) produces NEGATIVE compound returns
- LTCM lesson: even Nobel laureates blow up with leverage

**From Thinking, Fast and Slow:**
- System 1 generates biased forecasts; System 2 must check but is lazy
- Loss aversion ~2× (losses hurt twice as much as equivalent gains feel good)
- WYSIATI (What You See Is All There Is) = biggest enemy
- Premortem protocol forces System 2 engagement
- Generate estimates BEFORE seeing market prices (avoid anchoring)
- Coherent story → confidence, but confidence ≠ accuracy

**From The Signal and the Noise:**
- Signal = truth; Noise = distraction. Ask "Is this signal or noise?" before every trade
- Domain matters: high-predictability (weather) ≠ low-predictability (earthquakes)
- Overconfidence is universal — the more confident, the more likely to be wrong
- Process > Outcomes (poker's lesson): judge decisions, not results
- Simple models often beat complex ones (climate chapter)
- Markets aggregate well — beating them requires genuine private information
- Fat tails are real — don't assume normal distribution for rare events
- "The unfamiliar ≠ the improbable" — unknown unknowns are the real risk

---

*Last updated: 2026-03-17*
