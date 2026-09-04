# Survivor Longshot Basket Analysis

## CRITICAL FINDING: The Math Doesn't Work

After running the numbers, I have to report that the Survivor longshot short thesis **does not produce positive EV after fees**.

### The Problem: Tick Size vs. Edge

**Cirie Fields Example (Best Longshot Opportunity):**

| Metric | Value |
|--------|-------|
| YES Price | 4-5¢ |
| NO Price | 95-96¢ |
| Implied win probability | 5% |
| Bias-adjusted probability | 4.18% |
| Edge | 0.82 percentage points |

**EV Calculation (1 NO contract @ 96¢):**
```
EV = P(she loses) × Profit + P(she wins) × Loss
EV = 0.9582 × $0.04 + 0.0418 × (-$0.96)
EV = $0.0383 - $0.0401
EV = -$0.002 per contract (BEFORE fees)
```

**With fees (1¢ each way = 2¢ round trip):**
```
Net EV = -$0.002 - $0.02 = -$0.022 per contract
```

**Result: NEGATIVE EV**

### Why This Happens

1. **Tick size too coarse**: Kalshi's 1¢ minimum tick means spreads can't get tight enough
2. **Edge too small at extremes**: At 5¢, the bias adjustment is only ~0.8 points
3. **Fees dominate**: 2¢ round-trip on a trade expecting 0.8¢ edge = net negative

### All Longshots Have Same Problem

| Contestant | YES Price | NO Cost | Gross Edge | Fees | Net EV |
|------------|-----------|---------|------------|------|--------|
| Cirie Fields | 4-5¢ | 96¢ | +0.8¢ | -2¢ | **-1.2¢** |
| Jonathan Young | 2-3¢ | 98¢ | +0.4¢ | -2¢ | **-1.6¢** |
| Joe Hunter | 2-3¢ | 98¢ | +0.4¢ | -2¢ | **-1.6¢** |
| Coach Wade | 1-2¢ | 99¢ | +0.2¢ | -2¢ | **-1.8¢** |
| 0/1¢ contestants | 0-1¢ | 100¢ | 0¢ | -2¢ | **-2¢** |

Every single position is negative EV after fees.

### The Structural Problem

Survivor Season 50 has:
- 24 contestants, 1 winner
- One massive frontrunner (Aubry at 87%)
- 23 longshots priced at 0-5%
- No middle ground (20-40% range)

The bias thesis works best on:
- **Binary markets** (CPI > 0.5% yes/no)
- **Multi-way races with multiple contenders** (political primaries)
- **Mid-range probabilities** (20-40%) where absolute bias is larger

Survivor is essentially: "Aubry 87%, field 13% split 23 ways" — not exploitable.

## ALTERNATIVE STRATEGIES

### Option A: Wait for Volatility
If a longshot spikes (e.g., Cirie gets good airtime and goes from 5¢ to 20¢), the bias edge becomes tradeable:

| Price | Bias-Adjusted | Edge | After Fees |
|-------|---------------|------|------------|
| 5¢ | 4.2% | +0.8¢ | -1.2¢ ❌ |
| 10¢ | 8.8% | +1.2¢ | -0.8¢ ❌ |
| 15¢ | 13.5% | +1.5¢ | -0.5¢ ❌ |
| 20¢ | 17.8% | +2.2¢ | +0.2¢ ✅ |
| 25¢ | 22.5% | +2.5¢ | +0.5¢ ✅ |

**Trigger: Only short if a longshot spikes above 20¢**

### Option B: Look for Maker Fills
Place limit orders to SELL YES at better prices:
- Bid to sell Cirie YES at 6¢ (instead of current 4¢ bid)
- If filled, edge increases to +1.6¢ gross, -0.4¢ after fees

Still marginal, but moves toward positive territory.

### Option C: Different Market Category
The bias thesis is sound, but Survivor isn't the right venue. Better targets:
- **Oscar markets** (tight spreads, multiple categories)
- **Economic indicators** (binary outcomes, frequent settlement)
- **Crypto price thresholds** (high volume, emotional traders)

## RECOMMENDATION

**DO NOT EXECUTE the Survivor longshot basket.**

The structural edge exists but is smaller than transaction costs. This would be our first live trade — I don't want to start with a mathematically negative position.

**Instead, propose:**
1. Continue monitoring Survivor for volatility spikes (>20¢ on longshots)
2. Shift focus to Oscar Best Director (Ryan Coogler at 7-8¢ may have better dynamics)
3. Or wait for economics markets with >5¢ spreads where bias can overcome fees

---

*Analysis completed: March 13, 2026 01:00 UTC*
*Conclusion: Pass — fees > edge*
