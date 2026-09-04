"""
analysis/backtest.py — Backtesting engine for the prediction model.

Backtesting is how we validate the model works before risking (paper) money.
Walk-forward backtesting avoids look-ahead bias by only using data available
at prediction time.

Walk-forward approach:
1. Train on seasons [N-3, N-2, N-1]
2. Predict season N games day by day
3. For each game day:
   a. Use only data from before that date
   b. Generate predictions
   c. Compare to actual outcomes
4. Track cumulative performance

Key metrics:
- Log loss (calibration — do 60% predictions win 60% of the time?)
- ATS record (against the spread)
- Over/under record
- Moneyline ROI
- Bankroll curve (simulated Kelly betting)
"""

import logging
from dataclasses import dataclass, field
from datetime import date, timedelta

import numpy as np
import pandas as pd

from betting.bankroll import BankrollManager
from betting.odds import calculate_edge, american_to_decimal
from models.game.predictor import GamePredictor

logger = logging.getLogger(__name__)


@dataclass
class BacktestConfig:
    """Configuration for a backtest run."""
    train_seasons: list[str] = field(default_factory=lambda: ["2022-23", "2023-24"])
    test_season: str = "2024-25"
    n_simulations: int = 5000  # fewer for speed during backtest
    kelly_fraction: float = 0.25
    min_edge: float = 0.03
    initial_bankroll: float = 1000.0
    # What to bet on
    bet_spreads: bool = True
    bet_totals: bool = True
    bet_moneylines: bool = True


@dataclass
class BacktestResult:
    """Results from a backtest run."""
    config: BacktestConfig = field(default_factory=BacktestConfig)
    # Overall
    total_games: int = 0
    games_with_signal: int = 0
    # Spread
    spread_record: tuple = (0, 0, 0)  # W-L-P
    spread_roi: float = 0.0
    # Total
    total_record: tuple = (0, 0, 0)
    total_roi: float = 0.0
    # Moneyline
    ml_record: tuple = (0, 0, 0)
    ml_roi: float = 0.0
    # Bankroll
    final_bankroll: float = 0.0
    peak_bankroll: float = 0.0
    max_drawdown: float = 0.0
    bankroll_curve: list = field(default_factory=list)
    # Calibration
    calibration_bins: dict = field(default_factory=dict)
    log_loss: float = 0.0
    # Daily performance
    daily_results: list = field(default_factory=list)


class Backtester:
    """
    Walk-forward backtesting engine.

    Usage:
        bt = Backtester(config)
        result = bt.run()
        bt.print_report(result)
    """

    def __init__(self, config: BacktestConfig = None):
        self.config = config or BacktestConfig()
        self.predictor = GamePredictor(n_simulations=self.config.n_simulations)
        self.bankroll = BankrollManager(
            initial_balance=self.config.initial_bankroll,
            kelly_fraction=self.config.kelly_fraction,
            min_edge=self.config.min_edge,
        )

    def run(self) -> BacktestResult:
        """
        Execute the full walk-forward backtest.

        TODO:
        1. Load processed game data for the test season
        2. Get list of all game dates
        3. For each date (chronologically):
           a. Train/update models on data up to (but not including) this date
           b. Get today's games
           c. Generate predictions for each game
           d. Compare predictions to actual outcomes
           e. Simulate bets using Kelly criterion
           f. Record results
        4. Aggregate statistics
        5. Return BacktestResult

        Key implementation notes:
        - First ~20 games of season may have poor predictions (small sample)
        - Need historical odds data for realistic ROI calculation
        - Without odds data, use -110 standard juice as approximation
        """
        logger.info("Starting backtest: test season %s", self.config.test_season)

        result = BacktestResult(config=self.config)

        # TODO: Implement walk-forward backtest loop
        # 1. Load season game data
        # 2. Sort by date
        # 3. Walk forward day by day
        # 4. Predict → compare → record

        result.final_bankroll = self.bankroll.state.balance
        result.peak_bankroll = self.bankroll.state.peak_balance
        result.max_drawdown = self.bankroll.state.max_drawdown

        logger.info("Backtest complete: %d games, final bankroll $%.2f",
                     result.total_games, result.final_bankroll)
        return result

    def evaluate_prediction(self, prediction, actual_home: int,
                            actual_away: int, market_odds: dict = None) -> dict:
        """
        Evaluate a single prediction against actual outcome.

        TODO:
        Returns dict with:
        - spread_result: "won"/"lost"/"push"
        - total_result: "won"/"lost"/"push"
        - ml_result: "won"/"lost"
        - model_error: predicted margin - actual margin
        - total_error: predicted total - actual total
        """
        actual_margin = actual_home - actual_away
        actual_total = actual_home + actual_away

        # TODO: Compare prediction to actual
        return {
            "actual_home": actual_home,
            "actual_away": actual_away,
            "actual_margin": actual_margin,
            "actual_total": actual_total,
            "predicted_margin": prediction.predicted_spread,
            "predicted_total": prediction.predicted_total,
            "margin_error": prediction.predicted_spread - actual_margin,
            "total_error": prediction.predicted_total - actual_total,
        }

    def calibration_analysis(self, results: list[dict]) -> dict:
        """
        Check model calibration: do 60% predictions win 60% of the time?

        TODO:
        Bin predictions by predicted probability (e.g., 50-55%, 55-60%, etc.)
        and check actual win rate in each bin.
        Good calibration = bins match predicted probabilities.
        """
        # TODO: Implement calibration binning
        return {}

    def print_report(self, result: BacktestResult) -> str:
        """Format backtest results as a readable report."""
        lines = [
            "=" * 60,
            f"BACKTEST REPORT — {result.config.test_season}",
            "=" * 60,
            f"Games analyzed:    {result.total_games}",
            f"Games with signal: {result.games_with_signal}",
            "",
            f"Spread:  {result.spread_record[0]}-{result.spread_record[1]}-{result.spread_record[2]}  ROI: {result.spread_roi:.1%}",
            f"Total:   {result.total_record[0]}-{result.total_record[1]}-{result.total_record[2]}  ROI: {result.total_roi:.1%}",
            f"ML:      {result.ml_record[0]}-{result.ml_record[1]}-{result.ml_record[2]}  ROI: {result.ml_roi:.1%}",
            "",
            f"Bankroll: ${result.config.initial_bankroll:.0f} → ${result.final_bankroll:.2f}",
            f"Peak:     ${result.peak_bankroll:.2f}",
            f"Max DD:   {result.max_drawdown:.1%}",
            f"Log Loss: {result.log_loss:.4f}",
            "=" * 60,
        ]
        report = "\n".join(lines)
        logger.info("\n%s", report)
        return report
