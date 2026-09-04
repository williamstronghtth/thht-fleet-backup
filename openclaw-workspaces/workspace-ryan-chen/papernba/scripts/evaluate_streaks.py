#!/usr/bin/env python3
"""
scripts/evaluate_streaks.py — Evaluate Hot Streak Model Impact
===============================================================

Runs the ATS backtest with and without streaks, then compares results.
Specifically analyzes:
- Overall ATS record and ROI
- Edge bucket breakdown with directional analysis
- Closer game (1-3 pts) bucket performance
- Totals (over/under) impact
- Hot vs cold streak game performance
- Signal frequency analysis
"""

import os
import sys
import time

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import config as cfg
from analysis.ats_backtest import run_ats_backtest, compute_ats_metrics


def directional_analysis(df: pd.DataFrame, label: str) -> pd.DataFrame:
    """Break down spread ATS by direction: closer game vs bigger blowout.

    'Closer game' = our model predicts a tighter margin than the line.
    'Bigger blowout' = our model predicts a wider margin than the line.
    """
    bets = df[df['spread_result'].isin(['win', 'loss', 'push'])].copy()
    if bets.empty:
        return pd.DataFrame()

    # Direction: does our model predict closer or wider margin?
    # spread_edge = line_spread - model_spread
    # model_spread and line_spread are both (away - home), negative = home favored
    # If |model_spread| < |line_spread| → we think it's closer
    bets['model_abs_spread'] = bets['model_spread'].abs()
    bets['line_abs_spread'] = bets['line_spread'].abs()
    bets['direction'] = np.where(
        bets['model_abs_spread'] < bets['line_abs_spread'],
        'closer', 'wider'
    )

    # Edge magnitude buckets
    bets['edge_mag'] = bets['abs_spread_edge']
    bets['edge_range'] = pd.cut(
        bets['edge_mag'],
        bins=[0, 1, 2, 3, 5, 100],
        labels=['0-1', '1-2', '2-3', '3-5', '5+'],
        include_lowest=True
    )

    rows = []
    for direction in ['closer', 'wider']:
        for bucket in ['0-1', '1-2', '2-3', '3-5', '5+']:
            subset = bets[(bets['direction'] == direction) & (bets['edge_range'] == bucket)]
            w = (subset['spread_result'] == 'win').sum()
            l = (subset['spread_result'] == 'loss').sum()
            p = (subset['spread_result'] == 'push').sum()
            d = w + l
            pct = w / d if d > 0 else 0
            profit = subset['spread_profit'].sum()
            roi = profit / (d * 100) if d > 0 else 0
            rows.append({
                'label': label,
                'direction': direction,
                'edge_bucket': bucket,
                'record': f"{w}-{l}-{p}",
                'wins': w, 'losses': l, 'pushes': p,
                'win_pct': pct,
                'profit': profit,
                'roi': roi,
                'n_bets': len(subset),
            })

    return pd.DataFrame(rows)


def streak_signal_analysis(df: pd.DataFrame) -> dict:
    """Analyze how common hot/cold streaks are and their ATS impact."""
    if 'home_n_hot' not in df.columns:
        return {}

    bets = df[df['spread_result'].isin(['win', 'loss', 'push'])].copy()

    # Games with any hot players
    bets['any_hot'] = (bets['home_n_hot'] + bets['away_n_hot']) > 0
    bets['any_cold'] = (bets['home_n_cold'] + bets['away_n_cold']) > 0
    bets['hot_diff'] = (bets['home_n_hot'] - bets['away_n_hot']) + \
                       (bets['away_n_cold'] - bets['home_n_cold'])

    results = {}

    # Frequency
    results['pct_games_with_hot'] = bets['any_hot'].mean()
    results['pct_games_with_cold'] = bets['any_cold'].mean()
    results['avg_hot_per_game'] = (bets['home_n_hot'] + bets['away_n_hot']).mean()
    results['avg_cold_per_game'] = (bets['home_n_cold'] + bets['away_n_cold']).mean()

    # ATS when hot players present vs not
    for label, mask in [('hot_present', bets['any_hot']),
                         ('no_hot', ~bets['any_hot']),
                         ('cold_present', bets['any_cold']),
                         ('no_cold', ~bets['any_cold'])]:
        sub = bets[mask]
        w = (sub['spread_result'] == 'win').sum()
        l = (sub['spread_result'] == 'loss').sum()
        d = w + l
        results[f'{label}_record'] = f"{w}-{l}"
        results[f'{label}_pct'] = w / d if d > 0 else 0
        results[f'{label}_n'] = len(sub)

    # Streak adjustment magnitude
    bets['streak_diff'] = bets['home_streak_adj'] - bets['away_streak_adj']
    results['avg_abs_streak_adj'] = bets['streak_diff'].abs().mean()
    results['max_streak_adj'] = bets['streak_diff'].abs().max()
    results['median_streak_adj'] = bets['streak_diff'].abs().median()

    return results


def totals_analysis(df: pd.DataFrame, label: str) -> dict:
    """Analyze over/under performance."""
    bets = df[df['total_result'].isin(['win', 'loss', 'push'])].copy()
    if bets.empty:
        return {}

    w = (bets['total_result'] == 'win').sum()
    l = (bets['total_result'] == 'loss').sum()
    p = (bets['total_result'] == 'push').sum()
    d = w + l
    profit = bets['total_profit'].sum()

    result = {
        'label': label,
        'total_record': f"{w}-{l}-{p}",
        'total_pct': w / d if d > 0 else 0,
        'total_roi': profit / (d * 100) if d > 0 else 0,
        'total_profit': profit,
    }

    # Over vs Under
    for side, side_label in [('OVER', 'over'), ('UNDER', 'under')]:
        sub = bets[bets['total_bet_side'] == side]
        sw = (sub['total_result'] == 'win').sum()
        sl = (sub['total_result'] == 'loss').sum()
        sd = sw + sl
        result[f'{side_label}_record'] = f"{sw}-{sl}"
        result[f'{side_label}_pct'] = sw / sd if sd > 0 else 0

    return result


def main():
    db_path = os.path.join(cfg.DATA_DIR, 'nbadb', 'nba.duckdb')
    reports_dir = os.path.join(cfg.DATA_DIR, 'reports')
    os.makedirs(reports_dir, exist_ok=True)

    seasons = [2018, 2019, 2020, 2021, 2022, 2023]

    # ── Check if we already have baseline results ──
    baseline_csv = os.path.join(reports_dir, 'ats_backtest.csv')
    if os.path.exists(baseline_csv):
        print("Loading existing baseline ATS results...")
        baseline_df = pd.read_csv(baseline_csv)
        baseline_df['game_date'] = pd.to_datetime(baseline_df['game_date'])
        # Ensure computed columns exist (CSV may not have them)
        if 'abs_spread_edge' not in baseline_df.columns:
            baseline_df['abs_spread_edge'] = baseline_df['spread_edge'].abs()
        if 'abs_total_edge' not in baseline_df.columns:
            baseline_df['abs_total_edge'] = baseline_df['total_edge'].abs()
        print(f"  Loaded {len(baseline_df)} baseline results")
    else:
        print("Running baseline ATS backtest (no streaks)...")
        t0 = time.time()
        baseline_df = run_ats_backtest(db_path, seasons=seasons,
                                        use_all_layers=True,
                                        use_streaks=False, verbose=True)
        print(f"  Baseline done in {time.time() - t0:.0f}s")

    # ── Run with streaks ──
    streaks_csv = os.path.join(reports_dir, 'streaks_ats_backtest.csv')
    if os.path.exists(streaks_csv):
        print("\nLoading existing streaks ATS results...")
        streaks_df = pd.read_csv(streaks_csv)
        streaks_df['game_date'] = pd.to_datetime(streaks_df['game_date'])
        if 'abs_spread_edge' not in streaks_df.columns:
            streaks_df['abs_spread_edge'] = streaks_df['spread_edge'].abs()
        if 'abs_total_edge' not in streaks_df.columns:
            streaks_df['abs_total_edge'] = streaks_df['total_edge'].abs()
        print(f"  Loaded {len(streaks_df)} streaks results")
    else:
        print("\n" + "=" * 70)
        print("Running ATS backtest WITH HOT STREAKS...")
        print("=" * 70)
        t0 = time.time()
        streaks_df = run_ats_backtest(db_path, seasons=seasons,
                                      use_all_layers=True,
                                      use_streaks=True, verbose=True)
        elapsed = time.time() - t0
        print(f"\n  Streaks backtest done in {elapsed:.0f}s")

        # Save streaks results
        streaks_df.to_csv(streaks_csv, index=False)
        print(f"  Saved to {streaks_csv}")

    # ── Compute metrics ──
    baseline_metrics = compute_ats_metrics(baseline_df)
    streaks_metrics = compute_ats_metrics(streaks_df)

    # ── Print comparison ──
    print("\n" + "=" * 70)
    print("COMPARISON: WITHOUT STREAKS vs WITH STREAKS")
    print("=" * 70)

    print(f"\n{'Metric':<30} {'No Streaks':>15} {'With Streaks':>15} {'Delta':>10}")
    print("-" * 70)

    comparisons = [
        ('Spread Record', baseline_metrics['spread_record'], streaks_metrics['spread_record'], ''),
        ('Spread Win %', f"{baseline_metrics['spread_pct']:.3%}", f"{streaks_metrics['spread_pct']:.3%}",
         f"{(streaks_metrics['spread_pct'] - baseline_metrics['spread_pct'])*100:+.2f}pp"),
        ('Spread ROI', f"{baseline_metrics['spread_roi']:.3%}", f"{streaks_metrics['spread_roi']:.3%}",
         f"{(streaks_metrics['spread_roi'] - baseline_metrics['spread_roi'])*100:+.2f}pp"),
        ('Spread Profit', f"${baseline_metrics['spread_profit']:,.0f}", f"${streaks_metrics['spread_profit']:,.0f}",
         f"${streaks_metrics['spread_profit'] - baseline_metrics['spread_profit']:+,.0f}"),
        ('Total Record', baseline_metrics['total_record'], streaks_metrics['total_record'], ''),
        ('Total Win %', f"{baseline_metrics['total_pct']:.3%}", f"{streaks_metrics['total_pct']:.3%}",
         f"{(streaks_metrics['total_pct'] - baseline_metrics['total_pct'])*100:+.2f}pp"),
        ('Total ROI', f"{baseline_metrics['total_roi']:.3%}", f"{streaks_metrics['total_roi']:.3%}",
         f"{(streaks_metrics['total_roi'] - baseline_metrics['total_roi'])*100:+.2f}pp"),
    ]

    for name, base_val, streak_val, delta in comparisons:
        print(f"  {name:<28} {base_val:>15} {streak_val:>15} {delta:>10}")

    # ── Edge bucket comparison ──
    print(f"\n{'─'*70}")
    print("SPREAD EDGE BUCKETS")
    print(f"{'─'*70}")
    print(f"  {'Bucket':<8} {'No Streaks':>20} {'With Streaks':>20} {'Δ Win%':>10}")
    print(f"  {'─'*58}")

    for bucket in ['0-1', '1-2', '2-3', '3-5', '5+']:
        bb = baseline_metrics['spread_edge_buckets'][bucket]
        sb = streaks_metrics['spread_edge_buckets'][bucket]
        delta_pct = (sb['pct'] - bb['pct']) * 100
        print(f"  {bucket:<8} {bb['record']:>10} ({bb['pct']:.1%})"
              f"  {sb['record']:>10} ({sb['pct']:.1%})"
              f"  {delta_pct:>+8.2f}pp")

    # ── Directional analysis ──
    print(f"\n{'─'*70}")
    print("DIRECTIONAL ANALYSIS (Closer Game vs Wider Margin)")
    print(f"{'─'*70}")

    base_dir = directional_analysis(baseline_df, 'No Streaks')
    streak_dir = directional_analysis(streaks_df, 'With Streaks')

    if not base_dir.empty and not streak_dir.empty:
        for direction in ['closer', 'wider']:
            print(f"\n  Direction: {direction.upper()} (model predicts {direction} margin than Vegas)")
            print(f"  {'Bucket':<8} {'No Streaks':>20} {'With Streaks':>20} {'Δ Win%':>10}")
            print(f"  {'─'*58}")

            for bucket in ['0-1', '1-2', '2-3', '3-5', '5+']:
                b_row = base_dir[(base_dir['direction'] == direction) & (base_dir['edge_bucket'] == bucket)]
                s_row = streak_dir[(streak_dir['direction'] == direction) & (streak_dir['edge_bucket'] == bucket)]

                if b_row.empty or s_row.empty:
                    continue

                b = b_row.iloc[0]
                s = s_row.iloc[0]
                delta = (s['win_pct'] - b['win_pct']) * 100
                print(f"  {bucket:<8} {b['record']:>10} ({b['win_pct']:.1%})"
                      f"  {s['record']:>10} ({s['win_pct']:.1%})"
                      f"  {delta:>+8.2f}pp")

    # ── Specifically: closer game by 1-3 pts ──
    print(f"\n{'─'*70}")
    print("KEY METRIC: Closer Game by 1-3 pts")
    print(f"{'─'*70}")

    for label, df in [('No Streaks', baseline_df), ('With Streaks', streaks_df)]:
        bets = df[df['spread_result'].isin(['win', 'loss', 'push'])].copy()
        bets['model_abs'] = bets['model_spread'].abs()
        bets['line_abs'] = bets['line_spread'].abs()
        closer = bets[bets['model_abs'] < bets['line_abs']]
        bucket_13 = closer[(closer['abs_spread_edge'] >= 1) & (closer['abs_spread_edge'] < 3)]
        w = (bucket_13['spread_result'] == 'win').sum()
        l = (bucket_13['spread_result'] == 'loss').sum()
        p = (bucket_13['spread_result'] == 'push').sum()
        d = w + l
        pct = w / d if d > 0 else 0
        profit = bucket_13['spread_profit'].sum()
        roi = profit / (d * 100) if d > 0 else 0
        print(f"  {label}: {w}-{l}-{p} ({pct:.1%}) ROI: {roi:.2%}, Profit: ${profit:,.0f}")

    # ── Totals comparison ──
    print(f"\n{'─'*70}")
    print("TOTALS (OVER/UNDER) COMPARISON")
    print(f"{'─'*70}")

    base_totals = totals_analysis(baseline_df, 'No Streaks')
    streak_totals = totals_analysis(streaks_df, 'With Streaks')

    for label, t in [('No Streaks', base_totals), ('With Streaks', streak_totals)]:
        if t:
            print(f"  {label}: {t['total_record']} ({t['total_pct']:.1%}) ROI: {t['total_roi']:.2%}")
            print(f"    Over:  {t['over_record']} ({t['over_pct']:.1%})")
            print(f"    Under: {t['under_record']} ({t['under_pct']:.1%})")

    # ── Hot streak signal analysis ──
    print(f"\n{'─'*70}")
    print("HOT STREAK SIGNAL ANALYSIS")
    print(f"{'─'*70}")

    signal = streak_signal_analysis(streaks_df)
    if signal:
        print(f"  % of games with hot player(s):  {signal['pct_games_with_hot']:.1%}")
        print(f"  % of games with cold player(s): {signal['pct_games_with_cold']:.1%}")
        print(f"  Avg hot players per game:       {signal['avg_hot_per_game']:.2f}")
        print(f"  Avg cold players per game:      {signal['avg_cold_per_game']:.2f}")
        print(f"  Avg |streak adj| (spread pts):  {signal['avg_abs_streak_adj']:.3f}")
        print(f"  Max |streak adj|:               {signal['max_streak_adj']:.3f}")
        print(f"  Median |streak adj|:            {signal['median_streak_adj']:.3f}")
        print()
        print(f"  ATS when hot player(s) present: {signal['hot_present_record']} ({signal['hot_present_pct']:.1%}, n={signal['hot_present_n']})")
        print(f"  ATS when NO hot players:        {signal['no_hot_record']} ({signal['no_hot_pct']:.1%}, n={signal['no_hot_n']})")
        print(f"  ATS when cold player(s) present:{signal['cold_present_record']} ({signal['cold_present_pct']:.1%}, n={signal['cold_present_n']})")
        print(f"  ATS when NO cold players:       {signal['no_cold_record']} ({signal['no_cold_pct']:.1%}, n={signal['no_cold_n']})")

    # ── By season ──
    print(f"\n{'─'*70}")
    print("BY SEASON COMPARISON")
    print(f"{'─'*70}")
    print(f"  {'Season':<8} {'No Streaks':>20} {'With Streaks':>20} {'Δ Win%':>10}")
    print(f"  {'─'*58}")

    for season in sorted(set(list(baseline_metrics['by_season'].keys()) +
                             list(streaks_metrics['by_season'].keys()))):
        bs = baseline_metrics['by_season'].get(season, {})
        ss = streaks_metrics['by_season'].get(season, {})
        b_rec = bs.get('spread_record', 'N/A')
        s_rec = ss.get('spread_record', 'N/A')
        b_pct = bs.get('spread_pct', 0)
        s_pct = ss.get('spread_pct', 0)
        delta = (s_pct - b_pct) * 100
        print(f"  {season:<8} {b_rec:>10} ({b_pct:.1%})"
              f"  {s_rec:>10} ({s_pct:.1%})"
              f"  {delta:>+8.2f}pp")

    print(f"\n{'='*70}")
    print("Done! Results saved to data/reports/streaks_ats_backtest.csv")
    print(f"{'='*70}")


if __name__ == '__main__':
    main()
