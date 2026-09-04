#!/usr/bin/env python3
"""
scripts/ingest_season.py — Ingest all data for an NBA season.

This is the initial data pull. Run once per season to build the full dataset.
Subsequent updates use daily_update.py.

Usage:
    python scripts/ingest_season.py                    # current season
    python scripts/ingest_season.py --season 2023-24   # specific season
    python scripts/ingest_season.py --force             # re-fetch everything
    python scripts/ingest_season.py --skip-pbp          # skip play-by-play (slow)

Warning: Full PBP ingestion for a season (~1300 games) takes several hours
due to API rate limiting. Use --skip-pbp for initial setup, then backfill.
"""

import argparse
import logging
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import config
from ingestion import games, players, coaches, lineups, playbyplay, referees

logging.basicConfig(level=config.LOG_LEVEL, format=config.LOG_FORMAT)
logger = logging.getLogger(__name__)


def ingest_season(season: str, force: bool = False, skip_pbp: bool = False,
                  skip_refs: bool = False) -> None:
    """
    Run the full ingestion pipeline for a season.

    Steps:
    1. Games — league game log (fast, ~2 API calls)
    2. Players — all players + season stats (fast, ~2 API calls)
    3. Coaches — coach roster for all 30 teams (~30 API calls)
    4. Lineups — 5-man lineup stats (fast, ~1 API call)
    5. Play-by-play — per-game PBP data (slow, ~1300 API calls)
    6. Referees — officials per game via box scores (slow, ~1300 API calls)
    """
    logger.info("=" * 60)
    logger.info("INGESTING SEASON: %s", season)
    logger.info("=" * 60)

    # 1. Games
    logger.info("--- Step 1/6: Games ---")
    try:
        games.fetch_games(season, force=force)
        df_games = games.process_games(season)
        game_ids = games.get_game_ids(season)
        logger.info("Games: %d team-game rows, %d unique games",
                     len(df_games), len(game_ids))
    except Exception as e:
        logger.error("Failed to ingest games: %s", e)
        return

    # 2. Players
    logger.info("--- Step 2/6: Players ---")
    try:
        players.fetch_all_players(season, force=force)
        players.fetch_season_stats(season, force=force)
        df_players = players.process_season_stats(season)
        logger.info("Players: %d player season stat rows", len(df_players))
    except Exception as e:
        logger.error("Failed to ingest players: %s", e)

    # 3. Coaches
    logger.info("--- Step 3/6: Coaches ---")
    try:
        coaches.fetch_coaches(season, force=force)
        df_coaches = coaches.process_coaches(season)
        logger.info("Coaches: %d head coaches", len(df_coaches))
    except Exception as e:
        logger.error("Failed to ingest coaches: %s", e)

    # 4. Lineups
    logger.info("--- Step 4/6: Lineups ---")
    try:
        lineups.fetch_lineups(season, force=force)
        df_lineups = lineups.process_lineups(season)
        logger.info("Lineups: %d 5-man units", len(df_lineups))
    except Exception as e:
        logger.error("Failed to ingest lineups: %s", e)

    # 5. Play-by-play
    if skip_pbp:
        logger.info("--- Step 5/6: Play-by-Play (SKIPPED) ---")
    else:
        logger.info("--- Step 5/6: Play-by-Play (%d games) ---", len(game_ids))
        logger.info("This will take a while (~%.1f hours at %.1fs/request)...",
                     len(game_ids) * config.API_DELAY / 3600, config.API_DELAY)
        try:
            count = playbyplay.fetch_season_pbp(season, game_ids=game_ids, force=force)
            processed = playbyplay.process_season_pbp(season)
            logger.info("Play-by-play: fetched %d, processed %d games", count, processed)
        except Exception as e:
            logger.error("Failed to ingest play-by-play: %s", e)

    # 6. Referees
    if skip_refs:
        logger.info("--- Step 6/6: Referees (SKIPPED) ---")
    else:
        logger.info("--- Step 6/6: Referees (%d games) ---", len(game_ids))
        try:
            count = referees.fetch_season_officials(season, game_ids=game_ids, force=force)
            df_refs = referees.process_officials(season)
            logger.info("Referees: fetched %d games, %d official records",
                         count, len(df_refs))
        except Exception as e:
            logger.error("Failed to ingest referees: %s", e)

    logger.info("=" * 60)
    logger.info("INGESTION COMPLETE: %s", season)
    logger.info("=" * 60)


def main():
    parser = argparse.ArgumentParser(description="Ingest NBA season data")
    parser.add_argument("--season", default=config.CURRENT_SEASON,
                        help=f"Season to ingest (default: {config.CURRENT_SEASON})")
    parser.add_argument("--force", action="store_true",
                        help="Re-fetch all data even if cached")
    parser.add_argument("--skip-pbp", action="store_true",
                        help="Skip play-by-play ingestion (very slow)")
    parser.add_argument("--skip-refs", action="store_true",
                        help="Skip referee data ingestion (slow)")
    parser.add_argument("--all-seasons", action="store_true",
                        help="Ingest all supported seasons")

    args = parser.parse_args()

    if args.all_seasons:
        for season in config.SUPPORTED_SEASONS:
            ingest_season(season, force=args.force, skip_pbp=args.skip_pbp,
                          skip_refs=args.skip_refs)
    else:
        ingest_season(args.season, force=args.force, skip_pbp=args.skip_pbp,
                      skip_refs=args.skip_refs)


if __name__ == "__main__":
    main()
