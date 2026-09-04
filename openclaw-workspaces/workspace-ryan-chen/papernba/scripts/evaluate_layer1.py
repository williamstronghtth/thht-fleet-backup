#!/usr/bin/env python3
"""
Evaluate Layer 1: Player Availability Model
=============================================

Runs walk-forward backtesting with and without player availability adjustments,
then compares the results side by side.

Usage:
    python scripts/evaluate_layer1.py
"""

import sys
import os
import time

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
import pandas as pd
from models.team.backtest import Backtester

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data', 'nbadb', 'nba.duckdb')
REPORT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data', 'reports')


def print_comparison(baseline_metrics: dict, layer1_metrics: dict,
                     baseline_results: pd.DataFrame, layer1_results: pd.DataFrame):
    """Print side-by-side comparison of baseline vs Layer 1."""
    print("\n" + "=" * 70)
    print("LAYER 1: PLAYER AVAILABILITY — COMPARISON REPORT")
    print("=" * 70)

    print(f"\nGames evaluated: {layer1_metrics['total_games']}")

    # ---- Spread ----
    print(f"\n{'Metric':<30} {'Baseline':>12} {'Layer 1':>12} {'Δ':>10}")
    print("-" * 65)

    b, l = baseline_metrics, layer1_metrics
    rows = [
        ("Spread MAE", b['spread_mae'], l['spread_mae']),
        ("Spread Bias", b['spread_bias'], l['spread_bias']),
        ("Total MAE", b['total_mae'], l['total_mae']),
        ("Total Bias", b['total_bias'], l['total_bias']),
        ("Home Pts MAE", b['home_pts_mae'], l['home_pts_mae']),
        ("Away Pts MAE", b['away_pts_mae'], l['away_pts_mae']),
        ("Win Accuracy", b['win_accuracy'], l['win_accuracy']),
    ]

    for name, bv, lv in rows:
        delta = lv - bv
        sign = "+" if delta > 0 else ""
        if name == "Win Accuracy":
            print(f"  {name:<28} {bv:>11.1%} {lv:>11.1%} {sign}{delta:>9.1%}")
        else:
            print(f"  {name:<28} {bv:>11.2f} {lv:>11.2f} {sign}{delta:>9.2f}")

    # ---- Per-Season Breakdown ----
    print(f"\n--- Per-Season Spread MAE Comparison ---")
    print(f"  {'Season':<10} {'Baseline':>12} {'Layer 1':>12} {'Δ':>10} {'Games':>8}")
    print("  " + "-" * 55)

    for sid in sorted(layer1_results['season_id'].unique()):
        br = baseline_results[baseline_results['season_id'] == sid]
        lr = layer1_results[layer1_results['season_id'] == sid]
        b_mae = np.abs(br['spread_error']).mean()
        l_mae = np.abs(lr['adj_spread_error']).mean()
        delta = l_mae - b_mae
        sign = "+" if delta > 0 else ""
        print(f"  {sid[1:]:<10} {b_mae:>12.2f} {l_mae:>12.2f} {sign}{delta:>9.2f} {len(lr):>8}")

    # ---- Adjustment Stats ----
    print(f"\n--- Player Availability Adjustment Stats ---")
    # home_adj is the spread adjustment applied to home team's score
    # (positive = boosted home, negative = penalized home)
    spread_adj = layer1_results['adj_spread'] - layer1_results['pred_spread']
    nonzero_adj = spread_adj[spread_adj.abs() > 0.001]

    print(f"  Games with spread adjustment: {len(nonzero_adj)} / {len(layer1_results)}")
    if len(nonzero_adj) > 0:
        print(f"  Avg |spread adjustment|:      {nonzero_adj.abs().mean():.2f} pts")
        print(f"  Max |spread adjustment|:      {nonzero_adj.abs().max():.2f} pts")
    print(f"  Avg home inactive count:      {layer1_results['n_home_inactive'].mean():.1f}")
    print(f"  Avg away inactive count:      {layer1_results['n_away_inactive'].mean():.1f}")
    print(f"  Avg |inactive diff|:          {(layer1_results['n_home_inactive'] - layer1_results['n_away_inactive']).abs().mean():.1f}")

    # ---- Impact on high-absence games ----
    print(f"\n--- Impact on High-Absence Games ---")
    lr = layer1_results.copy()
    lr['total_inactive'] = lr['n_home_inactive'] + lr['n_away_inactive']
    lr['baseline_spread_ae'] = np.abs(lr['spread_error'])
    lr['layer1_spread_ae'] = np.abs(lr['adj_spread_error'])

    for threshold, label in [(0, "All games"), (5, "5+ inactive"), (10, "10+ inactive")]:
        subset = lr[lr['total_inactive'] >= threshold]
        if len(subset) == 0:
            continue
        b_mae = subset['baseline_spread_ae'].mean()
        l_mae = subset['layer1_spread_ae'].mean()
        delta = l_mae - b_mae
        sign = "+" if delta > 0 else ""
        print(f"  {label:<20} (n={len(subset):>5}): Baseline={b_mae:.2f}  Layer1={l_mae:.2f}  Δ={sign}{delta:.2f}")


def main():
    os.makedirs(REPORT_DIR, exist_ok=True)

    print("=" * 70)
    print("PAPERNBA — Layer 1: Player Availability Evaluation")
    print("=" * 70)

    # Same seasons as baseline evaluation
    seasons = ['22021', '22022']

    backtester = Backtester(DB_PATH)

    # ---- Run Baseline ----
    print(f"\n[1/2] Running BASELINE backtest on seasons {[s[1:] for s in seasons]}...")
    t0 = time.time()
    baseline_results = backtester.run(seasons, verbose=True, use_player_availability=False)
    t_baseline = time.time() - t0

    if baseline_results.empty:
        print("ERROR: No baseline predictions generated!")
        sys.exit(1)

    baseline_metrics = Backtester.compute_metrics(baseline_results)
    print(f"  Baseline done in {t_baseline:.1f}s")

    # ---- Run Layer 1 ----
    print(f"\n[2/2] Running LAYER 1 backtest on seasons {[s[1:] for s in seasons]}...")
    t0 = time.time()
    layer1_results = backtester.run(seasons, verbose=True, use_player_availability=True)
    t_layer1 = time.time() - t0

    if layer1_results.empty:
        print("ERROR: No Layer 1 predictions generated!")
        sys.exit(1)

    # Compute Layer 1 metrics using adjusted predictions
    layer1_for_metrics = layer1_results.copy()
    layer1_for_metrics['spread_error'] = layer1_for_metrics['adj_spread_error']
    layer1_for_metrics['total_error'] = layer1_for_metrics['adj_total_error']
    layer1_for_metrics['pred_home_pts'] = layer1_for_metrics['adj_home_pts']
    layer1_for_metrics['pred_away_pts'] = layer1_for_metrics['adj_away_pts']
    layer1_for_metrics['pred_spread'] = layer1_for_metrics['adj_spread']
    layer1_for_metrics['pred_total'] = layer1_for_metrics['adj_total']
    layer1_metrics = Backtester.compute_metrics(layer1_for_metrics)
    print(f"  Layer 1 done in {t_layer1:.1f}s")

    # ---- Print Comparison ----
    print_comparison(baseline_metrics, layer1_metrics, baseline_results, layer1_results)

    # ---- Save Results ----
    output_path = os.path.join(REPORT_DIR, 'layer1_player_availability.csv')
    layer1_results.to_csv(output_path, index=False)
    print(f"\nDetailed results saved to: {output_path}")
    print(f"Total predictions: {len(layer1_results)}")


if __name__ == '__main__':
    main()
