#!/usr/bin/env python3
"""
Populate inactive_players for the 2025-26 season.

For each game in season_id='22025':
  1. Build a "roster" for each team: players who played in the 30 days prior
  2. Compare against who actually played in the game (min > 0)
  3. Insert the difference into inactive_players
"""

import duckdb
import pandas as pd
import sys
import time

DB_PATH = 'data/nbadb/nba.duckdb'
SEASON_ID = '22025'
SEASON_LABEL = '2025-26'


def main():
    con = duckdb.connect(DB_PATH)

    # Clear any existing 2025-26 inactive data
    existing = con.execute(
        "SELECT COUNT(*) FROM inactive_players WHERE game_id LIKE '002250%'"
    ).fetchone()[0]
    if existing > 0:
        print(f"Clearing {existing} existing 2025-26 inactive_players rows...")
        con.execute("DELETE FROM inactive_players WHERE game_id LIKE '002250%'")

    # Load all 2025-26 games
    games = con.execute("""
        SELECT game_id, game_date, team_id_home, team_id_away
        FROM game
        WHERE season_id = ?
          AND season_type = 'Regular Season'
          AND pts_home IS NOT NULL
        ORDER BY game_date, game_id
    """, [SEASON_ID]).fetchdf()
    games['game_date'] = pd.to_datetime(games['game_date'])
    print(f"Found {len(games)} games for {SEASON_LABEL}")

    # Load all player game logs for 2025-26 into memory
    logs = con.execute("""
        SELECT player_id, player_name, team_id, team_abbreviation, 
               game_id, game_date, min
        FROM player_game_log
        WHERE season = ?
    """, [SEASON_LABEL]).fetchdf()
    logs['game_date'] = pd.to_datetime(logs['game_date'])
    logs['player_id'] = logs['player_id'].astype(int)
    logs['team_id'] = logs['team_id'].astype(int)
    print(f"Loaded {len(logs)} player game log entries")

    # Load player info for names
    players = con.execute("SELECT id, first_name, last_name FROM player").fetchdf()
    players['id'] = players['id'].astype(int)
    player_info = dict(zip(players['id'], zip(players['first_name'], players['last_name'])))

    # Load team info
    teams = con.execute("SELECT id, city, nickname, abbreviation FROM team").fetchdf()
    teams['id'] = teams['id'].astype(int)
    team_info = dict(zip(teams['id'], zip(teams['city'], teams['nickname'], teams['abbreviation'])))

    # Build lookup: game_id -> set of player_ids who played (min > 0)
    played_in_game = {}
    for gid, grp in logs[logs['min'] > 0].groupby('game_id'):
        played_in_game[gid] = set(grp['player_id'].tolist())

    # Build lookup: (team_id, game_id) -> set of player_ids who played
    team_played_in_game = {}
    for (gid, tid), grp in logs[logs['min'] > 0].groupby(['game_id', 'team_id']):
        team_played_in_game[(gid, int(tid))] = set(grp['player_id'].tolist())

    # For each game, find the "roster" (players active in last 30 days) vs who played
    total_inactive = 0
    batch = []
    batch_size = 5000
    t0 = time.time()

    for i, (_, game) in enumerate(games.iterrows()):
        game_id = game['game_id']
        game_date = game['game_date']
        home_id = int(game['team_id_home'])
        away_id = int(game['team_id_away'])

        cutoff = game_date - pd.Timedelta(days=60)

        for team_id in [home_id, away_id]:
            # Roster: players who played for this team in last 30 days
            mask = (
                (logs['team_id'] == team_id) &
                (logs['min'] > 0) &
                (logs['game_date'] >= cutoff) &
                (logs['game_date'] < game_date)
            )
            roster = set(logs.loc[mask, 'player_id'].unique())

            # Who actually played in this game for this team
            actually_played = team_played_in_game.get((game_id, team_id), set())

            # Inactive = on roster but didn't play
            inactive = roster - actually_played

            # Get team details
            t_city, t_name, t_abbr = team_info.get(team_id, ('', '', ''))

            for pid in inactive:
                fname, lname = player_info.get(pid, ('', ''))
                batch.append((
                    game_id, str(pid), fname, lname, '',
                    str(team_id), t_city, t_name, t_abbr
                ))
                total_inactive += 1

        # Flush batch
        if len(batch) >= batch_size:
            con.executemany(
                "INSERT INTO inactive_players VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                batch
            )
            batch.clear()

        if (i + 1) % 100 == 0:
            elapsed = time.time() - t0
            print(f"  Processed {i+1}/{len(games)} games | {total_inactive} inactive entries | {elapsed:.1f}s")

    # Final flush
    if batch:
        con.executemany(
            "INSERT INTO inactive_players VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            batch
        )

    elapsed = time.time() - t0
    print(f"\nDone! Inserted {total_inactive} inactive_players rows for {SEASON_LABEL}")
    print(f"Time: {elapsed:.1f}s")

    # Verify
    count = con.execute(
        "SELECT COUNT(*) FROM inactive_players WHERE game_id LIKE '002250%'"
    ).fetchone()[0]
    print(f"Verification: {count} rows in inactive_players for 2025-26")

    con.close()


if __name__ == '__main__':
    main()
