"""
ingestion/referees.py — Pull referee assignments per game.

Extracts referee info from game box scores (BoxScoreSummaryV2).
Each game has 3 officials — we track their assignments across the season
for foul-rate modeling and bias analysis.

Uses nba_api.stats.endpoints.BoxScoreSummaryV2.
"""

import json
import logging
import os
import time

import pandas as pd
from nba_api.stats.endpoints import BoxScoreSummaryV2

import config

logger = logging.getLogger(__name__)


def fetch_game_officials(game_id: str, season: str = config.CURRENT_SEASON,
                         force: bool = False) -> dict:
    """
    Fetch box score summary for a game (includes Officials result set).

    Parameters
    ----------
    game_id : str
        NBA game ID.
    season : str
        Season string for directory organization.
    force : bool
        Re-fetch even if cached.

    Returns
    -------
    dict
        Raw normalized JSON.
    """
    out_dir = config.raw_season_dir(season, "referees")
    cache_path = os.path.join(out_dir, f"{game_id}.json")

    if os.path.exists(cache_path) and not force:
        logger.debug("Cache hit: %s", cache_path)
        with open(cache_path, "r") as f:
            return json.load(f)

    logger.debug("Fetching officials for game %s ...", game_id)
    retries = 0
    while retries < config.API_MAX_RETRIES:
        try:
            result = BoxScoreSummaryV2(
                game_id=game_id,
                timeout=config.API_TIMEOUT,
            )
            data = result.get_normalized_dict()
            time.sleep(config.API_DELAY)

            with open(cache_path, "w") as f:
                json.dump(data, f)
            return data

        except Exception as e:
            retries += 1
            logger.warning("Officials fetch failed for %s (attempt %d/%d): %s",
                           game_id, retries, config.API_MAX_RETRIES, e)
            if retries < config.API_MAX_RETRIES:
                time.sleep(config.API_RETRY_DELAY)

    raise RuntimeError(f"Failed to fetch officials for {game_id}")


def fetch_season_officials(season: str = config.CURRENT_SEASON,
                           game_ids: list[str] | None = None,
                           force: bool = False) -> int:
    """
    Fetch official assignments for all games in a season.

    Parameters
    ----------
    season : str
        Season string.
    game_ids : list[str] | None
        If None, pulls from games.py.
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

    logger.info("Fetching officials for %d games in %s ...", len(game_ids), season)
    success = 0
    for i, gid in enumerate(game_ids):
        try:
            fetch_game_officials(gid, season=season, force=force)
            success += 1
            if (i + 1) % 50 == 0:
                logger.info("Progress: %d/%d games", i + 1, len(game_ids))
        except Exception as e:
            logger.error("Skipping game %s: %s", gid, e)

    logger.info("Fetched officials for %d/%d games", success, len(game_ids))
    return success


def process_officials(season: str = config.CURRENT_SEASON) -> pd.DataFrame:
    """
    Process all cached official data into a single DataFrame.

    Output columns: game_id, official_id, first_name, last_name, jersey_num.
    Saved as processed/{season}/referees/season.parquet.
    """
    raw_dir = config.raw_season_dir(season, "referees")
    if not os.path.exists(raw_dir):
        logger.warning("No referee cache for %s", season)
        return pd.DataFrame()

    all_rows = []
    for fname in os.listdir(raw_dir):
        if not fname.endswith(".json"):
            continue
        game_id = fname.replace(".json", "")
        try:
            with open(os.path.join(raw_dir, fname), "r") as f:
                data = json.load(f)

            officials = data.get("Officials", [])
            for off in officials:
                off["GAME_ID"] = game_id
                all_rows.append(off)
        except Exception as e:
            logger.error("Failed to process officials for %s: %s", game_id, e)

    if not all_rows:
        logger.warning("No official records found for %s", season)
        return pd.DataFrame()

    df = pd.DataFrame(all_rows)
    df.columns = [c.strip().lower() for c in df.columns]

    out_dir = config.processed_season_dir(season, "referees")
    out_path = os.path.join(out_dir, "season.parquet")
    df.to_parquet(out_path, index=False)
    logger.info("Saved processed officials (%d rows, %d unique refs) → %s",
                len(df), df["official_id"].nunique() if "official_id" in df.columns else 0,
                out_path)

    return df


def get_referee_game_counts(season: str = config.CURRENT_SEASON) -> pd.DataFrame:
    """Return a DataFrame of referee → number of games officiated."""
    out_dir = config.processed_season_dir(season, "referees")
    parquet_path = os.path.join(out_dir, "season.parquet")

    if os.path.exists(parquet_path):
        df = pd.read_parquet(parquet_path)
    else:
        df = process_officials(season)

    if df.empty:
        return df

    name_cols = [c for c in ["first_name", "last_name"] if c in df.columns]
    group_cols = ["official_id"] + name_cols
    return df.groupby(group_cols).size().reset_index(name="game_count").sort_values(
        "game_count", ascending=False
    )
