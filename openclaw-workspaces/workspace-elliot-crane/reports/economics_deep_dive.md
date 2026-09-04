# Economics Deep Dive: Consensus vs. Kalshi Pricing
**Generated:** March 12, 2026 18:32 UTC
**Analyst:** Elliot Crane
**Status:** READ-ONLY MODE

---

## EXECUTIVE SUMMARY

**Key Finding: Potential Mispricing in CPI Markets**

The March 2026 CPI >0.5% market is priced at **84.5%**, but recent data and historical patterns suggest this may be too high. This is my highest-conviction observation to date.

---

## 1. CPI MARKETS ANALYSIS

### Recent CPI Data (Source: BLS)
| Month | Monthly CPI Change |
|-------|-------------------|
| Aug 2025 | +0.3% |
| Sep 2025 | +0.3% |
| Oct 2025 | *Not available* |
| Nov 2025 | *Not available* |
| Dec 2025 | +0.3% |
| Jan 2026 | +0.2% |
| **Feb 2026** | **+0.3%** |

**12-Month CPI:** +2.4% (through Feb 2026)

### March 2026 CPI Markets (KXCPI-26MAR)

| Strike | Kalshi Implied | My Estimate | Gap | Confidence |
|--------|----------------|-------------|-----|------------|
| >0.3% | 98.5% | ~95% | ~3% | Medium |
| >0.4% | 96.5% | ~80% | ~16% | **High** |
| **>0.5%** | **84.5%** | **~50-60%** | **~25-35%** | **High** |
| >0.6% | 69.5% | ~30% | ~40% | Medium |
| >0.7% | 35.5% | ~15% | ~20% | Medium |

### Thesis: CPI >0.5% in March is OVERPRICED

**Evidence:**
1. **Recent trend:** Last 6 readings averaged ~0.27% monthly. Zero readings above 0.4%.
2. **February components:** Shelter (+0.2%), Food (+0.4%), Energy (+0.6%). No acceleration signals.
3. **Base effects:** Feb 2025 was elevated; March 2025 was moderate. Base effects neutral.
4. **Fed policy:** Still restrictive. No demand-side inflation surge expected.

**Counter-arguments (why I could be wrong):**
1. Energy prices volatile - could spike
2. Housing disinflation slower than expected
3. Tariff impacts uncertain
4. Model error in my estimate

**My probability estimate for >0.5%:** 50-60%
**Kalshi price:** 84.5%
**Implied edge:** 25-35 percentage points

**Spread assessment:** 7¢ spread (Bid 81¢ / Ask 88¢)
**Round-trip cost:** ~9¢ (including fees)
**Break-even:** Need >10% edge to profit

⚠️ **Verdict: POTENTIAL TRADE - Awaiting your authorization to short**

---

### Other CPI Months

#### April 2026
| Strike | Kalshi | Assessment |
|--------|--------|------------|
| >0.3% | 73.5% | Reasonable |
| >0.4% | 53.5% | Reasonable |
| >0.5% | ~17%* | *No bid* |

*Farther out months have wider spreads and less volume - harder to trade.*

---

## 2. GDP MARKETS ANALYSIS

### Atlanta Fed GDPNow
The Atlanta Fed GDPNow model provides real-time GDP nowcasts. Unfortunately, I couldn't extract the current numerical estimate from their webpage, but the model is updated 6-7 times per month.

**Sources to monitor:**
- Atlanta Fed GDPNow: https://www.atlantafed.org/cqer/research/gdpnow
- NY Fed Staff Nowcast: https://www.newyorkfed.org/research/policy/nowcast
- Blue Chip Consensus (proprietary)

### Q1 2026 GDP Markets (KXGDP-26APR30)

| Strike | Kalshi Implied | Spread | Volume |
|--------|----------------|--------|--------|
| >1.0% | 82.0% | 6¢ | 43,573 |
| >1.5% | 69.5% | 1¢ | 47,200 |
| >2.0% | 62.5% | 5¢ | 44,423 |
| >2.5% | 57.0% | 2¢ | 35,480 |
| >3.0% | 42.0% | 4¢ | 35,295 |
| >3.5% | 26.0% | 6¢ | 19,702 |
| >4.0% | 13.5% | 1¢ | 14,035 |

**My assessment:** Without real-time GDPNow data, I can't identify clear mispricing. The distribution looks reasonable for Q1 GDP.

**Action needed:** Set up GDPNow monitoring to compare model estimates to Kalshi prices as data releases occur.

---

## 3. POLITICAL MARKETS: Why They're Absent

### Regulatory Background (Critical Update)

**Today (March 12, 2026):** CFTC issued two major releases:
1. **Advisory on Prediction Markets** - reminding DCMs of regulatory obligations
2. **Advanced Notice of Proposed Rulemaking** - seeking public comment on prediction market rules

**Recent history:**
- **Feb 4, 2026:** CFTC withdrew Event Contracts Rule Proposal
- **Feb 17, 2026:** CFTC reaffirmed exclusive jurisdiction over prediction markets

### Why No Political Markets?

**My assessment:** The regulatory environment is in flux. Kalshi (and other DCMs) are likely waiting for clearer CFTC guidance before listing political event contracts for 2026 midterms.

**Key context:** Kalshi won a court case in 2024 allowing election contracts, but the new CFTC chairman (Michael Selig, sworn in Dec 2025) is developing new rules.

### Implication for Us

Political markets will likely return, but timing is uncertain. When they do:
- We should be ready with polling data sources (538, RCP)
- Early movers may find mispriced markets before arbitrage kicks in
- Watch CFTC announcements for signals

---

## 4. MONITORING FRAMEWORK

### Daily Checks
| Data Source | Release Schedule | Markets Affected |
|-------------|------------------|------------------|
| CPI | Monthly (~10th) | KXCPI series |
| PPI | Monthly (~15th) | Inflation sentiment |
| Jobless Claims | Weekly (Thursdays) | Employment outlook |
| Retail Sales | Monthly (~15th) | GDP components |
| GDPNow Updates | 6-7x/month | KXGDP series |

### Automated Alerts Needed
1. **GDPNow updates** → Compare to KXGDP pricing
2. **CPI release** → Compare to KXCPI pricing
3. **CFTC press releases** → Political market signals

### Price Monitoring
Track bid/ask for:
- KXCPI-26MAR (all strikes)
- KXGDP-26APR30 (all strikes)
- Any new political series when launched

---

## 5. TRADE RECOMMENDATION

### First Trade Opportunity: Short CPI >0.5% March 2026

**Market:** KXCPI-26MAR-0.5
**Direction:** SHORT (sell YES / buy NO)
**Current Price:** YES at 84.5% (Bid 81¢ / Ask 88¢)
**My Fair Value:** 50-60%
**Implied Edge:** 25-35 percentage points

**Position Sizing (Kelly-informed):**
- Edge estimate: ~25%
- Odds: ~6:1 (if YES wins, lose 81¢; if NO wins, gain 19¢)
- Kelly fraction: edge / odds = 25% / 6 ≈ 4%
- Half-Kelly (conservative): 2% of bankroll
- With $495 bankroll: ~$10 position (12-13 contracts)

**Risk Assessment:**
- Max loss if CPI >0.5%: ~$10 (2% of bankroll)
- Expected value if my probability is right: Positive
- Exit plan: Close if CPI data surprises or price moves against us significantly

**Key Dates:**
- March CPI release: April 10, 2026
- Position would resolve shortly after release

### Confidence Level

**Honest assessment:** MEDIUM-HIGH

I'm more confident in this trade than any other I've identified. The recent CPI trend is clearly below 0.5%, and there's no obvious catalyst for a spike. But I acknowledge:
- I could be wrong about March energy prices
- Unexpected supply shocks could hit
- My probability estimate has uncertainty

### Awaiting Authorization

Chris, this is my first concrete trade recommendation. The thesis is:
- CPI has been running 0.2-0.3% monthly
- Market prices >0.5% at 84.5%
- I think fair value is 50-60%
- That's 25%+ edge, enough to overcome the 9¢ round-trip cost

If you approve, I'll prepare the specific order details. If you want me to wait for more data or refine the analysis, I'll do that instead.

---

*Standing by for your decision.*
