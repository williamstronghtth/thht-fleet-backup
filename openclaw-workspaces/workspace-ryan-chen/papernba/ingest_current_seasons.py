#!/usr/bin/env python3
"""
Ingest 2024-25 and 2025-26 season data into DuckDB.

Pulls: games, player game logs, officials, inactive players, play-by-play
For both completed (2024-25) and current (2025-26) seasons.
"""

import os
import sys
import time
import json
import logging
import duckdb
import pandas as pd
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import config

from nba_api.stats.endpoints import (
    LeagueGameLog,
    BoxScoreTraditionalV2,
    BoxScoreSummaryV2,
    PlayByPlayV2,
)

logging.basicConfig(level=logging.INFO, format=config.LOG_FORMAT)
logger = logging.getLogger(__name__)

DB_PATH = 'data/nbadb/nba.duckdb'
SEASONS_TO_PULL = ['2023-24', '2024-25', '2025-26']
SEASON_IDS = {'2023-24': '22023', '2024-25': '22024', '2025-26': '22025'}
DELAY = 0.7  # seconds between API calls


def fetch_season_games(season: str) -> pd.DataFrame:
    """Fetch all games for a season via LeagueGameLog."""
    logger.info(f"Fetching games for {season}...")
    
    # LeagueGameLog returns one row per team-game
    result = LeagueGameLog(
        season=season,
        season_type_all_star="Regular Season",
        timeout=30,
    )
    df = result.get_data_frames()[0]
    time.sleep(DELAY)
    
    logger.info(f"  Got {len(df)} team-game rows for {season}")
    return df


def build_game_table(team_game_df: pd.DataFrame, season_id: str) -> pd.DataFrame:
    """Convert team-game rows into one-row-per-game format matching our game table."""
    df = team_game_df.copy()
    df.columns = [c.lower() for c in df.columns]
    
    # Determine home/away from matchup string
    df['is_home'] = df['matchup'].str.contains('vs.')
    
    home = df[df['is_home']].copy()
    away = df[~df['is_home']].copy()
    
    # Rename columns for merge
    home_cols = {
        'team_id': 'team_id_home',
        'team_abbreviation': 'team_abbreviation_home', 
        'team_name': 'team_name_home',
        'matchup': 'matchup_home',
        'wl': 'wl_home',
        'pts': 'pts_home',
        'fgm': 'fgm_home', 'fga': 'fga_home', 'fg_pct': 'fg_pct_home',
        'fg3m': 'fg3m_home', 'fg3a': 'fg3a_home', 'fg3_pct': 'fg3_pct_home',
        'ftm': 'ftm_home', 'fta': 'fta_home', 'ft_pct': 'ft_pct_home',
        'oreb': 'oreb_home', 'dreb': 'dreb_home', 'reb': 'reb_home',
        'ast': 'ast_home', 'stl': 'stl_home', 'blk': 'blk_home',
        'tov': 'tov_home', 'pf': 'pf_home',
        'plus_minus': 'plus_minus_home',
    }
    away_cols = {k: v.replace('_home', '_away') for k, v in home_cols.items()}
    
    home = home.rename(columns=home_cols)
    away = away.rename(columns=away_cols)
    
    # Merge on game_id
    games = home.merge(away, on=['game_id', 'game_date', 'season_id'], 
                       suffixes=('', '_drop'))
    
    # Drop duplicates
    games = games[[c for c in games.columns if not c.endswith('_drop') 
                    and c not in ['is_home_x', 'is_home_y', 'is_home',
                                  'video_available_x', 'video_available_y',
                                  'min_x', 'min_y']]]
    
    games['season_id'] = season_id
    games['season_type'] = 'Regular Season'
    games['game_date'] = pd.to_datetime(games['game_date'])
    
    # Add min column if missing
    if 'min' not in games.columns:
        games['min'] = 240
    
    logger.info(f"  Built {len(games)} game rows")
    return games


def fetch_game_details(game_ids: list, season: str) -> tuple:
    """Fetch officials and inactive players for a list of games."""
    officials_rows = []
    inactive_rows = []
    
    total = len(game_ids)
    for i, gid in enumerate(game_ids):
        if (i + 1) % 50 == 0:
            logger.info(f"  Game details: {i+1}/{total}")
        
        try:
            summary = BoxScoreSummaryV2(game_id=gid, timeout=30)
            dfs = summary.get_data_frames()
            time.sleep(DELAY)
            
            # Officials (usually index 2)
            for df_idx, df in enumerate(dfs):
                cols = [c.lower() for c in df.columns]
                if 'official_id' in cols:
                    for _, row in df.iterrows():
                        officials_rows.append({
                            'game_id': gid,
                            'official_id': row.get('OFFICIAL_ID', row.get('official_id')),
                            'first_name': row.get('FIRST_NAME', row.get('first_name', '')),
                            'last_name': row.get('LAST_NAME', row.get('last_name', '')),
                        })
                
                # Inactive players
                if 'player_id' in cols and 'team_id' in cols and len(df.columns) < 10:
                    for _, row in df.iterrows():
                        pid = row.get('PLAYER_ID', row.get('player_id'))
                        tid = row.get('TEAM_ID', row.get('team_id'))
                        if pid and tid:
                            inactive_rows.append({
                                'game_id': gid,
                                'player_id': int(pid),
                                'team_id': int(tid),
                            })
        except Exception as e:
            logger.warning(f"  Failed game {gid}: {e}")
            time.sleep(1)
    
    officials_df = pd.DataFrame(officials_rows) if officials_rows else pd.DataFrame()
    inactive_df = pd.DataFrame(inactive_rows) if inactive_rows else pd.DataFrame()
    
    logger.info(f"  Officials: {len(officials_df)} rows, Inactive: {len(inactive_df)} rows")
    return officials_df, inactive_df


def fetch_player_gamelogs(season: str) -> pd.DataFrame:
    """Fetch player game logs for a season."""
    logger.info(f"Fetching player game logs for {season}...")
    
    from nba_api.stats.endpoints import PlayerGameLogs
    result = PlayerGameLogs(season_nullable=season, season_type_nullable="Regular Season", timeout=30)
    df = result.get_data_frames()[0]
    time.sleep(DELAY)
    
    logger.info(f"  Got {len(df)} player game log rows")
    return df


def load_to_duckdb(games_df, officials_df, inactive_df, player_logs_df, season_id):
    """Insert new data into DuckDB."""
    con = duckdb.connect(DB_PATH)
    
    # Insert games
    if len(games_df) > 0:
        # Delete existing games for this season first
        con.execute(f"DELETE FROM game WHERE season_id = '{season_id}'")
        con.execute("INSERT INTO game SELECT * FROM games_df")
        logger.info(f"  Inserted {len(games_df)} games for season {season_id}")
    
    # Insert officials
    if len(officials_df) > 0:
        game_ids = tuple(games_df['game_id'].unique().tolist())
        if len(game_ids) == 1:
            con.execute(f"DELETE FROM officials WHERE game_id = '{game_ids[0]}'")
        else:
            con.execute(f"DELETE FROM officials WHERE game_id IN {game_ids}")
        con.execute("INSERT INTO officials SELECT * FROM officials_df")
        logger.info(f"  Inserted {len(officials_df)} official assignments")
    
    # Insert inactive players
    if len(inactive_df) > 0:
        game_ids = tuple(games_df['game_id'].unique().tolist())
        if len(game_ids) == 1:
            con.execute(f"DELETE FROM inactive_players WHERE game_id = '{game_ids[0]}'")
        else:
            con.execute(f"DELETE FROM inactive_players WHERE game_id IN {game_ids}")
        con.execute("INSERT INTO inactive_players SELECT * FROM inactive_df")
        logger.info(f"  Inserted {len(inactive_df)} inactive player records")
    
    # Insert player game logs
    if len(player_logs_df) > 0:
        season_str = f"20{season_id[1:3]}-{int(season_id[1:3])+1:02d}" if len(season_id) == 5 else season_id
        con.execute(f"DELETE FROM player_game_log WHERE season = '{season_str}'")
        con.execute("INSERT INTO player_game_log SELECT * FROM player_logs_df")
        logger.info(f"  Inserted {len(player_logs_df)} player game log rows")
    
    con.close()


def main():
    for season in SEASONS_TO_PULL:
        season_id = SEASON_IDS[season]
        logger.info(f"\n{'='*60}")
        logger.info(f"  Processing {season} (season_id: {season_id})")
        logger.info(f"{'='*60}")
        
        # Check if we already have this season
        con = duckdb.connect(DB_PATH, read_only=True)
        existing = con.execute(f"SELECT COUNT(*) FROM game WHERE season_id = '{season_id}'").fetchone()[0]
        con.close()
        
        if existing > 0 and season != '2025-26':
            logger.info(f"  Already have {existing} games for {season}, skipping")
            continue
        
        # 1. Fetch games
        try:
            team_games = fetch_season_games(season)
            games = build_game_table(team_games, season_id)
        except Exception as e:
            logger.error(f"  Failed to fetch games for {season}: {e}")
            continue
        
        if len(games) == 0:
            logger.warning(f"  No games found for {season}")
            continue
        
        # 2. Fetch game details (officials + inactive)
        game_ids = games['game_id'].unique().tolist()
        logger.info(f"  Fetching details for {len(game_ids)} games (this will take a while)...")
        officials, inactive = fetch_game_details(game_ids, season)
        
        # 3. Load to DB
        # For now just insert games — player logs already exist for 2024-25
        try:
            load_to_duckdb(games, officials, inactive, pd.DataFrame(), season_id)
        except Exception as e:
            logger.error(f"  DB insert failed: {e}")
            # Try simpler approach — just save as parquet
            games.to_parquet(f'data/processed/{season}/games.parquet', index=False)
            logger.info(f"  Saved games to parquet as fallback")
        
        logger.info(f"  Done with {season}!")
    
    logger.info("\nAll seasons processed!")


if __name__ == '__main__':
    main()
