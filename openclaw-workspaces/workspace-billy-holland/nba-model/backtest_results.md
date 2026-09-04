# NBA Model Backtest Results - 2025-26 Season

*Generated: 2026-02-07 00:47 UTC*

## Summary Statistics

- **Total Games Analyzed:** 769
- **Winner Prediction Accuracy:** 410/769 (53.3%)
- **Mean Absolute Error (MAE):** 12.94 points
- **Root Mean Square Error (RMSE):** 16.48 points
- **Average Error (Bias):** -1.39 points
  - ⚠️ Model tends to underrate home teams

## Against The Spread (ATS) Performance

*Simulated betting with 2+ point edge, assuming market 1.5 pts tighter than model*

### Overall ATS Record: 229-330 (41.0%)
- **ROI at -110 odds:** -21.79%
- **Break-even requirement:** 52.4%
- ❌ **Unprofitable** - Below break-even

### ATS Breakdown:

| Category | W-L | Win% | ROI |
|----------|-----|------|-----|
| Home Picks | 186-257 | 42.0% | -19.8% |
| Away Picks | 43-73 | 37.1% | -29.2% |
| 4+ Point Edge | 138-244 | 36.1% | -31.0% |
| 2-4 Point Edge | 91-86 | 51.4% | -1.8% |
| Backing Favorites | 229-330 | 41.0% | -21.8% |

## Pattern Analysis

### By Home Team Strength:

| Category | Games | Accuracy | MAE |
|----------|-------|----------|-----|
| Elite Home | 153 | 62.1% | 13.1 |
| Good Home | 254 | 57.1% | 12.4 |
| Mediocre Home | 204 | 52.9% | 12.0 |
| Bad Home | 158 | 39.2% | 14.8 |

### By Game Type (Predicted):

| Category | Games | Accuracy | MAE |
|----------|-------|----------|-----|
| Big Mismatch | 66 | 53.0% | 15.1 |
| Moderate | 245 | 52.2% | 13.5 |
| Close Game | 458 | 53.9% | 12.3 |

### By Actual Game Result:

| Category | Games | Accuracy |
|----------|-------|----------|
| Blowout | 372 | 52.7% |
| Comfortable | 187 | 53.5% |
| Nail Biter | 210 | 54.3% |

### By Month:

| Month | Games | Accuracy | MAE |
|-------|-------|----------|-----|

### By Reliability Score:

| Category | Games | Accuracy | MAE |
|----------|-------|----------|-----|
| Medium Reliability | 551 | 52.3% | 13.5 |
| Low Reliability | 218 | 56.0% | 11.4 |

## Model Improvement Suggestions

### 1. Increase Home Court Advantage
- Current HCA: 3.2 points
- Model underestimates home margins by 1.4 points on average
- **Recommendation:** Increase HCA to ~3.9 points

### 2. Improve Close Game Prediction
- Current accuracy in close games (predicted <5 pts): 53.9%
- **Recommendations:**
  - Add recent form/momentum weighting (last 5-10 games)
  - Factor in rest days more heavily
  - Consider clutch/late-game performance metrics

### 4. Better Model Bad Teams
- Accuracy for bad home teams: 39.2% (vs overall 53.3%)
- **Recommendations:**
  - Bad teams have higher variance - factor into reliability
  - Consider tanking/motivation factors late season

### 5. Re-evaluate Large Edge Plays
- 4+ point edge: 36.1% (138-244)
- 2-4 point edge: 51.4% (91-86)
- **Recommendation:** Larger edges aren't performing better, suggesting:
  - Market is efficient at pricing large mismatches
  - Consider reducing confidence on extreme predictions

### General Recommendations

1. **Add Historical Market Lines** - Compare against actual Vegas lines for true edge detection
2. **Include Player-Level Data** - Track injuries, rest, minutes trends
3. **Incorporate Recent Form** - Weight last 10 games more heavily
4. **Tempo Matching** - Factor in pace mismatches more explicitly
5. **Home/Road Splits** - Some teams perform very differently home vs away

---

## Key Takeaways

### What's Working ✅
- 53.3% winner accuracy is above coin-flip (statistically significant)
- Model does well predicting elite home team wins (62.1%)
- 2-4 point edge plays are near break-even (51.4%)

### What's Not Working ❌
- **MAE of 12.94 pts is too high** - typical sports models target 8-10 pts
- **4+ point edges are awful (36.1%)** - suggests extreme predictions are wrong
- **Bad home teams (39.2%)** - model fails to predict upsets
- **All favorites, no dogs** - missing value on underdog side

### Priority Fixes
1. **Increase HCA to 3.9 pts** (immediate, easy fix)
2. **Cap max predicted margin at 8-10 pts** (stops overconfident picks)
3. **Add regression to mean for extreme ratings** (elite/bad teams)
4. **Never bet 4+ point edges** until model improves
5. **Add recent form component** (EWMA of last 10 game margins)