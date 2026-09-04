"""
models/game/simulator.py — Monte Carlo game simulation engine.

This is the heart of the model. Instead of predicting a single final score,
we simulate thousands of game outcomes to generate probability distributions.

The simulator works at the possession level:
1. Determine who's on the floor (coach rotation model)
2. Determine the lineup quality (player per-possession + chemistry models)
3. Adjust for matchups (player matchup model)
4. Adjust for referee tendencies (foul rates, bias, late-game)
5. Simulate each possession: score, turnover, foul, etc.
6. Track foul accumulation → trigger coach foul trouble decisions
7. Run thousands of times → distribution of outcomes

This gives us:
- Win probability
- Score distribution (for over/under bets)
- Spread distribution (for ATS bets)
- Player prop distributions (for player prop bets)
"""

import logging
from dataclasses import dataclass, field

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)


@dataclass
class GameState:
    """Current state during a game simulation."""
    period: int = 1
    time_remaining: float = 720.0  # seconds in current period
    home_score: int = 0
    away_score: int = 0
    home_fouls: dict = field(default_factory=dict)  # player_id → foul count
    away_fouls: dict = field(default_factory=dict)
    home_timeouts: int = 7
    away_timeouts: int = 7
    home_on_floor: list = field(default_factory=list)
    away_on_floor: list = field(default_factory=list)
    possession: str = "home"  # who has the ball


@dataclass
class SimulationResult:
    """Result of a single game simulation."""
    home_score: int = 0
    away_score: int = 0
    total: int = 0
    spread: int = 0  # home perspective (negative = home favored)
    overtime: bool = False
    home_win: bool = False


@dataclass
class SimulationSummary:
    """Aggregated results from many simulations."""
    n_simulations: int = 0
    home_win_pct: float = 0.0
    avg_home_score: float = 0.0
    avg_away_score: float = 0.0
    avg_total: float = 0.0
    avg_spread: float = 0.0
    median_total: float = 0.0
    std_total: float = 0.0
    overtime_pct: float = 0.0
    # Distribution data for betting
    score_distribution: list = field(default_factory=list)
    spread_distribution: list = field(default_factory=list)


class GameSimulator:
    """
    Monte Carlo NBA game simulator.

    Usage:
        sim = GameSimulator()
        sim.configure(
            home_team_id=..., away_team_id=...,
            rotation_model=..., player_model=...,
            chemistry_model=..., matchup_model=...,
            referee_model=..., crew_ids=[...]
        )
        summary = sim.run(n_simulations=10000)
    """

    def __init__(self, seed: int | None = None):
        self.rng = np.random.default_rng(seed)
        # Models (set via configure())
        self.rotation_model = None
        self.player_model = None
        self.chemistry_model = None
        self.matchup_model = None
        self.referee_model = None
        # Game parameters
        self.home_team_id: int = 0
        self.away_team_id: int = 0
        self.crew_ids: list[int] = []
        # League averages for baseline
        self.league_avg_pace: float = 100.0  # possessions per 48 min
        self.league_avg_off_rating: float = 112.0  # pts per 100 poss

    def configure(self, home_team_id: int, away_team_id: int,
                  crew_ids: list[int] = None,
                  rotation_model=None, player_model=None,
                  chemistry_model=None, matchup_model=None,
                  referee_model=None) -> None:
        """Configure the simulator with team IDs and model references."""
        self.home_team_id = home_team_id
        self.away_team_id = away_team_id
        self.crew_ids = crew_ids or []
        self.rotation_model = rotation_model
        self.player_model = player_model
        self.chemistry_model = chemistry_model
        self.matchup_model = matchup_model
        self.referee_model = referee_model

    def simulate_one(self) -> SimulationResult:
        """
        Simulate a single complete game.

        TODO:
        1. Initialize GameState
        2. For each period (1-4, plus OT if needed):
           a. Determine starting lineup (rotation model)
           b. For each possession:
              - Estimate possession outcome probabilities
              - Draw outcome: 2pt make/miss, 3pt make/miss, FT, turnover
              - Apply referee adjustments (foul probability)
              - Update score, fouls, time
              - Check for substitutions (rotation + foul trouble)
           c. Handle end-of-period scenarios
        3. Handle overtime if tied
        4. Return SimulationResult

        Possession outcome model:
        - Base rates from team offensive/defensive ratings
        - Adjust for current lineup quality (chemistry model)
        - Adjust for matchup (matchup model)
        - Adjust for referee crew (foul rate / bias models)
        - Add noise (this is stochastic simulation)
        """
        state = GameState()

        # TODO: Implement full game simulation loop
        # For now, use simplified score generation

        # Simplified placeholder: draw scores from normal distributions
        # based on team ratings (to be replaced with possession-level sim)
        home_score = int(self.rng.normal(112, 12))
        away_score = int(self.rng.normal(110, 12))

        home_score = max(70, home_score)
        away_score = max(70, away_score)

        overtime = False
        if home_score == away_score:
            # Simple OT resolution
            ot_home = int(self.rng.normal(8, 3))
            ot_away = int(self.rng.normal(8, 3))
            home_score += max(0, ot_home)
            away_score += max(0, ot_away)
            overtime = True
            if home_score == away_score:
                home_score += 1  # force resolution

        return SimulationResult(
            home_score=home_score,
            away_score=away_score,
            total=home_score + away_score,
            spread=away_score - home_score,
            overtime=overtime,
            home_win=home_score > away_score,
        )

    def run(self, n_simulations: int = 10000) -> SimulationSummary:
        """
        Run N simulations and aggregate results.

        Parameters
        ----------
        n_simulations : int
            Number of game simulations to run.

        Returns
        -------
        SimulationSummary
            Aggregated statistics from all simulations.
        """
        logger.info("Running %d simulations: %d vs %d",
                     n_simulations, self.home_team_id, self.away_team_id)

        results = [self.simulate_one() for _ in range(n_simulations)]

        home_scores = [r.home_score for r in results]
        away_scores = [r.away_score for r in results]
        totals = [r.total for r in results]
        spreads = [r.spread for r in results]

        summary = SimulationSummary(
            n_simulations=n_simulations,
            home_win_pct=sum(1 for r in results if r.home_win) / n_simulations,
            avg_home_score=np.mean(home_scores),
            avg_away_score=np.mean(away_scores),
            avg_total=np.mean(totals),
            avg_spread=np.mean(spreads),
            median_total=np.median(totals),
            std_total=np.std(totals),
            overtime_pct=sum(1 for r in results if r.overtime) / n_simulations,
            score_distribution=totals,
            spread_distribution=spreads,
        )

        logger.info("Simulation complete: Home win %.1f%%, Avg total %.1f, Avg spread %.1f",
                     summary.home_win_pct * 100, summary.avg_total, summary.avg_spread)

        return summary

    def probability_over(self, total_line: float, summary: SimulationSummary) -> float:
        """Calculate probability of the game going over a total line."""
        overs = sum(1 for t in summary.score_distribution if t > total_line)
        return overs / len(summary.score_distribution)

    def probability_cover(self, spread_line: float, summary: SimulationSummary) -> float:
        """Calculate probability of the home team covering a spread."""
        covers = sum(1 for s in summary.spread_distribution if s < spread_line)
        return covers / len(summary.spread_distribution)
