# TOOLS.md - Local Notes

## Kalshi API

- **Docs:** https://docs.kalshi.com
- **API Base:** https://api.elections.kalshi.com/trade-api/v2
- **Authentication:** RSA-PSS signing (SHA256, MAX_LENGTH salt)
- **Credentials:** Stored in gateway config (env.vars)
- **Client:** `/root/.openclaw/workspace-elliot-crane/kalshi/kalshi_client.py`

### Key Endpoints
- `GET /portfolio/balance` - Account balance
- `GET /portfolio/positions` - Current positions
- `GET /portfolio/orders` - Orders
- `POST /portfolio/orders` - Place order
- `GET /markets` - List markets
- `GET /markets/{ticker}` - Market details
- `GET /markets/{ticker}/orderbook` - Order book

## Web Scraping

When scraping data, use **Scrapling** for sites with bot protection:
```python
source /root/.openclaw/workspace-ryan-chen/scrapling_env/bin/activate
from scrapling import StealthyFetcher
fetcher = StealthyFetcher()
page = fetcher.fetch('https://example.com')
```

## Data Sources

- Kalshi API (market prices, volumes)
- Economic calendars (FOMC, CPI releases)
- Weather APIs (for weather markets)
- News feeds (for breaking events)
- Polymarket API (for cross-platform arbitrage checks)

## Scripts Built

| Script | Purpose | Status |
|--------|---------|--------|
| `kalshi_client.py` | Core API client | ✅ Working |
| `hourly_scanner.py` | Economics market scanner | ✅ Running hourly (cron) |
| `bias_calibration.py` | F-L bias adjustment | ✅ Working |
| `entertainment_scanner.py` | Entertainment/culture markets | ✅ Working |
| `backtest_framework.py` | Historical simulation | ⚠️ Needs external data (API doesn't expose settled history) |
| `arbitrage_scanner.py` | Cross-platform arb finder | ✅ Working (no current matches) |
| `scripts/news-digest.mjs` | Hourly news + energy prices | ✅ Running :45 past hour (Ryan built) |
| `scripts/breaking-news-monitor.mjs` | Oil spike alerts (5%+) | ✅ Running every 10 min (Ryan built) |
| `weather_scanner.py` | Weather market edge finder (12 cities) | ✅ Working |
| `gdp_scanner.py` | GDP market analysis | ✅ Working |
| `cpi_scanner.py` | CPI markets + Cleveland Fed nowcast | ✅ Working |
| `fed_scanner.py` | Fed/FOMC rate decision markets | ✅ Working |
| `opportunity_scanner.py` | Multi-category unified scanner | ✅ Working |
| `polymarket_monitor.py` | Cross-platform intelligence | ✅ Working (no econ overlap) |
| `darwin.py` | Darwinian signal weighting | ✅ Working |
| `signal_combiner.py` | Multi-signal combination | ✅ Working |
| `pairs_scanner.py` | Cointegration pairs/spread trading | ✅ Working |
| `category_scoring.py` | Category risk multipliers | ✅ Working |
| `signal_disagreement.py` | Multi-signal consensus detection | ✅ Working |
| `opportunity_evaluator.py` | Unified decision engine | ✅ Working |
| `validation/bootstrap.py` | 10K simulation edge validation | ✅ Waiting for trades |
| `validation/feature_importance.py` | Signal importance tracking | ✅ Working |
| `validation/markov.py` | Price state transition model | ✅ Working |
| `news_monitor.py` | WorldMonitor + Grok news intelligence | ✅ Working |
| `data_source_tracker.py` | Maps 10 public data sources → Kalshi markets; flags new data each hourly scan | ✅ Working |

## Microstructure Module (NEW)

**Location:** `kalshi/microstructure/`

Implements market microstructure analysis from Kyle (1985), Hawkes (1971), Easley et al. (2012), and Almgren-Chriss (2001).

### Quick Scan
```bash
cd ~/workspace && python3 kalshi/microstructure/scan.py TICKER
python3 kalshi/microstructure/scan.py KXCPI-26MAR-T0.7 --exec 100
```

### Components

| Module | Purpose | Key Metric |
|--------|---------|------------|
| `kyle_lambda.py` | Information detection | R² > 0.15 = informed traders |
| `hawkes.py` | Order flow clustering | Branching > 0.7 = momentum cascade |
| `vpin.py` | Flow toxicity | VPIN > 0.65 = one-sided flow |
| `almgren_chriss.py` | Execution scheduling | Optimal trade splitting |
| `analyzer.py` | Unified interface | Risk score 0-100 |

### Decision Rules

| VPIN | R² | Branching | Action |
|------|-----|-----------|--------|
| < 0.4 | < 0.15 | < 0.5 | ✅ TRADE - Normal conditions |
| 0.4-0.65 | < 0.15 | < 0.7 | ⚠️ CAUTION - Size down |
| > 0.65 | ANY | ANY | ❌ AVOID - Informed flow |
| ANY | > 0.15 | ANY | ❌ AVOID - Price reveals info |
| ANY | ANY | > 0.8 | ⚠️ FADE - Momentum, likely to revert |

### Python Usage
```python
from kalshi.microstructure.analyzer import MarketAnalyzer

analyzer = MarketAnalyzer()
result = analyzer.analyze_market('KXCPI-26MAR-T0.7')
print(result.safe_to_trade)  # bool
print(result.risk_score)     # 0-100

schedule = analyzer.get_execution_schedule('TICKER', 100)  # $100 position
print(schedule.trade_sizes)  # array of tranches
```

## Darwinian Signal Weighting (Inspired by ATLAS)

**Location:** `kalshi/darwin.py`, `kalshi/signal_combiner.py`

Tracks signal source accuracy over time and adjusts weights.

### Signal Sources
| Source | Description |
|--------|-------------|
| `weather_forecast` | Open-Meteo/NWS forecasts |
| `sentiment_grok` | X Search sentiment |
| `vpin` | Volume-synchronized flow toxicity |
| `kyle_lambda` | Informed trading detection |
| `cleveland_nowcast` | Cleveland Fed CPI nowcast |
| `edge_estimate` | Our probability vs market |

### Weight Range
- **Minimum:** 0.3x (nearly silenced)
- **Default:** 1.0x (neutral)
- **Maximum:** 2.5x (amplified)

### Daily Update
```bash
python3 kalshi/darwin.py update   # Run daily to adjust weights
python3 kalshi/darwin.py report   # View current weights
```

### Combined Analysis
```python
from kalshi.signal_combiner import SignalCombiner

combiner = SignalCombiner()
analysis = combiner.analyze_market('KXHIGHDEN-26MAR28-B79.5', market_price=0.33)

print(f"Combined probability: {analysis.combined_probability:.0%}")
print(f"Recommendation: {analysis.recommendation}")
print(f"Dominant signal: {analysis.dominant_signal}")
```

### Auto-Integration
The execution engine automatically:
1. Logs all signals when trades execute
2. Scores signals when trades settle
3. Updates weights daily based on performance

## Sentiment Module (NEW)

**Location:** `kalshi/sentiment/`

Uses xAI Grok API with X Search for real-time Twitter/X sentiment analysis.

### Quick Usage
```python
from kalshi.sentiment import SentimentScanner
scanner = SentimentScanner()

# Analyze a specific market
result = scanner.analyze_market('KXCPI-26MAR-T0.7')
print(result.sentiment)  # bullish/bearish/neutral/mixed
print(result.gap)        # crowd_belief - market_price

# Quick topic sentiment
sent = scanner.quick_sentiment('Federal Reserve rate decision')
```

### Cost
- ~$0.01-0.02 per sentiment scan (8 X searches + tokens)
- Billed to xAI API ($25 balance loaded)

### Spike Scanner Integration
```bash
# Run spike check with deep analysis (microstructure + sentiment)
python3 kalshi/spike_alert.py --deep
```

When `--deep` is enabled, actionable spikes get:
1. Microstructure analysis (VPIN, Kyle's λ, Hawkes)
2. X sentiment analysis (crowd belief vs market)
3. Combined signal recommendation

## Execution Engine (NEW)

**Location:** `kalshi/execution/`

Semi-autonomous trading engine with configurable automation levels.

### Decision Rules

| Edge | Checks | Action |
|------|--------|--------|
| ≥15 pts | All pass | 🟢 AUTO-EXECUTE (up to $25) |
| ≥10 pts | ≤1 fail | 🟡 NOTIFY (wait for approval) |
| <10 pts | Any | ⚪ SKIP (log only) |

### Usage

```bash
# Evaluate a single market
python3 kalshi/execution/engine.py evaluate --ticker KXCPI-26MAR-T0.7

# Scan multiple markets (dry run)
python3 kalshi/execution/engine.py scan --tickers KXCPI-26MAR-T0.7 KXCPI-26MAR-T0.8 --dry-run

# View performance report
python3 kalshi/execution/engine.py report

# See pending trades
python3 kalshi/execution/engine.py pending
```

### Python Usage

```python
from kalshi.execution import TradingEngine

engine = TradingEngine(dry_run=True)

# Evaluate opportunity
outcome, analysis = engine.evaluate('KXCPI-26MAR-T0.7')
print(outcome.decision)  # auto_execute / notify / skip
print(outcome.edge)      # edge in points

# Full pipeline (evaluate + execute + log)
result = engine.process_opportunity('KXCPI-26MAR-T0.7')

# Performance report
print(engine.report())
```

### Trade Logging

All decisions logged to `kalshi/execution/logs/trades.jsonl`:
- Signal data (edge, sentiment, microstructure)
- Decision made (auto/notify/skip)
- Execution details (if any)
- Outcome (once resolved)

### Resolve Trades

```python
engine.resolve_trade('T20260327171052', won=True, exit_price=1.0, pnl=25.50)
```

## API Limitations

- Kalshi API doesn't expose historical settled market data
- Must collect our own price history for future backtesting
- Event status field often returns null/unknown

## Position Sizing

Using fractional Kelly:
- Full Kelly: edge / odds
- Half Kelly: (edge / odds) / 2 (recommended for safety)
- Max position: 5% of bankroll on any single trade

---

Add API keys and specific configurations as they become available.
