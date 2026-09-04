#!/usr/bin/env python3
"""
Layer 1 v2 Backtest Runner
==========================

Runs walk-forward backtests comparing:
1. Baseline (no player adjustments)
2. Player Impact v2 (best calibrated parameters)
3. All layers combined (baseline + player v2 + refs + coach)

Also generates player impact rankings and analysis.
"""

import os
import sys
import pandas as pd
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from models.team.backtest import Backtester
from models.player.impact import PlayerImpactModel
from models.player.profile import PlayerProfileEngine

DB_PATH = 'data/nbadb/nba.duckdb'
REPORT_DIR = 'data/reports'
SEASONS = ['22021', '22022']


def compute_metrics(results, spread_col, total_col, label):
    """Compute MAE metrics for a layer."""
    spread_errors = results[spread_col] - results['actual_spread']
    total_errors = results[total_col] - results['actual_total']

    # Win accuracy
    home_col = spread_col.replace('spread', 'home_pts').replace('_spread', '_home_pts')
    away_col = spread_col.replace('spread', 'away_pts').replace('_spread', '_away_pts')
    if home_col in results.columns and away_col in results.columns:
        pred_w = results[home_col] > results[away_col]
        actual_w = results['actual_home_pts'] > results['actual_away_pts']
        win_acc = (pred_w == actual_w).mean()
    else:
        win_acc = None

    return {
        'label': label,
        'spread_mae': round(np.abs(spread_errors).mean(), 4),
        'total_mae': round(np.abs(total_errors).mean(), 4),
        'spread_bias': round(spread_errors.mean(), 4),
        'total_bias': round(total_errors.mean(), 4),
        'win_accuracy': round(win_acc, 4) if win_acc else None,
        'n_games': len(results),
    }


def player_rankings_analysis(replacement_factor=0.5):
    """Generate player impact rankings and tier analysis."""
    print(f"\n{'='*60}")
    print("PLAYER IMPACT RANKINGS (end of 2022-23 season)")
    print(f"{'='*60}")

    model = PlayerImpactModel(DB_PATH, replacement_factor=replacement_factor)
    as_of = pd.Timestamp('2023-04-10')
    rankings = model.get_player_value_ranking(as_of, min_games=15, top_n=30)

    if rankings.empty:
        print("No rankings generated.")
        return None

    print(f"\nTop 20 Most Impactful Players (whose absence hurts most):")
    print(f"{'Rank':<5} {'Player':<22} {'PPG':>5} {'MPG':>5} {'TS%':>5} "
          f"{'Impact':>7} {'Obs Diff':>9} {'#Out':>5} {'Tier':<10}")
    print("-" * 80)
    for i, row in rankings.head(20).iterrows():
        obs = f"{row['observed_diff']:+.1f}" if row['observed_diff'] is not None else "N/A"
        print(f"{i+1:<5} {row['player_name']:<22} {row['ppg']:>5.1f} {row['mpg']:>5.1f} "
              f"{row['ts_pct']:>5.3f} {row['impact_pts']:>+7.2f} {obs:>9} "
              f"{row['n_games_absent']:>5} {row['tier']:<10}")

    # Tier analysis
    print(f"\nAverage Impact by Player Tier:")
    tier_order = ['Star', 'Starter', 'Rotation', 'Bench']
    tier_stats = rankings.groupby('tier').agg(
        avg_impact=('impact_pts', 'mean'),
        avg_ppg=('ppg', 'mean'),
        avg_mpg=('mpg', 'mean'),
        count=('player_id', 'count'),
    )
    for t in tier_order:
        if t in tier_stats.index:
            r = tier_stats.loc[t]
            print(f"  {t:<10}: impact={r['avg_impact']:+.2f}, ppg={r['avg_ppg']:.1f}, "
                  f"mpg={r['avg_mpg']:.1f}, n={int(r['count'])}")

    return rankings


def find_example_games(results, n_examples=8):
    """Find games where player adjustments correctly predicted outcome."""
    print(f"\n{'='*60}")
    print("EXAMPLE GAMES: Model Correctly Adjusted for Star Absence")
    print(f"{'='*60}")

    if 'adj_spread' not in results.columns:
        return

    results = results.copy()
    results['baseline_error'] = np.abs(results['pred_spread'] - results['actual_spread'])
    results['adj_error'] = np.abs(results['adj_spread'] - results['actual_spread'])
    results['improvement'] = results['baseline_error'] - results['adj_error']
    margin_adj = results['adj_spread'] - results['pred_spread']
    results['margin_adj'] = margin_adj

    # Games with meaningful adjustments that improved prediction
    good = results[
        (np.abs(margin_adj) > 1.0) &
        (results['improvement'] > 1.5)
    ].sort_values('improvement', ascending=False).head(n_examples)

    if good.empty:
        good = results[results['improvement'] > 0.5].sort_values(
            'improvement', ascending=False).head(n_examples)

    for _, g in good.iterrows():
        print(f"\n{g['game_date'].strftime('%Y-%m-%d')}: {g['away_team']} @ {g['home_team']}")
        print(f"  Actual: {int(g['actual_home_pts'])}-{int(g['actual_away_pts'])} "
              f"(spread: {g['actual_spread']:+.0f})")
        print(f"  Baseline pred spread: {g['pred_spread']:+.1f}")
        print(f"  Adjusted pred spread: {g['adj_spread']:+.1f} (adj: {g['margin_adj']:+.1f})")
        print(f"  Error: {g['baseline_error']:.1f} → {g['adj_error']:.1f} "
              f"(improved {g['improvement']:.1f} pts)")
        print(f"  Inactive: home={int(g['n_home_inactive'])}, away={int(g['n_away_inactive'])}")


def main():
    os.makedirs(REPORT_DIR, exist_ok=True)

    # 1. Baseline
    print(f"\n{'='*60}")
    print("Running BASELINE backtest")
    print(f"{'='*60}")
    bt_base = Backtester(DB_PATH)
    baseline_results = bt_base.run(SEASONS, verbose=True)
    base_m = compute_metrics(baseline_results, 'pred_spread', 'pred_total', 'Baseline')
    print(f"\nBaseline: Spread MAE={base_m['spread_mae']}, Total MAE={base_m['total_mae']}, "
          f"Win%={base_m['win_accuracy']}")

    # 2. Player Impact v2 (calibrated: RF=0.5, RD=0.10)
    print(f"\n{'='*60}")
    print("Running PLAYER IMPACT v2 backtest")
    print(f"{'='*60}")
    bt_player = Backtester(DB_PATH)
    bt_player.predictor.player_impact = PlayerImpactModel(DB_PATH, replacement_factor=0.5)
    player_results = bt_player.run(SEASONS, verbose=True, use_player_availability=True)
    player_m = compute_metrics(player_results, 'adj_spread', 'adj_total', 'Player v2')
    print(f"\nPlayer v2: Spread MAE={player_m['spread_mae']}, Total MAE={player_m['total_mae']}, "
          f"Win%={player_m['win_accuracy']}")

    # 3. All layers combined
    print(f"\n{'='*60}")
    print("Running ALL LAYERS backtest")
    print(f"{'='*60}")
    bt_all = Backtester(DB_PATH)
    bt_all.predictor.player_impact = PlayerImpactModel(DB_PATH, replacement_factor=0.5)
    all_results = bt_all.run(SEASONS, verbose=True,
                              use_player_availability=True,
                              use_referee=True,
                              use_coach=True)

    all_metrics = [base_m, player_m]

    if 'final_spread' in all_results.columns:
        all_m = compute_metrics(all_results, 'final_spread', 'final_total', 'All Layers')
        all_metrics.append(all_m)
        print(f"\nAll Layers: Spread MAE={all_m['spread_mae']}, Total MAE={all_m['total_mae']}, "
              f"Win%={all_m['win_accuracy']}")

    # 4. Comparison table
    print(f"\n{'='*70}")
    print("COMPARISON TABLE")
    print(f"{'='*70}")
    print(f"{'Model':<20} {'Spread MAE':>11} {'Total MAE':>11} {'Spread Bias':>12} {'Win%':>8} {'Games':>7}")
    print("-" * 70)
    for m in all_metrics:
        win_str = f"{m['win_accuracy']:.1%}" if m['win_accuracy'] else "N/A"
        print(f"{m['label']:<20} {m['spread_mae']:>11.4f} {m['total_mae']:>11.4f} "
              f"{m['spread_bias']:>+12.4f} {win_str:>8} {m['n_games']:>7}")

    print(f"\nImprovement vs Baseline:")
    for m in all_metrics[1:]:
        s_imp = base_m['spread_mae'] - m['spread_mae']
        t_imp = base_m['total_mae'] - m['total_mae']
        print(f"  {m['label']}: Spread MAE {s_imp:+.4f}, Total MAE {t_imp:+.4f}")

    # 5. Player rankings
    rankings = player_rankings_analysis(0.5)

    # 6. Example games
    find_example_games(player_results)

    # 7. Save results
    player_results.to_csv(f'{REPORT_DIR}/layer1v2_player_impact.csv', index=False)
    all_results.to_csv(f'{REPORT_DIR}/layer1v2_all_layers.csv', index=False)
    if rankings is not None and not rankings.empty:
        rankings.to_csv(f'{REPORT_DIR}/player_impact_rankings.csv', index=False)
    pd.DataFrame(all_metrics).to_csv(f'{REPORT_DIR}/layer1v2_comparison.csv', index=False)

    print(f"\nResults saved to {REPORT_DIR}/")
    print(f"\n{'='*60}")
    print("DONE! Layer 1 v2 Player Impact Model complete.")
    print(f"{'='*60}")


if __name__ == '__main__':
    main()
