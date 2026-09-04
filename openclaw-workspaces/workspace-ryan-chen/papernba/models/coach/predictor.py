"""
Coach Predictor (Layer 4)
==========================

Translates coaching profiles into prediction adjustments:
1. Clutch performance → spread adjustment for predicted-close games
2. Pace management → total adjustment for predicted-close games
3. Rotation depth → not directly predictive (information, not adjustment)

Adjustments are conservative and additive on top of baseline + players + refs.
"""

import pandas as pd
from typing import Optional, Dict, List
from .rotations import RotationAnalyzer
from .decisions import CoachDecisionAnalyzer


class CoachPredictor:
    """Calculate prediction adjustments based on coaching profiles."""

    # How much of the clutch Q4 signal to apply
    # Conservative — the signal is noisy
    CLUTCH_WEIGHT = 0.15

    # How much pace ratio affects total prediction
    # Only applies to games predicted to be close (within 5 pts)
    PACE_WEIGHT = 0.3

    # Threshold: a game must be predicted within this spread
    # for clutch/pace adjustments to apply
    CLOSE_GAME_THRESHOLD = 7.0

    def __init__(self, db_path: str):
        self.db_path = db_path
        self.rotation_analyzer = RotationAnalyzer(db_path)
        self.decision_analyzer = CoachDecisionAnalyzer(db_path)

    def preload(self, season_ids: list):
        """Pre-load all PBP data for given seasons. Call before backtesting."""
        # Expand to include 2 prior seasons for each requested season
        all_seasons = set()
        for sid in season_ids:
            try:
                year = int(sid[1:])
                for y in range(year - 2, year + 1):
                    all_seasons.add(f"2{y}")
            except ValueError:
                all_seasons.add(sid)
        all_seasons = sorted(all_seasons)
        self.rotation_analyzer.preload(all_seasons)
        self.decision_analyzer.preload(all_seasons)

    def get_adjustment(self, home_team_id: str, away_team_id: str,
                       game_date: pd.Timestamp, season_id: str,
                       predicted_spread: float,
                       predicted_total: float) -> Dict[str, float]:
        """Calculate coach-based adjustments for a game prediction.
        
        Args:
            home_team_id: Home team NBA ID
            away_team_id: Away team NBA ID
            game_date: Game date (walk-forward safe)
            season_id: Season identifier
            predicted_spread: Current predicted spread (negative = home favored)
            predicted_total: Current predicted total
            
        Returns:
            dict with spread_adj, total_adj, and diagnostic info
        """
        # Get coaching profiles
        home_decision = self.decision_analyzer.get_decision_profile(
            home_team_id, season_id, game_date)
        away_decision = self.decision_analyzer.get_decision_profile(
            away_team_id, season_id, game_date)

        home_rotation = self.rotation_analyzer.get_rotation_profile(
            home_team_id, season_id, game_date)
        away_rotation = self.rotation_analyzer.get_rotation_profile(
            away_team_id, season_id, game_date)

        spread_adj = 0.0
        total_adj = 0.0
        n_profiles = 0

        # Only apply clutch/pace adjustments for close games
        is_close = abs(predicted_spread) <= self.CLOSE_GAME_THRESHOLD

        if is_close:
            # Clutch performance adjustment
            # If home coach's team overperforms in Q4 close games, nudge spread toward home
            # If away coach's team overperforms, nudge spread toward away
            home_clutch = 0.0
            away_clutch = 0.0

            if home_decision is not None and home_decision.q4_close_games >= 5:
                home_clutch = home_decision.shrunk_q4_margin * self.CLUTCH_WEIGHT
                n_profiles += 1

            if away_decision is not None and away_decision.q4_close_games >= 5:
                away_clutch = away_decision.shrunk_q4_margin * self.CLUTCH_WEIGHT
                n_profiles += 1

            # Spread adjustment: positive clutch = home does better = more negative spread
            # Net effect: home_clutch - away_clutch
            spread_adj = -(home_clutch - away_clutch)

            # Pace management total adjustment
            # If both coaches slow down in close Q4, expect slightly lower total
            home_pace = 1.0
            away_pace = 1.0

            if home_decision is not None and home_decision.q4_close_games >= 5:
                home_pace = home_decision.shrunk_pace_ratio

            if away_decision is not None and away_decision.q4_close_games >= 5:
                away_pace = away_decision.shrunk_pace_ratio

            # Average pace ratio deviation from 1.0
            avg_pace_dev = ((home_pace - 1.0) + (away_pace - 1.0)) / 2
            # Convert to total adjustment (scaled by predicted total and weight)
            total_adj = avg_pace_dev * predicted_total * self.PACE_WEIGHT

        # Cap adjustments to prevent extreme values
        spread_adj = max(-2.0, min(2.0, spread_adj))
        total_adj = max(-3.0, min(3.0, total_adj))

        return {
            'spread_adj': round(spread_adj, 2),
            'total_adj': round(total_adj, 2),
            'n_profiles': n_profiles,
            'is_close_game': is_close,
            'home_rotation_depth': (home_rotation.shrunk_players_used
                                    if home_rotation else None),
            'away_rotation_depth': (away_rotation.shrunk_players_used
                                    if away_rotation else None),
            'home_clutch_q4': (home_decision.shrunk_q4_margin
                               if home_decision else None),
            'away_clutch_q4': (away_decision.shrunk_q4_margin
                               if away_decision else None),
        }

    def clear_cache(self):
        self.rotation_analyzer.clear_cache()
        self.decision_analyzer.clear_cache()
