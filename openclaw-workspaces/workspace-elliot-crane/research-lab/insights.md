# Elliot's Insights

Learnings from prediction market analysis. Updated weekly.

---

## 2026-03-30 — Lab Initialized

Starting structured tracking for Kalshi positions.

**Baseline hypothesis from STRATEGY.md:**
- Spike/reactive trades should have highest edge (P1)
- Pure systematic mid-range has negative edge after fees
- Entertainment markets have tightest spreads — need info edge
- Maker advantage real but only matters with wide spreads

**What to watch:**
- Does spike detection actually produce better entries?
- Which categories deliver consistent ROI?
- Hold time optimization — are we exiting too early/late?
- Fee drag at different position sizes

---

## Category Hypotheses

| Category | Hypothesis | Expected Win Rate |
|----------|------------|-------------------|
| Spike/Reactive | Best edge, fast money | 60%+ |
| Political | Emotional retail, inefficient | 55-60% (when available) |
| Entertainment | Need Chris's info edge | 50-55% solo, 60%+ with info |
| Economics | CPI/Fed — can be systematic | 52-55% |
| Weather | Wide spreads, low volume | 50-52% |
| Sports | Avoid — parlay volume, no edge | <50% |

---

## Open Questions

1. What's the optimal position size given fee structure?
2. Should we ever take maker vs taker?
3. How much does hold time correlate with P&L?
4. Are we better at YES or NO positions?

---

## 2026-04-06 — Low-Volume Review Week

Structured lab tracking still shows **0 closed positions** for the week ending 2026-04-05, so no statistically meaningful performance conclusions can be drawn yet.

**What did matter this week:**
- Infrastructure quality improved more than trade sample size
- Correcting Kalshi API field mappings surfaced many more liquid non-sports markets
- Entertainment and politics appear more promising on liquidity than initially assumed
- We need closed-trade discipline in the research ledger before changing weights or thresholds

**Operational takeaway:**
- Do **not** update category weights from intuition alone
- Keep current config conservative until we have at least a modest resolved sample
- Prioritize complete position/outcome logging so weekly review becomes decision-useful

*More insights as data accumulates...*
