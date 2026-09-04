# 2026-03-26 — Side Model: Line Movement Prediction

## Discovery Path
1. Phase 4 CLV test showed 22% beat rate — we're on wrong side of sharp money
2. But opening line underdogs are structurally profitable (+1.4% blind)
3. Sharp money on dogs = +8.9% ROI (1,973 games)
4. Reverse engineered: SIERA gap is the #1 predictor of sharp dog movement

## Key Findings from Reverse Engineering

### Strongest Predictor: Dog Pitcher SIERA
- Dog pitcher SIERA advantage ≥ +0.5 → 57.6% of time line moves toward dog
- Avg SIERA gap in sharp→dog games: -0.32 (close matchup)
- Avg SIERA gap in sharp→fav games: -0.52 (dog pitcher much worse)
- **Sharps bet when the dog's pitcher isn't as bad as the odds imply**

### Other Predictors
- Small dogs (+100 to +140) get more sharp action (34-35%) than big dogs (+200+, 28%)
- Mid-late season (Jul-Oct) more sharp action than early (Mar-Apr)
- Specific teams attract/repel sharp money consistently

### Results
- Sharp→Dog: dog wins 44.6%, +8.9% ROI
- Sharp→Fav: dog wins 38.2%, -7.3% ROI
- 16.2% ROI spread between the two groups

### Teams
- Sharp dog magnets: NYM (46%), TOR (40%), MIL (40%), CLE (39%)
- Sharp-faded favorites: LAA (40%), HOU (39%), STL (39%)

## Model Architecture
- Predict: will line move toward dog by ≥1% before close? (binary)
- Primary feature: pitcher SIERA gap (dog vs fav)
- Secondary: opening odds range, month, team patterns
- Walk-forward: train prior years, test next year
- Bet: underdog ML on Kalshi at opening price when model says sharp money incoming

## Status: BUILDING
