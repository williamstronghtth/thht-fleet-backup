#!/usr/bin/env python3
"""
Simulation Validation Script
==============================

Picks specific games from the 2022-23 season, runs the simulator,
and validates that scores are in realistic ranges.
"""

import sys
import os
import time

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import duckdb
import pandas as pd
import numpy as np

from models.simulation.predictor import SimulationPredictor
from models.simulation.monte_carlo import MonteCarloRunner


DB_PATH = 'data/nbadb/nba.duckdb'
N_SIMS = 10000
REPORT_PATH = 'data/reports/simulation_validation.txt'


def get_test_games(db_path: str, n_games: int = 10) -> pd.DataFrame:
    """Get a diverse set of test games from the 2022-23 season."""
    con = duckdb.connect(db_path, read_only=True)

    # Pick games spread across the season with varied matchups
    df = con.execute("""
        SELECT
            g.game_id, g.game_date, g.season_id,
            g.team_id_home, g.team_abbreviation_home,
            g.team_id_away, g.team_abbreviation_away,
            g.pts_home, g.pts_away,
            g.pts_home - g.pts_away as actual_spread,
            g.pts_home + g.pts_away as actual_total
        FROM game g
        WHERE g.season_id = '22022'
          AND g.season_type = 'Regular Season'
          AND g.pts_home IS NOT NULL
          AND g.game_date >= '2023-01-01'
          AND g.game_date <= '2023-03-31'
        ORDER BY RANDOM()
        LIMIT ?
    """, [n_games]).fetchdf()
    con.close()

    df['game_date'] = pd.to_datetime(df['game_date'])
    return df


def main():
    print("=" * 70)
    print("NBA GAME SIMULATION VALIDATION")
    print("=" * 70)
    print()

    predictor = SimulationPredictor(DB_PATH)

    # Get test games
    test_games = get_test_games(DB_PATH, n_games=8)
    print(f"Testing {len(test_games)} games from 2022-23 season")
    print(f"Running {N_SIMS:,} simulations per game")
    print()

    results = []
    output_lines = []

    header = (
        f"{'Date':<12} {'Matchup':<15} {'Actual':>8} {'Pred':>8} "
        f"{'ActTotal':>9} {'PredTotal':>9} {'HomeW%':>7} {'Time':>6}"
    )
    print(header)
    print("-" * len(header))
    output_lines.append("NBA GAME SIMULATION VALIDATION")
    output_lines.append(f"Simulations per game: {N_SIMS:,}")
    output_lines.append("")
    output_lines.append(header)
    output_lines.append("-" * len(header))

    total_time = 0
    spread_errors = []
    total_errors = []
    score_issues = []

    for _, game in test_games.iterrows():
        t0 = time.time()

        pred = predictor.predict_game_row(game.to_dict(), n_sims=N_SIMS, seed=42)

        elapsed = time.time() - t0
        total_time += elapsed

        actual_spread = game['actual_spread']
        pred_spread = pred['predicted_spread']
        actual_total = game['actual_total']
        pred_total = pred['predicted_total']
        home_win = pred['home_win_pct']

        spread_err = pred_spread - actual_spread
        total_err = pred_total - actual_total
        spread_errors.append(spread_err)
        total_errors.append(total_err)

        # Check for unrealistic scores
        if pred['mean_home_score'] < 80 or pred['mean_home_score'] > 140:
            score_issues.append(f"  ⚠ Home score {pred['mean_home_score']:.0f} out of range")
        if pred['mean_away_score'] < 80 or pred['mean_away_score'] > 140:
            score_issues.append(f"  ⚠ Away score {pred['mean_away_score']:.0f} out of range")

        matchup = f"{game['team_abbreviation_away']}@{game['team_abbreviation_home']}"
        date_str = game['game_date'].strftime('%Y-%m-%d')

        line = (
            f"{date_str:<12} {matchup:<15} {actual_spread:>+8.1f} {pred_spread:>+8.1f} "
            f"{actual_total:>9.0f} {pred_total:>9.1f} {home_win:>7.1%} {elapsed:>5.1f}s"
        )
        print(line)
        output_lines.append(line)

        results.append(pred)

    print()
    output_lines.append("")

    # Summary statistics
    spread_errors = np.array(spread_errors)
    total_errors = np.array(total_errors)

    summary_lines = [
        "SUMMARY STATISTICS",
        "=" * 40,
        f"Games tested: {len(test_games)}",
        f"Sims per game: {N_SIMS:,}",
        f"Total time: {total_time:.1f}s ({total_time/len(test_games):.1f}s per game)",
        f"",
        f"Spread Error (pred - actual):",
        f"  Mean: {spread_errors.mean():+.2f}",
        f"  MAE:  {np.abs(spread_errors).mean():.2f}",
        f"  RMSE: {np.sqrt((spread_errors**2).mean()):.2f}",
        f"  Std:  {spread_errors.std():.2f}",
        f"",
        f"Total Error (pred - actual):",
        f"  Mean: {total_errors.mean():+.2f}",
        f"  MAE:  {np.abs(total_errors).mean():.2f}",
        f"  RMSE: {np.sqrt((total_errors**2).mean()):.2f}",
        f"  Std:  {total_errors.std():.2f}",
    ]

    if score_issues:
        summary_lines.append("")
        summary_lines.append("SCORE RANGE WARNINGS:")
        summary_lines.extend(score_issues)
    else:
        summary_lines.append("")
        summary_lines.append("✓ All predicted scores in realistic range (80-140)")

    for line in summary_lines:
        print(line)
        output_lines.append(line)

    # Show distribution for the first game
    if results:
        first = results[0]
        print("\n" + "=" * 40)
        print(f"DISTRIBUTION EXAMPLE: Game 1")
        print(f"  Home scores: mean={first['mean_home_score']:.1f}, std={first['std_spread']:.1f}")
        print(f"  Away scores: mean={first['mean_away_score']:.1f}")
        output_lines.append(f"\nDISTRIBUTION EXAMPLE: Game 1")
        output_lines.append(f"  Home: {first['mean_home_score']:.1f} pts | Away: {first['mean_away_score']:.1f} pts")

    # Save report
    os.makedirs(os.path.dirname(REPORT_PATH), exist_ok=True)
    with open(REPORT_PATH, 'w') as f:
        f.write('\n'.join(output_lines))
    print(f"\nReport saved to {REPORT_PATH}")


if __name__ == '__main__':
    main()
