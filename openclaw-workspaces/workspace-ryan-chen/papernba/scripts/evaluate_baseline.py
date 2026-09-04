#!/usr/bin/env python3
"""
Evaluate Baseline Model
=======================

CLI script that runs the walk-forward backtester on the baseline team model
and generates an evaluation report.

Usage:
    python scripts/evaluate_baseline.py
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
from models.team.backtest import Backtester
from models.team.home_court import HomeCourtModel

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data', 'nbadb', 'nba.duckdb')
REPORT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data', 'reports')


def main():
    os.makedirs(REPORT_DIR, exist_ok=True)

    print("=" * 60)
    print("PAPERNBA — Baseline Team Model Evaluation")
    print("=" * 60)

    # Show home court trends first
    print("\n--- Home Court Advantage Trends ---")
    hc = HomeCourtModel(DB_PATH)
    hc.print_trends()
    overall = hc.overall_stats()
    print(f"\nOverall: {overall['avg_home_margin']:.2f} pt home advantage, "
          f"{overall['home_win_pct']:.1%} home win rate ({overall['total_games']} games)")

    # Run backtest
    # Using 2021-22 and 2022-23 seasons (most recent available)
    backtester = Backtester(DB_PATH)
    seasons = ['22021', '22022']
    
    print(f"\nRunning walk-forward backtest on seasons: {[s[1:] for s in seasons]}")
    results = backtester.run(seasons, verbose=True)

    if results.empty:
        print("ERROR: No predictions generated!")
        sys.exit(1)

    # Compute and print metrics
    metrics = Backtester.compute_metrics(results)
    Backtester.print_report(metrics, results)

    # Save detailed results
    output_path = os.path.join(REPORT_DIR, 'baseline_evaluation.csv')
    results.to_csv(output_path, index=False)
    print(f"\nDetailed results saved to: {output_path}")
    print(f"Total predictions: {len(results)}")

    # Quality check
    if metrics['spread_mae'] > 15:
        print("\n⚠️  WARNING: Spread MAE is very high. Something may be wrong.")
    elif metrics['spread_mae'] > 12:
        print("\n⚠️  Spread MAE is above typical range (8-12). Could be improved.")
    else:
        print(f"\n✅ Spread MAE of {metrics['spread_mae']:.2f} is in expected range.")


if __name__ == '__main__':
    main()
