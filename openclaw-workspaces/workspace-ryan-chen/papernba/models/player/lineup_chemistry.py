"""
models/player/lineup_chemistry.py — Model how player combinations perform together.

The NBA is fundamentally a chemistry sport. Some player pairings produce
results far better (or worse) than you'd predict by summing their individual
stats. This model captures those nonlinear interactions.

Key concepts:
- Pairwise synergy: Does Player A + Player B produce more than expected?
- Lineup net rating: Actual +/- per 100 possessions vs predicted from individuals
- Role complementarity: Floor spacers + drivers, rim protectors + perimeter D
- Minutes overlap: How often do these players actually share the floor?
- New lineup risk: Lineups with <50 minutes together have high variance

This is one of our biggest edges — most models treat players independently.
"""

import logging
from dataclasses import dataclass, field

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)


@dataclass
class PairSynergy:
    """Performance of a specific two-player combination."""
    player_a: int = 0
    player_b: int = 0
    minutes_together: float = 0.0
    net_rating_together: float = 0.0
    net_rating_apart_a: float = 0.0  # A's net rating without B
    net_rating_apart_b: float = 0.0  # B's net rating without A
    synergy_score: float = 0.0       # actual - expected


@dataclass
class LineupProfile:
    """Stats for a specific 5-man lineup."""
    player_ids: tuple = ()
    minutes: float = 0.0
    off_rating: float = 0.0
    def_rating: float = 0.0
    net_rating: float = 0.0
    predicted_net_rating: float = 0.0  # from individual stats
    chemistry_bonus: float = 0.0       # actual - predicted
    sample_confidence: float = 0.0     # 0-1 based on minutes


class LineupChemistryModel:
    """
    Model nonlinear interactions between player combinations.

    Usage:
        model = LineupChemistryModel()
        model.fit(lineup_df, player_profiles)
        bonus = model.predict_chemistry(lineup=[203999, 201566, ...])
    """

    def __init__(self, min_minutes: float = 50.0):
        self.min_minutes = min_minutes  # minimum minutes for reliable estimate
        self.pair_synergies: dict[tuple, PairSynergy] = {}
        self.lineup_profiles: dict[tuple, LineupProfile] = {}

    def fit(self, lineup_df: pd.DataFrame, player_profiles: dict) -> None:
        """
        Build chemistry model from lineup data.

        TODO:
        1. Parse lineup_df (from ingestion/lineups.py) — each row is a 5-man unit
        2. Calculate expected net rating from sum of individual player profiles
        3. Compare to actual net rating → chemistry_bonus
        4. Extract all pairwise combinations and compute pair synergies
        5. Weight by minutes (more minutes = higher confidence)
        6. Flag lineups with < min_minutes as high-variance

        Parameters
        ----------
        lineup_df : pd.DataFrame
            Season lineup data from ingestion/lineups.py.
        player_profiles : dict
            {player_id: PlayerPossessionProfile} from per_possession model.
        """
        logger.info("Fitting lineup chemistry model on %d lineups", len(lineup_df))

        # TODO: Implement chemistry analysis
        # Key: GROUP_ID in lineup data encodes the 5 player IDs
        # Parse that into individual player IDs
        # Then compare actual vs predicted performance

    def predict_chemistry(self, lineup: list[int]) -> float:
        """
        Predict chemistry bonus for a specific 5-man lineup.

        TODO:
        1. Check if exact lineup exists in history → use directly
        2. If not, estimate from pairwise synergies:
           - Sum all C(5,2)=10 pair synergies
           - Scale by confidence factor
        3. Apply uncertainty penalty for novel combinations

        Returns net rating adjustment (positive = better than expected).
        """
        lineup_key = tuple(sorted(lineup))

        if lineup_key in self.lineup_profiles:
            profile = self.lineup_profiles[lineup_key]
            if profile.minutes >= self.min_minutes:
                return profile.chemistry_bonus

        # TODO: Estimate from pairwise synergies
        # Sum pair synergies, apply confidence weighting
        return 0.0

    def best_lineups(self, team_id: int, n: int = 5) -> list[LineupProfile]:
        """
        Return the top N lineups for a team by net rating.

        TODO: Filter to lineups with sufficient minutes for reliability.
        """
        # TODO: Filter and sort lineup_profiles
        return []

    def replacement_impact(self, current_lineup: list[int],
                           player_out: int, player_in: int) -> float:
        """
        Estimate the net rating impact of swapping one player.

        This is critical for injury/foul trouble analysis.
        Change = individual skill delta + chemistry delta.

        TODO:
        1. Get individual rating difference (in vs out)
        2. Recalculate pair synergies with new player
        3. Return total estimated impact
        """
        return 0.0
