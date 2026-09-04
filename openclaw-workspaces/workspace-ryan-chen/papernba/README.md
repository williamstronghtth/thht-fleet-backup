# 🏀 PaperNBA — NBA Paper Betting Model

A Python-based NBA prediction system that uses three specialized model layers — **Coach**, **Player**, and **Referee** — combined with Monte Carlo simulation to identify betting edges. All bets are paper (simulated) to track model performance without financial risk.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Data Ingestion                          │
│  games • players • coaches • lineups • playbyplay • refs    │
│              (nba_api → raw JSON → parquet)                 │
└──────────────────────┬──────────────────────────────────────┘
                       │
       ┌───────────────┼───────────────┐
       ▼               ▼               ▼
┌─────────────┐ ┌─────────────┐ ┌─────────────┐
│ Coach Model │ │Player Model │ │  Ref Model  │
│ • rotations │ │• per-poss   │ │• foul rates │
│ • foul mgmt │ │• chemistry  │ │• home bias  │
│ • timeouts  │ │• matchups   │ │• late game  │
└──────┬──────┘ └──────┬──────┘ └──────┬──────┘
       │               │               │
       └───────────────┼───────────────┘
                       ▼
              ┌─────────────────┐
              │ Game Simulator  │
              │ (Monte Carlo)   │
              │ 10,000 sims/game│
              └────────┬────────┘
                       ▼
              ┌─────────────────┐
              │ Betting Engine  │
              │ • Edge calc     │
              │ • Kelly sizing  │
              │ • Paper bankroll│
              └─────────────────┘
```

## The Three-Model Approach

### 🧑‍💼 Coach Model (`models/coach/`)

Coaches are creatures of habit. We model their decision-making:

- **Rotations** — Who plays when? Starter minutes, bench rotation sequences, crunch-time lineups. Tells us *who will be on the floor* at any moment.
- **Foul Trouble** — How does the coach react when a star picks up early fouls? Conservative (bench immediately) or aggressive (leave them in)?
- **Timeouts** — When do they call timeouts? Response to opponent runs, late-game strategy, challenge usage. Affects pace projections.

### 🏃 Player Model (`models/player/`)

Individual and collective player performance:

- **Per-Possession** — Pace-normalized stats (pts/100 poss, TS%, usage rate). Includes fatigue curves, home/away splits, and rolling averages.
- **Lineup Chemistry** — The nonlinear interactions when players share the floor. Some duos produce more than the sum of their parts; others less.
- **Matchups** — How does a player perform against specific opponents? Adjustments for defensive archetype, pace, and team scheme.

### 👨‍⚖️ Referee Model (`models/referee/`)

The most underrated factor in NBA modeling:

- **Foul Rates** — Each ref has measurably different foul-calling tendencies. A whistle-happy crew means more FTAs, more foul trouble, different pace.
- **Home Bias** — Refs are influenced by home crowds. We model which refs show the most bias and adjust free-throw projections.
- **Late Game** — "Swallowing the whistle" in crunch time varies by ref. This affects 4th quarter scoring, overtime probability, and closing line value.

## Data Pipeline

### Ingestion (`ingestion/`)

All data comes from `nba_api` (stats.nba.com):

| Module | Source | What it fetches |
|--------|--------|----------------|
| `games.py` | LeagueGameLog | Season schedule and scores |
| `players.py` | LeagueDashPlayerStats, PlayerGameLog | Player stats and game logs |
| `coaches.py` | CommonTeamRoster | Coach assignments per team |
| `lineups.py` | LeagueDashLineups | 5-man lineup performance |
| `playbyplay.py` | PlayByPlayV2 | Every event in every game |
| `referees.py` | BoxScoreSummaryV2 | Referee assignments per game |

Data is cached as raw JSON in `data/raw/` and processed to parquet in `data/processed/`.

### Processing Flow

```
nba_api → data/raw/{season}/{category}/*.json
       → data/processed/{season}/{category}/*.parquet
       → models trained in memory
       → predictions generated
       → bets tracked in data/betting/history.json
```

## Betting Engine (`betting/`)

- **`odds.py`** — American ↔ decimal odds conversion, implied probability, vig removal, edge/EV calculation
- **`bankroll.py`** — Paper bankroll with fractional Kelly criterion sizing (default: quarter-Kelly with 5% max bet cap)
- **`tracker.py`** — Persistent bet logging with full context (game, odds, model probability, result, P&L)

## Getting Started

### Prerequisites

- Python 3.11+
- ~2GB disk space for a full season of data

### Installation

```bash
cd projects/papernba
pip install -r requirements.txt
```

### Initial Data Pull

```bash
# Quick start — games, players, coaches, lineups (takes ~5 minutes)
python scripts/ingest_season.py --skip-pbp --skip-refs

# Full data pull including play-by-play (~3-4 hours due to API rate limits)
python scripts/ingest_season.py
```

### Daily Workflow

```bash
# Morning: update data from yesterday's games
python scripts/daily_update.py

# Afternoon: generate today's predictions
python scripts/predict_today.py --dry-run    # preview
python scripts/predict_today.py              # with paper bets
```

## Project Structure

```
papernba/
├── config.py              # Central configuration
├── requirements.txt       # Python dependencies
├── README.md
│
├── ingestion/             # Data fetching & processing
│   ├── games.py
│   ├── players.py
│   ├── coaches.py
│   ├── lineups.py
│   ├── playbyplay.py
│   └── referees.py
│
├── models/
│   ├── coach/
│   │   ├── rotations.py      # Rotation pattern analysis
│   │   ├── foul_trouble.py   # Foul trouble management
│   │   └── timeouts.py       # Timeout usage patterns
│   ├── player/
│   │   ├── per_possession.py  # Per-possession performance
│   │   ├── lineup_chemistry.py # Lineup interaction effects
│   │   └── matchups.py        # Player/team matchup adjustments
│   ├── referee/
│   │   ├── foul_rates.py     # Foul-calling tendencies
│   │   ├── home_bias.py      # Home-court foul bias
│   │   └── late_game.py      # Clutch-time officiating
│   └── game/
│       ├── simulator.py      # Monte Carlo game engine
│       └── predictor.py      # Prediction orchestrator
│
├── betting/
│   ├── odds.py            # Odds math
│   ├── bankroll.py        # Kelly criterion bankroll
│   ├── tracker.py         # Bet logging & tracking
│   └── history.json       # Persistent bet history
│
├── analysis/
│   ├── backtest.py        # Walk-forward backtesting
│   └── reports.py         # Report generation
│
├── scripts/
│   ├── ingest_season.py   # Full season data pull
│   ├── daily_update.py    # Daily data refresh
│   └── predict_today.py   # Generate today's picks
│
├── data/
│   ├── raw/               # Raw API responses (JSON)
│   ├── processed/         # Clean data (parquet)
│   └── models/            # Serialized trained models
│
└── books/                 # Reference reading material
```

## Roadmap

- [x] Data ingestion layer (nba_api integration)
- [x] Model skeletons (coach, player, referee)
- [x] Game simulator framework (Monte Carlo)
- [x] Betting engine (odds, Kelly, tracking)
- [x] Analysis framework (backtest, reports)
- [ ] Implement rotation extraction from PBP
- [ ] Implement per-possession calculations
- [ ] Implement lineup chemistry scoring
- [ ] Implement referee foul rate decomposition
- [ ] Implement full possession-level simulation
- [ ] Add historical odds data source
- [ ] Build walk-forward backtest
- [ ] Calibration analysis and model tuning
- [ ] Player prop predictions
- [ ] Live/in-game model updates

## Philosophy

This model is built on a few key beliefs:

1. **Context matters more than box scores.** Who's reffing, who's coaching, who's on the floor together — these contextual factors are underweighted by most models.

2. **Simulate, don't predict.** Instead of predicting a single score, we simulate thousands of outcomes to get probability distributions. This is how we find edges.

3. **Bankroll management is the edge.** Even a small predictive edge becomes profitable with proper Kelly criterion sizing. Most bettors lose money from bad sizing, not bad picks.

4. **Paper first.** We track everything on paper before ever considering real money. The model needs to prove itself over hundreds of bets.
