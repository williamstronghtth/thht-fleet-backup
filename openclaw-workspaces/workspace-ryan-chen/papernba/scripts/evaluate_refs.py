#!/usr/bin/env python3
"""
Evaluate Layer 3: Referee Impact Model
========================================

Runs walk-forward backtesting with referee crew adjustments and compares
against baseline and player availability models.

Also produces analysis of referee tendencies:
- Highest/lowest scoring refs
- Most/least foul-calling refs
- Home bias analysis
- Variance explained by ref assignment

Usage:
    python scripts/evaluate_refs.py
"""

import sys
import os
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
import pandas as pd
from models.team.backtest import Backtester
from models.referee.profile import RefereeProfileModel

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data', 'nbadb', 'nba.duckdb')
REPORT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data', 'reports')


def compute_metrics_for_columns(results, home_col, away_col, spread_col, total_col):
    """Compute metrics using specified column names."""
    spread_errors = results[spread_col] - results['actual_spread']
    total_errors = results[total_col] - results['actual_total']
    
    pred_winner_home = results[home_col] > results[away_col]
    actual_winner_home = results['actual_home_pts'] > results['actual_away_pts']
    
    return {
        'spread_mae': np.abs(spread_errors).mean(),
        'spread_bias': spread_errors.mean(),
        'total_mae': np.abs(total_errors).mean(),
        'total_bias': total_errors.mean(),
        'win_accuracy': (pred_winner_home == actual_winner_home).mean(),
        'home_pts_mae': np.abs(results[home_col] - results['actual_home_pts']).mean(),
        'away_pts_mae': np.abs(results[away_col] - results['actual_away_pts']).mean(),
    }


def print_comparison(results):
    """Print side-by-side comparison of all model variants."""
    print("\n" + "=" * 80)
    print("LAYER 3: REFEREE IMPACT — COMPARISON REPORT")
    print("=" * 80)
    print(f"\nGames evaluated: {len(results)}")

    # Baseline metrics
    baseline = compute_metrics_for_columns(
        results, 'pred_home_pts', 'pred_away_pts', 'pred_spread', 'pred_total')

    # Layer 1 (players only) — uses adj_ columns
    has_layer1 = 'adj_spread' in results.columns
    if has_layer1:
        layer1 = compute_metrics_for_columns(
            results, 'adj_home_pts', 'adj_away_pts', 'adj_spread', 'adj_total')

    # Layer 3 (refs only — on top of baseline+players)
    has_refs = 'ref_adj_spread' in results.columns
    if has_refs:
        refs = compute_metrics_for_columns(
            results, 'ref_adj_home_pts', 'ref_adj_away_pts', 'ref_adj_spread', 'ref_adj_total')

    # Print comparison table
    print(f"\n{'Metric':<25}", end="")
    print(f"{'Baseline':>12}", end="")
    if has_layer1:
        print(f"{'+ Players':>12}{'Δ':>8}", end="")
    if has_refs:
        print(f"{'+ Refs':>12}{'Δ':>8}", end="")
    print()
    print("-" * (25 + 12 + (20 if has_layer1 else 0) + (20 if has_refs else 0)))

    metrics_to_show = [
        ("Spread MAE", 'spread_mae', False),
        ("Spread Bias", 'spread_bias', False),
        ("Total MAE", 'total_mae', False),
        ("Total Bias", 'total_bias', False),
        ("Win Accuracy", 'win_accuracy', True),
        ("Home Pts MAE", 'home_pts_mae', False),
        ("Away Pts MAE", 'away_pts_mae', False),
    ]

    for label, key, is_pct in metrics_to_show:
        bv = baseline[key]
        print(f"  {label:<23}", end="")
        if is_pct:
            print(f"{bv:>11.1%}", end="")
        else:
            print(f"{bv:>11.2f}", end="")

        if has_layer1:
            lv = layer1[key]
            delta = lv - bv
            sign = "+" if delta > 0 else ""
            if is_pct:
                print(f"{lv:>11.1%}{sign}{delta:>7.1%}", end="")
            else:
                print(f"{lv:>11.2f}{sign}{delta:>7.2f}", end="")

        if has_refs:
            rv = refs[key]
            delta = rv - bv
            sign = "+" if delta > 0 else ""
            if is_pct:
                print(f"{rv:>11.1%}{sign}{delta:>7.1%}", end="")
            else:
                print(f"{rv:>11.2f}{sign}{delta:>7.2f}", end="")
        print()

    # Per-season breakdown
    print(f"\n--- Per-Season Total MAE Comparison ---")
    print(f"  {'Season':<10} {'Baseline':>12}", end="")
    if has_layer1:
        print(f"{'+ Players':>12}", end="")
    if has_refs:
        print(f"{'+ Refs':>12}", end="")
    print(f"{'Games':>8}")
    print("  " + "-" * 60)

    for sid in sorted(results['season_id'].unique()):
        sr = results[results['season_id'] == sid]
        b_total_mae = np.abs(sr['pred_total'] - sr['actual_total']).mean()
        print(f"  {sid[1:]:<10} {b_total_mae:>12.2f}", end="")
        if has_layer1:
            l_total_mae = np.abs(sr['adj_total'] - sr['actual_total']).mean()
            print(f"{l_total_mae:>12.2f}", end="")
        if has_refs:
            r_total_mae = np.abs(sr['ref_adj_total'] - sr['actual_total']).mean()
            print(f"{r_total_mae:>12.2f}", end="")
        print(f"{len(sr):>8}")

    # Referee adjustment stats
    if has_refs:
        print(f"\n--- Referee Adjustment Stats ---")
        ref_adjs = results['ref_total_adj']
        nonzero = ref_adjs[ref_adjs.abs() > 0.001]
        print(f"  Games with ref adjustment:  {len(nonzero)} / {len(results)}")
        print(f"  Games with ref data:        {(results['ref_n_refs'] > 0).sum()} / {len(results)}")
        if len(nonzero) > 0:
            print(f"  Avg |total adjustment|:     {nonzero.abs().mean():.2f} pts")
            print(f"  Max |total adjustment|:     {nonzero.abs().max():.2f} pts")
            print(f"  Avg total adjustment:       {nonzero.mean():+.2f} pts")
        spread_adjs = results['ref_spread_adj']
        nonzero_sp = spread_adjs[spread_adjs.abs() > 0.001]
        if len(nonzero_sp) > 0:
            print(f"  Avg |spread adjustment|:    {nonzero_sp.abs().mean():.2f} pts")


def print_referee_analysis(db_path, seasons):
    """Print interesting referee analysis."""
    model = RefereeProfileModel(db_path)

    # Use the end of the last season as the analysis date
    last_season = seasons[-1]
    analysis_date = pd.Timestamp('2023-06-30')

    analysis = model.get_analysis(analysis_date, last_season)

    print("\n" + "=" * 80)
    print("REFEREE ANALYSIS — Fun Findings")
    print("=" * 80)

    print(f"\nReferees analyzed: {analysis['n_refs_analyzed']} (30+ games)")
    print(f"Games in sample:  {analysis['n_games_used']}")
    print(f"Variance in totals explained by ref assignment (R²): {analysis['variance_explained_r2']:.4f}")

    # Top 10 high-total refs
    print(f"\n--- Top 10 Highest-Scoring Refs (total pts impact) ---")
    print(f"  {'Rank':<5} {'Name':<25} {'Impact':>8} {'Avg Total':>10} {'Games':>6} {'Shrink':>8}")
    print("  " + "-" * 65)
    for i, p in enumerate(analysis['top_total_refs'][:10], 1):
        print(f"  {i:<5} {p.name:<25} {p.total_pts_impact:>+7.1f} {p.avg_total_pts:>10.1f} {p.games:>6} {p.shrinkage:>7.2f}")

    # Top 10 low-total refs
    print(f"\n--- Top 10 Lowest-Scoring Refs (total pts impact) ---")
    print(f"  {'Rank':<5} {'Name':<25} {'Impact':>8} {'Avg Total':>10} {'Games':>6} {'Shrink':>8}")
    print("  " + "-" * 65)
    for i, p in enumerate(analysis['bottom_total_refs'][:10], 1):
        print(f"  {i:<5} {p.name:<25} {p.total_pts_impact:>+7.1f} {p.avg_total_pts:>10.1f} {p.games:>6} {p.shrinkage:>7.2f}")

    # Top foul callers
    print(f"\n--- Top 10 Most Foul-Calling Refs ---")
    print(f"  {'Rank':<5} {'Name':<25} {'PF Impact':>10} {'Avg PF':>8} {'Avg FTA':>9} {'Games':>6}")
    print("  " + "-" * 66)
    for i, p in enumerate(analysis['top_foul_refs'][:10], 1):
        print(f"  {i:<5} {p.name:<25} {p.total_pf_impact:>+9.1f} {p.avg_total_pf:>8.1f} {p.avg_total_fta:>9.1f} {p.games:>6}")

    # Home bias
    print(f"\n--- Top 10 Refs with Strongest Home Bias ---")
    print(f"  (positive = more fouls on away team than league norm)")
    print(f"  {'Rank':<5} {'Name':<25} {'Home Bias':>10} {'Home PF':>8} {'Away PF':>8} {'Games':>6}")
    print("  " + "-" * 64)
    for i, p in enumerate(analysis['top_home_bias_refs'][:10], 1):
        print(f"  {i:<5} {p.name:<25} {p.home_foul_diff:>+9.2f} {p.avg_home_pf:>8.1f} {p.avg_away_pf:>8.1f} {p.games:>6}")

    return analysis


def save_report(results, analysis, report_dir):
    """Save results to CSV."""
    os.makedirs(report_dir, exist_ok=True)
    
    # Save backtest results
    output_path = os.path.join(report_dir, 'layer3_referee_impact.csv')
    results.to_csv(output_path, index=False)
    print(f"\nBacktest results saved to: {output_path}")

    # Save referee profiles
    profiles = analysis.get('top_total_refs', []) + analysis.get('bottom_total_refs', [])
    # Deduplicate
    seen = set()
    unique_profiles = []
    for p in profiles:
        if p.official_id not in seen:
            seen.add(p.official_id)
            unique_profiles.append(p)

    if unique_profiles:
        ref_df = pd.DataFrame([{
            'official_id': p.official_id,
            'name': p.name,
            'games': p.games,
            'total_pts_impact': round(p.total_pts_impact, 2),
            'total_pf_impact': round(p.total_pf_impact, 2),
            'total_fta_impact': round(p.total_fta_impact, 2),
            'pace_impact': round(p.pace_impact, 2),
            'home_foul_diff': round(p.home_foul_diff, 2),
            'avg_total_pts': round(p.avg_total_pts, 1),
            'avg_total_pf': round(p.avg_total_pf, 1),
            'shrinkage': round(p.shrinkage, 3),
        } for p in unique_profiles])
        ref_path = os.path.join(report_dir, 'referee_profiles.csv')
        ref_df.to_csv(ref_path, index=False)
        print(f"Referee profiles saved to: {ref_path}")


def main():
    os.makedirs(REPORT_DIR, exist_ok=True)

    print("=" * 80)
    print("PAPERNBA — Layer 3: Referee Impact Model Evaluation")
    print("=" * 80)

    seasons = ['22021', '22022']
    backtester = Backtester(DB_PATH)

    # Run combined backtest (baseline + players + refs in one pass)
    print(f"\nRunning combined backtest on seasons {[s[1:] for s in seasons]}...")
    print("(This includes baseline, player availability, and referee adjustments)")
    t0 = time.time()
    results = backtester.run(
        seasons, verbose=True,
        use_player_availability=True,
        use_referee=True,
    )
    elapsed = time.time() - t0

    if results.empty:
        print("ERROR: No predictions generated!")
        sys.exit(1)

    print(f"\nBacktest complete in {elapsed:.1f}s — {len(results)} games")

    # Print comparison
    print_comparison(results)

    # Print fun referee analysis
    analysis = print_referee_analysis(DB_PATH, seasons)

    # Save results
    save_report(results, analysis, REPORT_DIR)

    print(f"\n{'=' * 80}")
    print("SUMMARY")
    print(f"{'=' * 80}")

    baseline = compute_metrics_for_columns(
        results, 'pred_home_pts', 'pred_away_pts', 'pred_spread', 'pred_total')
    refs = compute_metrics_for_columns(
        results, 'ref_adj_home_pts', 'ref_adj_away_pts', 'ref_adj_spread', 'ref_adj_total')

    print(f"\n  Baseline Total MAE:     {baseline['total_mae']:.2f}")
    print(f"  With Refs Total MAE:    {refs['total_mae']:.2f}")
    delta = refs['total_mae'] - baseline['total_mae']
    print(f"  Improvement:            {-delta:+.2f} pts")
    print(f"\n  Baseline Spread MAE:    {baseline['spread_mae']:.2f}")
    print(f"  With Refs Spread MAE:   {refs['spread_mae']:.2f}")
    delta_sp = refs['spread_mae'] - baseline['spread_mae']
    print(f"  Improvement:            {-delta_sp:+.2f} pts")
    print(f"\n  Baseline Win Accuracy:  {baseline['win_accuracy']:.1%}")
    print(f"  With Refs Win Accuracy: {refs['win_accuracy']:.1%}")


if __name__ == '__main__':
    main()
