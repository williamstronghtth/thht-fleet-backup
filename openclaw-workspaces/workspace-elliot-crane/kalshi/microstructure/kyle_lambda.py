"""
Kyle's Lambda - Price Impact Estimation
Based on Kyle (1985) "Continuous Auctions and Insider Trading"

Lambda measures how much prices move per unit of signed order flow.
High lambda + high R² = informed traders are active.
"""

import numpy as np
from scipy.stats import linregress
from dataclasses import dataclass
from typing import Optional


@dataclass
class KyleLambdaResult:
    """Results from Kyle's lambda estimation."""
    lambda_value: float          # Price impact coefficient
    r_squared: float             # How much variance is explained by flow
    std_error: float             # Standard error of lambda estimate
    p_value: float               # Statistical significance
    n_observations: int          # Number of trades used
    interpretation: str          # Human-readable assessment
    safe_to_trade: bool          # Quick decision flag
    
    def __str__(self):
        status = "✅ SAFE" if self.safe_to_trade else "⚠️ CAUTION"
        return (
            f"Kyle's Lambda Analysis [{status}]\n"
            f"  λ = {self.lambda_value:.6f} (price impact per $ flow)\n"
            f"  R² = {self.r_squared:.4f} (variance explained)\n"
            f"  p-value = {self.p_value:.4f}\n"
            f"  n = {self.n_observations} trades\n"
            f"  → {self.interpretation}"
        )


def estimate_kyle_lambda(
    prices: np.ndarray,
    volumes: np.ndarray,
    signs: np.ndarray,
    informed_r2_threshold: float = 0.15,
    high_lambda_threshold: float = 0.002
) -> KyleLambdaResult:
    """
    Estimate Kyle's lambda via regression: Δp_t = λ * Q_t + ε_t
    
    Parameters:
    -----------
    prices : array of prices [p_0, p_1, ..., p_T]
    volumes : size of each trade (in dollars or contracts)
    signs : +1 (buy/aggressor hit ask) / -1 (sell/aggressor hit bid)
    informed_r2_threshold : R² above this suggests informed trading
    high_lambda_threshold : Lambda above this suggests high impact
    
    Returns:
    --------
    KyleLambdaResult with lambda, R², and interpretation
    """
    if len(prices) < 10:
        return KyleLambdaResult(
            lambda_value=0.0,
            r_squared=0.0,
            std_error=0.0,
            p_value=1.0,
            n_observations=len(prices),
            interpretation="Insufficient data (need 10+ trades)",
            safe_to_trade=False
        )
    
    # Signed order flow
    signed_volume = volumes * signs
    
    # Price changes
    price_changes = np.diff(prices)
    
    # Align arrays (price_changes is one shorter)
    signed_flow = signed_volume[1:]
    
    # Drop zero-change ticks if desired (tied trades)
    mask = price_changes != 0
    if mask.sum() < 5:
        # Not enough non-zero changes, use all data
        mask = np.ones(len(price_changes), dtype=bool)
    
    x = signed_flow[mask]
    y = price_changes[mask]
    
    if len(x) < 5:
        return KyleLambdaResult(
            lambda_value=0.0,
            r_squared=0.0,
            std_error=0.0,
            p_value=1.0,
            n_observations=len(x),
            interpretation="Insufficient non-zero price changes",
            safe_to_trade=False
        )
    
    slope, intercept, r_value, p_value, std_err = linregress(x, y)
    r_squared = r_value ** 2
    
    # Interpretation
    high_r2 = r_squared > informed_r2_threshold
    high_lambda = abs(slope) > high_lambda_threshold
    
    if high_r2 and high_lambda:
        interpretation = "HIGH INFORMED TRADING - price moves strongly correlated with flow"
        safe = False
    elif high_r2:
        interpretation = "ELEVATED - flow explains price moves, possible informed activity"
        safe = False
    elif high_lambda:
        interpretation = "HIGH IMPACT - large price moves per trade, but noisy"
        safe = True  # High impact but random is tradeable with care
    else:
        interpretation = "NORMAL - liquid market, low information asymmetry"
        safe = True
    
    return KyleLambdaResult(
        lambda_value=slope,
        r_squared=r_squared,
        std_error=std_err,
        p_value=p_value,
        n_observations=len(x),
        interpretation=interpretation,
        safe_to_trade=safe
    )


def infer_trade_direction(trade_price: float, bid: float, ask: float) -> int:
    """
    Lee-Ready algorithm: infer trade direction from price vs quotes.
    
    Returns:
    --------
    +1 if buyer-initiated (trade near ask)
    -1 if seller-initiated (trade near bid)
    0 if ambiguous (at midpoint)
    """
    mid = (bid + ask) / 2
    
    if trade_price > mid:
        return 1  # Buyer hit the ask
    elif trade_price < mid:
        return -1  # Seller hit the bid
    else:
        return 0  # At midpoint, ambiguous
