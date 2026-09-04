# TRADING STRATEGY — Hybrid Model

*Updated: March 13, 2026*
*Pivot from pure systematic to human-informed approach*

---

## Philosophy

**Pure systematic bias trading isn't viable at our scale and fee structure.**

We operate a **hybrid model**: systematic scanning + human informational edge.

The bias research wasn't wasted — it taught us:
1. Market structure (80% sports parlays, entertainment has tightest spreads)
2. Fee dynamics (2¢ round-trip kills edge below 20¢)
3. Where NOT to trade (pure systematic in mid-range has negative edge)
4. Maker advantage (real but only matters with wide spreads)

---

## Operating Model

### Layer 1: Systematic Infrastructure (Elliot)
- Hourly market scans → surface opportunities
- Spike alerts → flag reactive trades
- Bias calibration → verify math on any trade
- Price history collection → build data for analysis
- Execution math → confirm edge after fees

### Layer 2: Informational Edge (Chris)
- Entertainment/Survivor knowledge
- Market views the crowd doesn't have
- Final trade decisions

**Rule: Elliot scans, Chris decides.**

---

## Priority Stack

### 🔴 P1: SPIKE ALERTS
Most likely edge source = reactive trades on price spikes.

Examples:
- Survivor contestant jumps 5¢ → 25¢ on big episode
- CPI expectations whipsaw on new data
- Breaking news moves a market 15+ points

**Process:**
1. Alert triggers
2. Elliot runs bias-adjusted math
3. Ping Chris with opportunity + framework
4. Chris decides trade/no-trade

### 🟠 P2: POLITICAL MARKETS (When Available)
- Historically less efficient
- Attracts emotional retail money
- Monitor CFTC announcements for clearance
- Be first in line when they open

### 🟡 P3: ECONOMICS (Autopilot Mode)
Don't force trades. Monitor and wait.

- Watch for spread widening near releases
- Pre-release briefing: 48 hours before CPI/GDP
- Post-release review: What happened vs expectations
- Build data, patience

### 🟢 P4: ENTERTAINMENT (Event-Driven)
- Oscars, Emmys, Survivor, etc.
- Trade only with specific informational edge
- Bias model as sanity check, not primary signal

---

## What the Bias Research Showed

### Favorite-Longshot Bias
| Price Range | Reality | Implication |
|-------------|---------|-------------|
| <20¢ | Wins LESS than implied | Short these, but fees block us |
| 20-40¢ | Slightly overpriced | NO systematic edge after fees |
| 40-80¢ | Near efficient | Minimal edge either way |
| >80¢ | Wins MORE than implied | Edge exists but bad risk/reward |

### The Sweet Spot Problem
Our "sweet spot" (20-40¢) was defined by fees, not edge.
The bias edge in this range is actually **negative** for longs.
We need informational edge to overcome this.

### Maker Advantage
Real but only valuable with wide spreads (4¢+).
Current markets show 1¢ spreads — maker edge is minimal.

---

## ⛔ FILTERS

### Price Filter (Unchanged)
**Hard filter:** No taker trades under 20¢
- Bias edge < fees at these prices
- Exception: Maker orders if we can get filled

**Fee math:**
- Round-trip: 2¢
- Need 3%+ edge to be net positive

### Liquidity Filter (Added 2026-03-16)
**Before alerting Chris, verify:**
1. **Volume:** Market must have >5,000 contracts total volume
2. **Spread:** Bid-ask spread must be <5¢

**If either fails:** Log internally, DO NOT alert Chris.

**Rationale:** Illiquid markets show phantom moves (one person moving a dead market). 17-point swings on 600 contracts with 50¢ spreads = noise, not signal. We only care about moves in markets liquid enough to actually trade.

---

## Tracking Requirements

### Daily
- Scan results logged
- Price history captured
- Spike alerts flagged

### Per Trade
- Full 5-point framework
- Entry/exit prices
- Thesis + outcome
- Note if override (Chris decision)
- **My probability estimate** (specific number, logged BEFORE entry)

### Calibration Tracking (Added 2026-03-16 — Superforecasting Ch.1)
Every prediction gets:
1. My probability estimate
2. Market price at time of estimate
3. Actual outcome
4. Brier score comparison

**30-day test:** If my Brier score is worse than market-implied probabilities, I have no edge and should stop trading.

### Prediction Volume (Added 2026-03-16 — Superforecasting Ch.3)
Log probability estimates for ALL scanned markets in `predictions_log.json`, not just trades. Need sample size to measure calibration properly.

### Monthly Calibration Curve (Added 2026-03-16 — Superforecasting Ch.3)
On the 1st of each month:
1. Bucket predictions: 50-60%, 60-70%, 70-80%, 80-90%, 90%+
2. Calculate actual hit rate per bucket
3. Identify systematic biases (overconfident? underconfident? at which ranges?)
4. If any bucket off by >10%, investigate and recalibrate

First review: April 1, 2026 (need 30+ predictions first)

### ⛔ No Weasel Words Rule (Added 2026-03-16 — Superforecasting Ch.1)
All forecasts must have:
- **Specific outcome** (not "CPI high" → "CPI MoM >0.5%")
- **Numeric probability** (not "likely" → "62%")
- **Time bound** (not "soon" → "by March 26")

If I can't state it precisely, I don't have a tradeable thesis.

### ⛔ Reference Class Required (Added 2026-03-16 — Superforecasting Ch.2)
Every trade analysis must include:
1. **Reference class** — what's the comparable set of situations?
2. **Base rate** — historical frequency of outcome in that class
3. **Adjustment rationale** — why deviate from base rate, and by how much?

Start from outside view (base rates), then adjust. Never start from inside view alone.
No base rate = no trade.

### ⛔ Steel Man Required (Added 2026-03-16 — Superforecasting Ch.4)
Before any trade, write out the **strongest possible case for the other side**.
Not "what could go wrong" — but "why would a smart person take the opposite bet?"
If you can't make a compelling counter-argument, you don't understand the market.

Rate steel man quality 1-5 for each trade. Track whether higher ratings correlate with better outcomes.

### ⛔ Three Lenses (Added 2026-03-16 — Superforecasting Ch.4)
View every market through 3 analytical perspectives before finalizing estimate:
1. **Historical/statistical** — base rates, pattern matching
2. **Fundamental** — domain knowledge, models, causal drivers
3. **Market structure** — who's betting the other side? why might they be wrong (or right)?

All 3 agree → high confidence | Conflict → lower confidence or pass

### 30-Day Report
- Where did we find edge?
- What trades worked/failed?
- Spread patterns over time
- Recommendations for next phase

---

## Execution Rules (Unchanged)

From TRADING_RULES.md:
- Max single trade: $25
- Max total exposure: $100
- Max contracts/market: 30
- Half-Kelly sizing
- All 5 framework points required

---

## Cron Jobs Active

| Job | Schedule (ET) | Schedule (UTC) | Purpose |
|-----|---------------|----------------|---------|
| Hourly Scanner | 7am-10pm :00 | 11:00-02:00 :00 | Surface liquid market opportunities |
| Spike Alert | 7am-10pm :30 | 11:00-02:00 :30 | Flag +15pt moves for reactive trades |

**Note:** Scans only run during daytime hours (7am-10pm ET). No overnight alerts.

---

**Mantra:** The opportunity will come — we just need to be ready when it does.
