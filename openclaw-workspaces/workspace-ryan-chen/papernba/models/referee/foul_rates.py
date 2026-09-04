"""
models/referee/foul_rates.py — Model individual referee foul-calling tendencies.

Referees are among the most underrated factors in NBA modeling. Each ref
has measurably different tendencies for:
- Total fouls called per game (some refs let them play, others are whistle-happy)
- Foul type distribution (shooting fouls, offensive fouls, charges, technicals)
- Impact on pace (more fouls = more free throws = different pace)
- Star treatment (do certain refs give stars more favorable calls?)

A 3-ref crew that averages 45 fouls/game vs one that averages 38 changes
the entire game dynamic — more foul trouble risk, more free throws,
different pace.

Data source: Cross-reference ingestion/referees.py (who reffed which game)
with play-by-play foul events.
"""

import logging
from dataclasses import dataclass

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)


@dataclass
class RefereeFoulProfile:
    """Foul-calling profile for an individual referee."""
    official_id: int = 0
    name: str = ""
    games_officiated: int = 0
    # Per-game averages
    fouls_per_game: float = 0.0
    personal_fouls_pg: float = 0.0
    shooting_fouls_pg: float = 0.0
    offensive_fouls_pg: float = 0.0
    charges_pg: float = 0.0
    flagrant_pg: float = 0.0
    technical_pg: float = 0.0
    # Impact metrics
    fta_per_game: float = 0.0  # free throw attempts (both teams combined)
    pace_impact: float = 0.0   # deviation from league avg pace
    # Comparison to league average
    foul_rate_vs_league: float = 0.0  # +/- relative to league avg


class FoulRateModel:
    """
    Model referee foul-calling tendencies.

    Usage:
        model = FoulRateModel()
        model.fit(officials_df, pbp_fouls_df)
        profile = model.get_profile(official_id=123456)
        crew_impact = model.predict_crew_impact([ref1_id, ref2_id, ref3_id])
    """

    def __init__(self):
        self.profiles: dict[int, RefereeFoulProfile] = {}
        self.league_avg_fouls_pg: float = 0.0

    def fit(self, officials_df: pd.DataFrame, pbp_df: pd.DataFrame) -> int:
        """
        Build foul profiles for all referees.

        TODO:
        1. Join officials_df (game_id → ref assignment) with pbp_df (foul events)
        2. Filter PBP to foul events (EVENTMSGTYPE == 6)
        3. Categorize fouls by type (EVENTMSGACTIONTYPE codes):
           - 1-4: Shooting fouls
           - 5: Offensive foul
           - 26: Charge
           - 6: Loose ball foul
           - 10-11: Flagrant
           - etc.
        4. Aggregate per referee per game, then average
        5. Calculate league averages for comparison
        6. Compute confidence intervals (more games = tighter)

        Parameters
        ----------
        officials_df : pd.DataFrame
            From ingestion/referees.py — game_id to official mapping.
        pbp_df : pd.DataFrame
            Play-by-play data with foul events.

        Returns
        -------
        int
            Number of referee profiles built.
        """
        logger.info("Fitting foul rate model...")

        # TODO: Implement foul rate analysis
        # Key challenge: attributing specific fouls to specific refs
        # (3 refs per game, PBP doesn't say which ref made the call)
        # Solution: Use game-level aggregates per crew, then decompose
        # via ridge regression or similar

        return len(self.profiles)

    def get_profile(self, official_id: int) -> RefereeFoulProfile | None:
        """Get a referee's foul-calling profile."""
        return self.profiles.get(official_id)

    def predict_crew_impact(self, crew_ids: list[int]) -> dict:
        """
        Predict the impact of a 3-referee crew on game dynamics.

        TODO:
        Returns dict with:
        - expected_total_fouls: float
        - expected_fta: float (combined both teams)
        - pace_adjustment: float (multiplier on expected pace)
        - foul_trouble_risk: float (probability a starter gets 4+ fouls)
        - over_under_lean: float (more fouls → more FTA → slightly higher scoring)

        The 3-ref crew effect is roughly: avg(ref1, ref2, ref3) with slight
        regression toward league mean.
        """
        if not crew_ids:
            return {}

        profiles = [self.profiles.get(rid) for rid in crew_ids]
        profiles = [p for p in profiles if p is not None]

        if not profiles:
            logger.warning("No profiles found for crew: %s", crew_ids)
            return {}

        # TODO: Implement crew prediction
        # Average the three refs' tendencies
        # Regress toward league mean (shrinkage based on sample size)
        # Calculate downstream impacts

        return {
            "expected_total_fouls": 0.0,
            "expected_fta": 0.0,
            "pace_adjustment": 1.0,
            "foul_trouble_risk": 0.0,
            "over_under_lean": 0.0,
        }
