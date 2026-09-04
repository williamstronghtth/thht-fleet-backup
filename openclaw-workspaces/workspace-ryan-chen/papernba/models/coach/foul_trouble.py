"""
models/coach/foul_trouble.py — Model coach decisions under foul trouble.

How a coach manages foul trouble is a major edge in NBA modeling. When a
star player picks up early fouls, coaches face a dilemma: bench them to
preserve availability for crunch time, or leave them in and risk fouling out.

Key features:
- Threshold for benching (2 fouls in 1st quarter? 3 by halftime?)
- How long do they sit when benched for fouls?
- Replacement quality differential (how much worse is the backup?)
- Impact on team performance (point differential with/without star)
- Historical tendencies by coach (some coaches are aggressive, others conservative)

This model is critical because it directly affects lineup quality predictions.
"""

import logging
from dataclasses import dataclass

import pandas as pd

logger = logging.getLogger(__name__)


@dataclass
class FoulTroubleProfile:
    """A coach's historical foul-trouble management tendencies."""
    coach_id: str = ""
    # At what foul count does the coach typically bench a starter?
    bench_threshold_q1: int = 2  # fouls to trigger bench in Q1
    bench_threshold_q2: int = 3  # fouls to trigger bench in Q2
    bench_threshold_q3: int = 4  # fouls to trigger bench in Q3
    # Average minutes benched when pulled for foul trouble
    avg_bench_duration: float = 6.0
    # Does the coach differentiate by player importance?
    star_bias: float = 0.0  # >0 means stars get more leeway
    # Win rate when star in foul trouble vs normal
    foul_trouble_win_pct: float = 0.0
    normal_win_pct: float = 0.0


class FoulTroubleModel:
    """
    Predict coaching decisions and team impact when players are in foul trouble.

    Usage:
        model = FoulTroubleModel()
        model.fit(pbp_df, games_df, coach_id="...")
        impact = model.predict_impact(player_fouls=3, period=2, coach_id="...")
    """

    def __init__(self):
        self.profiles: dict[str, FoulTroubleProfile] = {}

    def fit(self, pbp_df: pd.DataFrame, games_df: pd.DataFrame,
            coach_id: str) -> FoulTroubleProfile:
        """
        Analyze PBP data to build foul-trouble management profile.

        TODO:
        1. Identify foul events in PBP (EVENTMSGTYPE == 6)
        2. Track which player committed each foul and their cumulative count
        3. Detect subsequent substitution events — did the coach pull them?
        4. Measure time between foul and substitution
        5. Calculate per-quarter bench thresholds
        6. Compare team performance during foul-trouble stints vs normal
        7. Assess star vs role player treatment differences
        """
        logger.info("Fitting foul trouble model for coach %s", coach_id)

        profile = FoulTroubleProfile(coach_id=coach_id)

        # TODO: Implement foul trouble analysis
        # Key PBP columns: EVENTMSGTYPE (6=foul), PLAYER1_ID (fouler),
        # PERIOD, PCTIMESTRING

        self.profiles[coach_id] = profile
        return profile

    def predict_impact(self, player_id: int, foul_count: int,
                       period: int, coach_id: str) -> dict:
        """
        Predict the impact of a player's foul situation.

        TODO: Returns dict with:
        - will_be_benched: bool (probability)
        - expected_bench_minutes: float
        - team_point_differential_impact: float (expected swing)
        - replacement_player_id: int (most likely sub)

        Parameters
        ----------
        player_id : int
            Player in foul trouble.
        foul_count : int
            Current personal fouls.
        period : int
            Current game period (1-4+).
        coach_id : str
            Head coach making the decision.
        """
        if coach_id not in self.profiles:
            logger.warning("No foul trouble profile for coach %s", coach_id)
            return {}

        # TODO: Implement prediction
        # 1. Look up coach threshold for this period
        # 2. Compare foul_count to threshold
        # 3. Estimate bench probability
        # 4. Calculate lineup quality impact

        return {
            "will_be_benched_prob": 0.0,
            "expected_bench_minutes": 0.0,
            "point_differential_impact": 0.0,
        }
