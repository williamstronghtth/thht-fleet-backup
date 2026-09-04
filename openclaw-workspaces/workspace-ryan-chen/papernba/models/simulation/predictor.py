"""
Simulation Predictor
=====================

High-level interface: given home_team, away_team, date, ref_crew,
inactive_players → run Monte Carlo → return predictions.

The 5 players on the court ARE the offense/defense. No team-level
OffRtg/DefRtg multiplier. Team ratings are only used for pace
and as a fallback when player data is insufficient.
"""

import pandas as pd
import numpy as np
from typing import Optional, List, Dict

from .player_model import PlayerPossessionModel
from .engine import GameConfig
from .monte_carlo import MonteCarloRunner, SimulationResult
from ..team.ratings import TeamRatings
from ..coach.rotations import RotationAnalyzer
from ..referee.profile import RefereeProfileModel


class SimulationPredictor:
    """High-level prediction interface using the game simulator."""

    def __init__(self, db_path: str):
        self.db_path = db_path
        self.player_model = PlayerPossessionModel(db_path)
        self.team_ratings = TeamRatings(db_path)
        self.rotation_analyzer = RotationAnalyzer(db_path)
        self.ref_model = RefereeProfileModel(db_path)

    def predict(self, home_team_id: str, away_team_id: str,
                game_date: pd.Timestamp, season_id: str,
                ref_crew_ids: Optional[List[int]] = None,
                inactive_player_ids: Optional[List[int]] = None,
                n_sims: int = 10000,
                seed: Optional[int] = None) -> SimulationResult:
        """Run a full simulation prediction for a game."""
        before_date = game_date
        inactive_set = set(inactive_player_ids or [])

        # 1. Get player profiles for both teams
        home_profiles = self.player_model.get_team_profiles(int(home_team_id), before_date, top_n=13)
        away_profiles = self.player_model.get_team_profiles(int(away_team_id), before_date, top_n=13)

        if inactive_set:
            home_profiles = [p for p in home_profiles if p.player_id not in inactive_set]
            away_profiles = [p for p in away_profiles if p.player_id not in inactive_set]

            # Backfill if too many players were removed — get deeper roster
            min_roster = 10
            if len(home_profiles) < min_roster:
                deeper = self.player_model.get_team_profiles(int(home_team_id), before_date, top_n=20)
                deeper = [p for p in deeper if p.player_id not in inactive_set
                          and p.player_id not in {pp.player_id for pp in home_profiles}]
                home_profiles.extend(deeper[:min_roster - len(home_profiles)])
            if len(away_profiles) < min_roster:
                deeper = self.player_model.get_team_profiles(int(away_team_id), before_date, top_n=20)
                deeper = [p for p in deeper if p.player_id not in inactive_set
                          and p.player_id not in {pp.player_id for pp in away_profiles}]
                away_profiles.extend(deeper[:min_roster - len(away_profiles)])

        if len(home_profiles) < 5 or len(away_profiles) < 5:
            return self._fallback_prediction(home_team_id, away_team_id,
                                              before_date, season_id, n_sims, seed)

        # 2. Get team pace (only thing we need from team ratings now)
        home_rating = self.team_ratings.get_team_rating_before_date(home_team_id, before_date, season_id)
        away_rating = self.team_ratings.get_team_rating_before_date(away_team_id, before_date, season_id)
        league_avg = self.team_ratings.league_average_before_date(season_id, before_date)

        home_pace = home_rating['pace'] if home_rating else 98.0
        away_pace = away_rating['pace'] if away_rating else 98.0
        league_pace = league_avg['pace'] if league_avg else 98.0

        # 3. Get coach rotation profiles
        home_rotation = self.rotation_analyzer.get_rotation_profile(home_team_id, season_id, before_date)
        away_rotation = self.rotation_analyzer.get_rotation_profile(away_team_id, season_id, before_date)

        # 4. Get ref crew adjustments
        ref_foul_modifier = 1.0
        ref_home_bias = 0.0
        if ref_crew_ids:
            ref_adj = self.ref_model.get_crew_adjustment(ref_crew_ids, before_date, season_id)
            if ref_adj['n_refs_found'] > 0:
                base_pf = 42.0
                ref_foul_modifier = 1.0 + (ref_adj['total_pf_adj'] / base_pf)
                ref_foul_modifier = np.clip(ref_foul_modifier, 0.85, 1.15)
                ref_home_bias = ref_adj['home_foul_adj'] / 200.0
                ref_home_bias = np.clip(ref_home_bias, -0.02, 0.02)

        # 5. Build GameConfig — players ARE the offense, no OffRtg/DefRtg
        config = GameConfig(
            home_roster=home_profiles,
            away_roster=away_profiles,
            ref_foul_modifier=ref_foul_modifier,
            ref_home_bias=ref_home_bias,
            home_pace=home_pace,
            away_pace=away_pace,
            league_avg_pace=league_pace,
            home_players_used=int(home_rotation.shrunk_players_used) if home_rotation else 9,
            away_players_used=int(away_rotation.shrunk_players_used) if away_rotation else 9,
        )

        # 6. Run Monte Carlo
        runner = MonteCarloRunner(config, seed=seed)
        return runner.run(n_sims=n_sims)

    def _fallback_prediction(self, home_team_id: str, away_team_id: str,
                              before_date: pd.Timestamp, season_id: str,
                              n_sims: int, seed: Optional[int]) -> SimulationResult:
        """Fallback when insufficient player data — use default arrays."""
        home_rating = self.team_ratings.get_team_rating_before_date(home_team_id, before_date, season_id)
        away_rating = self.team_ratings.get_team_rating_before_date(away_team_id, before_date, season_id)
        league_avg = self.team_ratings.league_average_before_date(season_id, before_date)

        config = GameConfig(
            home_roster=[],
            away_roster=[],
            home_pace=home_rating['pace'] if home_rating else 98.0,
            away_pace=away_rating['pace'] if away_rating else 98.0,
            league_avg_pace=league_avg['pace'] if league_avg else 98.0,
        )

        runner = MonteCarloRunner(config, seed=seed)
        return runner.run(n_sims=n_sims)

    def predict_game_row(self, game_row: dict, n_sims: int = 1000,
                         seed: Optional[int] = None) -> Dict:
        """Predict from a game row dict (for backtest compatibility)."""
        game_date = pd.Timestamp(game_row['game_date'])
        season_id = str(game_row['season_id'])
        home_id = str(game_row['team_id_home'])
        away_id = str(game_row['team_id_away'])

        ref_crew = self._get_ref_crew(game_row['game_id'])
        inactive = self._get_inactive_players(game_row['game_id'])

        result = self.predict(
            home_team_id=home_id,
            away_team_id=away_id,
            game_date=game_date,
            season_id=season_id,
            ref_crew_ids=ref_crew,
            inactive_player_ids=inactive,
            n_sims=n_sims,
            seed=seed,
        )

        actual_spread = game_row.get('pts_home', 0) - game_row.get('pts_away', 0)

        return {
            'game_id': game_row['game_id'],
            'game_date': game_date,
            'home_team': home_id,
            'away_team': away_id,
            'predicted_spread': result.mean_spread,
            'predicted_total': result.mean_total,
            'home_win_pct': result.home_win_pct,
            'actual_spread': actual_spread,
            'actual_total': game_row.get('pts_home', 0) + game_row.get('pts_away', 0),
            'mean_home_score': result.mean_home_score,
            'mean_away_score': result.mean_away_score,
            'std_spread': result.std_spread,
            'std_total': result.std_total,
            'elapsed_seconds': result.elapsed_seconds,
        }

    def _get_ref_crew(self, game_id: str) -> List[int]:
        import duckdb
        con = duckdb.connect(self.db_path, read_only=True)
        try:
            rows = con.execute("SELECT official_id FROM officials WHERE game_id = ?", [game_id]).fetchall()
            return [int(r[0]) for r in rows]
        except Exception:
            return []
        finally:
            con.close()

    def _get_inactive_players(self, game_id: str) -> List[int]:
        """Get inactive players for a game.
        
        Strategy:
        1. Check inactive_players table (historical data)
        2. If empty, derive from game log (players on roster who got 0 minutes)
        """
        import duckdb
        con = duckdb.connect(self.db_path, read_only=True)
        try:
            # First try the explicit inactive table
            rows = con.execute(
                "SELECT player_id FROM inactive_players WHERE game_id = ?", [game_id]
            ).fetchall()
            if rows:
                return [int(r[0]) for r in rows]

            # Fallback: derive from game log
            # Get all players who played in this game (min > 0)
            played = con.execute("""
                SELECT DISTINCT player_id FROM player_game_log
                WHERE game_id = ? AND min > 0
            """, [game_id]).fetchall()
            played_ids = {int(r[0]) for r in played}

            if not played_ids:
                return []

            # Get the game's teams and date
            game_info = con.execute("""
                SELECT team_id_home, team_id_away, game_date
                FROM game WHERE game_id = ?
            """, [game_id]).fetchone()
            if not game_info:
                return []

            home_id, away_id, game_date = game_info

            # Get the roster: players who played for these teams in the last 60 days
            # (matches get_team_profiles 60-day window)
            roster = con.execute("""
                SELECT DISTINCT player_id FROM player_game_log
                WHERE team_id IN (?, ?) AND min > 0
                AND game_date >= ? - INTERVAL '60 days'
                AND game_date < ?
            """, [home_id, away_id, game_date, game_date]).fetchall()
            roster_ids = {int(r[0]) for r in roster}

            # Inactive = on recent roster but didn't play in this game
            inactive = roster_ids - played_ids
            return list(inactive)
        except Exception:
            return []
        finally:
            con.close()

    def get_todays_inactive(self, team_id: str, game_date: pd.Timestamp) -> List[int]:
        """Get likely inactive players for a future game using injury reports + heuristic.
        
        Strategy:
        1. Check injury_report table for Out/Doubtful players on this team
        2. Fall back to 7-day absence heuristic for anyone else
        3. Return combined list
        """
        import duckdb
        con = duckdb.connect(self.db_path, read_only=True)
        try:
            inactive = set()

            # 1. Check injury_report for Out/Doubtful players on this team
            try:
                injury_rows = con.execute("""
                    SELECT player_id FROM injury_report
                    WHERE team_id = ? AND status IN ('Out', 'Doubtful')
                    AND player_id > 0
                """, [int(team_id)]).fetchall()
                for row in injury_rows:
                    inactive.add(int(row[0]))
            except Exception:
                pass  # Table may not exist yet

            # 2. Heuristic: players who haven't played in 7+ days
            roster = con.execute("""
                SELECT player_id, player_name,
                       MAX(game_date) as last_played,
                       COUNT(*) as games_30d,
                       AVG(min) as avg_min
                FROM player_game_log
                WHERE team_id = ? AND min > 0
                AND game_date >= ? - INTERVAL '30 days'
                AND game_date < ?
                GROUP BY player_id, player_name
            """, [int(team_id), game_date, game_date]).fetchdf()

            if not roster.empty:
                cutoff = game_date - pd.Timedelta(days=7)
                for _, row in roster.iterrows():
                    last_played = pd.Timestamp(row['last_played'])
                    pid = int(row['player_id'])
                    if last_played < cutoff and row['avg_min'] > 10 and pid not in inactive:
                        inactive.add(pid)

            return list(inactive)
        except Exception:
            return []
        finally:
            con.close()

    def clear_cache(self):
        self.player_model.clear_cache()
        self.rotation_analyzer.clear_cache()
        self.ref_model.clear_cache()
