"""
Almgren-Chriss Optimal Execution
Based on Almgren & Chriss (2001) "Optimal execution of portfolio transactions"

Calculates optimal schedule for executing large orders to minimize
market impact + timing risk.
"""

import numpy as np
from dataclasses import dataclass
from typing import List, Tuple


@dataclass
class AlmgrenChrissParams:
    """Parameters for optimal execution model."""
    total_position: float        # Total position size to execute ($)
    T_hours: float               # Execution horizon (hours)
    N_intervals: int             # Number of execution intervals
    sigma: float                 # Price volatility (per hour)
    eta: float                   # Permanent impact ($ per $ volume)
    gamma: float                 # Temporary impact ($ per $ volume rate)
    risk_aversion: float         # λ: 0=ignore risk, higher=trade faster


@dataclass
class ExecutionSchedule:
    """Results from Almgren-Chriss optimization."""
    times: np.ndarray            # Execution timestamps (hours)
    trade_sizes: np.ndarray      # Size to execute at each time
    remaining: np.ndarray        # Remaining position at each time
    expected_cost: float         # Total expected execution cost ($)
    implementation_shortfall: float  # Cost as % of position
    kappa: float                 # Urgency parameter
    urgency: str                 # Human-readable urgency
    
    def __str__(self):
        lines = [
            f"Almgren-Chriss Execution Schedule",
            f"  Urgency: {self.urgency} (κ = {self.kappa:.4f})",
            f"  Expected cost: ${self.expected_cost:.2f}",
            f"  Implementation shortfall: {self.implementation_shortfall*100:.2f}%",
            f"",
            f"  {'Hour':>6} {'Trade $':>10} {'Remaining $':>12}",
            f"  {'-'*32}"
        ]
        for t, size, rem in zip(self.times, self.trade_sizes, self.remaining):
            lines.append(f"  {t:>6.2f} {size:>10.0f} {rem:>12.0f}")
        return "\n".join(lines)
    
    def to_schedule_list(self) -> List[Tuple[float, float]]:
        """Return list of (hours_from_now, trade_size) tuples."""
        return [(float(t), float(s)) for t, s in zip(self.times, self.trade_sizes)]


def almgren_chriss_schedule(params: AlmgrenChrissParams) -> ExecutionSchedule:
    """
    Compute optimal execution schedule via Almgren-Chriss.
    
    The optimal trajectory minimizes: E[cost] + λ * Var[cost]
    
    Parameters:
    -----------
    params : AlmgrenChrissParams with position size, horizon, impact params
    
    Returns:
    --------
    ExecutionSchedule with times, sizes, and expected costs
    """
    p = params
    
    if p.total_position <= 0:
        return ExecutionSchedule(
            times=np.array([0]),
            trade_sizes=np.array([0]),
            remaining=np.array([0]),
            expected_cost=0.0,
            implementation_shortfall=0.0,
            kappa=0.0,
            urgency="N/A - no position"
        )
    
    tau = p.T_hours / p.N_intervals
    
    # Urgency parameter
    if p.eta <= 0:
        # No permanent impact - trade evenly
        kappa = 0.01
    else:
        kappa_sq = p.risk_aversion * p.sigma**2 / p.eta
        kappa = np.sqrt(max(kappa_sq, 0.0001))
    
    times = np.linspace(0, p.T_hours, p.N_intervals + 1)
    
    # Optimal remaining position at each time
    # X_k = X_0 * sinh(κ(T-t_k)) / sinh(κT)
    sinh_kT = np.sinh(kappa * p.T_hours)
    if sinh_kT < 1e-10:
        # Very low kappa - approximately linear
        remaining = p.total_position * (1 - times / p.T_hours)
    else:
        remaining = p.total_position * np.sinh(kappa * (p.T_hours - times)) / sinh_kT
    
    # Trade sizes (difference in remaining)
    trade_sizes = -np.diff(remaining)
    
    # Expected costs
    if tau > 0:
        temporary_impact = p.gamma * np.sum(trade_sizes**2) / tau
    else:
        temporary_impact = 0
    permanent_impact = 0.5 * p.eta * p.total_position**2
    
    total_cost = temporary_impact + permanent_impact
    implementation_shortfall = total_cost / p.total_position if p.total_position > 0 else 0
    
    # Urgency interpretation
    if kappa > 2:
        urgency = "HIGH - trade fast (front-loaded)"
    elif kappa > 0.5:
        urgency = "MODERATE - balanced execution"
    else:
        urgency = "LOW - trade slowly (spread evenly)"
    
    return ExecutionSchedule(
        times=times[:-1],
        trade_sizes=trade_sizes,
        remaining=remaining[:-1],
        expected_cost=total_cost,
        implementation_shortfall=implementation_shortfall,
        kappa=kappa,
        urgency=urgency
    )


def estimate_impact_params(
    orderbook_depth: float,
    spread: float,
    recent_volatility: float,
    avg_trade_size: float
) -> Tuple[float, float, float]:
    """
    Estimate Almgren-Chriss impact parameters from market data.
    
    Parameters:
    -----------
    orderbook_depth : total $ available within 5% of mid
    spread : bid-ask spread in price units
    recent_volatility : std of price changes (per hour)
    avg_trade_size : average trade size in $
    
    Returns:
    --------
    (eta, gamma, sigma) - permanent impact, temporary impact, volatility
    """
    # Permanent impact: how much does price move permanently per $ traded
    # Approximation: inversely proportional to book depth
    eta = 1.0 / max(orderbook_depth, 1000) if orderbook_depth > 0 else 0.001
    
    # Temporary impact: spread + depth effect
    gamma = spread / (2 * max(avg_trade_size, 10))
    
    sigma = recent_volatility
    
    return eta, gamma, sigma


def quick_schedule(
    position_size: float,
    hours_available: float,
    book_depth: float,
    spread: float,
    volatility: float = 0.02,
    risk_aversion: float = 1e-6
) -> ExecutionSchedule:
    """
    Quick helper to generate execution schedule from basic inputs.
    
    Parameters:
    -----------
    position_size : total $ to execute
    hours_available : time window for execution
    book_depth : $ available in order book
    spread : bid-ask spread
    volatility : price volatility per hour (default 2%)
    risk_aversion : urgency parameter (higher = faster)
    
    Returns:
    --------
    ExecutionSchedule
    """
    # Estimate parameters
    eta, gamma, sigma = estimate_impact_params(
        book_depth, spread, volatility, position_size / 4
    )
    
    # Number of intervals based on position size
    if position_size < 50:
        n_intervals = 1  # Small position, just market order
    elif position_size < 150:
        n_intervals = 3
    elif position_size < 300:
        n_intervals = 5
    else:
        n_intervals = 8
    
    params = AlmgrenChrissParams(
        total_position=position_size,
        T_hours=hours_available,
        N_intervals=n_intervals,
        sigma=sigma,
        eta=eta,
        gamma=gamma,
        risk_aversion=risk_aversion
    )
    
    return almgren_chriss_schedule(params)
