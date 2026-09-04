# Elliot's Research Lab 📈

Self-improving system for prediction market trading. Track positions, measure accuracy, refine the edge.

Inspired by Karpathy's autoresearch — iterate on your model, not just run it.

## The Loop

```
3am EST daily: Markets settled → Check outcomes → Log results
     ↓
Track which thesis fired → Which hit, which missed
     ↓
Update shadow ledger → Paper P&L
     ↓
Weekly review → Pattern analysis → Strategy refinement
     ↓
Update STRATEGY.md with learnings → Repeat
```

---

## Files

| File | Purpose |
|------|---------|
| `positions.jsonl` | Every position logged with thesis, entry price, size |
| `outcomes.jsonl` | Results: win/loss, ROI, actual vs expected |
| `shadow-ledger.json` | Running P&L for paper trades |
| `category-performance.json` | Win rate by market category |
| `insights.md` | Human-readable learnings |
| `current-config.json` | Active model parameters |

---

## Position Logging Format

### positions.jsonl
```json
{
  "id": "pos-2026-03-30-001",
  "timestamp": "2026-03-30T14:00:00Z",
  "platform": "kalshi",
  "market": "KXCPI-26MAR-T3.0",
  "market_title": "CPI YoY > 3.0%?",
  "category": "economics|politics|entertainment|crypto|weather|sports",
  "position": "yes|no",
  "entry_price": 0.35,
  "contracts": 100,
  "cost_basis": 35.00,
  "max_payout": 100.00,
  "thesis": "Cleveland Fed nowcast shows 3.2%, market underpricing...",
  "edge_estimate_pct": 8,
  "expiry": "2026-04-10",
  "spike_trade": false,
  "reactive_to": null
}
```

### outcomes.jsonl
```json
{
  "id": "pos-2026-03-30-001",
  "timestamp": "2026-03-31T08:00:00Z",
  "result": "win|loss|expired",
  "exit_price": 1.00,
  "pnl_dollars": 65.00,
  "pnl_pct": 185.7,
  "hold_time_hours": 240,
  "thesis_correct": true,
  "category": "economics",
  "notes": "CPI came in at 3.1%, thesis validated"
}
```

---

## Metrics Tracked

### Primary (Edge Validation)
1. **ROI by Category** — Which market types are we actually profitable in?
2. **Win Rate** — Overall and by category
3. **Edge Estimate Accuracy** — Are our 8% edge estimates actually 8%?

### Trade Analysis
4. **Spike vs Non-Spike** — Do reactive trades outperform?
5. **Hold Time vs P&L** — Optimal holding periods
6. **Entry Price Zones** — Better edge at extremes (<20¢, >80¢)?

### Calibration
7. **Thesis accuracy** — When we're confident, are we right?
8. **Category drift** — Are we chasing categories where we have no edge?

---

## Shadow Ledger

Paper trading until the model proves itself. Track as if real money:

```json
{
  "starting_bankroll": 1000,
  "current_bankroll": 1000,
  "total_deployed": 0,
  "total_returned": 0,
  "realized_pnl": 0,
  "unrealized_pnl": 0,
  "roi_pct": 0,
  "positions_opened": 0,
  "positions_closed": 0,
  "win_count": 0,
  "loss_count": 0,
  "best_trade_pnl": 0,
  "worst_trade_pnl": 0,
  "last_updated": "2026-03-30T00:00:00Z"
}
```

---

## Daily Review (3am EST)

1. Check which markets settled/expired since yesterday
2. Calculate P&L for closed positions
3. Update shadow ledger
4. Log to outcomes.jsonl
5. Update category-performance.json
6. Flag any category with 3+ consecutive losses

## Weekly Review (Sundays 7pm EST)

1. Calculate weekly ROI by category
2. Analyze spike trades vs thesis trades
3. Identify categories with edge vs noise
4. Review open positions — any to exit early?
5. Update insights.md with patterns
6. Propose STRATEGY.md amendments if data supports
7. Report to Chris

---

## Success Criteria (Before Scaling Up)

- [ ] 50+ closed positions
- [ ] Overall ROI > 5% (beating fees + opportunity cost)
- [ ] At least one category with >60% win rate, 10+ trades
- [ ] Spike trades outperforming non-spike by 10%+ ROI
- [ ] No category with 15+ trades below 40% win rate

---

## Category Focus (from STRATEGY.md)

| Category | Priority | Notes |
|----------|----------|-------|
| Spike/Reactive | P1 | Highest expected edge |
| Political | P2 | When available, emotional retail |
| Entertainment | P3 | Chris's info edge |
| Economics | P4 | CPI, Fed — systematic possible |
| Weather | P5 | Low priority, wide spreads |
| Sports | Avoid | 80% parlay volume, no edge |

---

*"Scan systematically, decide with information, track everything."*
