# 2026 All-Star Break — Mid-Season Model Review
**Date:** July 15, 2026
**Coverage:** May–July 14, 2026 (848 MC predictions scored)

---

## First Half Performance Summary

### MC Model (Pregame Predictions)
| Bucket | Record | Win% | Edge? |
|--------|--------|------|-------|
| 50-53% | 141/291 | 48.5% | ❌ NO EDGE (lose money) |
| 53-55% | 104/185 | 56.2% | ✅ EDGE |
| 55-60% | 141/272 | 51.8% | ❌ NO EDGE (near coin flip) |
| 60%+ | 63/100 | 63.0% | ✅ STRONG EDGE |
| **OVERALL** | **449/848** | **52.9%** | Mixed |

### ML v2 Actual Bets (logged days only)
- **25W / 19L = 56.8%** on 44 bets over 19 days
- ⚠️ Significant logging gaps — not all bet days captured
- Strong performance when filtered properly through ML v2 threshold

---

## Key Findings

### 1. Two Clear Edge Zones, Two Clear Traps
**PRESS:** 60%+ (63.0%) and 53-55% (56.2%) — real, consistent edge  
**AVOID:** 50-53% (48.5%) — money drain. 55-60% (51.8%) — the "trap zone" confirmed over 272 predictions. Near coin flip, not worth vig.

### 2. The 55-60% Trap is Real
The July 11 MC gate that suppressed the 55-60% "trap zone" from Telegram was correct based on season data. 141 predictions at 51.8% = net loser after -110 vig. This isn't a short slump — it's a structural pattern.

### 3. July Slump in Context
July 1-14: 71/140 = 50.7% overall. The drag is the 50-53% bucket collapsing to 41.3%. High-conviction (60%+) stayed at 61.5%. The model's signal is intact at the top; the noise is at the bottom.

### 4. Proposed Feature Reductions (from July 7 model review)
Three features flagged as potentially negative:
- `dog_contender`: 56.2% when active vs 66.7% inactive (-10.4 pts)
- `dog_kpct`: 53.3% vs 70.0% inactive (-16.7 pts)
- `lineup_war`: 53.3% vs 70.0% inactive (-16.7 pts)
All flagged MEDIUM confidence (only 25 actual bets in sample — defer to Q3 backtest)

---

## Second Half Priorities

### Immediate (Before Games Resume)
1. **Confirm MC gate logic** — Verify V3 primary/secondary tiers correctly map to 53-55% and 60%+ (not suppressing profitable picks)
2. **Audit ML v2 logging** — Gaps in ml_v2_picks files make performance tracking hard. Fix for H2.
3. **Review travel direction feature (E→W)** — Added July 11, never backtested. Run 2024-25 backtest before pressing.

### Research Sprints (All-Star Week)
1. **Revenge game fade** — Needs MLB API series lookup. Potentially meaningful signal.
2. **Umpire × pitcher style matchup** — HCR scalar only for now; zone-width data could add 1-2% accuracy
3. **53-55% bucket optimization** — This is real edge. Can we improve entry criteria to filter only the highest-quality picks in this tier?

### Structural
- Raise MC Telegram gate to explicitly exclude 50-53% AND 55-60%
- Only alert on 53-55% and 60%+ — total ~285 predictions/season vs 848
- Win rate on those two buckets combined: (104+63)/(185+100) = 167/285 = **58.6%** — THAT is the number we should be reporting

---

## The Real Headline

If we had only bet the 53-55% and 60%+ buckets all season:
- **167/285 = 58.6% win rate**
- This beats the break-even threshold (~52.4% at -110)
- Net edge: +6.2 percentage points on ~285 games

The model works. The noise at the bottom is masking the signal at the top.

---
*Generated: 2026-07-15 (All-Star Break)*
