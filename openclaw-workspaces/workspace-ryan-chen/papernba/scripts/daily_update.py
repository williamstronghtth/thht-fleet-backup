#!/usr/bin/env python3
"""
scripts/daily_update.py — Daily data refresh and model update.

Run this each morning to:
1. Fetch yesterday's game results
2. Update player game logs for players who played
3. Refresh season stats
4. Retrain models with new data
5. Resolve any pending bets from yesterday

Usage:
    python scripts/daily_update.py
    python scripts/daily_update.py --date 2025-03-14   # specific date
"""

import argparse
import logging
import sys
import os
from datetime import date, timedelta

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import config
from ingestion import games, players, coaches, lineups

logging.basicConfig(level=config.LOG_LEVEL, format=config.LOG_FORMAT)
logger = logging.getLogger(__name__)


def daily_update(target_date: date = None, season: str = config.CURRENT_SEASON) -> None:
    """
    Run the daily data update pipeline.

    TODO:
    1. Re-fetch the game log (to get yesterday's results)
    2. Identify which games were played yesterday
    3. Fetch play-by-play for those games
    4. Fetch referee assignments for those games
    5. Update player season stats
    6. Refresh player game logs for players who played
    7. Update lineup data
    8. Retrain any models that need it
    9. Resolve pending bets

    Parameters
    ----------
    target_date : date
        Date to update for. Defaults to yesterday.
    season : str
        NBA season string.
    """
    if target_date is None:
        target_date = date.today() - timedelta(days=1)

    logger.info("=" * 60)
    logger.info("DAILY UPDATE: %s (season %s)", target_date, season)
    logger.info("=" * 60)

    # Step 1: Refresh game log
    logger.info("--- Refreshing game log ---")
    try:
        games.fetch_games(season, force=True)
        df_games = games.process_games(season)
        logger.info("Updated game log: %d rows", len(df_games))
    except Exception as e:
        logger.error("Failed to refresh games: %s", e)
        return

    # Step 2: Identify yesterday's games
    # TODO: Filter df_games to target_date
    # yesterday_games = df_games[df_games["game_date"].dt.date == target_date]
    # game_ids = yesterday_games["game_id"].unique().tolist()
    # logger.info("Found %d games on %s", len(game_ids), target_date)

    # Step 3: Fetch PBP for yesterday's games
    # TODO: playbyplay.fetch_season_pbp(season, game_ids=game_ids)

    # Step 4: Fetch referee data for yesterday's games
    # TODO: referees.fetch_season_officials(season, game_ids=game_ids)

    # Step 5: Refresh player stats
    logger.info("--- Refreshing player stats ---")
    try:
        players.fetch_season_stats(season, force=True)
        players.process_season_stats(season)
        logger.info("Player stats updated")
    except Exception as e:
        logger.error("Failed to refresh player stats: %s", e)

    # Step 6: Update lineup data
    logger.info("--- Refreshing lineups ---")
    try:
        lineups.fetch_lineups(season, force=True)
        lineups.process_lineups(season)
        logger.info("Lineup data updated")
    except Exception as e:
        logger.error("Failed to refresh lineups: %s", e)

    # Step 7: Resolve pending bets
    # TODO: Load tracker, match pending bets to actual results, resolve
    logger.info("--- Resolving pending bets ---")
    # from betting.tracker import BetTracker
    # tracker = BetTracker()
    # tracker.load()
    # ... resolve bets against actual scores ...
    # tracker.save()

    logger.info("=" * 60)
    logger.info("DAILY UPDATE COMPLETE")
    logger.info("=" * 60)


def main():
    parser = argparse.ArgumentParser(description="Daily NBA data update")
    parser.add_argument("--date", type=str, default=None,
                        help="Date to update for (YYYY-MM-DD, default: yesterday)")
    parser.add_argument("--season", default=config.CURRENT_SEASON,
                        help=f"Season (default: {config.CURRENT_SEASON})")

    args = parser.parse_args()

    target_date = None
    if args.date:
        target_date = date.fromisoformat(args.date)

    daily_update(target_date=target_date, season=args.season)


if __name__ == "__main__":
    main()
