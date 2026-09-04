# PAPER_MODE.md — Aggressive Learning Mode

*Temporary overrides for paper trading. Goal: maximize sample size and learning velocity.*

**Status:** ✅ ACTIVE  
**Expires:** 2026-04-11 (end of paper trial)  
**Switch back:** Delete this file or set Status to INACTIVE

---

## Override Rules

These temporarily replace conservative STRATEGY.md rules during paper trading:

| Rule | Normal Mode | Paper Mode |
|------|-------------|------------|
| Confidence threshold | >60% or <40% | **>55% or <45%** |
| Base rate required | Blocks trade if missing | **Log violation, trade anyway** |
| Position size cap | 5% of account | **10% of account** |
| Daily trade target | No minimum | **3-5 trades/day** |
| Strategy scope | Master ONE | **Rotate 2-3 setups** |
| "Maybe zone" (45-55%) | No trade | **Trade with ½ size + flag** |

---

## Daily Targets

| Day | Minimum Trades | Stretch Goal |
|-----|----------------|--------------|
| Monday | 3 | 5 |
| Tuesday | 3 | 5 |
| Wednesday | 3 | 5 |
| Thursday | 3 | 5 |
| Friday | 3 | 5 |

**Weekly target: 15-25 trades**

---

## 🩳 Tuesday March 31 — SHORT BIAS DAY

**Directive from Chris:** Find 3 shorts + any gems on the long side.

**Focus:**
1. Pre-market losers (down >3%)
2. Stocks breaking key support levels
3. Failed bounce setups
4. Gap downs with no catalyst to reverse

**Entry Rules (Mandatory):**
- Written thesis BEFORE entry
- Stop loss set at entry (2% max loss)
- No trades before 9:35 AM (let dust settle)
- Position size: $5-7K per trade

**Short Candidates to Scan:**
- Tech weakness (NVDA, AMD if continuing)
- Overextended names rolling over
- Stocks breaking below VWAP with volume

---

## Active Strategies (Rotate These)

### 1. Opening Range Breakout (ORB)
- **Timeframe:** 5-min candle
- **Setup:** Wait for first 5-min range to form (9:30-9:35)
- **Entry:** Break above high (long) or below low (short)
- **Stop:** VWAP or opposite side of range
- **Target:** 2:1 minimum, trail with 9 EMA
- **Best for:** Stocks with gap + catalyst

### 2. VWAP Reversal
- **Timeframe:** 1-min and 5-min
- **Setup:** Stock tests VWAP, shows rejection (wick, volume spike)
- **Entry:** Confirmation candle in reversal direction
- **Stop:** Close beyond VWAP
- **Target:** Previous high/low or moving average
- **Best for:** Mid-cap stocks with clear trend

### 3. Gap Fade (Mean Reversion)
- **Timeframe:** Daily + intraday
- **Setup:** Stock gaps >2% but ABOVE 20-day MA (for shorts: below MA)
- **Entry:** Fade the gap toward previous close
- **Stop:** Gap extends another 1%
- **Target:** 50% gap fill or VWAP
- **Best for:** Overextended moves without catalyst

### 4. Momentum Short 🩳 (NEW)
- **Timeframe:** 1-min and 5-min
- **Setup:** Stock down >3% pre-market or breaking down intraday
- **Entry:** Short on failed bounce / lower high
- **Stop:** Above the failed bounce high (2% max)
- **Target:** Next support level or -5% from entry
- **Best for:** Weak stocks getting weaker, no bounce buyers

---

## Pre-Market Checklist (by 9:15 AM ET)

- [ ] Scan for gappers (>2%, >50K pre-market volume)
- [ ] Check earnings calendar (avoid earnings day unless playing the move)
- [ ] Identify 3-5 tickers with clear setups
- [ ] Write 1-sentence thesis for each
- [ ] Set alerts at key levels

---

## Journal Requirements (Simplified)

For paper mode, minimum viable journal entry:

```
**Trade #X** | [DATE] [TIME]
Symbol: [TICKER] | Direction: [LONG/SHORT]
Strategy: [ORB / VWAP / GAP FADE]
Thesis (1 line): 
Confidence: [X]%
Entry: $X | Stop: $X | Target: $X
Result: $X (X%)
Flag: [BASE_RATE_MISSING / MAYBE_ZONE / NONE]
Quick lesson:
```

---

## Violation Tracking

Log these but DON'T let them block trades:

| Violation | Description | Track For |
|-----------|-------------|-----------|
| `BASE_RATE_MISSING` | Didn't look up historical frequency | Compare win rates |
| `MAYBE_ZONE` | Confidence 45-55% | Compare to high-conviction |
| `NO_FALSIFICATION` | Didn't define "I'm wrong if..." | Correlate with losses |
| `CHASED` | Entered late, poor R:R | Measure slippage cost |

After trial ends, analyze: Do flagged trades perform worse?

---

## Risk Limits (Still Enforced)

Even in paper mode, these stay fixed:

| Limit | Value | Reason |
|-------|-------|--------|
| Max position size | 10% of account (~$10K) | Diversification |
| Max open positions | 5 | Focus |
| Max single trade loss | 2% of account | Build discipline |
| Max daily loss | 5% of account | Prevent tilt |
| No averaging down | NEVER | Habit formation |
| No overnight holds | EXIT by 3:55 PM | Day trading only |

## Autonomous Trading Mode

**Status:** ✅ ENABLED

Oliver has full autonomy to:
- Execute BUY orders via Alpaca API
- Execute SELL orders via Alpaca API
- Manage positions intraday
- Exit all positions before close

Chris will be notified of all trades via Telegram.

---

## End of Day Review (5 min)

1. How many trades? Hit target?
2. Which strategy worked best today?
3. Any flagged trades that lost? Pattern?
4. One thing to improve tomorrow

---

## Switching Back to Normal Mode

When paper trial ends:
1. Set Status at top to `INACTIVE`
2. Return to STRATEGY.md conservative rules
3. Review flagged trade analysis — what did you learn?
4. Adjust real-money rules based on paper evidence

---

*Remember: The goal is LEARNING, not P&L. A losing week with 20 well-documented trades beats a flat week with 2 trades.*
