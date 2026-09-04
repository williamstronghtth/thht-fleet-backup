#!/usr/bin/env python3
"""
Evaluate Coach Model (Layer 4)
==============================

Run full backtest comparing:
1. Baseline only
2. All layers without coach (players + refs)
3. All layers with coach (players + refs + coach)

Also shows top coaching tendencies analysis.
Saves results to data/reports/layer4_coach_model.csv
"""

import sys
import os
import time

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
import pandas as pd
from models.team.backtest import Backtester

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                        'data', 'nbadb', 'nba.duckdb')
REPORT_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                            'data', 'reports', 'layer4_coach_model.csv')

# Test on recent seasons with play-by-play data
SEASONS = ['22019', '22020', '22021', '22022']


def compute_layer_metrics(results: pd.DataFrame, spread_col: str, total_col: str) -> dict:
    """Compute MAE and accuracy for a specific layer's predictions."""
    actual_spread = results['actual_spread']
    actual_total = results['actual_total']

    spread_err = results[spread_col] - actual_spread
    total_err = results[total_col] - actual_total

    # Win accuracy
    pred_home_wins = results[spread_col] < 0  # negative spread = home favored
    actual_home_wins = results['actual_home_pts'] > results['actual_away_pts']
    win_acc = (pred_home_wins == actual_home_wins).mean()

    return {
        'spread_mae': np.abs(spread_err).mean(),
        'spread_bias': spread_err.mean(),
        'total_mae': np.abs(total_err).mean(),
        'total_bias': total_err.mean(),
        'win_accuracy': win_acc,
        'games': len(results),
    }


def run_evaluation():
    print("=" * 70)
    print("LAYER 4: COACH MODEL EVALUATION")
    print("=" * 70)
    print(f"\nSeasons: {SEASONS}")
    print(f"Database: {DB_PATH}")

    bt = Backtester(DB_PATH)

    # Run 1: Baseline only
    print("\n--- Running Baseline backtest ---")
    t0 = time.time()
    baseline = bt.run(SEASONS, verbose=True,
                      use_player_availability=False,
                      use_referee=False,
                      use_coach=False)
    print(f"  Baseline: {time.time() - t0:.1f}s")

    # Run 2: All layers WITHOUT coach
    print("\n--- Running Players + Refs backtest ---")
    t0 = time.time()
    layers_no_coach = bt.run(SEASONS, verbose=True,
                             use_player_availability=True,
                             use_referee=True,
                             use_coach=False)
    print(f"  Players+Refs: {time.time() - t0:.1f}s")

    # Run 3: All layers WITH coach
    print("\n--- Running Players + Refs + Coach backtest ---")
    t0 = time.time()
    layers_with_coach = bt.run(SEASONS, verbose=True,
                               use_player_availability=True,
                               use_referee=True,
                               use_coach=True)
    print(f"  All Layers: {time.time() - t0:.1f}s")

    # Compute metrics
    baseline_metrics = compute_layer_metrics(baseline, 'pred_spread', 'pred_total')
    no_coach_metrics = compute_layer_metrics(layers_no_coach, 'ref_adj_spread', 'ref_adj_total')
    with_coach_metrics = compute_layer_metrics(layers_with_coach, 'final_spread', 'final_total')

    # Print comparison
    print("\n" + "=" * 70)
    print("RESULTS COMPARISON")
    print("=" * 70)

    headers = f"{'Metric':<25} {'Baseline':>12} {'Players+Refs':>14} {'+ Coach':>12} {'Δ Coach':>10}"
    print(headers)
    print("-" * 73)

    for label, key, fmt in [
        ('Spread MAE', 'spread_mae', '.2f'),
        ('Spread Bias', 'spread_bias', '+.2f'),
        ('Total MAE', 'total_mae', '.2f'),
        ('Total Bias', 'total_bias', '+.2f'),
        ('Win Accuracy', 'win_accuracy', '.1%'),
        ('Games', 'games', 'd'),
    ]:
        b = baseline_metrics[key]
        nr = no_coach_metrics[key]
        wc = with_coach_metrics[key]
        delta = wc - nr

        if fmt == '.1%':
            print(f"{label:<25} {b:>12.1%} {nr:>14.1%} {wc:>12.1%} {delta:>+10.2%}")
        elif fmt == 'd':
            print(f"{label:<25} {b:>12d} {nr:>14d} {wc:>12d} {delta:>10d}")
        elif fmt == '+.2f':
            print(f"{label:<25} {b:>+12.2f} {nr:>+14.2f} {wc:>+12.2f} {delta:>+10.3f}")
        else:
            print(f"{label:<25} {b:>12.2f} {nr:>14.2f} {wc:>12.2f} {delta:>+10.3f}")

    # Coach adjustment analysis
    if 'coach_spread_adj' in layers_with_coach.columns:
        print("\n--- Coach Adjustment Distribution ---")
        coach_adj = layers_with_coach['coach_spread_adj']
        print(f"  Mean spread adj:  {coach_adj.mean():+.4f}")
        print(f"  Std spread adj:   {coach_adj.std():.4f}")
        print(f"  Non-zero adj:     {(coach_adj != 0).sum()} / {len(coach_adj)} "
              f"({(coach_adj != 0).mean():.1%})")

        total_adj = layers_with_coach['coach_total_adj']
        print(f"  Mean total adj:   {total_adj.mean():+.4f}")
        print(f"  Std total adj:    {total_adj.std():.4f}")

    # Coach profiles analysis
    print("\n--- Coach Profile Analysis ---")
    try:
        from models.coach.decisions import CoachDecisionAnalyzer
        analyzer = CoachDecisionAnalyzer(DB_PATH)
        profiles = analyzer.build_profiles(
            pd.Timestamp('2023-06-01'), '22022')

        if profiles:
            # Top 10 by Q4 overperformance
            sorted_profiles = sorted(
                [p for p in profiles.values() if p.q4_close_games >= 10],
                key=lambda p: p.shrunk_q4_margin, reverse=True)

            print(f"\n  Top 10 by 4Q Close-Game Overperformance (team-seasons):")
            print(f"  {'Team-Season':<20} {'Q4 Adj':>8} {'Close Games':>12} {'Close Win%':>10}")
            print("  " + "-" * 52)
            for p in sorted_profiles[:10]:
                print(f"  {p.team_id}_{p.season_id[-4:]:<16} {p.shrunk_q4_margin:>+8.2f} "
                      f"{p.q4_close_games:>12} {p.q4_win_rate_close:>10.1%}")

            print(f"\n  Bottom 10 by 4Q Close-Game Performance:")
            print(f"  {'Team-Season':<20} {'Q4 Adj':>8} {'Close Games':>12} {'Close Win%':>10}")
            print("  " + "-" * 52)
            for p in sorted_profiles[-10:]:
                print(f"  {p.team_id}_{p.season_id[-4:]:<16} {p.shrunk_q4_margin:>+8.2f} "
                      f"{p.q4_close_games:>12} {p.q4_win_rate_close:>10.1%}")
    except Exception as e:
        print(f"  Error loading profiles: {e}")

    # Rotation depth analysis
    try:
        from models.coach.rotations import RotationAnalyzer
        rot_analyzer = RotationAnalyzer(DB_PATH)
        rot_profiles = rot_analyzer.build_profiles(
            pd.Timestamp('2023-06-01'), '22022')

        if rot_profiles:
            sorted_rot = sorted(
                [p for p in rot_profiles.values() if p.games >= 20],
                key=lambda p: p.shrunk_players_used)

            print(f"\n  Tightest Rotations (fewest players):")
            print(f"  {'Team-Season':<20} {'Avg Players':>12} {'Games':>6}")
            print("  " + "-" * 40)
            for p in sorted_rot[:10]:
                print(f"  {p.team_id}_{p.season_id[-4:]:<16} {p.shrunk_players_used:>12.1f} {p.games:>6}")

            print(f"\n  Deepest Rotations (most players):")
            print(f"  {'Team-Season':<20} {'Avg Players':>12} {'Games':>6}")
            print("  " + "-" * 40)
            for p in sorted_rot[-10:]:
                print(f"  {p.team_id}_{p.season_id[-4:]:<16} {p.shrunk_players_used:>12.1f} {p.games:>6}")
    except Exception as e:
        print(f"  Error loading rotation profiles: {e}")

    # Save results
    report_data = []
    for sid in SEASONS:
        b = baseline[baseline['season_id'] == sid]
        nr = layers_no_coach[layers_no_coach['season_id'] == sid]
        wc = layers_with_coach[layers_with_coach['season_id'] == sid]

        bm = compute_layer_metrics(b, 'pred_spread', 'pred_total') if len(b) > 0 else {}
        nrm = compute_layer_metrics(nr, 'ref_adj_spread', 'ref_adj_total') if len(nr) > 0 else {}
        wcm = compute_layer_metrics(wc, 'final_spread', 'final_total') if len(wc) > 0 else {}

        report_data.append({
            'season_id': sid,
            'baseline_spread_mae': bm.get('spread_mae'),
            'baseline_total_mae': bm.get('total_mae'),
            'baseline_win_acc': bm.get('win_accuracy'),
            'layers_spread_mae': nrm.get('spread_mae'),
            'layers_total_mae': nrm.get('total_mae'),
            'layers_win_acc': nrm.get('win_accuracy'),
            'coach_spread_mae': wcm.get('spread_mae'),
            'coach_total_mae': wcm.get('total_mae'),
            'coach_win_acc': wcm.get('win_accuracy'),
            'games': wcm.get('games', 0),
        })

    report_df = pd.DataFrame(report_data)
    report_df.to_csv(REPORT_PATH, index=False)
    print(f"\n✅ Report saved to {REPORT_PATH}")

    # Also save the full backtest results
    full_path = REPORT_PATH.replace('.csv', '_full_backtest.csv')
    layers_with_coach.to_csv(full_path, index=False)
    print(f"✅ Full backtest saved to {full_path}")


if __name__ == '__main__':
    run_evaluation()
