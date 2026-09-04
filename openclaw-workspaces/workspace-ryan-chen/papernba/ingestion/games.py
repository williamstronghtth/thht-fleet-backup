"""
ingestion/games.py — Pull NBA game schedule and scores for a season.

Uses nba_api.stats.endpoints.LeagueGameLog to fetch all games,
caches raw JSON, and processes into a clean DataFrame.
"""

import json
import logging
import os
import time

import pandas as pd
from nba_api.stats.endpoints import LeagueGameLog
from nba_api.stats.static import teams as nba_teams

import config

logger = logging.getLogger(__name__)


def fetch_games(season: str = config.CURRENT_SEASON, force: bool = False) -> dict:
    """
    Fetch all games for a season from nba_api and cache the raw JSON.

    Parameters
    ----------
    season : str
        NBA season string, e.g. "2024-25".
    force : bool
        Re-fetch even if cache exists.

    Returns
    -------
    dict
        Raw JSON response from the API.
    """
    out_dir = config.raw_season_dir(season, "games")
    cache_path = os.path.join(out_dir, "league_game_log.json")

    if os.path.exists(cache_path) and not force:
        logger.info("Cache hit: %s", cache_path)
        with open(cache_path, "r") as f:
            return json.load(f)

    logger.info("Fetching games for season %s ...", season)
    try:
        result = LeagueGameLog(
            season=season,
            season_type_all_star="Regular Season",
            timeout=config.API_TIMEOUT,
        )
        data = result.get_normalized_dict()
        time.sleep(config.API_DELAY)

        with open(cache_path, "w") as f:
            json.dump(data, f)
        logger.info("Saved raw games → %s", cache_path)

        # Also fetch playoff games
        time.sleep(config.API_DELAY)
        try:
            playoffs = LeagueGameLog(
                season=season,
                season_type_all_star="Playoffs",
                timeout=config.API_TIMEOUT,
            )
            playoff_data = playoffs.get_normalized_dict()
            playoff_path = os.path.join(out_dir, "league_game_log_playoffs.json")
            with open(playoff_path, "w") as f:
                json.dump(playoff_data, f)
            logger.info("Saved playoff games → %s", playoff_path)
            time.sleep(config.API_DELAY)
        except Exception as e:
            logger.warning("Could not fetch playoff games (may not exist yet): %s", e)

        return data

    except Exception as e:
        logger.error("Failed to fetch games for %s: %s", season, e)
        raise


def process_games(season: str = config.CURRENT_SEASON) -> pd.DataFrame:
    """
    Process raw game log JSON into a clean DataFrame and save as parquet.

    Returns a DataFrame with one row per team-game (so each game appears twice,
    once for each team).
    """
    raw_dir = config.raw_season_dir(season, "games")
    cache_path = os.path.join(raw_dir, "league_game_log.json")

    if not os.path.exists(cache_path):
        logger.info("Raw data not found, fetching first...")
        fetch_games(season)

    with open(cache_path, "r") as f:
        data = json.load(f)

    rows = data.get("LeagueGameLog", [])
    if not rows:
        logger.warning("No game log rows found for %s", season)
        return pd.DataFrame()

    df = pd.DataFrame(rows)

    # Clean up column names (lowercase, strip whitespace)
    df.columns = [c.strip().lower() for c in df.columns]

    # Parse game date
    if "game_date" in df.columns:
        df["game_date"] = pd.to_datetime(df["game_date"])

    # Save processed
    out_dir = config.processed_season_dir(season, "games")
    out_path = os.path.join(out_dir, "season.parquet")
    df.to_parquet(out_path, index=False)
    logger.info("Saved processed games (%d rows) → %s", len(df), out_path)

    return df


def get_game_ids(season: str = config.CURRENT_SEASON) -> list[str]:
    """Return a list of all GAME_IDs for a season."""
    out_dir = config.processed_season_dir(season, "games")
    parquet_path = os.path.join(out_dir, "season.parquet")

    if os.path.exists(parquet_path):
        df = pd.read_parquet(parquet_path)
    else:
        df = process_games(season)

    if "game_id" in df.columns:
        return sorted(df["game_id"].unique().tolist())
    return []


def get_team_lookup() -> dict:
    """Return {team_id: team_info} for all NBA teams."""
    return {t["id"]: t for t in nba_teams.get_teams()}
