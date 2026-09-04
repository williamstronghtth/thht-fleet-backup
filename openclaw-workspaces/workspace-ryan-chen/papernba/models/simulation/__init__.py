"""
NBA Game Simulation Engine
===========================

Possession-by-possession game simulator with Monte Carlo analysis.

Modules:
- player_model: Per-possession player tendency profiles
- engine: Core game simulation engine
- monte_carlo: Monte Carlo runner and result aggregation
- predictor: High-level prediction interface
"""

from .player_model import PlayerPossessionModel, PossessionProfile
from .engine import GameSimulator, GameResult
from .monte_carlo import MonteCarloRunner, SimulationResult
from .predictor import SimulationPredictor
