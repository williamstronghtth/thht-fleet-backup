#!/usr/bin/env python3
"""
scripts/evaluate_ats.py — ATS Backtest Evaluation Report
==========================================================

The moment of truth. Run the full ATS backtest and print a clean report
showing whether our model would have been profitable betting against Vegas.

Usage:
    python scripts/evaluate_ats.py
    python scripts/evaluate_ats.py --seasons 2022 2023
    python scripts/evaluate_ats.py --baseline-only
"""

import argparse
import os
import sys
import time

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import config
from analysis.ats_backtest import run_ats_backtest, compute_ats_metrics, get_top_results
from analysis.kelly_backtest import run_kelly_backtest


def print_separator(char='=', width=70):
    print(char * width)


def print_header(title, width=70):
    print()
    print_separator('=', width)
    print(f"  {title}")
    print_separator('=', width)


def print_section(title, width=70):
    print()
    print(f"── {title} {'─' * (width - len(title) - 4)}")


def format_pct(val, decimal=1):
    """Format a percentage."""
    return f"{val*100:.{decimal}f}%"


def format_money(val):
    """Format a dollar amount."""
    if val >= 0:
        return f"${val:,.2f}"
    else:
        return f"-${abs(val):,.2f}"


def main():
    parser = argparse.ArgumentParser(description='ATS Backtest Evaluation')
    parser.add_argument('--seasons', nargs='+', type=int,
                        default=[2018, 2019, 2020, 2021, 2022, 2023],
                        help='Seasons to backtest (ending year)')
    parser.add_argument('--baseline-only', action='store_true',
                        help='Only use baseline model (no player/ref/coach layers)')
    parser.add_argument('--min-edge', type=float, default=0.0,
                        help='Minimum edge in points to count as a bet')
    parser.add_argument('--kelly-min-edge', type=float, default=2.0,
                        help='Minimum edge for Kelly criterion bets')
    parser.add_argument('--kelly-bankroll', type=float, default=10000.0,
                        help='Starting bankroll for Kelly simulation')
    parser.add_argument('--no-kelly', action='store_true',
                        help='Skip Kelly criterion simulation')
    parser.add_argument('--save-csv', action='store_true', default=True,
                        help='Save detailed results to CSV')
    args = parser.parse_args()

    db_path = os.path.join(config.DATA_DIR, 'nbadb', 'nba.duckdb')

    print_header("NBA AGAINST THE SPREAD (ATS) BACKTEST")
    print(f"  Seasons: {args.seasons}")
    print(f"  Model: {'Baseline only' if args.baseline_only else 'Full stack (baseline + players + refs + coach)'}")
    print(f"  Min edge filter: {args.min_edge} pts")
    print()

    start_time = time.time()

    # ── Run the backtest ──
    results = run_ats_backtest(
        db_path=db_path,
        seasons=args.seasons,
        use_all_layers=not args.baseline_only,
        verbose=True,
    )

    elapsed = time.time() - start_time
    print(f"\n  Backtest completed in {elapsed/60:.1f} minutes ({elapsed:.0f}s)")

    if results.empty:
        print("\n  ❌ No results — check data availability")
        return

    # ── Compute metrics ──
    # All bets (any disagreement)
    all_metrics = compute_ats_metrics(results, min_edge=0.0)
    # Filtered bets (minimum edge)
    filtered_metrics = compute_ats_metrics(results, min_edge=args.min_edge) if args.min_edge > 0 else all_metrics
    # 1+ point edge (the threshold that matters)
    edge1_metrics = compute_ats_metrics(results, min_edge=1.0)

    # ──────────────────────────────────────────────────────
    # REPORT
    # ──────────────────────────────────────────────────────

    print_header("ATS RESULTS — OVERALL")

    print_section("Spread ATS (all disagreements)")
    print(f"  Record:    {all_metrics['spread_record']}")
    print(f"  Win rate:  {format_pct(all_metrics['spread_pct'])}")
    print(f"  Profit:    {format_money(all_metrics['spread_profit'])} (flat $100 bets at -110)")
    print(f"  ROI:       {format_pct(all_metrics['spread_roi'])}")
    print(f"  Break-even: 52.4%")

    print_section("Spread ATS (1+ point edge)")
    print(f"  Record:    {edge1_metrics['spread_record']}")
    print(f"  Win rate:  {format_pct(edge1_metrics['spread_pct'])}")
    print(f"  Profit:    {format_money(edge1_metrics['spread_profit'])}")
    print(f"  ROI:       {format_pct(edge1_metrics['spread_roi'])}")

    print_section("Totals ATS (all disagreements)")
    print(f"  Record:    {all_metrics['total_record']}")
    print(f"  Win rate:  {format_pct(all_metrics['total_pct'])}")
    print(f"  Profit:    {format_money(all_metrics['total_profit'])}")
    print(f"  ROI:       {format_pct(all_metrics['total_roi'])}")

    print_section("Totals ATS (1+ point edge)")
    print(f"  Record:    {edge1_metrics['total_record']}")
    print(f"  Win rate:  {format_pct(edge1_metrics['total_pct'])}")
    print(f"  Profit:    {format_money(edge1_metrics['total_profit'])}")
    print(f"  ROI:       {format_pct(edge1_metrics['total_roi'])}")

    # ── EDGE BUCKETS (THE KEY METRIC) ──
    print_header("EDGE BUCKETS — SPREAD")
    print(f"  {'Bucket':<10} {'Record':<15} {'Win%':>8} {'Profit':>12} {'ROI':>8} {'Bets':>6}")
    print(f"  {'─'*10} {'─'*15} {'─'*8} {'─'*12} {'─'*8} {'─'*6}")
    for bucket_name in ['0-1', '1-2', '2-3', '3-5', '5+']:
        b = all_metrics['spread_edge_buckets'].get(bucket_name, {})
        if b.get('n_bets', 0) > 0:
            print(f"  {bucket_name + ' pts':<10} {b['record']:<15} "
                  f"{format_pct(b['pct']):>8} {format_money(b['profit']):>12} "
                  f"{format_pct(b['roi']):>8} {b['n_bets']:>6}")

    print_header("EDGE BUCKETS — TOTALS")
    print(f"  {'Bucket':<10} {'Record':<15} {'Win%':>8} {'Profit':>12} {'ROI':>8} {'Bets':>6}")
    print(f"  {'─'*10} {'─'*15} {'─'*8} {'─'*12} {'─'*8} {'─'*6}")
    for bucket_name in ['0-1', '1-2', '2-3', '3-5', '5+']:
        b = all_metrics['total_edge_buckets'].get(bucket_name, {})
        if b.get('n_bets', 0) > 0:
            print(f"  {bucket_name + ' pts':<10} {b['record']:<15} "
                  f"{format_pct(b['pct']):>8} {format_money(b['profit']):>12} "
                  f"{format_pct(b['roi']):>8} {b['n_bets']:>6}")

    # ── BY SEASON ──
    print_header("RESULTS BY SEASON")
    print(f"  {'Season':<10} {'Spread Record':<15} {'Spread%':>8} {'Spread ROI':>10} "
          f"{'Total Record':<15} {'Total%':>8} {'Total ROI':>10}")
    print(f"  {'─'*10} {'─'*15} {'─'*8} {'─'*10} {'─'*15} {'─'*8} {'─'*10}")
    for season in sorted(all_metrics['by_season'].keys()):
        s = all_metrics['by_season'][season]
        season_label = f"{season-1}-{str(season)[2:]}"
        print(f"  {season_label:<10} {s['spread_record']:<15} "
              f"{format_pct(s['spread_pct']):>8} {format_pct(s['spread_roi']):>10} "
              f"{s['total_record']:<15} {format_pct(s['total_pct']):>8} "
              f"{format_pct(s['total_roi']):>10}")

    # ── TOP WINS AND LOSSES ──
    top = get_top_results(results, n=10)

    print_header("TOP 10 BIGGEST WINS")
    for _, r in top['biggest_wins'].iterrows():
        date_str = str(r['game_date'])[:10]
        print(f"  {date_str}  {r['away_team']}@{r['home_team']}  "
              f"Bet: {r['spread_bet_side']}  "
              f"Line: {r['line_spread']:+.1f}  Model: {r['model_spread']:+.1f}  "
              f"Actual: {r['actual_spread']:+.1f}  "
              f"Cover margin: {r['cover_margin']:.1f}")

    print_header("TOP 10 BIGGEST LOSSES")
    for _, r in top['biggest_losses'].iterrows():
        date_str = str(r['game_date'])[:10]
        print(f"  {date_str}  {r['away_team']}@{r['home_team']}  "
              f"Bet: {r['spread_bet_side']}  "
              f"Line: {r['line_spread']:+.1f}  Model: {r['model_spread']:+.1f}  "
              f"Actual: {r['actual_spread']:+.1f}  "
              f"Cover margin: {r['cover_margin']:.1f}")

    # ── KELLY SIMULATION ──
    if not args.no_kelly:
        print_header("KELLY CRITERION SIMULATION")
        kelly = run_kelly_backtest(
            results,
            starting_bankroll=args.kelly_bankroll,
            kelly_fraction=0.25,
            min_edge_pts=args.kelly_min_edge,
            include_totals=True,
            verbose=True,
        )

    # ── SAVE CSV ──
    if args.save_csv:
        reports_dir = os.path.join(config.DATA_DIR, 'reports')
        os.makedirs(reports_dir, exist_ok=True)
        csv_path = os.path.join(reports_dir, 'ats_backtest.csv')

        # Select key columns for the CSV
        csv_cols = [
            'game_id', 'game_date', 'season', 'season_id',
            'away_team', 'home_team',
            'actual_home_pts', 'actual_away_pts', 'actual_spread', 'actual_total',
            'model_spread', 'model_total',
            'line_spread', 'line_total',
            'spread_edge', 'total_edge',
            'spread_edge_bucket', 'total_edge_bucket',
            'spread_bet_side', 'total_bet_side',
            'spread_result', 'total_result',
            'spread_profit', 'total_profit',
        ]
        # Only include columns that exist
        save_cols = [c for c in csv_cols if c in results.columns]
        results[save_cols].to_csv(csv_path, index=False)
        print(f"\n  📊 Detailed results saved to: {csv_path}")
        print(f"     ({len(results)} rows)")

        # Also save Kelly bet log if available
        if not args.no_kelly and kelly.bet_log:
            kelly_path = os.path.join(reports_dir, 'kelly_backtest.csv')
            import pandas as pd
            kelly_df = pd.DataFrame(kelly.bet_log)
            kelly_df.to_csv(kelly_path, index=False)
            print(f"  📊 Kelly bet log saved to: {kelly_path}")
            print(f"     ({len(kelly_df)} bets)")

    # ── FINAL VERDICT ──
    print_header("THE VERDICT")
    spread_pct = all_metrics['spread_pct']
    if spread_pct > 0.524:
        print(f"  ✅ PROFITABLE — {format_pct(spread_pct)} ATS (need >52.4%)")
        print(f"  💰 Spread ROI: {format_pct(all_metrics['spread_roi'])}")
    elif spread_pct > 0.50:
        print(f"  ⚠️  ABOVE 50% but below profitability threshold")
        print(f"  📊 {format_pct(spread_pct)} ATS (need >52.4% for profit at -110)")
    else:
        print(f"  ❌ NOT PROFITABLE — {format_pct(spread_pct)} ATS")
        print(f"  📊 Below 50%, the model needs work")

    # Check if higher edge = higher win rate (the real test)
    buckets = all_metrics['spread_edge_buckets']
    bucket_pcts = []
    for bn in ['1-2', '2-3', '3-5', '5+']:
        b = buckets.get(bn, {})
        if b.get('wins', 0) + b.get('losses', 0) >= 20:
            bucket_pcts.append((bn, b['pct']))

    if len(bucket_pcts) >= 2:
        increasing = all(bucket_pcts[i][1] <= bucket_pcts[i+1][1]
                        for i in range(len(bucket_pcts)-1))
        if increasing:
            print(f"  ✅ Higher edge → higher win rate (good calibration!)")
        else:
            print(f"  ⚠️  Edge-win rate relationship is not monotonically increasing")
            for bn, pct in bucket_pcts:
                print(f"      {bn} pts: {format_pct(pct)}")

    print()
    print_separator()
    print(f"  Total games analyzed: {len(results)}")
    print(f"  Backtest time: {elapsed/60:.1f} minutes")
    print_separator()


if __name__ == '__main__':
    main()
