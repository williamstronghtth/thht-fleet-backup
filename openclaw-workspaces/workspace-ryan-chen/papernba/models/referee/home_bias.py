"""
models/referee/home_bias.py — Model referee home-court bias in foul calls.

Home court advantage in the NBA is real and partially explained by referee
bias. Studies show refs call more fouls on the away team, especially in
front of loud home crowds. This effect varies by:

- Individual referee tendencies (some refs are more crowd-influenced)
- Arena/crowd intensity (playoff games amplify this)
- Game context (close games may see more bias than blowouts)
- Era trends (bias has decreased somewhat with replay review)

Modeling this helps predict:
- Free throw attempt differential (home vs away)
- Foul trouble probability by team
- Spread adjustments for home/away games with specific crews
"""

import logging
from dataclasses import dataclass

import pandas as pd

logger = logging.getLogger(__name__)


@dataclass
class HomeBiasProfile:
    """Home-court bias metrics for a single referee."""
    official_id: int = 0
    name: str = ""
    games_officiated: int = 0
    # Foul differential (home fouls - away fouls, per game)
    # Negative = more fouls on away team = home bias
    avg_foul_differential: float = 0.0
    # FTA differential
    avg_fta_differential: float = 0.0  # home FTA - away FTA
    # Win rates
    home_win_pct: float = 0.0
    league_avg_home_win_pct: float = 0.0
    # Context
    close_game_foul_diff: float = 0.0  # bias in games within 5 pts
    blowout_foul_diff: float = 0.0     # bias in games decided by 15+


class HomeBiasModel:
    """
    Model referee home-court bias.

    Usage:
        model = HomeBiasModel()
        model.fit(officials_df, games_df, pbp_df)
        bias = model.predict_bias(crew_ids, venue_info)
    """

    def __init__(self):
        self.profiles: dict[int, HomeBiasProfile] = {}
        self.league_avg_home_bias: float = 0.0

    def fit(self, officials_df: pd.DataFrame, games_df: pd.DataFrame,
            pbp_df: pd.DataFrame) -> int:
        """
        Build home bias profiles for all referees.

        TODO:
        1. Join officials (ref → game) with games (game → home/away teams, score)
        2. For each game, calculate:
           - Fouls called on home team vs away team
           - FTA for home team vs away team
        3. Aggregate per referee:
           - Average foul differential
           - Average FTA differential
           - Home team win % in their games
        4. Split by game context (close vs blowout)
        5. Calculate league averages for baseline comparison
        6. Statistical significance testing (some refs have small samples)

        Parameters
        ----------
        officials_df : pd.DataFrame
            Referee-to-game assignments.
        games_df : pd.DataFrame
            Game results with home/away info.
        pbp_df : pd.DataFrame
            Play-by-play for foul attribution.

        Returns
        -------
        int
            Number of referee profiles built.
        """
        logger.info("Fitting home bias model...")

        # TODO: Implement home bias analysis
        # Challenge: need to identify which fouls are on home vs away players
        # PBP has PLAYER1_TEAM_ID for the fouler

        return len(self.profiles)

    def predict_bias(self, crew_ids: list[int], is_home: bool = True) -> dict:
        """
        Predict foul call bias for a specific crew.

        TODO:
        Returns adjustments for the specified team:
        - foul_adjustment: float (expected extra/fewer fouls)
        - fta_adjustment: float (expected extra/fewer FTA)
        - spread_adjustment: float (points to add/subtract from spread)

        Rule of thumb: each extra FTA ≈ 0.75 points (league avg FT%)
        """
        if not crew_ids:
            return {}

        # TODO: Implement crew bias prediction
        # Average the crew members' bias profiles
        # Adjust direction based on is_home
        # Regress toward league mean

        return {
            "foul_adjustment": 0.0,
            "fta_adjustment": 0.0,
            "spread_adjustment": 0.0,
        }

    def get_most_biased_refs(self, n: int = 10, direction: str = "home") -> list:
        """
        Return the N most home-biased (or away-biased) referees.

        TODO: Sort profiles by foul_differential, return top N.
        Useful for quick crew scouting.
        """
        return []
