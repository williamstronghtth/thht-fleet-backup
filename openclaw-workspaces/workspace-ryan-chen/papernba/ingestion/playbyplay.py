"""
ingestion/playbyplay.py — Pull play-by-play data for individual NBA games.

Critical for:
- Coach rotation analysis (sub patterns, stint lengths)
- Referee foul tracking (who calls what, when)
- Per-possession player stats (usage, efficiency in context)

Uses nba_api.stats.endpoints.PlayByPlayV2.
"""

import json
import logging
import os
import time

import pandas as pd
from nba_api.stats.endpoints import PlayByPlayV2

import config

logger = logging.getLogger(__name__)


def fetch_game_pbp(game_id: str, season: str = config.CURRENT_SEASON,
                   force: bool = False) -> dict:
    """
    Fetch play-by-play data for a single game and cache the raw JSON.

    Parameters
    ----------
    game_id : str
        NBA game ID (e.g. "0022400001").
    season : str
        Season string for directory organization.
    force : bool
        Re-fetch even if cache exists.

    Returns
    -------
    dict
        Raw normalized JSON from the API.
    """
    out_dir = config.raw_season_dir(season, "playbyplay")
    cache_path = os.path.join(out_dir, f"{game_id}.json")

    if os.path.exists(cache_path) and not force:
        logger.debug("Cache hit: %s", cache_path)
        with open(cache_path, "r") as f:
            return json.load(f)

    logger.info("Fetching PBP for game %s ...", game_id)
    retries = 0
    while retries < config.API_MAX_RETRIES:
        try:
            result = PlayByPlayV2(
                game_id=game_id,
                timeout=config.API_TIMEOUT,
            )
            data = result.get_normalized_dict()
            time.sleep(config.API_DELAY)

            with open(cache_path, "w") as f:
                json.dump(data, f)
            logger.debug("Saved PBP → %s", cache_path)
            return data

        except Exception as e:
            retries += 1
            logger.warning("PBP fetch failed for %s (attempt %d/%d): %s",
                           game_id, retries, config.API_MAX_RETRIES, e)
            if retries < config.API_MAX_RETRIES:
                time.sleep(config.API_RETRY_DELAY)

    raise RuntimeError(f"Failed to fetch PBP for {game_id} after {config.API_MAX_RETRIES} retries")


def fetch_season_pbp(season: str = config.CURRENT_SEASON,
                     game_ids: list[str] | None = None,
                     force: bool = False) -> int:
    """
    Fetch play-by-play for all games in a season (or a subset).

    Parameters
    ----------
    season : str
        Season string.
    game_ids : list[str] | None
        Specific game IDs to fetch. If None, uses all games from games.py.
    force : bool
        Re-fetch even if cached.

    Returns
    -------
    int
        Number of games successfully fetched.
    """
    if game_ids is None:
        from ingestion.games import get_game_ids
        game_ids = get_game_ids(season)

    logger.info("Fetching PBP for %d games in %s ...", len(game_ids), season)
    success = 0
    for i, gid in enumerate(game_ids):
        try:
            fetch_game_pbp(gid, season=season, force=force)
            success += 1
            if (i + 1) % 50 == 0:
                logger.info("Progress: %d/%d games", i + 1, len(game_ids))
        except Exception as e:
            logger.error("Skipping game %s: %s", gid, e)

    logger.info("Fetched PBP for %d/%d games", success, len(game_ids))
    return success


def process_game_pbp(game_id: str, season: str = config.CURRENT_SEASON) -> pd.DataFrame:
    """
    Process a single game's play-by-play JSON into a clean DataFrame.

    Columns include: period, event_type, event_action_type, description,
    player1/2/3 info, score, time remaining, etc.
    """
    raw_dir = config.raw_season_dir(season, "playbyplay")
    cache_path = os.path.join(raw_dir, f"{game_id}.json")

    if not os.path.exists(cache_path):
        fetch_game_pbp(game_id, season=season)

    with open(cache_path, "r") as f:
        data = json.load(f)

    rows = data.get("PlayByPlay", [])
    if not rows:
        logger.warning("No PBP data for game %s", game_id)
        return pd.DataFrame()

    df = pd.DataFrame(rows)
    df.columns = [c.strip().lower() for c in df.columns]

    # Save individual game
    out_dir = config.processed_season_dir(season, "playbyplay")
    out_path = os.path.join(out_dir, f"{game_id}.parquet")
    df.to_parquet(out_path, index=False)

    return df


def process_season_pbp(season: str = config.CURRENT_SEASON,
                       game_ids: list[str] | None = None) -> int:
    """Process all cached PBP files for a season into parquet."""
    if game_ids is None:
        raw_dir = config.raw_season_dir(season, "playbyplay")
        game_ids = [
            f.replace(".json", "")
            for f in os.listdir(raw_dir)
            if f.endswith(".json")
        ]

    count = 0
    for gid in game_ids:
        try:
            process_game_pbp(gid, season=season)
            count += 1
        except Exception as e:
            logger.error("Failed to process PBP for %s: %s", gid, e)

    logger.info("Processed PBP for %d games in %s", count, season)
    return count
