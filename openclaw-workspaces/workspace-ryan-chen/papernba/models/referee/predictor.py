"""
Referee Predictor (Layer 3)
============================

Applies referee crew adjustments to game predictions.
Given a crew of 3 officials, calculates adjustments to:
- Total points (primary signal)
- Spread (slight, via home foul bias)

The adjustments are additive on top of the baseline + player availability.
"""

from typing import List, Optional, Dict
import pandas as pd
from .profile import RefereeProfileModel


class RefereePredictor:
    """Calculate prediction adjustments based on referee crew assignment."""

    # How much of the ref total adjustment to apply (conservative)
    TOTAL_WEIGHT = 0.7
    # How much home foul bias translates to spread adjustment
    # (more fouls on away team → slight home advantage via FTs)
    HOME_BIAS_TO_SPREAD = 0.15

    def __init__(self, db_path: str):
        self.db_path = db_path
        self.profile_model = RefereeProfileModel(db_path)

    def get_adjustment(self, crew_ids: List[int],
                       game_date: pd.Timestamp,
                       season_id: str) -> Dict[str, float]:
        """Calculate referee-based adjustments for a game.
        
        Args:
            crew_ids: List of official_ids for the game's referee crew
            game_date: Date of the game (walk-forward: only uses prior data)
            season_id: Season identifier
            
        Returns:
            dict with:
                total_adj: Adjustment to predicted total (positive = expect higher scoring)
                spread_adj: Adjustment to predicted spread (positive = away team boosted)
                n_refs: Number of refs found in profiles
        """
        if not crew_ids:
            return {'total_adj': 0.0, 'spread_adj': 0.0, 'n_refs': 0}

        crew = self.profile_model.get_crew_adjustment(
            crew_ids, game_date, season_id)

        if crew['n_refs_found'] == 0:
            return {'total_adj': 0.0, 'spread_adj': 0.0, 'n_refs': 0}

        # Total points adjustment (the primary signal)
        total_adj = crew['total_pts_adj'] * self.TOTAL_WEIGHT

        # Spread adjustment from home foul bias
        # Positive home_foul_adj = more fouls on away team = slight home advantage
        # This translates to a small spread adjustment (home team benefits)
        spread_adj = crew['home_foul_adj'] * self.HOME_BIAS_TO_SPREAD

        return {
            'total_adj': round(total_adj, 2),
            'spread_adj': round(spread_adj, 2),
            'n_refs': crew['n_refs_found'],
        }

    def clear_cache(self):
        self.profile_model.clear_cache()
