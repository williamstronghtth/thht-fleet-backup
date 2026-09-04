"""
models/coach/timeouts.py — Model coach timeout usage patterns.

Timeouts are a coaching signal. When a coach calls a timeout, it often
indicates they see momentum shifting against them, want to set up a
specific play, or need to disrupt the opponent's rhythm.

Modeling timeout patterns helps predict:
- When a coach will slow the game down (affects pace projections)
- End-of-game strategy (advance the ball, final shot design)
- Response to opponent runs (some coaches call early, some late)
- Challenge usage (when do they burn their challenge?)

Features:
- Timeout frequency per quarter
- Response time to opponent runs (points allowed before calling TO)
- Timeout clustering (multiple TOs in short span = desperation?)
- Challenge success rate and timing
- Advance-the-ball usage in final 2 minutes
"""

import logging
from dataclasses import dataclass

import pandas as pd

logger = logging.getLogger(__name__)


@dataclass
class TimeoutProfile:
    """A coach's timeout usage patterns."""
    coach_id: str = ""
    # Average timeouts per game by quarter
    avg_to_q1: float = 0.0
    avg_to_q2: float = 0.0
    avg_to_q3: float = 0.0
    avg_to_q4: float = 0.0
    # How many opponent points in a run before calling TO?
    run_response_threshold: float = 8.0  # e.g., calls TO after ~8-0 run
    # Challenge usage
    challenge_rate: float = 0.0  # challenges per game
    challenge_success_rate: float = 0.0
    avg_challenge_period: float = 3.0  # when they typically challenge
    # Late-game patterns
    advance_ball_rate: float = 0.0  # % of eligible situations


class TimeoutModel:
    """
    Analyze and predict coach timeout usage.

    Usage:
        model = TimeoutModel()
        model.fit(pbp_df, coach_id="...")
        prediction = model.predict_timeout_prob(game_state)
    """

    def __init__(self):
        self.profiles: dict[str, TimeoutProfile] = {}

    def fit(self, pbp_df: pd.DataFrame, coach_id: str) -> TimeoutProfile:
        """
        Analyze PBP data to build timeout usage profile.

        TODO:
        1. Identify timeout events in PBP (EVENTMSGTYPE == 9)
        2. Track timing: which quarter, time remaining, score differential
        3. Detect opponent runs preceding timeouts
           - Look at scoring events in the 2-3 minutes before TO
           - Calculate run magnitude that triggers the call
        4. Identify challenge events (EVENTMSGTYPE == 18 or related)
        5. Analyze late-game timeout strategy
           - Under 2:00 in Q4, does coach advance the ball?
           - Final possession design (TO before inbound?)
        6. Calculate per-quarter frequency
        """
        logger.info("Fitting timeout model for coach %s", coach_id)

        profile = TimeoutProfile(coach_id=coach_id)

        # TODO: Implement timeout analysis from PBP
        # EVENTMSGTYPE 9 = timeout
        # HOMEDESCRIPTION or VISITORDESCRIPTION contains timeout info

        self.profiles[coach_id] = profile
        return profile

    def predict_timeout_prob(self, coach_id: str, game_state: dict) -> float:
        """
        Predict probability of a timeout being called.

        TODO:
        Parameters via game_state:
        - period: int (1-4+)
        - time_remaining: float (seconds in period)
        - score_diff: int (team's perspective, + is leading)
        - opponent_run: int (unanswered points by opponent)
        - timeouts_remaining: int
        - last_timeout_ago: float (minutes since last TO)

        Returns probability 0.0 to 1.0.
        """
        if coach_id not in self.profiles:
            return 0.0

        # TODO: Implement prediction
        # Higher prob when:
        # - opponent_run > threshold
        # - Late in close game
        # - Coming out of TV timeout window
        # Lower prob when:
        # - Team is on a run themselves
        # - Few timeouts remaining (saving them)

        return 0.0

    def pace_impact(self, coach_id: str, period: int) -> float:
        """
        Estimate how much this coach's timeout patterns affect game pace.

        TODO: More timeouts = more stoppages = slightly lower pace.
        Returns adjustment factor (e.g., 0.98 means 2% pace reduction).
        """
        return 1.0
