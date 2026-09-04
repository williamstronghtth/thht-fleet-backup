# papernba — Project Roadmap

## Phase 1: Data Foundation ✅
- [x] Project structure
- [x] Ingestion layer (nba_api)
- [x] Model stubs
- [x] Betting module
- [x] Book research & summaries

## Phase 2: Data Collection (NEXT)
- [ ] Pull 2023-24 + 2024-25 season data (games, PBP, lineups, players)
- [ ] Pull referee assignment data
- [ ] Pull coach data
- [ ] Validate data quality & completeness
- [ ] Build processed parquet files from raw JSON

## Phase 3: Model Training
- [ ] Coach rotation model — analyze PBP for substitution patterns
- [ ] Coach foul trouble model — how each coach adjusts
- [ ] Player per-possession profiles
- [ ] Lineup chemistry scoring (5-man unit performance)
- [ ] Referee foul rate baselines
- [ ] Referee home bias analysis
- [ ] Referee late-game whistle tendencies

## Phase 4: Game Simulator
- [ ] Wire up coach + player + ref models into simulator
- [ ] Monte Carlo simulation engine
- [ ] Calibrate against known results
- [ ] Backtest against 2023-24 season

## Phase 5: Betting & Validation
- [ ] Connect predictions to betting odds
- [ ] Kelly criterion position sizing
- [ ] Paper bet tracking
- [ ] ROI analysis & reporting
