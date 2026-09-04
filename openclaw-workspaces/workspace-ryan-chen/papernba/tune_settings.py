#!/usr/bin/env python3
"""
Settings Tuner
===============

Tests different parameter combinations and finds what produces
the best prediction accuracy. Uses a sample of games for speed.

Usage:
    python tune_settings.py              # Quick test (50 games)
    python tune_settings.py --full       # Full test (200 games)
    python tune_settings.py --param WINDOW --range 10,15,20,25,30
"""

import sys
import os
import json
import time
import shutil
import argparse
import importlib
import numpy as np
import pandas as pd
import duckdb

sys.path.insert(0, '.')

DB_PATH = 'data/nbadb/nba.duckdb'
SETTINGS_PATH = 'models/simulation/settings.py'
BACKUP_DIR = 'data/reports/settings_backups'


def get_test_games(n_games=50, seed=42):
    """Get a random sample of games for testing."""
    con = duckdb.connect(DB_PATH, read_only=True)
    games = con.execute(f"""
        SELECT game_id, game_date, team_id_home, team_id_away,
               team_abbreviation_home, team_abbreviation_away,
               pts_home, pts_away
        FROM game WHERE season_id = '22025' AND pts_home IS NOT NULL
        AND game_date >= '2025-12-01'
        ORDER BY md5(game_id || '{seed}')
        LIMIT {n_games}
    """).fetchdf()
    con.close()
    return games


def evaluate_settings(games, n_sims=100, overrides=None):
    """Run sims with current settings and return accuracy metrics.
    
    overrides: dict of {param: value} to apply directly to the model class.
    """
    from models.simulation.predictor import SimulationPredictor
    from models.simulation.player_model import PlayerPossessionModel
    
    # Apply overrides directly to the class (bypasses import caching)
    if overrides:
        for k, v in overrides.items():
            if hasattr(PlayerPossessionModel, k):
                setattr(PlayerPossessionModel, k, v)
    
    pred = SimulationPredictor(DB_PATH)
    
    results = []
    for i, (_, g) in enumerate(games.iterrows()):
        try:
            r = pred.predict(str(g['team_id_home']), str(g['team_id_away']),
                             pd.Timestamp(g['game_date']), '22025',
                             n_sims=n_sims, seed=i)
            results.append({
                'pred_spread': r.mean_spread,
                'actual_spread': g['pts_home'] - g['pts_away'],
                'pred_total': r.mean_total,
                'actual_total': g['pts_home'] + g['pts_away'],
            })
        except:
            pass
        if (i + 1) % 25 == 0:
            pred.clear_cache()
    
    if not results:
        return {'win_pct': 0, 'spread_mae': 99, 'total_mae': 99}
    
    df = pd.DataFrame(results)
    win_pct = ((df['pred_spread'] > 0) == (df['actual_spread'] > 0)).mean()
    spread_mae = np.abs(df['pred_spread'] - df['actual_spread']).mean()
    total_mae = np.abs(df['pred_total'] - df['actual_total']).mean()
    
    return {
        'n_games': len(df),
        'win_pct': round(float(win_pct), 4),
        'spread_mae': round(float(spread_mae), 2),
        'total_mae': round(float(total_mae), 2),
    }


def read_current_settings():
    """Read current settings as a dict."""
    settings = {}
    with open(SETTINGS_PATH) as f:
        for line in f:
            line = line.strip()
            if '=' in line and not line.startswith('#') and not line.startswith('"""'):
                key, _, val = line.partition('=')
                key = key.strip()
                val = val.split('#')[0].strip()
                try:
                    settings[key] = float(val) if '.' in val else int(val)
                except:
                    pass
    return settings


def write_setting(param, value):
    """Update a single setting in the settings file."""
    lines = []
    with open(SETTINGS_PATH) as f:
        for line in f:
            if line.strip().startswith(f'{param} =') or line.strip().startswith(f'{param}='):
                # Preserve comment
                parts = line.split('#', 1)
                comment = f'  # {parts[1].strip()}' if len(parts) > 1 else ''
                if isinstance(value, float):
                    lines.append(f'{param} = {value}{comment}\n')
                else:
                    lines.append(f'{param} = {value}{comment}\n')
            else:
                lines.append(line)
    with open(SETTINGS_PATH, 'w') as f:
        f.writelines(lines)


def backup_settings(label):
    """Save current settings with a label."""
    os.makedirs(BACKUP_DIR, exist_ok=True)
    dst = os.path.join(BACKUP_DIR, f'settings_{label}.py')
    shutil.copy2(SETTINGS_PATH, dst)
    return dst


def main():
    parser = argparse.ArgumentParser(description='Tune simulation settings')
    parser.add_argument('--full', action='store_true', help='Use 200 games instead of 50')
    parser.add_argument('--param', type=str, help='Single parameter to sweep')
    parser.add_argument('--range', type=str, help='Comma-separated values to try')
    parser.add_argument('--sims', type=int, default=100, help='Sims per game')
    args = parser.parse_args()
    
    n_games = 200 if args.full else 50
    print(f'Loading {n_games} test games...')
    games = get_test_games(n_games)
    print(f'Got {len(games)} games\n')
    
    # Save baseline
    backup_settings('baseline')
    current = read_current_settings()
    print(f'Current settings:')
    for k, v in sorted(current.items()):
        print(f'  {k} = {v}')
    
    # Baseline evaluation
    print(f'\nRunning baseline ({args.sims} sims/game)...')
    t0 = time.time()
    baseline = evaluate_settings(games, n_sims=args.sims)
    elapsed = time.time() - t0
    print(f'Baseline: {baseline} ({elapsed:.0f}s)\n')
    
    if args.param and args.range:
        # Sweep a single parameter
        values = [float(v) if '.' in v else int(v) for v in args.range.split(',')]
        original = current.get(args.param)
        
        print(f'Sweeping {args.param}: {values}')
        print(f'{"Value":<12} {"Win%":>7} {"SpreadMAE":>10} {"TotalMAE":>10}')
        print('-' * 42)
        
        results = []
        for val in values:
            t0 = time.time()
            metrics = evaluate_settings(games, n_sims=args.sims, overrides={args.param: val})
            elapsed = time.time() - t0
            results.append({'value': val, **metrics})
            marker = ' ← current' if val == original else ''
            print(f'{val:<12} {metrics["win_pct"]:>6.1%} {metrics["spread_mae"]:>10.2f} {metrics["total_mae"]:>10.2f}  ({elapsed:.0f}s){marker}')
        
        # Restore original
        evaluate_settings(games, n_sims=1, overrides={args.param: original})
        
        # Find best
        best = min(results, key=lambda r: r['spread_mae'])
        print(f'\nBest {args.param} = {best["value"]} (MAE: {best["spread_mae"]:.2f})')
        
        # Save results
        os.makedirs(BACKUP_DIR, exist_ok=True)
        with open(os.path.join(BACKUP_DIR, f'sweep_{args.param}.json'), 'w') as f:
            json.dump(results, f, indent=2)
    
    else:
        # Quick sweep of key params
        sweeps = {
            'WINDOW': [10, 15, 20, 25, 30, 40],
            'DECAY': [0.88, 0.90, 0.93, 0.95, 0.97],
            'PRIOR_FGA': [20, 35, 50, 75, 100],
            'PRIOR_POSS': [20, 30, 40, 60, 80],
        }
        
        all_results = {}
        for param, values in sweeps.items():
            original = current.get(param)
            if original is None:
                continue
            
            print(f'Sweeping {param}: {values}')
            param_results = []
            for val in values:
                metrics = evaluate_settings(games, n_sims=args.sims, overrides={param: val})
                param_results.append({'value': val, **metrics})
                marker = ' ← current' if val == original else ''
                print(f'  {val}: Win {metrics["win_pct"]:.1%} | MAE {metrics["spread_mae"]:.2f}{marker}')
            
            # Restore original
            evaluate_settings(games, n_sims=1, overrides={param: original})
            
            best = min(param_results, key=lambda r: r['spread_mae'])
            print(f'  Best: {param} = {best["value"]} (MAE: {best["spread_mae"]:.2f})')
            print()
            
            all_results[param] = param_results
        
        # Save all results
        os.makedirs(BACKUP_DIR, exist_ok=True)
        with open(os.path.join(BACKUP_DIR, 'sweep_all.json'), 'w') as f:
            json.dump(all_results, f, indent=2)
        
        print('Results saved to', os.path.join(BACKUP_DIR, 'sweep_all.json'))


if __name__ == '__main__':
    main()
