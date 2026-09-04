"""
Hawkes Process - Order Flow Clustering Analysis
Based on Hawkes (1971) "Spectra of some self-exciting and mutually exciting point processes"

Models how trades cluster in time. High branching ratio = trades cause more trades
(momentum/cascade). Low branching ratio = trades driven by external news.
"""

import numpy as np
from scipy.optimize import minimize
from dataclasses import dataclass
from typing import Optional


@dataclass
class HawkesResult:
    """Results from Hawkes process fitting."""
    mu: float                    # Baseline intensity (trades/sec without excitation)
    alpha: float                 # Excitation parameter
    beta: float                  # Decay rate
    branching_ratio: float       # α/β - fraction of trades caused by other trades
    avg_intensity: float         # Expected average trades/sec
    log_likelihood: float        # Model fit quality
    interpretation: str          # Human-readable assessment
    is_momentum: bool            # True if likely momentum/cascade
    
    def __str__(self):
        status = "⚠️ MOMENTUM" if self.is_momentum else "✅ NEWS-DRIVEN"
        return (
            f"Hawkes Process Analysis [{status}]\n"
            f"  μ (baseline) = {self.mu:.4f} trades/sec\n"
            f"  α (excitation) = {self.alpha:.4f}\n"
            f"  β (decay) = {self.beta:.4f}\n"
            f"  Branching ratio = {self.branching_ratio:.1%}\n"
            f"  → {self.interpretation}"
        )


def _hawkes_log_likelihood(params, event_times, T):
    """
    Negative log-likelihood for univariate Hawkes process.
    Uses O(n) recursive computation.
    """
    mu, alpha, beta = params
    
    # Parameter constraints
    if mu <= 0 or alpha <= 0 or beta <= 0 or alpha >= beta:
        return 1e10
    
    # Sanity bounds to prevent overflow
    if mu > 100 or alpha > 100 or beta > 100:
        return 1e10
    
    n = len(event_times)
    if n == 0:
        return 1e10
    
    # Integral term
    integral_term = mu * T
    
    # Recursive computation of intensity at each event
    R = np.zeros(n)
    for i in range(1, n):
        dt = event_times[i] - event_times[i-1]
        exp_term = np.exp(-beta * dt)
        if np.isfinite(exp_term):
            R[i] = exp_term * (1 + R[i-1])
        else:
            R[i] = 0  # Decay to 0 for very large dt
        # Prevent overflow
        R[i] = min(R[i], 1e10)
    
    # Add contribution from each event to the integral
    exp_terms = np.exp(-beta * (T - event_times))
    exp_terms = np.clip(exp_terms, 0, 1)  # Should be between 0 and 1
    integral_term += (alpha / beta) * np.sum(1 - exp_terms)
    
    # Log intensity at each event time
    intensities = mu + alpha * R
    
    # Avoid log(0) and overflow
    intensities = np.clip(intensities, 1e-10, 1e10)
    log_terms = np.log(intensities)
    
    ll = np.sum(log_terms) - integral_term
    
    # Check for invalid result
    if not np.isfinite(ll):
        return 1e10
    
    return -ll  # Return negative for minimization


def fit_hawkes(
    event_times: np.ndarray,
    T: float,
    n_starts: int = 10,
    momentum_threshold: float = 0.7
) -> HawkesResult:
    """
    Fit a Hawkes process to observed event times via MLE.
    
    Parameters:
    -----------
    event_times : array of trade timestamps (in seconds from start)
    T : total observation window length (seconds)
    n_starts : number of random starting points (non-convex optimization)
    momentum_threshold : branching ratio above this = momentum trading
    
    Returns:
    --------
    HawkesResult with fitted parameters and interpretation
    """
    if len(event_times) < 20:
        return HawkesResult(
            mu=0.0,
            alpha=0.0,
            beta=1.0,
            branching_ratio=0.0,
            avg_intensity=0.0,
            log_likelihood=0.0,
            interpretation="Insufficient data (need 20+ trades)",
            is_momentum=False
        )
    
    # Sort times and normalize to start at 0
    times = np.sort(event_times)
    times = times - times[0]
    T_adj = times[-1] + 1.0  # Observation window
    
    best_result = None
    best_ll = np.inf
    
    # Multiple starting points (landscape is non-convex)
    np.random.seed(42)  # Reproducibility
    for _ in range(n_starts):
        x0 = [
            np.random.uniform(0.1, 2.0),   # mu
            np.random.uniform(0.1, 0.8),   # alpha
            np.random.uniform(1.0, 5.0)    # beta
        ]
        
        try:
            result = minimize(
                _hawkes_log_likelihood,
                x0,
                args=(times, T_adj),
                method='Nelder-Mead',
                options={'xatol': 1e-6, 'fatol': 1e-6, 'maxiter': 5000}
            )
            
            if result.fun < best_ll:
                best_ll = result.fun
                best_result = result
        except Exception:
            continue
    
    if best_result is None:
        return HawkesResult(
            mu=0.0,
            alpha=0.0,
            beta=1.0,
            branching_ratio=0.0,
            avg_intensity=0.0,
            log_likelihood=0.0,
            interpretation="Optimization failed",
            is_momentum=False
        )
    
    mu, alpha, beta = best_result.x
    branching_ratio = alpha / beta
    
    # Ensure stationarity
    if branching_ratio >= 1.0:
        branching_ratio = 0.99
        interpretation = "Warning: near-unstable process (branching ≈ 1)"
        is_momentum = True
    elif branching_ratio > momentum_threshold:
        interpretation = f"{branching_ratio:.0%} of trades caused by prior trades - MOMENTUM/CASCADE"
        is_momentum = True
    elif branching_ratio > 0.5:
        interpretation = f"{branching_ratio:.0%} of trades caused by prior trades - mixed flow"
        is_momentum = False
    else:
        interpretation = f"{branching_ratio:.0%} of trades caused by prior trades - NEWS-DRIVEN"
        is_momentum = False
    
    avg_intensity = mu / (1 - branching_ratio) if branching_ratio < 1 else float('inf')
    
    return HawkesResult(
        mu=mu,
        alpha=alpha,
        beta=beta,
        branching_ratio=branching_ratio,
        avg_intensity=avg_intensity,
        log_likelihood=-best_ll,
        interpretation=interpretation,
        is_momentum=is_momentum
    )
