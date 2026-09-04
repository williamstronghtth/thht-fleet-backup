"""
ingestion/players.py — Pull player stats (game logs, season averages).

Stores data granularly so any time window can be computed:
- Individual game logs → processed/{season}/players/games/{player_id}.parquet
- Monthly splits    → processed/{season}/players/monthly/
- Season totals     → processed/{season}/players/season.parquet

Uses nba_api.stats.endpoints: PlayerGameLog, LeagueDashPlayerStats, CommonAllPlayers.
"""

import json
import logging
import os
import time

import pandas as pd
from nba_api.stats.endpoints import (
    LeagueDashPlayerStats,
    PlayerGameLog,
    CommonAllPlayers,
)

import config

logger = logging.getLogger(__name__)


def fetch_all_players(season: str = config.CURRENT_SEASON,
                      force: bool = False) -> dict:
    """Fetch the list of all players active in a season."""
    out_dir = config.raw_season_dir(season, "players")
    cache_path = os.path.join(out_dir, "all_players.json")

    if os.path.exists(cache_path) and not force:
        logger.info("Cache hit: %s", cache_path)
        with open(cache_path, "r") as f:
            return json.load(f)

    logger.info("Fetching all players for %s ...", season)
    try:
        result = CommonAllPlayers(
            is_only_current_season=1,
            league_id="00",
            season=season,
            timeout=config.API_TIMEOUT,
        )
        data = result.get_normalized_dict()
        time.sleep(config.API_DELAY)

        with open(cache_path, "w") as f:
            json.dump(data, f)
        logger.info("Saved player list → %s", cache_path)
        return data

    except Exception as e:
        logger.error("Failed to fetch player list: %s", e)
        raise


def fetch_season_stats(season: str = config.CURRENT_SEASON,
                       force: bool = False) -> dict:
    """Fetch league-wide per-game player stats for a season."""
    out_dir = config.raw_season_dir(season, "players")
    cache_path = os.path.join(out_dir, "season_stats.json")

    if os.path.exists(cache_path) and not force:
        logger.info("Cache hit: %s", cache_path)
        with open(cache_path, "r") as f:
            return json.load(f)

    logger.info("Fetching season stats for %s ...", season)
    try:
        result = LeagueDashPlayerStats(
            season=season,
            season_type_all_star="Regular Season",
            per_mode_detailed="PerGame",
            timeout=config.API_TIMEOUT,
        )
        data = result.get_normalized_dict()
        time.sleep(config.API_DELAY)

        with open(cache_path, "w") as f:
            json.dump(data, f)
        logger.info("Saved season stats → %s", cache_path)
        return data

    except Exception as e:
        logger.error("Failed to fetch season stats: %s", e)
        raise


def fetch_player_game_log(player_id: int, season: str = config.CURRENT_SEASON,
                          force: bool = False) -> dict:
    """Fetch individual game logs for a single player."""
    out_dir = config.raw_season_dir(season, "players")
    games_dir = os.path.join(out_dir, "game_logs")
    os.makedirs(games_dir, exist_ok=True)
    cache_path = os.path.join(games_dir, f"{player_id}.json")

    if os.path.exists(cache_path) and not force:
        logger.debug("Cache hit: %s", cache_path)
        with open(cache_path, "r") as f:
            return json.load(f)

    logger.debug("Fetching game log for player %s ...", player_id)
    retries = 0
    while retries < config.API_MAX_RETRIES:
        try:
            result = PlayerGameLog(
                player_id=player_id,
                season=season,
                season_type_all_star="Regular Season",
                timeout=config.API_TIMEOUT,
            )
            data = result.get_normalized_dict()
            time.sleep(config.API_DELAY)

            with open(cache_path, "w") as f:
                json.dump(data, f)
            return data

        except Exception as e:
            retries += 1
            logger.warning("Game log fetch failed for player %s (attempt %d/%d): %s",
                           player_id, retries, config.API_MAX_RETRIES, e)
            if retries < config.API_MAX_RETRIES:
                time.sleep(config.API_RETRY_DELAY)

    raise RuntimeError(f"Failed to fetch game log for player {player_id}")


def process_season_stats(season: str = config.CURRENT_SEASON) -> pd.DataFrame:
    """Process league-wide season stats into parquet."""
    raw_dir = config.raw_season_dir(season, "players")
    cache_path = os.path.join(raw_dir, "season_stats.json")

    if not os.path.exists(cache_path):
        fetch_season_stats(season)

    with open(cache_path, "r") as f:
        data = json.load(f)

    rows = data.get("LeagueDashPlayerStats", [])
    if not rows:
        logger.warning("No season stats for %s", season)
        return pd.DataFrame()

    df = pd.DataFrame(rows)
    df.columns = [c.strip().lower() for c in df.columns]

    out_dir = config.processed_season_dir(season, "players")
    out_path = os.path.join(out_dir, "season.parquet")
    df.to_parquet(out_path, index=False)
    logger.info("Saved processed player stats (%d rows) → %s", len(df), out_path)
    return df


def process_player_game_logs(season: str = config.CURRENT_SEASON) -> int:
    """Process all cached player game logs into individual parquet files."""
    raw_dir = config.raw_season_dir(season, "players")
    games_dir = os.path.join(raw_dir, "game_logs")
    if not os.path.exists(games_dir):
        logger.warning("No game log cache found for %s", season)
        return 0

    out_dir = config.processed_season_dir(season, "players")
    games_out = os.path.join(out_dir, "games")
    os.makedirs(games_out, exist_ok=True)

    count = 0
    for fname in os.listdir(games_dir):
        if not fname.endswith(".json"):
            continue
        player_id = fname.replace(".json", "")
        try:
            with open(os.path.join(games_dir, fname), "r") as f:
                data = json.load(f)

            rows = data.get("PlayerGameLog", [])
            if not rows:
                continue

            df = pd.DataFrame(rows)
            df.columns = [c.strip().lower() for c in df.columns]

            if "game_date" in df.columns:
                df["game_date"] = pd.to_datetime(df["game_date"])

            df.to_parquet(os.path.join(games_out, f"{player_id}.parquet"), index=False)
            count += 1
        except Exception as e:
            logger.error("Failed to process game log for player %s: %s", player_id, e)

    logger.info("Processed game logs for %d players in %s", count, season)
    return count


def get_active_player_ids(season: str = config.CURRENT_SEASON) -> list[int]:
    """Return list of active player IDs for a season."""
    raw_dir = config.raw_season_dir(season, "players")
    cache_path = os.path.join(raw_dir, "all_players.json")

    if not os.path.exists(cache_path):
        fetch_all_players(season)

    with open(cache_path, "r") as f:
        data = json.load(f)

    players = data.get("CommonAllPlayers", [])
    return [p["PERSON_ID"] for p in players if p.get("PERSON_ID")]
