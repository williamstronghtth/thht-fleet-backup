#!/usr/bin/env python3
"""
Test the impact of inactive player filtering on simulation accuracy.

Runs a subset of recent games with and without inactive filtering,
comparing prediction accuracy.
"""

import os
import sys
import time
import json
import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

DB_PATH = 'data/nbadb/nba.duckdb'
SEASON_ID = '22025'
N_SIMS = 500
N_GAMES = 50  # Test on last 50 games


def load_test_games():
    """Load recent games for testing."""
    import duckdb
    con = duckdb.connect(DB_PATH, read_only=True)
    df = con.execute("""
        SELECT
            g.game_id, g.game_date, g.season_id,
            g.team_id_home, g.team_id_away,
            g.pts_home, g.pts_away,
            g.team_abbreviation_home, g.team_abbreviation_away
        FROM game g
        WHERE g.season_id = ?
          AND g.season_type = 'Regular Season'
          AND g.pts_home IS NOT NULL
        ORDER BY g.game_date DESC
        LIMIT ?
    """, [SEASON_ID, N_GAMES]).fetchdf()
    con.close()
    df['game_date'] = pd.to_datetime(df['game_date'])
    return df.sort_values('game_date').reset_index(drop=True)


def run_predictions(games, use_inactive: bool):
    """Run predictions for all games with or without inactive filtering."""
    from models.simulation.player_model import PlayerPossessionModel
    from models.simulation.engine import GameConfig
    from models.simulation.monte_carlo import MonteCarloRunner
    from models.team.ratings import TeamRatings
    from models.coach.rotations import RotationAnalyzer
    from models.referee.profile import RefereeProfileModel

    import duckdb

    player_model = PlayerPossessionModel(DB_PATH)
    team_ratings = TeamRatings(DB_PATH)
    rotation_analyzer = RotationAnalyzer(DB_PATH)
    ref_model = RefereeProfileModel(DB_PATH)
    rotation_analyzer.preload([SEASON_ID])

    # Load officials
    con = duckdb.connect(DB_PATH, read_only=True)
    officials_df = con.execute("""
        SELECT o.game_id, o.official_id FROM officials o
        JOIN game g ON o.game_id = g.game_id
        WHERE g.season_id = ?
    """, [SEASON_ID]).fetchdf()
    officials_by_game = {}
    for _, row in officials_df.iterrows():
        gid = row['game_id']
        if gid not in officials_by_game:
            officials_by_game[gid] = []
        officials_by_game[gid].append(int(row['official_id']))

    # Load inactive players (only if use_inactive=True)
    inactive_by_game = {}
    if use_inactive:
        inactive_df = con.execute("""
            SELECT game_id, player_id FROM inactive_players
            WHERE game_id LIKE '002250%'
        """).fetchdf()
        for _, row in inactive_df.iterrows():
            gid = row['game_id']
            if gid not in inactive_by_game:
                inactive_by_game[gid] = []
            inactive_by_game[gid].append(int(row['player_id']))
    con.close()

    results = []
    total = len(games)

    for i, (_, game) in enumerate(games.iterrows()):
        game_id = game['game_id']
        game_date = pd.Timestamp(game['game_date'])
        home_id = str(game['team_id_home'])
        away_id = str(game['team_id_away'])

        try:
            inactive_set = set(inactive_by_game.get(game_id, []))
            home_profiles = player_model.get_team_profiles(int(home_id), game_date, top_n=13)
            away_profiles = player_model.get_team_profiles(int(away_id), game_date, top_n=13)

            if inactive_set:
                home_profiles = [p for p in home_profiles if p.player_id not in inactive_set]
                away_profiles = [p for p in away_profiles if p.player_id not in inactive_set]
                # Backfill
                if len(home_profiles) < 10:
                    deeper = player_model.get_team_profiles(int(home_id), game_date, top_n=20)
                    deeper = [p for p in deeper if p.player_id not in inactive_set
                              and p.player_id not in {pp.player_id for pp in home_profiles}]
                    home_profiles.extend(deeper[:10 - len(home_profiles)])
                if len(away_profiles) < 10:
                    deeper = player_model.get_team_profiles(int(away_id), game_date, top_n=20)
                    deeper = [p for p in deeper if p.player_id not in inactive_set
                              and p.player_id not in {pp.player_id for pp in away_profiles}]
                    away_profiles.extend(deeper[:10 - len(away_profiles)])

            if len(home_profiles) < 5 or len(away_profiles) < 5:
                continue

            home_rating = team_ratings.get_team_rating_before_date(home_id, game_date, SEASON_ID)
            away_rating = team_ratings.get_team_rating_before_date(away_id, game_date, SEASON_ID)
            league_avg = team_ratings.league_average_before_date(SEASON_ID, game_date)

            home_rotation = rotation_analyzer.get_rotation_profile(home_id, SEASON_ID, game_date)
            away_rotation = rotation_analyzer.get_rotation_profile(away_id, SEASON_ID, game_date)

            ref_foul_modifier = 1.0
            ref_home_bias = 0.0
            ref_crew = officials_by_game.get(game_id, [])
            if ref_crew:
                ref_adj = ref_model.get_crew_adjustment(ref_crew, game_date, SEASON_ID)
                if ref_adj['n_refs_found'] > 0:
                    ref_foul_modifier = 1.0 + (ref_adj['total_pf_adj'] / 42.0)
                    ref_foul_modifier = np.clip(ref_foul_modifier, 0.85, 1.15)
                    ref_home_bias = ref_adj['home_foul_adj'] / 200.0
                    ref_home_bias = np.clip(ref_home_bias, -0.02, 0.02)

            config = GameConfig(
                home_roster=home_profiles,
                away_roster=away_profiles,
                ref_foul_modifier=float(ref_foul_modifier),
                ref_home_bias=float(ref_home_bias),
                home_pace=home_rating['pace'] if home_rating else 98.0,
                away_pace=away_rating['pace'] if away_rating else 98.0,
                league_avg_pace=league_avg['pace'] if league_avg else 98.0,
                home_players_used=int(home_rotation.shrunk_players_used) if home_rotation else 9,
                away_players_used=int(away_rotation.shrunk_players_used) if away_rotation else 9,
            )

            runner = MonteCarloRunner(config, seed=i)
            result = runner.run(n_sims=N_SIMS)

            actual_spread = game['pts_home'] - game['pts_away']
            actual_total = game['pts_home'] + game['pts_away']

            results.append({
                'game_id': game_id,
                'game_date': str(game_date),
                'home_abbr': game.get('team_abbreviation_home', ''),
                'away_abbr': game.get('team_abbreviation_away', ''),
                'predicted_spread': result.mean_spread,
                'predicted_total': result.mean_total,
                'home_win_pct': result.home_win_pct,
                'actual_spread': actual_spread,
                'actual_total': actual_total,
                'n_inactive': len(inactive_set),
                'mean_home_score': result.mean_home_score,
                'mean_away_score': result.mean_away_score,
            })

        except Exception as e:
            print(f"  Error on {game_id}: {e}")
            continue

        if (i + 1) % 10 == 0:
            print(f"  [{i+1}/{total}] processed")

    return pd.DataFrame(results)


def compute_metrics(df, label):
    """Compute accuracy metrics."""
    spread_err = df['predicted_spread'] - df['actual_spread']
    total_err = df['predicted_total'] - df['actual_total']
    pred_hw = df['predicted_spread'] > 0
    actual_hw = df['actual_spread'] > 0
    win_acc = (pred_hw == actual_hw).mean()

    return {
        'label': label,
        'n_games': len(df),
        'spread_mae': round(np.abs(spread_err).mean(), 3),
        'spread_rmse': round(np.sqrt((spread_err ** 2).mean()), 3),
        'spread_bias': round(spread_err.mean(), 3),
        'total_mae': round(np.abs(total_err).mean(), 3),
        'total_rmse': round(np.sqrt((total_err ** 2).mean()), 3),
        'total_bias': round(total_err.mean(), 3),
        'win_accuracy': round(win_acc, 4),
    }


def main():
    print("=" * 60)
    print("  INACTIVE PLAYER FILTERING - A/B TEST")
    print("=" * 60)
    print(f"  Season: {SEASON_ID} | Sims: {N_SIMS} | Games: {N_GAMES}")
    print()

    # Load games
    print("Loading test games...")
    games = load_test_games()
    print(f"  Loaded {len(games)} games ({games['game_date'].min()} to {games['game_date'].max()})")

    # Run WITHOUT inactive filtering
    print(f"\n--- RUN 1: WITHOUT inactive filtering ---")
    t0 = time.time()
    df_no_filter = run_predictions(games, use_inactive=False)
    t1 = time.time()
    print(f"  Completed in {t1-t0:.1f}s ({len(df_no_filter)} games)")

    # Run WITH inactive filtering
    print(f"\n--- RUN 2: WITH inactive filtering ---")
    t0 = time.time()
    df_with_filter = run_predictions(games, use_inactive=True)
    t2 = time.time()
    print(f"  Completed in {t2-t0:.1f}s ({len(df_with_filter)} games)")

    # Compute metrics
    m_without = compute_metrics(df_no_filter, "Without Inactive Filter")
    m_with = compute_metrics(df_with_filter, "With Inactive Filter")

    # Print comparison
    print(f"\n{'=' * 60}")
    print("  RESULTS COMPARISON")
    print(f"{'=' * 60}")
    print(f"  {'Metric':<20} {'No Filter':>12} {'With Filter':>12} {'Delta':>10} {'Better?':>8}")
    print(f"  {'-' * 62}")

    comparisons = [
        ('Spread MAE', m_without['spread_mae'], m_with['spread_mae'], 'lower'),
        ('Spread RMSE', m_without['spread_rmse'], m_with['spread_rmse'], 'lower'),
        ('Spread Bias', m_without['spread_bias'], m_with['spread_bias'], 'abs_lower'),
        ('Total MAE', m_without['total_mae'], m_with['total_mae'], 'lower'),
        ('Total RMSE', m_without['total_rmse'], m_with['total_rmse'], 'lower'),
        ('Total Bias', m_without['total_bias'], m_with['total_bias'], 'abs_lower'),
        ('Win Accuracy', m_without['win_accuracy'], m_with['win_accuracy'], 'higher'),
    ]

    output_lines = []
    for name, old, new, direction in comparisons:
        delta = new - old
        if direction == 'lower':
            better = '✅' if delta < 0 else ('➖' if delta == 0 else '❌')
        elif direction == 'higher':
            better = '✅' if delta > 0 else ('➖' if delta == 0 else '❌')
        else:  # abs_lower
            better = '✅' if abs(new) < abs(old) else ('➖' if abs(new) == abs(old) else '❌')

        if 'Accuracy' in name:
            line = f"  {name:<20} {old:>12.1%} {new:>12.1%} {delta:>+10.4f} {better}"
        else:
            line = f"  {name:<20} {old:>12.3f} {new:>12.3f} {delta:>+10.3f} {better}"
        print(line)
        output_lines.append(line)

    # Avg inactive per game
    avg_inactive = df_with_filter['n_inactive'].mean()
    print(f"\n  Avg inactive players per game: {avg_inactive:.1f}")

    # Save results
    os.makedirs('data/reports', exist_ok=True)
    results = {
        'without_filter': m_without,
        'with_filter': m_with,
        'avg_inactive_per_game': round(avg_inactive, 1),
        'n_games': len(df_with_filter),
        'test_date_range': f"{games['game_date'].min()} to {games['game_date'].max()}",
    }
    with open('data/reports/inactive_filter_ab_test.json', 'w') as f:
        json.dump(results, f, indent=2)

    print(f"\n  Results saved to data/reports/inactive_filter_ab_test.json")

    return results


if __name__ == '__main__':
    results = main()
