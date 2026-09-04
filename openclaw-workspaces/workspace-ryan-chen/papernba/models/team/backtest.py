"""
Backtester for Baseline Model
==============================

Walk-forward validation: for each game, only uses data available
BEFORE that game to make predictions. No future data leakage.

Metrics:
- MAE on predicted spread vs actual spread
- MAE on predicted total vs actual total
- ATS accuracy (predicted spread vs actual margin)
- Calibration analysis
"""

import duckdb
import pandas as pd
import numpy as np
from typing import List, Optional, Dict
from .predictor import BaselinePredictor


class Backtester:
    """Walk-forward backtesting of the baseline prediction model."""

    def __init__(self, db_path: str):
        self.db_path = db_path
        self.predictor = BaselinePredictor(db_path)
        self._inactive_by_game: Optional[Dict] = None
        self._officials_by_game: Optional[Dict] = None

    def _load_inactive_players(self):
        """Load all inactive player records grouped by game_id and team_id."""
        if self._inactive_by_game is not None:
            return
        con = duckdb.connect(self.db_path, read_only=True)
        df = con.execute("""
            SELECT i.game_id, i.player_id, i.team_id
            FROM inactive_players i
            JOIN game g ON i.game_id = g.game_id
            WHERE g.season_type = 'Regular Season'
        """).fetchdf()
        con.close()

        # Build lookup: (game_id, team_id) -> list of player_ids
        self._inactive_by_game = {}
        for _, row in df.iterrows():
            key = (row['game_id'], row['team_id'])
            if key not in self._inactive_by_game:
                self._inactive_by_game[key] = []
            self._inactive_by_game[key].append(row['player_id'])

    def _load_officials(self):
        """Load all official assignments grouped by game_id."""
        if self._officials_by_game is not None:
            return
        con = duckdb.connect(self.db_path, read_only=True)
        df = con.execute("""
            SELECT o.game_id, o.official_id
            FROM officials o
            JOIN game g ON o.game_id = g.game_id
            WHERE g.season_type = 'Regular Season'
        """).fetchdf()
        con.close()

        self._officials_by_game = {}
        for _, row in df.iterrows():
            gid = row['game_id']
            if gid not in self._officials_by_game:
                self._officials_by_game[gid] = []
            self._officials_by_game[gid].append(int(row['official_id']))

    def get_officials_for_game(self, game_id: str) -> List[int]:
        """Get list of official IDs for a specific game."""
        self._load_officials()
        return self._officials_by_game.get(game_id, [])

    def get_inactive_for_game(self, game_id: str, team_id: str) -> List[str]:
        """Get list of inactive player IDs for a team in a specific game."""
        self._load_inactive_players()
        return self._inactive_by_game.get((game_id, team_id), [])

    def get_games_for_season(self, season_id: str) -> pd.DataFrame:
        """Load all regular season games for backtesting."""
        con = duckdb.connect(self.db_path, read_only=True)
        df = con.execute("""
            SELECT game_id, game_date, season_id,
                   team_id_home, team_id_away,
                   team_abbreviation_home, team_abbreviation_away,
                   pts_home, pts_away
            FROM game
            WHERE season_type = 'Regular Season'
              AND season_id = ?
              AND pts_home IS NOT NULL AND pts_away IS NOT NULL
            ORDER BY game_date
        """, [season_id]).fetchdf()
        con.close()
        df['game_date'] = pd.to_datetime(df['game_date'])
        return df

    def run(self, season_ids: List[str], verbose: bool = True,
            use_player_availability: bool = False,
            use_referee: bool = False,
            use_coach: bool = False,
            use_streaks: bool = False) -> pd.DataFrame:
        """Run walk-forward backtest across specified seasons.
        
        Args:
            season_ids: List of season IDs to backtest (e.g., ['22021', '22022'])
            verbose: Print progress updates
            use_player_availability: If True, include player availability adjustments
            use_referee: If True, include referee crew adjustments (Layer 3)
        
        Returns:
            DataFrame with one row per predicted game, including actual and predicted values
        """
        if use_player_availability:
            self._load_inactive_players()
        if use_referee:
            self._load_officials()
        if use_coach:
            if verbose:
                print("Pre-loading coach play-by-play data...")
            self.predictor.coach_predictor.preload(season_ids)

        results = []
        
        for season_id in season_ids:
            games = self.get_games_for_season(season_id)
            n_games = len(games)
            skipped = 0

            mode_parts = []
            if use_player_availability:
                mode_parts.append("players")
            if use_referee:
                mode_parts.append("refs")
            if use_coach:
                mode_parts.append("coach")
            if use_streaks:
                mode_parts.append("streaks")
            mode = "Baseline" if not mode_parts else f"Layers: {'+'.join(mode_parts)}"
            
            if verbose:
                print(f"\nBacktesting season {season_id} ({n_games} games) — {mode}...")

            for idx, game in games.iterrows():
                home_inactive = None
                away_inactive = None
                if use_player_availability:
                    home_inactive = self.get_inactive_for_game(
                        game['game_id'], game['team_id_home'])
                    away_inactive = self.get_inactive_for_game(
                        game['game_id'], game['team_id_away'])

                ref_crew = None
                if use_referee:
                    ref_crew = self.get_officials_for_game(game['game_id'])
                    if not ref_crew:
                        ref_crew = None  # no officials data for this game

                pred = self.predictor.predict_game(
                    home_team_id=game['team_id_home'],
                    away_team_id=game['team_id_away'],
                    game_date=game['game_date'],
                    season_id=season_id,
                    home_inactive=home_inactive if use_player_availability else None,
                    away_inactive=away_inactive if use_player_availability else None,
                    ref_crew_ids=ref_crew,
                    use_coach=use_coach,
                    use_streaks=use_streaks,
                )

                if pred is None:
                    skipped += 1
                    continue

                actual_spread = game['pts_away'] - game['pts_home']
                actual_total = game['pts_home'] + game['pts_away']
                actual_margin = game['pts_home'] - game['pts_away']  # positive = home won

                row = {
                    'game_id': game['game_id'],
                    'game_date': game['game_date'],
                    'season_id': season_id,
                    'home_team': game['team_abbreviation_home'],
                    'away_team': game['team_abbreviation_away'],
                    'actual_home_pts': game['pts_home'],
                    'actual_away_pts': game['pts_away'],
                    'actual_spread': actual_spread,
                    'actual_total': actual_total,
                    'actual_margin': actual_margin,
                    'pred_home_pts': pred['pred_home_pts'],
                    'pred_away_pts': pred['pred_away_pts'],
                    'pred_spread': pred['pred_spread'],
                    'pred_total': pred['pred_total'],
                    'spread_error': pred['pred_spread'] - actual_spread,
                    'total_error': pred['pred_total'] - actual_total,
                }

                if use_player_availability:
                    row.update({
                        'adj_home_pts': pred['adj_home_pts'],
                        'adj_away_pts': pred['adj_away_pts'],
                        'adj_spread': pred['adj_spread'],
                        'adj_total': pred['adj_total'],
                        'home_adj': pred['home_adj'],
                        'away_adj': pred['away_adj'],
                        'adj_spread_error': pred['adj_spread'] - actual_spread,
                        'adj_total_error': pred['adj_total'] - actual_total,
                        'n_home_inactive': len(home_inactive) if home_inactive else 0,
                        'n_away_inactive': len(away_inactive) if away_inactive else 0,
                    })

                if use_referee:
                    row.update({
                        'ref_adj_home_pts': pred.get('ref_adj_home_pts', pred['pred_home_pts']),
                        'ref_adj_away_pts': pred.get('ref_adj_away_pts', pred['pred_away_pts']),
                        'ref_adj_spread': pred.get('ref_adj_spread', pred['pred_spread']),
                        'ref_adj_total': pred.get('ref_adj_total', pred['pred_total']),
                        'ref_total_adj': pred.get('ref_total_adj', 0.0),
                        'ref_spread_adj': pred.get('ref_spread_adj', 0.0),
                        'ref_n_refs': pred.get('ref_n_refs', 0),
                        'ref_spread_error': pred.get('ref_adj_spread', pred['pred_spread']) - actual_spread,
                        'ref_total_error': pred.get('ref_adj_total', pred['pred_total']) - actual_total,
                    })

                if use_coach or use_streaks:
                    final_spread = pred.get('final_spread', pred.get('ref_adj_spread', pred['pred_spread']))
                    final_total = pred.get('final_total', pred.get('ref_adj_total', pred['pred_total']))
                    row.update({
                        'final_home_pts': pred.get('final_home_pts', pred['pred_home_pts']),
                        'final_away_pts': pred.get('final_away_pts', pred['pred_away_pts']),
                        'final_spread': final_spread,
                        'final_total': final_total,
                        'coach_spread_adj': pred.get('coach_spread_adj', 0.0),
                        'coach_total_adj': pred.get('coach_total_adj', 0.0),
                        'coach_n_profiles': pred.get('coach_n_profiles', 0),
                        'final_spread_error': final_spread - actual_spread,
                        'final_total_error': final_total - actual_total,
                    })

                if use_streaks:
                    row.update({
                        'home_streak_adj': pred.get('home_streak_adj', 0.0),
                        'away_streak_adj': pred.get('away_streak_adj', 0.0),
                        'home_n_hot': pred.get('home_n_hot', 0),
                        'home_n_cold': pred.get('home_n_cold', 0),
                        'away_n_hot': pred.get('away_n_hot', 0),
                        'away_n_cold': pred.get('away_n_cold', 0),
                        'home_weighted_streak': pred.get('home_weighted_streak', 0.0),
                        'away_weighted_streak': pred.get('away_weighted_streak', 0.0),
                    })

                results.append(row)

                if verbose and (len(results) % 500 == 0):
                    print(f"  Processed {len(results)} games...")

            if verbose:
                print(f"  Season {season_id}: {n_games - skipped}/{n_games} games predicted ({skipped} skipped)")

        return pd.DataFrame(results)

    @staticmethod
    def compute_metrics(results: pd.DataFrame) -> dict:
        """Compute evaluation metrics from backtest results.
        
        Returns dict with MAE, bias, ATS accuracy, and calibration data.
        """
        if results.empty:
            return {}

        # Spread metrics
        spread_errors = results['pred_spread'] - results['actual_spread']
        spread_mae = np.abs(spread_errors).mean()
        spread_bias = spread_errors.mean()

        # Total metrics
        total_errors = results['pred_total'] - results['actual_total']
        total_mae = np.abs(total_errors).mean()
        total_bias = total_errors.mean()

        # Score prediction MAE
        home_mae = np.abs(results['pred_home_pts'] - results['actual_home_pts']).mean()
        away_mae = np.abs(results['pred_away_pts'] - results['actual_away_pts']).mean()

        # ATS-like accuracy: did we correctly predict which team covers?
        # Using predicted spread as our "line", check if actual margin exceeded it
        pred_home_margin = -results['pred_spread']  # convert to home perspective
        actual_home_margin = results['actual_margin']
        # "Covers" = home team beats the predicted spread
        home_covers = (actual_home_margin > pred_home_margin).mean()

        # Win prediction accuracy (did we pick the right winner?)
        pred_winner_home = results['pred_home_pts'] > results['pred_away_pts']
        actual_winner_home = results['actual_home_pts'] > results['actual_away_pts']
        win_accuracy = (pred_winner_home == actual_winner_home).mean()

        # Calibration: bin predicted margins and check actual win rates
        results_cal = results.copy()
        results_cal['pred_home_margin'] = -results_cal['pred_spread']
        results_cal['home_won'] = (results_cal['actual_margin'] > 0).astype(int)
        
        bins = [-np.inf, -10, -5, -2, 0, 2, 5, 10, np.inf]
        labels = ['<-10', '-10 to -5', '-5 to -2', '-2 to 0', '0 to 2', '2 to 5', '5 to 10', '>10']
        results_cal['margin_bin'] = pd.cut(results_cal['pred_home_margin'], bins=bins, labels=labels)
        
        calibration = results_cal.groupby('margin_bin', observed=True).agg(
            home_win_rate=('home_won', 'mean'),
            count=('game_id', 'count'),
            avg_pred_margin=('pred_home_margin', 'mean'),
            avg_actual_margin=('actual_margin', 'mean'),
        ).reset_index()

        return {
            'spread_mae': spread_mae,
            'spread_bias': spread_bias,
            'total_mae': total_mae,
            'total_bias': total_bias,
            'home_pts_mae': home_mae,
            'away_pts_mae': away_mae,
            'win_accuracy': win_accuracy,
            'home_covers_pct': home_covers,
            'total_games': len(results),
            'calibration': calibration,
            'avg_pred_total': results['pred_total'].mean(),
            'avg_actual_total': results['actual_total'].mean(),
            'avg_pred_home': results['pred_home_pts'].mean(),
            'avg_actual_home': results['actual_home_pts'].mean(),
        }

    @staticmethod
    def print_report(metrics: dict, results: pd.DataFrame):
        """Print a formatted evaluation report."""
        print("\n" + "=" * 60)
        print("BASELINE MODEL EVALUATION REPORT")
        print("=" * 60)

        print(f"\nGames evaluated: {metrics['total_games']}")
        
        print(f"\n--- Score Prediction ---")
        print(f"  Avg predicted home pts: {metrics['avg_pred_home']:.1f}")
        print(f"  Avg actual home pts:    {metrics['avg_actual_home']:.1f}")
        print(f"  Home pts MAE:           {metrics['home_pts_mae']:.2f}")
        print(f"  Away pts MAE:           {metrics['away_pts_mae']:.2f}")

        print(f"\n--- Spread Prediction ---")
        print(f"  Spread MAE:  {metrics['spread_mae']:.2f}")
        print(f"  Spread Bias: {metrics['spread_bias']:+.2f}")

        print(f"\n--- Total Prediction ---")
        print(f"  Total MAE:         {metrics['total_mae']:.2f}")
        print(f"  Total Bias:        {metrics['total_bias']:+.2f}")
        print(f"  Avg pred total:    {metrics['avg_pred_total']:.1f}")
        print(f"  Avg actual total:  {metrics['avg_actual_total']:.1f}")

        print(f"\n--- Accuracy ---")
        print(f"  Win prediction accuracy: {metrics['win_accuracy']:.1%}")
        print(f"  Home covers rate:        {metrics['home_covers_pct']:.1%}")

        print(f"\n--- Calibration ---")
        cal = metrics['calibration']
        print(f"  {'Pred Margin Bin':<15} {'Home Win%':>10} {'Avg Pred':>10} {'Avg Actual':>12} {'Count':>6}")
        print("  " + "-" * 55)
        for _, row in cal.iterrows():
            print(f"  {str(row['margin_bin']):<15} {row['home_win_rate']:>10.1%} "
                  f"{row['avg_pred_margin']:>10.1f} {row['avg_actual_margin']:>12.1f} {int(row['count']):>6}")

        # Per-season breakdown
        if 'season_id' in results.columns:
            print(f"\n--- Per-Season Breakdown ---")
            for sid in sorted(results['season_id'].unique()):
                sr = results[results['season_id'] == sid]
                mae = np.abs(sr['spread_error']).mean()  # Use spread_error directly
                total_mae = np.abs(sr['total_error']).mean()
                win_acc = ((sr['pred_home_pts'] > sr['pred_away_pts']) == 
                          (sr['actual_home_pts'] > sr['actual_away_pts'])).mean()
                print(f"  Season {sid[1:]}: Spread MAE={mae:.2f}, Total MAE={total_mae:.2f}, "
                      f"Win%={win_acc:.1%}, Games={len(sr)}")
