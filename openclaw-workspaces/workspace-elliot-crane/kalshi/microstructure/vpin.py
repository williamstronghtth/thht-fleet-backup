"""
VPIN - Volume-synchronized Probability of Informed Trading
Based on Easley et al. (2012) "Flow Toxicity and Liquidity in a High-frequency World"

Measures order flow imbalance. High VPIN = one side dominating = informed traders likely.
"""

import numpy as np
from dataclasses import dataclass
from typing import List, Tuple


@dataclass
class VPINResult:
    """Results from VPIN calculation."""
    vpin: float                  # Current VPIN value (0-1)
    vpin_history: np.ndarray     # VPIN over time buckets
    buy_volume: float            # Total buy volume in window
    sell_volume: float           # Total sell volume in window
    imbalance_direction: str     # "BUY" or "SELL" pressure
    interpretation: str          # Human-readable assessment
    safe_to_trade: bool          # Quick decision flag
    
    def __str__(self):
        status = "✅ SAFE" if self.safe_to_trade else "⚠️ TOXIC"
        return (
            f"VPIN Analysis [{status}]\n"
            f"  VPIN = {self.vpin:.3f}\n"
            f"  Buy volume = ${self.buy_volume:,.0f}\n"
            f"  Sell volume = ${self.sell_volume:,.0f}\n"
            f"  Pressure = {self.imbalance_direction}\n"
            f"  → {self.interpretation}"
        )


def compute_vpin(
    buy_volumes: np.ndarray,
    sell_volumes: np.ndarray,
    bucket_size: int = 50,
    danger_threshold: float = 0.65,
    critical_threshold: float = 0.80
) -> VPINResult:
    """
    Calculate VPIN from buy/sell volume arrays.
    
    VPIN = |V_buy - V_sell| / (V_buy + V_sell)
    
    Parameters:
    -----------
    buy_volumes : array of buy trade sizes
    sell_volumes : array of sell trade sizes
    bucket_size : trades per bucket for rolling calculation
    danger_threshold : VPIN above this = elevated risk
    critical_threshold : VPIN above this = stay out entirely
    
    Returns:
    --------
    VPINResult with current VPIN and interpretation
    """
    if len(buy_volumes) == 0 or len(sell_volumes) == 0:
        return VPINResult(
            vpin=0.0,
            vpin_history=np.array([]),
            buy_volume=0.0,
            sell_volume=0.0,
            imbalance_direction="NEUTRAL",
            interpretation="No trade data available",
            safe_to_trade=False
        )
    
    # Calculate bucketed VPIN
    n_buckets = max(1, min(len(buy_volumes), len(sell_volumes)) // bucket_size)
    vpin_values = []
    
    for i in range(n_buckets):
        start = i * bucket_size
        end = start + bucket_size
        
        V_buy = buy_volumes[start:end].sum() if end <= len(buy_volumes) else buy_volumes[start:].sum()
        V_sell = sell_volumes[start:end].sum() if end <= len(sell_volumes) else sell_volumes[start:].sum()
        V_total = V_buy + V_sell
        
        if V_total > 0:
            vpin = abs(V_buy - V_sell) / V_total
            vpin_values.append(vpin)
    
    vpin_history = np.array(vpin_values) if vpin_values else np.array([0.0])
    
    # Current VPIN (most recent bucket or overall)
    total_buy = float(buy_volumes.sum())
    total_sell = float(sell_volumes.sum())
    total_volume = total_buy + total_sell
    
    if total_volume > 0:
        current_vpin = abs(total_buy - total_sell) / total_volume
    else:
        current_vpin = 0.0
    
    # Direction of imbalance
    if total_buy > total_sell * 1.1:
        direction = "BUY"
    elif total_sell > total_buy * 1.1:
        direction = "SELL"
    else:
        direction = "NEUTRAL"
    
    # Interpretation
    if current_vpin >= critical_threshold:
        interpretation = f"CRITICAL - {current_vpin:.0%} imbalance, likely informed trading. STAY OUT."
        safe = False
    elif current_vpin >= danger_threshold:
        interpretation = f"ELEVATED - {current_vpin:.0%} imbalance, possible informed activity. CAUTION."
        safe = False
    elif current_vpin >= 0.4:
        interpretation = f"MODERATE - {current_vpin:.0%} imbalance, slightly one-sided flow."
        safe = True
    else:
        interpretation = f"HEALTHY - {current_vpin:.0%} imbalance, balanced two-sided flow."
        safe = True
    
    return VPINResult(
        vpin=current_vpin,
        vpin_history=vpin_history,
        buy_volume=total_buy,
        sell_volume=total_sell,
        imbalance_direction=direction,
        interpretation=interpretation,
        safe_to_trade=safe
    )


def compute_vpin_from_trades(
    trades: List[Tuple[float, float, int]],
    bucket_size: int = 50
) -> VPINResult:
    """
    Calculate VPIN from a list of trades.
    
    Parameters:
    -----------
    trades : list of (price, size, direction) where direction is +1 buy, -1 sell
    bucket_size : trades per bucket
    
    Returns:
    --------
    VPINResult
    """
    if not trades:
        return VPINResult(
            vpin=0.0,
            vpin_history=np.array([]),
            buy_volume=0.0,
            sell_volume=0.0,
            imbalance_direction="NEUTRAL",
            interpretation="No trade data available",
            safe_to_trade=False
        )
    
    buy_volumes = []
    sell_volumes = []
    
    for price, size, direction in trades:
        if direction > 0:
            buy_volumes.append(size)
            sell_volumes.append(0)
        else:
            buy_volumes.append(0)
            sell_volumes.append(size)
    
    return compute_vpin(
        np.array(buy_volumes),
        np.array(sell_volumes),
        bucket_size=bucket_size
    )
