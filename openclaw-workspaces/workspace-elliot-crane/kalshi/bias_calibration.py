#!/usr/bin/env python3
"""
Bias Calibration Model
Adjusts raw Kalshi prices for documented favorite-longshot bias

Based on:
- CEPR study: 300k+ contracts
- 72M trade analysis

Key finding: 5¢ contracts win only 4.18% of time (not 5%)
"""

import math
from typing import Dict, Tuple, Optional


# Calibration data from CEPR study
# Format: (implied_prob, actual_prob, sample_size)
CALIBRATION_POINTS = [
    (0.05, 0.0418, 50000),   # 5¢ → 4.18% actual
    (0.10, 0.088, 40000),    # 10¢ → ~8.8% actual  
    (0.15, 0.135, 35000),    # 15¢ → ~13.5% actual
    (0.20, 0.178, 30000),    # 20¢ → ~17.8% actual
    (0.25, 0.225, 25000),    # 25¢ → ~22.5% actual
    (0.30, 0.275, 20000),    # 30¢ → ~27.5% actual
    (0.40, 0.385, 15000),    # 40¢ → ~38.5% actual
    (0.50, 0.495, 15000),    # 50¢ → ~49.5% actual (near fair)
    (0.60, 0.615, 15000),    # 60¢ → ~61.5% actual
    (0.70, 0.725, 20000),    # 70¢ → ~72.5% actual
    (0.80, 0.835, 25000),    # 80¢ → ~83.5% actual
    (0.85, 0.885, 30000),    # 85¢ → ~88.5% actual
    (0.90, 0.928, 35000),    # 90¢ → ~92.8% actual
    (0.95, 0.968, 40000),    # 95¢ → ~96.8% actual
]


def interpolate_actual_prob(implied: float) -> float:
    """
    Interpolate actual probability from implied price
    Uses linear interpolation between calibration points
    """
    if implied <= 0:
        return 0.0
    if implied >= 1:
        return 1.0
    
    # Find bracketing points
    lower = None
    upper = None
    
    for i, (p_impl, p_actual, _) in enumerate(CALIBRATION_POINTS):
        if p_impl <= implied:
            lower = (p_impl, p_actual)
        if p_impl >= implied and upper is None:
            upper = (p_impl, p_actual)
            break
    
    if lower is None:
        return CALIBRATION_POINTS[0][1] * (implied / CALIBRATION_POINTS[0][0])
    if upper is None:
        return min(1.0, CALIBRATION_POINTS[-1][1] + (implied - CALIBRATION_POINTS[-1][0]) * 0.8)
    if lower == upper:
        return lower[1]
    
    # Linear interpolation
    ratio = (implied - lower[0]) / (upper[0] - lower[0])
    return lower[1] + ratio * (upper[1] - lower[1])


def calculate_bias(implied: float) -> Dict:
    """
    Calculate bias metrics for a given implied probability
    
    Returns:
        - implied: Raw price/probability
        - actual: Bias-adjusted probability
        - bias: Difference (positive = overpriced, negative = underpriced)
        - bias_pct: Bias as percentage of implied
        - edge_if_short: Edge from shorting (selling YES)
        - edge_if_long: Edge from buying (buying YES)
    """
    actual = interpolate_actual_prob(implied)
    bias = implied - actual
    bias_pct = (bias / implied * 100) if implied > 0 else 0
    
    return {
        'implied': round(implied * 100, 1),
        'actual': round(actual * 100, 1),
        'bias': round(bias * 100, 1),
        'bias_pct': round(bias_pct, 1),
        'edge_if_short': round(bias * 100, 1),  # Positive = good short
        'edge_if_long': round(-bias * 100, 1),  # Negative bias = good long
    }


def get_category_multiplier(category: str) -> float:
    """
    Adjust bias based on category efficiency
    Entertainment/Culture have LARGER bias (multiply)
    Economics have SMALLER bias (reduce)
    """
    multipliers = {
        'entertainment': 1.3,  # 30% more bias
        'culture': 1.3,
        'crypto': 1.2,
        'sports': 1.1,
        'politics': 1.0,  # baseline
        'weather': 1.0,
        'economics': 0.7,  # 30% less bias (more efficient)
        'finance': 0.7,
    }
    return multipliers.get(category.lower(), 1.0)


def calculate_adjusted_edge(
    implied: float,
    my_estimate: float,
    category: str = 'default',
    spread: float = 0.02,
    fee_rate: float = 0.01
) -> Dict:
    """
    Calculate total edge after bias adjustment, spread, and fees
    
    Args:
        implied: Market implied probability (0-1)
        my_estimate: My probability estimate (0-1)  
        category: Market category for bias adjustment
        spread: Bid-ask spread (default 2¢)
        fee_rate: Fee per contract (default 1¢)
    
    Returns:
        Full edge analysis
    """
    # Get base bias
    bias_data = calculate_bias(implied)
    category_mult = get_category_multiplier(category)
    
    # Adjust bias for category
    adjusted_bias = bias_data['bias'] * category_mult
    bias_adjusted_prob = implied - (adjusted_bias / 100)
    
    # Calculate raw edge vs my estimate
    raw_edge = (my_estimate - implied) * 100
    
    # Calculate edge including bias
    total_edge = raw_edge + adjusted_bias
    
    # Calculate costs
    round_trip_cost = (spread + 2 * fee_rate) * 100  # In percentage points
    
    # Net edge after costs
    net_edge = total_edge - round_trip_cost
    
    # Determine position direction
    if my_estimate > bias_adjusted_prob:
        direction = 'LONG'
    else:
        direction = 'SHORT'
    
    # Check if trade is viable
    viable = abs(net_edge) > 3  # Minimum 3 points net edge
    
    return {
        'implied_pct': round(implied * 100, 1),
        'my_estimate_pct': round(my_estimate * 100, 1),
        'bias_adjusted_pct': round(bias_adjusted_prob * 100, 1),
        'category': category,
        'category_multiplier': category_mult,
        'raw_edge': round(raw_edge, 1),
        'bias_edge': round(adjusted_bias, 1),
        'total_edge': round(total_edge, 1),
        'costs': round(round_trip_cost, 1),
        'net_edge': round(net_edge, 1),
        'direction': direction,
        'viable': viable,
    }


def score_opportunity(market_data: Dict) -> Dict:
    """
    Score a market opportunity based on bias exploitation potential
    
    Args:
        market_data: {ticker, yes_bid, yes_ask, category, volume}
    
    Returns:
        Opportunity score and analysis
    """
    yes_bid = market_data.get('yes_bid', 0) / 100
    yes_ask = market_data.get('yes_ask', 0) / 100
    mid = (yes_bid + yes_ask) / 2 if yes_bid and yes_ask else 0
    spread = yes_ask - yes_bid if yes_bid and yes_ask else 0
    category = market_data.get('category', 'default')
    volume = market_data.get('volume', 0)
    
    if mid == 0:
        return {'score': 0, 'reason': 'No price data'}
    
    # Get bias analysis
    bias_data = calculate_bias(mid)
    cat_mult = get_category_multiplier(category)
    
    # Calculate opportunity score (0-100)
    score = 0
    reasons = []
    
    # Favor longshot shorts (high bias)
    if mid < 0.20 and bias_data['bias'] > 0:
        score += 30 + bias_data['bias'] * cat_mult
        reasons.append(f"Longshot short: {bias_data['bias']:.1f}pt bias")
    
    # Favor favorites longs (negative bias / underpriced)
    if mid > 0.80 and bias_data['bias'] < 0:
        score += 20 + abs(bias_data['bias']) * cat_mult
        reasons.append(f"Favorite long: {abs(bias_data['bias']):.1f}pt edge")
    
    # Sweet spot bonus (40-70%)
    if 0.40 <= mid <= 0.70:
        score += 15
        reasons.append("Sweet spot range")
    
    # Category bonus
    if cat_mult > 1.0:
        score += (cat_mult - 1) * 20
        reasons.append(f"High-bias category ({category})")
    
    # Spread penalty
    if spread > 0.05:
        score -= (spread - 0.05) * 100
        reasons.append(f"Wide spread ({spread*100:.0f}¢)")
    
    # Volume bonus (liquidity)
    if volume > 10000:
        score += 10
        reasons.append("High volume")
    elif volume < 1000:
        score -= 10
        reasons.append("Low volume")
    
    return {
        'score': max(0, min(100, score)),
        'bias_data': bias_data,
        'category_multiplier': cat_mult,
        'spread_pct': round(spread * 100, 1),
        'reasons': reasons,
        'recommendation': 'SHORT' if mid < 0.50 and bias_data['bias'] > 0 else 'LONG' if mid > 0.50 and bias_data['bias'] < 0 else 'NEUTRAL',
    }


# Quick test
if __name__ == "__main__":
    print("=== BIAS CALIBRATION MODEL ===\n")
    
    print("Calibration Table:")
    print(f"{'Implied':>8} {'Actual':>8} {'Bias':>8} {'Edge':>8}")
    print("-" * 36)
    for p in [0.05, 0.10, 0.15, 0.20, 0.25, 0.50, 0.75, 0.80, 0.85, 0.90, 0.95]:
        data = calculate_bias(p)
        print(f"{data['implied']:>7.1f}% {data['actual']:>7.1f}% {data['bias']:>+7.1f}% {data['edge_if_short']:>+7.1f}%")
    
    print("\n=== EXAMPLE TRADE ANALYSIS ===")
    result = calculate_adjusted_edge(
        implied=0.15,
        my_estimate=0.10,
        category='entertainment',
        spread=0.02,
        fee_rate=0.01
    )
    for k, v in result.items():
        print(f"  {k}: {v}")
