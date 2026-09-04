#!/usr/bin/env python3
"""
Simulation Backtest Runner
===========================

Walk-forward backtest using the possession-by-possession game simulator.
For each game in the season, builds player profiles from prior data,
runs Monte Carlo simulations, and compares to actual outcomes.

Architecture:
  1. Main process loads ALL data from DuckDB once
  2. Main process pre-builds GameConfig for each game (walk-forward safe)
  3. Worker processes only run Monte Carlo (pure numpy, no DB)

Usage:
    python run_simulation_backtest.py [--season 22022] [--sims 500] [--jobs 4]
"""

import os
import sys
import time
import argparse
import json
import numpy as np
import pandas as pd
from concurrent.futures import ProcessPoolExecutor, as_completed
from multiprocessing import cpu_count

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

DB_PATH = 'data/nbadb/nba.duckdb'
REPORT_DIR = 'data/reports'


def load_season_games(db_path: str, season_id: str) -> pd.DataFrame:
    """Load all regular season games for a season, sorted by date."""
    import duckdb
    con = duckdb.connect(db_path, read_only=True)
    df = con.execute("""
        SELECT
            g.game_id,
            g.game_date,
            g.season_id,
            g.team_id_home,
            g.team_id_away,
            g.pts_home,
            g.pts_away,
            g.team_abbreviation_home,
            g.team_abbreviation_away
        FROM game g
        WHERE g.season_id = ?
          AND g.season_type = 'Regular Season'
          AND g.pts_home IS NOT NULL
          AND g.pts_away IS NOT NULL
        ORDER BY g.game_date, g.game_id
    """, [season_id]).fetchdf()
    con.close()
    df['game_date'] = pd.to_datetime(df['game_date'])
    return df


def build_all_configs(games: pd.DataFrame, db_path: str, season_id: str):
    """Pre-build GameConfig for every game in the main process.
    
    Walk-forward safe: each config only uses data before that game's date.
    Returns list of (game_info_dict, GameConfig) tuples.
    """
    from models.simulation.player_model import PlayerPossessionModel
    from models.simulation.engine import GameConfig
    from models.team.ratings import TeamRatings
    from models.coach.rotations import RotationAnalyzer
    from models.referee.profile import RefereeProfileModel

    # Initialize models (single load each)
    player_model = PlayerPossessionModel(db_path)
    team_ratings = TeamRatings(db_path)
    rotation_analyzer = RotationAnalyzer(db_path)
    ref_model = RefereeProfileModel(db_path)

    # Pre-load rotation data for the relevant seasons
    try:
        year = int(season_id[1:])
        rot_seasons = [f"2{y}" for y in range(year - 2, year + 1)]
    except ValueError:
        rot_seasons = [season_id]
    rotation_analyzer.preload(rot_seasons)

    # Pre-load officials and inactive players
    import duckdb
    con = duckdb.connect(db_path, read_only=True)
    
    officials_df = con.execute("""
        SELECT o.game_id, o.official_id
        FROM officials o
        JOIN game g ON o.game_id = g.game_id
        WHERE g.season_type = 'Regular Season'
    """).fetchdf()
    officials_by_game = {}
    for _, row in officials_df.iterrows():
        gid = row['game_id']
        if gid not in officials_by_game:
            officials_by_game[gid] = []
        officials_by_game[gid].append(int(row['official_id']))
    del officials_df

    inactive_df = con.execute("""
        SELECT i.game_id, i.player_id
        FROM inactive_players i
        JOIN game g ON i.game_id = g.game_id
        WHERE g.season_type = 'Regular Season'
    """).fetchdf()
    inactive_by_game = {}
    for _, row in inactive_df.iterrows():
        gid = row['game_id']
        if gid not in inactive_by_game:
            inactive_by_game[gid] = []
        inactive_by_game[gid].append(int(row['player_id']))
    del inactive_df
    con.close()

    configs = []
    total = len(games)

    for i, (_, game) in enumerate(games.iterrows()):
        game_date = pd.Timestamp(game['game_date'])
        home_id = str(game['team_id_home'])
        away_id = str(game['team_id_away'])
        game_id = game['game_id']

        # Game info for results
        game_info = {
            'game_id': game_id,
            'game_date': str(game_date),
            'home_team': home_id,
            'away_team': away_id,
            'home_abbr': game.get('team_abbreviation_home', ''),
            'away_abbr': game.get('team_abbreviation_away', ''),
            'actual_home_pts': game['pts_home'],
            'actual_away_pts': game['pts_away'],
            'actual_spread': game['pts_home'] - game['pts_away'],
            'actual_total': game['pts_home'] + game['pts_away'],
        }

        try:
            # 1. Player profiles
            inactive_set = set(inactive_by_game.get(game_id, []))
            home_profiles = player_model.get_team_profiles(int(home_id), game_date, top_n=13)
            away_profiles = player_model.get_team_profiles(int(away_id), game_date, top_n=13)

            if inactive_set:
                home_profiles = [p for p in home_profiles if p.player_id not in inactive_set]
                away_profiles = [p for p in away_profiles if p.player_id not in inactive_set]

            if len(home_profiles) < 5 or len(away_profiles) < 5:
                # Fallback: use default arrays (engine handles empty rosters)
                home_profiles = []
                away_profiles = []

            # 2. Team ratings
            home_rating = team_ratings.get_team_rating_before_date(home_id, game_date, season_id)
            away_rating = team_ratings.get_team_rating_before_date(away_id, game_date, season_id)
            league_avg = team_ratings.league_average_before_date(season_id, game_date)

            if home_rating is None:
                home_rating = {'off_rtg': 110.0, 'def_rtg': 110.0, 'pace': 98.0}
            if away_rating is None:
                away_rating = {'off_rtg': 110.0, 'def_rtg': 110.0, 'pace': 98.0}

            # 3. Coach rotation profiles
            home_rotation = rotation_analyzer.get_rotation_profile(home_id, season_id, game_date)
            away_rotation = rotation_analyzer.get_rotation_profile(away_id, season_id, game_date)

            # 4. Ref crew adjustments
            ref_foul_modifier = 1.0
            ref_home_bias = 0.0
            ref_crew = officials_by_game.get(game_id, [])
            if ref_crew:
                ref_adj = ref_model.get_crew_adjustment(ref_crew, game_date, season_id)
                if ref_adj['n_refs_found'] > 0:
                    base_pf = 42.0
                    ref_foul_modifier = 1.0 + (ref_adj['total_pf_adj'] / base_pf)
                    ref_foul_modifier = np.clip(ref_foul_modifier, 0.85, 1.15)
                    ref_home_bias = ref_adj['home_foul_adj'] / 200.0
                    ref_home_bias = np.clip(ref_home_bias, -0.02, 0.02)

            # 5. Build config — players ARE the offense, no OffRtg/DefRtg
            config = GameConfig(
                home_roster=home_profiles,
                away_roster=away_profiles,
                ref_foul_modifier=float(ref_foul_modifier),
                ref_home_bias=float(ref_home_bias),
                home_pace=home_rating['pace'],
                away_pace=away_rating['pace'],
                league_avg_pace=league_avg['pace'],
                home_players_used=int(home_rotation.shrunk_players_used) if home_rotation else 9,
                away_players_used=int(away_rotation.shrunk_players_used) if away_rotation else 9,
            )

            configs.append((game_info, config))

        except Exception as e:
            game_info['error'] = str(e)
            configs.append((game_info, None))

        if (i + 1) % 50 == 0 or i + 1 == total:
            print(f"    Built configs: {i+1}/{total}")

    return configs


def run_simulation(args):
    """Worker function: run Monte Carlo on a pre-built GameConfig. No DB needed."""
    game_info, config_data, n_sims, game_idx = args

    # Reconstruct GameConfig and run simulation
    from models.simulation.engine import GameConfig, GameSimulator
    from models.simulation.monte_carlo import MonteCarloRunner, SimulationResult
    import time as _time

    if config_data is None:
        return {**game_info, 'error': game_info.get('error', 'No config built')}

    config = config_data  # Already a GameConfig object

    try:
        t0 = _time.time()
        runner = MonteCarloRunner(config, seed=game_idx)
        result = runner.run(n_sims=n_sims)
        elapsed = _time.time() - t0

        return {
            **game_info,
            'predicted_spread': result.mean_spread,
            'predicted_total': result.mean_total,
            'home_win_pct': result.home_win_pct,
            'mean_home_score': result.mean_home_score,
            'mean_away_score': result.mean_away_score,
            'std_spread': result.std_spread,
            'std_total': result.std_total,
            'elapsed_seconds': elapsed,
        }
    except Exception as e:
        return {**game_info, 'error': str(e)}


def compute_metrics(df: pd.DataFrame, label: str) -> dict:
    """Compute prediction accuracy metrics."""
    spread_errors = df['predicted_spread'] - df['actual_spread']
    total_errors = df['predicted_total'] - df['actual_total']

    # Win accuracy
    pred_home_win = df['predicted_spread'] > 0
    actual_home_win = df['actual_spread'] > 0
    win_acc = (pred_home_win == actual_home_win).mean()

    # Calibration of win probabilities
    cal = None
    if 'home_win_pct' in df.columns:
        bins = [0, 0.3, 0.4, 0.5, 0.6, 0.7, 1.0]
        df_cal = df.copy()
        df_cal['bin'] = pd.cut(df_cal['home_win_pct'], bins=bins)
        cal = df_cal.groupby('bin', observed=True).agg(
            pred_win_pct=('home_win_pct', 'mean'),
            actual_win_pct=('actual_spread', lambda x: (x > 0).mean()),
            n_games=('game_id', 'count'),
        )

    return {
        'label': label,
        'n_games': len(df),
        'spread_mae': round(np.abs(spread_errors).mean(), 3),
        'total_mae': round(np.abs(total_errors).mean(), 3),
        'spread_bias': round(spread_errors.mean(), 3),
        'total_bias': round(total_errors.mean(), 3),
        'spread_rmse': round(np.sqrt((spread_errors ** 2).mean()), 3),
        'total_rmse': round(np.sqrt((total_errors ** 2).mean()), 3),
        'win_accuracy': round(win_acc, 4),
        'calibration': cal,
    }


def print_metrics(m: dict):
    """Pretty-print metrics."""
    print(f"\n{'='*60}")
    print(f"  {m['label']}  ({m['n_games']} games)")
    print(f"{'='*60}")
    print(f"  Spread MAE:    {m['spread_mae']:.3f}")
    print(f"  Spread RMSE:   {m['spread_rmse']:.3f}")
    print(f"  Spread Bias:   {m['spread_bias']:+.3f}")
    print(f"  Total MAE:     {m['total_mae']:.3f}")
    print(f"  Total RMSE:    {m['total_rmse']:.3f}")
    print(f"  Total Bias:    {m['total_bias']:+.3f}")
    print(f"  Win Accuracy:  {m['win_accuracy']:.1%}")

    if m['calibration'] is not None:
        print(f"\n  Win Probability Calibration:")
        print(f"  {'Bin':<15} {'Pred':>8} {'Actual':>8} {'Games':>7}")
        print(f"  {'-'*40}")
        for idx, row in m['calibration'].iterrows():
            print(f"  {str(idx):<15} {row['pred_win_pct']:>8.1%} "
                  f"{row['actual_win_pct']:>8.1%} {int(row['n_games']):>7}")


def monthly_breakdown(df: pd.DataFrame):
    """Print month-by-month accuracy."""
    df = df.copy()
    df['month'] = df['game_date'].dt.to_period('M')

    print(f"\n{'='*60}")
    print("  Monthly Breakdown")
    print(f"{'='*60}")
    print(f"  {'Month':<10} {'Games':>6} {'Spread MAE':>11} {'Win%':>7} {'Bias':>8}")
    print(f"  {'-'*45}")

    for month, grp in df.groupby('month'):
        spread_err = grp['predicted_spread'] - grp['actual_spread']
        pred_hw = grp['predicted_spread'] > 0
        actual_hw = grp['actual_spread'] > 0
        win_acc = (pred_hw == actual_hw).mean()
        print(f"  {str(month):<10} {len(grp):>6} {np.abs(spread_err).mean():>11.3f} "
              f"{win_acc:>7.1%} {spread_err.mean():>+8.3f}")


def main():
    parser = argparse.ArgumentParser(description='Simulation Backtest')
    parser.add_argument('--season', default='22022',
                        help='Season ID (default: 22022 = 2022-23)')
    parser.add_argument('--sims', type=int, default=500,
                        help='Monte Carlo sims per game (default: 500)')
    parser.add_argument('--jobs', type=int, default=None,
                        help='Parallel workers (default: CPU count - 1)')
    parser.add_argument('--start-game', type=int, default=0,
                        help='Start from game N (for resuming)')
    parser.add_argument('--max-games', type=int, default=None,
                        help='Max games to process (for testing)')
    parser.add_argument('--skip-early', type=int, default=100,
                        help='Skip first N games (not enough data, default: 100)')
    args = parser.parse_args()

    os.makedirs(REPORT_DIR, exist_ok=True)

    n_jobs = args.jobs or max(1, cpu_count() - 1)

    print(f"{'='*60}")
    print(f"  POSSESSION-BY-POSSESSION SIMULATION BACKTEST")
    print(f"{'='*60}")
    print(f"  Season:     {args.season}")
    print(f"  Sims/game:  {args.sims}")
    print(f"  Workers:    {n_jobs}")
    print(f"  Skip early: {args.skip_early} games")
    print()

    # 1. Load games
    print("Loading season games...")
    games = load_season_games(DB_PATH, args.season)
    print(f"  Found {len(games)} regular season games")

    games = games.iloc[args.skip_early:].reset_index(drop=True)
    print(f"  After skipping first {args.skip_early}: {len(games)} games")

    if args.start_game > 0:
        games = games.iloc[args.start_game:].reset_index(drop=True)
        print(f"  Resuming from game {args.start_game}: {len(games)} remaining")

    if args.max_games:
        games = games.head(args.max_games)
        print(f"  Capped at {args.max_games} games")

    total_games = len(games)

    # 2. Pre-build all GameConfigs in main process (single DB load)
    print(f"\n  Phase 1: Building {total_games} game configs (loading data once)...")
    t_config_start = time.time()
    configs = build_all_configs(games, DB_PATH, args.season)
    t_config = time.time() - t_config_start
    
    n_valid = sum(1 for _, c in configs if c is not None)
    n_errors = sum(1 for _, c in configs if c is None)
    print(f"  Built {n_valid} configs, {n_errors} errors in {t_config:.1f}s")

    # 3. Run Monte Carlo simulations (parallel, no DB needed)
    print(f"\n  Phase 2: Running Monte Carlo ({args.sims} sims × {n_valid} games)...")
    print(f"  Total simulations: {n_valid * args.sims:,}")
    print()

    tasks = [
        (info, config, args.sims, i)
        for i, (info, config) in enumerate(configs)
    ]

    results = []
    errors = []
    t_sim_start = time.time()

    if n_jobs == 1:
        for task in tasks:
            r = run_simulation(task)
            if 'error' in r:
                errors.append(r)
            else:
                results.append(r)
                done = len(results) + len(errors)
                elapsed = time.time() - t_sim_start
                rate = done / elapsed if elapsed > 0 else 0
                eta = (total_games - done) / rate if rate > 0 else 0
                if done % 25 == 0 or done == total_games:
                    print(f"  ✅ [{done}/{total_games}] "
                          f"Rate: {rate:.1f} games/s | ETA: {eta/60:.1f}m")
    else:
        with ProcessPoolExecutor(max_workers=n_jobs) as executor:
            future_map = {executor.submit(run_simulation, t): t for t in tasks}

            for future in as_completed(future_map):
                r = future.result()
                if 'error' in r:
                    errors.append(r)
                else:
                    results.append(r)

                done = len(results) + len(errors)
                elapsed = time.time() - t_sim_start
                rate = done / elapsed if elapsed > 0 else 0
                eta = (total_games - done) / rate if rate > 0 else 0

                if done % 50 == 0 or done == total_games:
                    print(f"  ✅ [{done}/{total_games}] "
                          f"Rate: {rate:.1f} games/s | ETA: {eta/60:.1f}m")

    total_time = time.time() - t_config_start
    sim_time = time.time() - t_sim_start
    print(f"\n  Config build: {t_config:.1f}s | Simulations: {sim_time:.1f}s | Total: {total_time:.1f}s")
    print(f"  Successful: {len(results)} | Errors: {len(errors)}")

    if not results:
        print("No successful predictions. Check errors.")
        if errors:
            for e in errors[:5]:
                print(f"  Error: {e.get('error', 'unknown')}")
        return

    # Build results DataFrame
    df = pd.DataFrame(results)
    df['game_date'] = pd.to_datetime(df['game_date'])
    df = df.sort_values('game_date').reset_index(drop=True)

    # Compute and print metrics
    metrics = compute_metrics(df, f'Simulation Backtest (season {args.season}, {args.sims} sims)')
    print_metrics(metrics)

    # Monthly breakdown
    monthly_breakdown(df)

    # Compare to baseline
    baseline_path = f'{REPORT_DIR}/layer1v2_comparison.csv'
    if os.path.exists(baseline_path):
        baseline = pd.read_csv(baseline_path)
        base_row = baseline[baseline['label'] == 'Baseline']
        if len(base_row) > 0:
            base_row = base_row.iloc[0]
            print(f"\n{'='*60}")
            print("  COMPARISON vs OLD STATISTICAL MODEL")
            print(f"{'='*60}")
            print(f"  {'Metric':<20} {'Old Baseline':>12} {'Simulation':>12} {'Delta':>10}")
            print(f"  {'-'*55}")
            for metric_name, old_key, new_val in [
                ('Spread MAE', 'spread_mae', metrics['spread_mae']),
                ('Total MAE', 'total_mae', metrics['total_mae']),
                ('Win Accuracy', 'win_accuracy', metrics['win_accuracy']),
                ('Spread Bias', 'spread_bias', metrics['spread_bias']),
            ]:
                old_val = base_row[old_key]
                delta = new_val - old_val
                if 'Accuracy' in metric_name:
                    better = '✅' if delta > 0 else '❌'
                    print(f"  {metric_name:<20} {old_val:>12.1%} {new_val:>12.1%} {delta:>+10.4f} {better}")
                elif 'Bias' in metric_name:
                    better = '✅' if abs(new_val) < abs(old_val) else '❌'
                    print(f"  {metric_name:<20} {old_val:>12.4f} {new_val:>12.4f} {delta:>+10.4f} {better}")
                else:
                    better = '✅' if delta < 0 else '❌'
                    print(f"  {metric_name:<20} {old_val:>12.4f} {new_val:>12.4f} {delta:>+10.4f} {better}")

    # Save results
    output_path = f'{REPORT_DIR}/simulation_backtest_{args.season}.csv'
    df.to_csv(output_path, index=False)
    print(f"\n  Results saved to {output_path}")

    # Save metrics
    metrics_out = {k: v for k, v in metrics.items() if k != 'calibration'}
    metrics_out['sims_per_game'] = args.sims
    metrics_out['config_build_seconds'] = round(t_config, 1)
    metrics_out['sim_seconds'] = round(sim_time, 1)
    metrics_out['total_seconds'] = round(total_time, 1)
    metrics_out['season'] = args.season
    metrics_out['n_workers'] = n_jobs

    with open(f'{REPORT_DIR}/simulation_backtest_{args.season}_metrics.json', 'w') as f:
        json.dump(metrics_out, f, indent=2)

    if errors:
        with open(f'{REPORT_DIR}/simulation_backtest_{args.season}_errors.json', 'w') as f:
            json.dump([{k: str(v) for k, v in e.items()} for e in errors], f, indent=2)

    print(f"\n{'='*60}")
    print("  DONE!")
    print(f"{'='*60}")


if __name__ == '__main__':
    main()
