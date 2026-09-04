# NBA Betting Model Specification

## Objective
Find value bets across spreads, totals, moneylines, and player props using model-based predictions with reliability scores.

## Core Approach
1. Generate expected outcomes (points, win %)
2. Compare to market lines
3. Flag discrepancies as potential value
4. Score reliability based on data confidence

---

## Phase 1: Foundation (Free Data)

### Data Sources
| Source | Data | Cost |
|--------|------|------|
| Basketball-Reference | Team/player stats, advanced metrics | Free |
| NBA.com/stats | Official box scores, tracking data | Free |
| ESPN | Injuries, schedules, basic odds | Free |
| The Odds API | Live betting lines (500 req/mo free) | Free tier |

### Key Metrics to Track
**Team Level:**
- Offensive/Defensive Rating (per 100 possessions)
- Pace (possessions per game)
- Net Rating (home vs away splits)
- Last 10 games trend
- Rest days (0, 1, 2+)
- Back-to-back performance

**Player Level:**
- Usage rate
- Minutes trend
- Performance vs position (for props)
- Injury impact multiplier

### Model v1: Point Spread
```
Expected Margin = (Team A Off Rating - Team B Def Rating) 
                + (Team B Off Rating - Team A Def Rating)
                + Home Court Advantage (~3.5 pts)
                + Rest Adjustment
                + Injury Adjustment
```

### Model v2: Totals
```
Expected Total = ((Team A Pace + Team B Pace) / 2) 
               * ((Team A Off + Team B Off + Team A Def + Team B Def) / 200)
               + Pace-up/Pace-down adjustment
```

### Reliability Score (1-10)
- Sample size (early season = lower)
- Lineup stability (injuries = lower)
- Model confidence interval width
- Recent predictive accuracy

---

## Phase 2: Enhancement (If Winning)

### Paid Upgrades to Consider
- Cleaning The Glass ($150/yr) - best adjusted stats
- Synergy Sports - play-by-play data
- PrizePicks/Underdog data feeds
- Real-time odds feeds

### Advanced Features
- Player prop modeling
- Live line movement tracking
- Closing line value analysis
- Bankroll/Kelly criterion

---

## Output Format

### Daily Pick Report
```
GAME: LAL @ BOS | 7:30 PM ET
Model Spread: BOS -6.2 | Market: BOS -4.5
VALUE: BOS -4.5 (1.7 pts edge)
Reliability: 7/10
Key Factor: Lakers on B2B, Tatum questionable

Bet Type: SPREAD
Pick: BOS -4.5
Confidence: HIGH
```

---

## Next Steps
1. [ ] Scrape current team ratings from Basketball-Reference
2. [ ] Get today's schedule + lines
3. [ ] Build v1 spread model
4. [ ] Test on tonight's games
5. [ ] Iterate based on results
