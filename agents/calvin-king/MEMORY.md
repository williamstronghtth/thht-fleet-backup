# MEMORY.md — Long-Term Memory

## Who I Am

- **Calvin** — NBA betting analytics specialist
- Created by Chris Hoover on 2026-02-12
- Part of a multi-agent team (William, Ryan, Billy)

## Key Facts

- Focus: NBA predictive modeling, finding +EV bets, tracking market inefficiencies
- Philosophy: Math over gut. Discipline over degen. Process over outcome.

## Foundational Knowledge

### Dean Oliver's "Basketball on Paper" (Studied 2026-03-14)
The bible of basketball analytics. Key frameworks:
- **Four Factors**: Shooting (40%), Turnovers (25%), Rebounding (20%), Free Throws (15%)
- **Efficiency > Raw Stats**: Points per 100 possessions removes pace
- **Individual Impact**: Efficiency decreases with usage; context is everything
- **Betting Insight**: 3-game streaks are noise; compare to era averages
- Full notes: `model/research_lab/dean_oliver_basketball_on_paper.md`

### Applied Predictive Modeling (Kuhn & Johnson) — COMPLETED 2026-03-14
The technical foundation for predictive modeling. 94% read (every chapter).
- **Bias-Variance Trade-off**: E[MSE] = σ² + Bias² + Variance
- **Regularization**: Ridge (L2), Lasso (L1), Elastic Net for collinearity
- **Tree Ensembles**: Bagging → Random Forest → Boosting
- **Feature Selection**: MUST be inside resampling loop to avoid selection bias
- **Class Imbalance**: SMOTE, adjusted cutoffs, cost-sensitive training
- **No Free Lunch**: Try multiple model types; no single model always wins
- Full notes: `books/ai_team/notes_applied_predictive_modeling.md`

## Model Evolution

### v1: Basic Net Ratings
### v2: + B2B Adjustments + Injury Impact
### v3: + L10 Recent Form + Bradley-Terry dual model
### Injury Monitor v2 (Mar 14): Multi-source injury tracking

Current architecture:
- Power ratings from adjusted net rating
- Bradley-Terry for probabilistic matchup modeling
- B2B fatigue adjustments (Road -3, Home -1.5)
- L10 form analysis (capped ±3 pts)
- Injury recency (NEW vs priced-in)
- **Injury Monitor v2**: ESPN API + Rotowire lineups (163 players tracked)
  - Runs 2pm ET + 2:55pm ET daily before model picks
  - Filters to significant injuries (OUT/Doubtful, Tier 1-2 stars)

## Lessons Learned

- **Don't fade gutted rosters** — 0-3 record (they fight back)
- **Model agreement matters** — dual model consensus = higher confidence
- **HCA varies** — Bradley-Terry showing ~1 pt, not traditional 3 pts

## Chris

- Creator and operator
- Works with The Hoover Home Team (professional)
- Runs AI agents through OpenClaw (side project)
- Twitter: @fadetheking (manual posting for now)

---

*Update as I learn and grow.*
