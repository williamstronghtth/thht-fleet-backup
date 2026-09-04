# NBA Betting Model V3 Specification

## Overview
Model V3 synthesizes learnings from 18 sports analytics and betting books into a robust, backtestable system.

## Core Principles (From Literature)

### 1. Market Selection (Skiena, Miller/Davidow)
- **Focus**: NBA player props + totals (less efficient than sides)
- **Avoid**: NFL sides (most efficient market)
- **Sweet spot**: 2-4 point edges (backtest validated)

### 2. Probability Framework (Silver, Wong, Buchdahl)
- Output TRUE probability, not just picks
- Compare to implied probability from odds
- Only bet when edge > vig + uncertainty margin
- Track Closing Line Value (CLV) as primary metric

### 3. Statistical Rigor (Pardo, Buchdahl)
- Minimum 200 bets for significance
- Walk-forward validation
- Max 8-10 parameters (prevent overfit)
- Expect 3-8% edge, 52-57% win rate

## Model Components

### A. Team Ratings (Oliver, Winston, Mack)
```python
# Core ratings from Basketball-Reference
ORtg = Offensive Rating (pts per 100 poss)
DRtg = Defensive Rating (pts allowed per 100 poss)
NetRtg = ORtg - DRtg

# Pace for totals
Pace = Possessions per 48 minutes
```

### B. Spread Prediction (Winston, Mack)
```python
predicted_margin = (home_netrtg - away_netrtg) / 2 + HCA + adjustments

Where:
- HCA = 3.9 (base) + altitude_bonus
- altitude_bonus = 1.0 if home in [DEN, UTA] else 0
```

### C. Adjustments

#### Rest (Wong, Shea)
| Situation | Adjustment |
|-----------|------------|
| Home B2B | -3.0 pts |
| Away B2B | +3.0 pts (to home) |
| Home 3+ rest | +0.5 pts |
| Away 3+ rest | -0.5 pts |

#### Injuries (Taylor, Oliver)
```python
# Star player impact (if OUT)
injury_adj = player_impact * minutes_share * efficiency_multiplier

# Efficiency multiplier: remaining players get worse as usage increases
efficiency_multiplier = 1.15  # 15% additional penalty
```

| Player Tier | Point Impact |
|-------------|--------------|
| MVP candidate | 6-8 pts |
| All-NBA | 4-6 pts |
| All-Star | 2.5-4 pts |
| Quality starter | 1.5-2.5 pts |

### D. Totals Prediction (Oliver, Goldsberry)
```python
expected_total = (home_ortg + away_ortg) * expected_pace / 100

expected_pace = (home_pace + away_pace) / 2
# Adjust: slower team has more control
```

### E. Shot Profile Score (Goldsberry)
```python
shot_quality = (rim_rate * 1.30 + 
                corner3_rate * 1.20 + 
                above3_rate * 1.11 + 
                midrange_rate * 0.84)

# Score > 1.10 = bonus to ORtg expectation
# Score < 1.00 = penalty
```

### F. Bayesian Shrinkage (Mack)
```python
def shrink_to_prior(observed, games_played, prior, prior_weight=15):
    """Early season: trust prior more. Late season: trust data."""
    weight = games_played / (games_played + prior_weight)
    return weight * observed + (1 - weight) * prior

# Prior = last season's rating (or league average if new team)
```

### G. Four Factors Weighting (Oliver)
```python
four_factors_edge = (
    0.40 * (team_efg - opp_efg_allowed) +
    0.25 * (opp_tov_rate - team_tov_rate) +
    0.20 * (team_oreb_rate - opp_dreb_rate) +
    0.15 * (team_ft_rate - opp_ft_rate_allowed)
)
```

## Bet Selection Criteria

### Must Pass All:
1. **Edge threshold**: Model edge ≥ 2.0 points
2. **Edge quality**: Prefer 2-4 pt range (sweet spot)
3. **No danger zone**: Skip if edge > 6 pts (historically unreliable)
4. **Confidence**: Model probability ≥ 53%

### Ranking (when multiple qualify):
1. Highest edge in sweet spot (2-4 pts)
2. Highest model confidence
3. Props > Totals > Spreads (market efficiency)

## Bet Sizing (Miller/Davidow, Wong)

### Kelly Criterion (Fractional)
```python
def kelly_bet(prob, odds, fraction=0.25):
    """
    Fractional Kelly for bet sizing
    prob: our estimated probability
    odds: American odds (e.g., -110)
    fraction: Kelly fraction (0.25 = quarter Kelly)
    """
    decimal_odds = 1 + 100/abs(odds) if odds < 0 else 1 + odds/100
    b = decimal_odds - 1
    q = 1 - prob
    kelly = (prob * b - q) / b
    return max(0, kelly * fraction)
```

### Unit Sizing
- Base unit: 1% of bankroll
- Max bet: 3% of bankroll (even with large edge)
- Quarter Kelly for safety

## Tracking Requirements (All Books)

### Per Bet:
- Date, game, pick type
- Line when placed
- Closing line (for CLV)
- Model probability
- Model edge (points)
- Result (W/L/P)
- Profit/Loss (units)
- Reasoning

### Aggregate:
- CLV (most important)
- ROI
- Win rate by confidence tier
- Win rate by bet type
- Calibration curve

## Backtest Protocol (Pardo)

### Methodology:
1. **Walk-forward**: Train on prior games, test on next week
2. **1 pick per day**: Best edge that passes criteria
3. **Include vig**: -110 standard
4. **No lookahead**: Only use data available at bet time
5. **Track CLV**: Compare to closing line

### Validation:
- Out-of-sample only (no peeking)
- Report confidence intervals
- Flag if results too good (>10% ROI suspicious)

## Expected Performance (Realistic)

| Metric | Target | Suspicious |
|--------|--------|------------|
| Win Rate | 53-57% | >60% |
| ROI | 3-8% | >12% |
| CLV | +0.5 to +1.5 pts | >3 pts |
| Max Drawdown | 15-25% | <5% |

## Model Limitations (Acknowledged)

1. **Sample size**: Need 200+ bets for significance
2. **Edge decay**: Expect edges to shrink over time
3. **Injury timing**: May miss late scratches
4. **Line movement**: Model doesn't react to steam
5. **Variance**: Even +EV bets lose sometimes

---

*V3 Built from: Miller/Davidow, Wong, Buchdahl, Winston, Oliver, Taylor, Shea (x2), Zuccolotto, Silver, Mack (x2), T. Miller, Elmore, Dinov, Skiena, Goldsberry, Pardo*
