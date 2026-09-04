"""
ingestion/lineups.py — Pull lineup stint data (5-man units).

Fetches lineup stats including minutes, plus/minus, offensive/defensive
ratings for all 5-man combinations used during a season.

Uses nba_api.stats.endpoints.LeagueDashLineups.
"""

import json
import logging
import os
import time

import pandas as pd
from nba_api.stats.endpoints import LeagueDashLineups

import config

logger = logging.getLogger(__name__)


def fetch_lineups(season: str = config.CURRENT_SEASON,
                  force: bool = False) -> dict:
    """
    Fetch all 5-man lineup data for a season and cache the raw JSON.

    Parameters
    ----------
    season : str
        NBA season string.
    force : bool
        Re-fetch even if cached.

    Returns
    -------
    dict
        Raw normalized JSON.
    """
    out_dir = config.raw_season_dir(season, "lineups")
    cache_path = os.path.join(out_dir, "five_man_lineups.json")

    if os.path.exists(cache_path) and not force:
        logger.info("Cache hit: %s", cache_path)
        with open(cache_path, "r") as f:
            return json.load(f)

    logger.info("Fetching 5-man lineups for %s ...", season)
    try:
        result = LeagueDashLineups(
            season=season,
            season_type_all_star="Regular Season",
            group_quantity=5,
            timeout=config.API_TIMEOUT,
        )
        data = result.get_normalized_dict()
        time.sleep(config.API_DELAY)

        with open(cache_path, "w") as f:
            json.dump(data, f)
        logger.info("Saved lineups → %s", cache_path)
        return data

    except Exception as e:
        logger.error("Failed to fetch lineups for %s: %s", season, e)
        raise


def process_lineups(season: str = config.CURRENT_SEASON) -> pd.DataFrame:
    """
    Process raw lineup JSON into a clean DataFrame and save as parquet.

    Each row represents a 5-man unit with stats like MIN, PLUS_MINUS,
    OFF_RATING, DEF_RATING, etc.
    """
    raw_dir = config.raw_season_dir(season, "lineups")
    cache_path = os.path.join(raw_dir, "five_man_lineups.json")

    if not os.path.exists(cache_path):
        fetch_lineups(season)

    with open(cache_path, "r") as f:
        data = json.load(f)

    rows = data.get("Lineups", [])
    if not rows:
        logger.warning("No lineup data for %s", season)
        return pd.DataFrame()

    df = pd.DataFrame(rows)
    df.columns = [c.strip().lower() for c in df.columns]

    # Save processed
    out_dir = config.processed_season_dir(season, "lineups")
    out_path = os.path.join(out_dir, "season.parquet")
    df.to_parquet(out_path, index=False)
    logger.info("Saved processed lineups (%d rows) → %s", len(df), out_path)

    return df
