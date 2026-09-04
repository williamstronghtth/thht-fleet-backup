#!/usr/bin/env python3
"""
scripts/predict_today.py — Generate predictions for today's NBA games.

This is the main daily workflow script:
1. Load trained models
2. Get today's schedule
3. Generate predictions for each game
4. Identify betting signals
5. Size bets using Kelly criterion
6. Output predictions report
7. Optionally place paper bets

Usage:
    python scripts/predict_today.py
    python scripts/predict_today.py --date 2025-03-15
    python scripts/predict_today.py --dry-run          # predictions only, no bets
    python scripts/predict_today.py --min-edge 0.05    # higher edge threshold
"""

import argparse
import logging
import sys
import os
from datetime import date

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import config
from models.game.predictor import GamePredictor
from betting.bankroll import BankrollManager
from betting.tracker import BetTracker, BetRecord
from betting.odds import (
    american_to_decimal,
    american_to_implied_prob,
    calculate_edge,
    calculate_ev_american,
)
from analysis.reports import daily_predictions_report

logging.basicConfig(level=config.LOG_LEVEL, format=config.LOG_FORMAT)
logger = logging.getLogger(__name__)


def predict_today(game_date: date = None, season: str = config.CURRENT_SEASON,
                  dry_run: bool = False, min_edge: float = 0.03,
                  n_simulations: int = 10000) -> None:
    """
    Generate predictions and betting signals for today's games.

    TODO:
    1. Load/train models
    2. Fetch today's schedule
    3. For each game:
       a. Get team rosters, injuries, ref crew
       b. Run game simulation
       c. Compare to market odds (manual input for now)
       d. Identify edges
       e. Size bets with Kelly criterion
    4. Generate report
    5. Place paper bets (unless dry_run)

    Parameters
    ----------
    game_date : date
        Date to predict. Defaults to today.
    season : str
        NBA season string.
    dry_run : bool
        If True, generate predictions but don't log bets.
    min_edge : float
        Minimum edge to generate a signal.
    n_simulations : int
        Number of Monte Carlo simulations per game.
    """
    if game_date is None:
        game_date = date.today()

    logger.info("=" * 60)
    logger.info("PREDICTING GAMES: %s", game_date)
    logger.info("=" * 60)

    # Load models
    predictor = GamePredictor(n_simulations=n_simulations)
    predictor.load_models(season=season)

    # Load bankroll and tracker
    bankroll = BankrollManager(min_edge=min_edge)
    bankroll.load_state()

    tracker = BetTracker()
    tracker.load()

    # Get predictions
    predictions = predictor.predict_games(game_date=game_date, season=season)

    if not predictions:
        logger.info("No games found for %s", game_date)
        print(f"\nNo games scheduled for {game_date}")
        return

    # Generate report
    report = daily_predictions_report(predictions, game_date)
    print(report)

    # Process signals
    # TODO: For each prediction with a signal:
    # 1. Calculate Kelly bet size
    # 2. Log the bet via tracker
    # 3. Save state

    if not dry_run:
        # TODO: Place paper bets
        # for pred in predictions:
        #     for signal in pred.signals:
        #         if signal.edge >= min_edge:
        #             decimal_odds = american_to_decimal(signal.odds_american)
        #             stake = bankroll.kelly_bet(signal.model_prob, decimal_odds)
        #             if stake > 0:
        #                 bet = BetRecord(
        #                     game_id=pred.game_id,
        #                     game_date=game_date.isoformat(),
        #                     home_team=pred.home_team,
        #                     away_team=pred.away_team,
        #                     bet_type=signal.bet_type,
        #                     side=signal.side,
        #                     line=signal.line,
        #                     odds_american=signal.odds_american,
        #                     odds_decimal=decimal_odds,
        #                     model_prob=signal.model_prob,
        #                     edge=signal.edge,
        #                     stake=stake,
        #                     bankroll_at_bet=bankroll.state.balance,
        #                 )
        #                 tracker.place_bet(bet)
        #                 bankroll.record_bet(stake, won=None, profit=-stake)

        tracker.save()
        bankroll.save_state()
        logger.info("Bets placed and state saved")
    else:
        logger.info("Dry run — no bets placed")

    # Print bankroll status
    print("\n" + bankroll.summary())
    print(f"Pending bets: {len(tracker.pending_bets())}")


def main():
    parser = argparse.ArgumentParser(description="Predict today's NBA games")
    parser.add_argument("--date", type=str, default=None,
                        help="Date to predict (YYYY-MM-DD, default: today)")
    parser.add_argument("--season", default=config.CURRENT_SEASON,
                        help=f"Season (default: {config.CURRENT_SEASON})")
    parser.add_argument("--dry-run", action="store_true",
                        help="Generate predictions without placing bets")
    parser.add_argument("--min-edge", type=float, default=0.03,
                        help="Minimum edge threshold (default: 0.03)")
    parser.add_argument("--simulations", type=int, default=10000,
                        help="Number of simulations per game (default: 10000)")

    args = parser.parse_args()

    game_date = None
    if args.date:
        game_date = date.fromisoformat(args.date)

    predict_today(
        game_date=game_date,
        season=args.season,
        dry_run=args.dry_run,
        min_edge=args.min_edge,
        n_simulations=args.simulations,
    )


if __name__ == "__main__":
    main()
