"""
models/referee/late_game.py — Model referee behavior in late-game situations.

Late-game officiating is different from the rest of the game. Refs tend to
"swallow the whistle" in close games — calling fewer fouls in the final
minutes to avoid deciding the outcome. But this varies by ref.

Key patterns to model:
- Foul rate change in final 5 minutes of close games
- "Letting them play" tendency (which refs do this most?)
- Charge/block call tendencies under pressure
- Impact on game outcomes (does swallowing the whistle favor one team?)
- Replay review tendencies (do they overturn more or less than average?)

This model matters for live/in-game betting and 4th quarter props.
"""

import logging
from dataclasses import dataclass

import pandas as pd

logger = logging.getLogger(__name__)


@dataclass
class LateGameProfile:
    """Referee late-game officiating tendencies."""
    official_id: int = 0
    name: str = ""
    # Close game = within 5 points in final 5 minutes
    close_games_officiated: int = 0
    # Foul rate comparison
    normal_fouls_per_min: float = 0.0
    late_close_fouls_per_min: float = 0.0
    whistle_suppression: float = 0.0  # % decrease in late-game foul rate
    # Specific call types in crunch time
    late_charge_rate: float = 0.0     # charges called per crunch-time game
    late_shooting_foul_rate: float = 0.0
    late_and1_rate: float = 0.0
    # Replay review
    reviews_per_close_game: float = 0.0
    overturn_rate: float = 0.0
    # Outcome impact
    favorite_cover_pct: float = 0.0   # do favorites cover more with this ref?
    overtime_rate: float = 0.0


class LateGameModel:
    """
    Model referee behavior in clutch situations.

    Usage:
        model = LateGameModel()
        model.fit(officials_df, pbp_df, games_df)
        profile = model.get_profile(official_id=123456)
        clutch_adj = model.predict_clutch_impact(crew_ids)
    """

    def __init__(self, close_margin: int = 5, clutch_minutes: float = 5.0):
        self.close_margin = close_margin
        self.clutch_minutes = clutch_minutes
        self.profiles: dict[int, LateGameProfile] = {}

    def fit(self, officials_df: pd.DataFrame, pbp_df: pd.DataFrame,
            games_df: pd.DataFrame) -> int:
        """
        Build late-game profiles for all referees.

        TODO:
        1. Identify "clutch" situations in PBP:
           - Period >= 4 (4th quarter or OT)
           - Time remaining <= clutch_minutes * 60 seconds
           - Score margin <= close_margin
        2. Calculate foul rates during clutch vs non-clutch
        3. Categorize clutch fouls by type
        4. Track replay review events (if identifiable in PBP)
        5. Correlate with game outcomes:
           - Did the favorite cover?
           - Did the game go to OT?
        6. Build statistical profiles with confidence intervals

        Parameters
        ----------
        officials_df : pd.DataFrame
            Referee-to-game assignments.
        pbp_df : pd.DataFrame
            Play-by-play with foul events and timing.
        games_df : pd.DataFrame
            Game results for outcome analysis.

        Returns
        -------
        int
            Number of profiles built.
        """
        logger.info("Fitting late-game model (margin=%d, minutes=%.1f)...",
                     self.close_margin, self.clutch_minutes)

        # TODO: Implement late-game analysis
        # Key PBP fields: PERIOD, PCTIMESTRING, EVENTMSGTYPE, SCORE

        return len(self.profiles)

    def get_profile(self, official_id: int) -> LateGameProfile | None:
        """Get a referee's late-game profile."""
        return self.profiles.get(official_id)

    def predict_clutch_impact(self, crew_ids: list[int]) -> dict:
        """
        Predict how a crew will officiate clutch situations.

        TODO:
        Returns:
        - whistle_suppression: float (how much foul rate drops in crunch time)
        - fta_reduction: float (expected fewer FTA in final 5 min)
        - overtime_probability_adj: float (adjustment to OT probability)
        - favorite_lean: float (slight edge to favorite or underdog?)
        """
        # TODO: Implement crew clutch prediction
        return {
            "whistle_suppression": 0.0,
            "fta_reduction": 0.0,
            "overtime_probability_adj": 0.0,
            "favorite_lean": 0.0,
        }

    def swallow_whistle_ranking(self, n: int = 10) -> list:
        """
        Rank refs by how much they suppress calls in crunch time.

        TODO: Sort by whistle_suppression score, return top N.
        """
        return []
