"""
Monte Carlo Runner
===================

Run the game simulator N times and aggregate results.

Collects:
- Mean predicted spread and total
- Standard deviation
- Win probability for each team
- Distribution percentiles
- Cover/over probabilities for any given line
"""

import numpy as np
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Dict, List, Optional

from .engine import GameSimulator, GameConfig, GameResult, PlayerBoxScore


@dataclass
class SimulationResult:
    """Aggregated results from Monte Carlo simulation."""
    n_sims: int = 0

    # Point predictions
    mean_home_score: float = 0.0
    mean_away_score: float = 0.0
    mean_spread: float = 0.0          # home - away (negative = home favored)
    mean_total: float = 0.0

    # Standard deviations
    std_spread: float = 0.0
    std_total: float = 0.0

    # Win probabilities
    home_win_pct: float = 0.5
    away_win_pct: float = 0.5

    # Distribution percentiles
    spread_p10: float = 0.0
    spread_p25: float = 0.0
    spread_p50: float = 0.0
    spread_p75: float = 0.0
    spread_p90: float = 0.0

    total_p10: float = 0.0
    total_p25: float = 0.0
    total_p50: float = 0.0
    total_p75: float = 0.0
    total_p90: float = 0.0

    # Quarter predictions
    mean_home_q1: float = 0.0
    mean_away_q1: float = 0.0
    mean_q1_spread: float = 0.0
    mean_q1_total: float = 0.0
    std_q1_spread: float = 0.0

    # Raw arrays for further analysis
    home_scores: np.ndarray = field(default_factory=lambda: np.array([]))
    away_scores: np.ndarray = field(default_factory=lambda: np.array([]))
    spreads: np.ndarray = field(default_factory=lambda: np.array([]))
    totals: np.ndarray = field(default_factory=lambda: np.array([]))
    q1_home_scores: np.ndarray = field(default_factory=lambda: np.array([]))
    q1_away_scores: np.ndarray = field(default_factory=lambda: np.array([]))

    # Player projections (averaged across sims)
    player_projections: Dict[str, Dict] = field(default_factory=dict)

    # Performance
    elapsed_seconds: float = 0.0

    def cover_probability(self, spread_line: float) -> float:
        """Probability of the home team covering a given spread.

        spread_line: Vegas spread (e.g., -5.5 means home favored by 5.5).
        Returns P(home_score + spread_line > away_score).
        """
        if len(self.spreads) == 0:
            return 0.5
        # Home covers if actual_spread > -spread_line
        # (since spread_line is negative for favorites)
        # Or equivalently: home_score - away_score > -spread_line
        adjusted = self.spreads + spread_line
        return float(np.mean(adjusted > 0))

    def over_probability(self, total_line: float) -> float:
        """Probability of the game going over a given total.

        total_line: Vegas over/under line (e.g., 220.5).
        """
        if len(self.totals) == 0:
            return 0.5
        return float(np.mean(self.totals > total_line))

    def summary(self) -> str:
        """Human-readable summary."""
        lines = [
            f"Monte Carlo Simulation ({self.n_sims:,} sims, {self.elapsed_seconds:.1f}s)",
            f"  Home: {self.mean_home_score:.1f} pts | Away: {self.mean_away_score:.1f} pts",
            f"  Spread: {self.mean_spread:+.1f} (std: {self.std_spread:.1f})",
            f"  Total: {self.mean_total:.1f} (std: {self.std_total:.1f})",
            f"  Home Win%: {self.home_win_pct:.1%} | Away Win%: {self.away_win_pct:.1%}",
            f"  Spread [10-90]: [{self.spread_p10:+.0f}, {self.spread_p90:+.0f}]",
            f"  Total [10-90]: [{self.total_p10:.0f}, {self.total_p90:.0f}]",
        ]
        return '\n'.join(lines)


class MonteCarloRunner:
    """Run Monte Carlo simulations of a game."""

    def __init__(self, config: GameConfig, seed: Optional[int] = None):
        self.config = config
        self.seed = seed

    def run(self, n_sims: int = 10000) -> SimulationResult:
        """Run n_sims simulations and aggregate results.

        Returns SimulationResult with all statistics.
        """
        import time
        t0 = time.time()

        rng = np.random.default_rng(self.seed)

        # Create simulator
        sim = GameSimulator(self.config, rng=rng)

        # Run simulations
        home_scores = np.zeros(n_sims, dtype=np.int32)
        away_scores = np.zeros(n_sims, dtype=np.int32)

        # Player stat accumulators: player_id -> {stat: [values]}
        player_stats_acc = defaultdict(lambda: defaultdict(list))
        player_names = {}
        player_teams = {}

        q1_home = np.zeros(n_sims, dtype=np.int32)
        q1_away = np.zeros(n_sims, dtype=np.int32)

        for i in range(n_sims):
            result = sim.simulate()
            home_scores[i] = result.home_score
            away_scores[i] = result.away_score

            # Capture Q1 scores
            if result.home_q_scores:
                q1_home[i] = result.home_q_scores[0]
            if result.away_q_scores:
                q1_away[i] = result.away_q_scores[0]

            # Accumulate player box scores
            for bs in result.player_box_scores:
                pid = bs.player_id
                player_names[pid] = bs.player_name
                player_teams[pid] = bs.team
                player_stats_acc[pid]['pts'].append(bs.points)
                player_stats_acc[pid]['min'].append(bs.minutes)
                player_stats_acc[pid]['fg2a'].append(bs.fg2a)
                player_stats_acc[pid]['fg2m'].append(bs.fg2m)
                player_stats_acc[pid]['fg3a'].append(bs.fg3a)
                player_stats_acc[pid]['fg3m'].append(bs.fg3m)
                player_stats_acc[pid]['fta'].append(bs.fta)
                player_stats_acc[pid]['ftm'].append(bs.ftm)
                player_stats_acc[pid]['tov'].append(bs.turnovers)
                player_stats_acc[pid]['fouls'].append(bs.fouls)
                player_stats_acc[pid]['oreb'].append(bs.oreb)
                player_stats_acc[pid]['dreb'].append(bs.dreb)
                player_stats_acc[pid]['ast'].append(bs.assists)
                player_stats_acc[pid]['stl'].append(bs.steals)
                player_stats_acc[pid]['blk'].append(bs.blocks)

        # Average player stats
        player_projections = {}
        for pid, stats in player_stats_acc.items():
            proj = {'player_id': pid, 'player_name': player_names[pid], 'team': player_teams[pid]}
            for stat, vals in stats.items():
                proj[stat] = round(float(np.mean(vals)), 1)
            proj['fga'] = round(proj.get('fg2a', 0) + proj.get('fg3a', 0), 1)
            proj['fgm'] = round(proj.get('fg2m', 0) + proj.get('fg3m', 0), 1)
            proj['reb'] = round(proj.get('oreb', 0) + proj.get('dreb', 0), 1)
            player_projections[pid] = proj

        spreads = home_scores.astype(np.float64) - away_scores.astype(np.float64)
        totals = home_scores.astype(np.float64) + away_scores.astype(np.float64)

        elapsed = time.time() - t0

        sim_result = SimulationResult(
            n_sims=n_sims,
            mean_home_score=float(np.mean(home_scores)),
            mean_away_score=float(np.mean(away_scores)),
            mean_spread=float(np.mean(spreads)),
            mean_total=float(np.mean(totals)),
            std_spread=float(np.std(spreads)),
            std_total=float(np.std(totals)),
            home_win_pct=float(np.mean(home_scores > away_scores)),
            away_win_pct=float(np.mean(away_scores > home_scores)),
            spread_p10=float(np.percentile(spreads, 10)),
            spread_p25=float(np.percentile(spreads, 25)),
            spread_p50=float(np.percentile(spreads, 50)),
            spread_p75=float(np.percentile(spreads, 75)),
            spread_p90=float(np.percentile(spreads, 90)),
            total_p10=float(np.percentile(totals, 10)),
            total_p25=float(np.percentile(totals, 25)),
            total_p50=float(np.percentile(totals, 50)),
            total_p75=float(np.percentile(totals, 75)),
            total_p90=float(np.percentile(totals, 90)),
            mean_home_q1=float(np.mean(q1_home)),
            mean_away_q1=float(np.mean(q1_away)),
            mean_q1_spread=float(np.mean(q1_home.astype(np.float64) - q1_away.astype(np.float64))),
            mean_q1_total=float(np.mean(q1_home.astype(np.float64) + q1_away.astype(np.float64))),
            std_q1_spread=float(np.std(q1_home.astype(np.float64) - q1_away.astype(np.float64))),
            home_scores=home_scores,
            away_scores=away_scores,
            spreads=spreads,
            totals=totals,
            q1_home_scores=q1_home,
            q1_away_scores=q1_away,
            player_projections=player_projections,
            elapsed_seconds=elapsed,
        )

        return sim_result
