"""
Ingest player game logs from NBA API using LeagueGameLog endpoint.
Pulls all player game logs for seasons 2015-16 through 2024-25 and stores in DuckDB.
"""

import json
import os
import sys
import time
from pathlib import Path

import duckdb
import pandas as pd
from nba_api.stats.endpoints import LeagueGameLog


# Config
SEASONS = [
    "2024-25", "2023-24", "2022-23", "2021-22", "2020-21",
    "2019-20", "2018-19", "2017-18", "2016-17", "2015-16",
]

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DB_PATH = PROJECT_ROOT / "data" / "nbadb" / "nba.duckdb"
RAW_DIR = PROJECT_ROOT / "data" / "raw" / "player_gamelogs"
TABLE_NAME = "player_game_log"

# Column mapping from API to our schema
COLUMN_MAP = {
    "PLAYER_ID": "player_id",
    "PLAYER_NAME": "player_name",
    "TEAM_ID": "team_id",
    "TEAM_ABBREVIATION": "team_abbreviation",
    "TEAM_NAME": "team_name",
    "GAME_ID": "game_id",
    "GAME_DATE": "game_date",
    "MATCHUP": "matchup",
    "WL": "wl",
    "MIN": "min",
    "FGM": "fgm",
    "FGA": "fga",
    "FG_PCT": "fg_pct",
    "FG3M": "fg3m",
    "FG3A": "fg3a",
    "FG3_PCT": "fg3_pct",
    "FTM": "ftm",
    "FTA": "fta",
    "FT_PCT": "ft_pct",
    "OREB": "oreb",
    "DREB": "dreb",
    "REB": "reb",
    "AST": "ast",
    "STL": "stl",
    "BLK": "blk",
    "TOV": "tov",
    "PF": "pf",
    "PTS": "pts",
    "PLUS_MINUS": "plus_minus",
}


def fetch_season(season: str, max_retries: int = 3) -> pd.DataFrame | None:
    """Fetch all player game logs for a single season with retry logic."""
    for attempt in range(1, max_retries + 1):
        try:
            print(f"  Fetching {season} (attempt {attempt}/{max_retries})...")
            log = LeagueGameLog(
                season=season,
                player_or_team_abbreviation="P",
                season_type_all_star="Regular Season",
                timeout=60,
            )
            df = log.get_data_frames()[0]
            print(f"  Got {len(df)} rows for {season}")
            return df
        except Exception as e:
            print(f"  Error on attempt {attempt}: {e}")
            if attempt < max_retries:
                wait = 30 * attempt
                print(f"  Waiting {wait}s before retry...")
                time.sleep(wait)
            else:
                print(f"  FAILED after {max_retries} attempts for {season}")
                return None


def save_raw(df: pd.DataFrame, season: str):
    """Save raw data as JSON."""
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    path = RAW_DIR / f"{season}.json"
    df.to_json(path, orient="records", date_format="iso")
    print(f"  Saved raw JSON to {path}")


def process_dataframe(df: pd.DataFrame, season: str) -> pd.DataFrame:
    """Rename columns and add season."""
    # Only keep columns we have mappings for
    cols_to_keep = [c for c in COLUMN_MAP if c in df.columns]
    df = df[cols_to_keep].copy()
    df = df.rename(columns={k: v for k, v in COLUMN_MAP.items() if k in df.columns})
    df["season"] = season
    return df


def ingest():
    """Main ingestion function."""
    print(f"Database: {DB_PATH}")
    print(f"Raw data dir: {RAW_DIR}")
    print()

    conn = duckdb.connect(str(DB_PATH))

    # Check if table exists and has data
    existing_seasons = set()
    try:
        result = conn.execute(f"SELECT DISTINCT season FROM {TABLE_NAME}").fetchall()
        existing_seasons = {r[0] for r in result}
        print(f"Existing seasons in DB: {sorted(existing_seasons)}")
    except Exception:
        print("Table does not exist yet — will create.")

    all_dfs = []
    for season in SEASONS:
        if season in existing_seasons:
            print(f"\n[SKIP] {season} — already in database")
            continue

        print(f"\n[PULL] {season}")
        df = fetch_season(season)

        if df is not None and len(df) > 0:
            save_raw(df, season)
            processed = process_dataframe(df, season)
            all_dfs.append(processed)
            print(f"  Processed: {len(processed)} rows")
        else:
            print(f"  No data for {season}")

        # Rate limit between API calls
        time.sleep(0.6)

    if not all_dfs:
        print("\nNo new data to load.")
        conn.close()
        return

    # Combine all seasons
    combined = pd.concat(all_dfs, ignore_index=True)
    print(f"\nTotal new rows to insert: {len(combined)}")

    # Create or append to table
    if existing_seasons:
        conn.execute(f"INSERT INTO {TABLE_NAME} SELECT * FROM combined")
        print(f"Appended to existing {TABLE_NAME} table.")
    else:
        conn.execute(f"CREATE TABLE {TABLE_NAME} AS SELECT * FROM combined")
        print(f"Created {TABLE_NAME} table.")

    conn.close()
    print("\nIngestion complete!")


def verify():
    """Run verification queries."""
    print("\n" + "=" * 60)
    print("VERIFICATION")
    print("=" * 60)

    conn = duckdb.connect(str(DB_PATH))

    # Total rows per season
    print("\n--- Rows per season ---")
    result = conn.execute(f"""
        SELECT season, COUNT(*) as rows
        FROM {TABLE_NAME}
        GROUP BY season
        ORDER BY season DESC
    """).fetchdf()
    print(result.to_string(index=False))

    total = conn.execute(f"SELECT COUNT(*) FROM {TABLE_NAME}").fetchone()[0]
    print(f"\nTotal rows: {total:,}")

    # Top 5 scorers 2024-25
    print("\n--- Top 5 scorers 2024-25 (total points) ---")
    result = conn.execute(f"""
        SELECT player_name, SUM(pts) as total_pts, COUNT(*) as games,
               ROUND(AVG(pts), 1) as ppg
        FROM {TABLE_NAME}
        WHERE season = '2024-25'
        GROUP BY player_name
        ORDER BY total_pts DESC
        LIMIT 5
    """).fetchdf()
    print(result.to_string(index=False))

    # Sample data
    print("\n--- Sample rows ---")
    result = conn.execute(f"""
        SELECT player_name, game_date, matchup, pts, reb, ast, season
        FROM {TABLE_NAME}
        ORDER BY game_date DESC
        LIMIT 5
    """).fetchdf()
    print(result.to_string(index=False))

    conn.close()


if __name__ == "__main__":
    ingest()
    verify()
