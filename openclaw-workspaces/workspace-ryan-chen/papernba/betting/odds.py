"""
betting/odds.py — Odds conversion and edge/EV calculation.

Handles the math behind sports betting:
- American ↔ decimal ↔ implied probability conversions
- Edge calculation (model probability vs market implied probability)
- Expected value (EV) calculation
- Vig/juice estimation and fair odds extraction

Understanding odds formats:
- American: +150 means win $150 on $100 bet; -150 means bet $150 to win $100
- Decimal: 2.50 means total return of $2.50 per $1 bet (includes stake)
- Implied probability: what % chance the odds imply (includes vig)
"""

import logging

logger = logging.getLogger(__name__)


def american_to_decimal(american: int | float) -> float:
    """
    Convert American odds to decimal.

    Examples:
        +150 → 2.50
        -150 → 1.667
        +100 → 2.00
        -110 → 1.909
    """
    if american > 0:
        return 1.0 + (american / 100.0)
    elif american < 0:
        return 1.0 + (100.0 / abs(american))
    else:
        return 2.0  # even money


def decimal_to_american(decimal_odds: float) -> int:
    """
    Convert decimal odds to American.

    Examples:
        2.50 → +150
        1.667 → -150
        2.00 → +100
    """
    if decimal_odds >= 2.0:
        return round((decimal_odds - 1.0) * 100)
    elif decimal_odds > 1.0:
        return round(-100.0 / (decimal_odds - 1.0))
    else:
        raise ValueError(f"Invalid decimal odds: {decimal_odds} (must be > 1.0)")


def american_to_implied_prob(american: int | float) -> float:
    """
    Convert American odds to implied probability.

    NOTE: This includes the vig/juice. To get the "true" no-vig probability,
    use remove_vig() on both sides of a market.

    Examples:
        -110 → 0.5238 (52.38%)
        +150 → 0.4000 (40.00%)
        -200 → 0.6667 (66.67%)
    """
    if american < 0:
        return abs(american) / (abs(american) + 100.0)
    elif american > 0:
        return 100.0 / (american + 100.0)
    else:
        return 0.5


def decimal_to_implied_prob(decimal_odds: float) -> float:
    """Convert decimal odds to implied probability."""
    if decimal_odds <= 0:
        raise ValueError(f"Invalid decimal odds: {decimal_odds}")
    return 1.0 / decimal_odds


def remove_vig(prob_a: float, prob_b: float) -> tuple[float, float]:
    """
    Remove the vig/juice from a two-way market.

    Sportsbooks set odds so implied probabilities sum to >100%.
    The excess is the vig (their profit margin).

    This normalizes the probabilities to sum to exactly 100%.

    Parameters
    ----------
    prob_a : float
        Implied probability for side A (e.g., home team).
    prob_b : float
        Implied probability for side B (e.g., away team).

    Returns
    -------
    tuple[float, float]
        Fair (no-vig) probabilities for (side_a, side_b).

    Example:
        Home -110 → 0.5238, Away -110 → 0.5238
        Sum = 1.0476 (4.76% vig)
        Fair: (0.5, 0.5)
    """
    total = prob_a + prob_b
    if total <= 0:
        raise ValueError("Probabilities must be positive")
    return (prob_a / total, prob_b / total)


def calculate_vig(american_a: int | float, american_b: int | float) -> float:
    """
    Calculate the vig/juice percentage for a two-way market.

    Returns the overround as a percentage (e.g., 4.76 for standard -110/-110).
    """
    prob_a = american_to_implied_prob(american_a)
    prob_b = american_to_implied_prob(american_b)
    return (prob_a + prob_b - 1.0) * 100


def calculate_edge(model_prob: float, market_odds_american: int | float) -> float:
    """
    Calculate our edge: model probability minus market implied probability.

    A positive edge means our model thinks the bet is underpriced by the market.

    Parameters
    ----------
    model_prob : float
        Our model's estimated probability (0-1).
    market_odds_american : int | float
        The market odds in American format.

    Returns
    -------
    float
        Edge as a decimal (e.g., 0.05 = 5% edge).

    Example:
        Model thinks home team wins 55% of the time.
        Market has home team at -110 (implied 52.38%).
        Edge = 0.55 - 0.5238 = 0.0262 (2.62% edge)
    """
    implied = american_to_implied_prob(market_odds_american)
    return model_prob - implied


def calculate_ev(model_prob: float, decimal_odds: float, stake: float = 1.0) -> float:
    """
    Calculate expected value of a bet.

    EV = (probability of winning * profit) - (probability of losing * stake)

    Parameters
    ----------
    model_prob : float
        Our estimated probability of winning.
    decimal_odds : float
        Decimal odds offered.
    stake : float
        Amount wagered.

    Returns
    -------
    float
        Expected value in dollars. Positive = profitable long-term.

    Example:
        55% chance at decimal 2.0 ($1 bet):
        EV = (0.55 * 1.0) - (0.45 * 1.0) = +$0.10
    """
    profit = stake * (decimal_odds - 1.0)
    return (model_prob * profit) - ((1.0 - model_prob) * stake)


def calculate_ev_american(model_prob: float, american_odds: int | float,
                          stake: float = 1.0) -> float:
    """Calculate EV using American odds (convenience wrapper)."""
    decimal = american_to_decimal(american_odds)
    return calculate_ev(model_prob, decimal, stake)


def minimum_edge_threshold(vig_pct: float = 4.76) -> float:
    """
    Suggest minimum edge threshold to overcome the vig.

    Rule of thumb: need at least vig/2 edge to be profitable after juice.
    In practice, we want a buffer above that.

    Parameters
    ----------
    vig_pct : float
        Market vig as percentage.

    Returns
    -------
    float
        Suggested minimum edge as decimal.
    """
    # Need to overcome half the vig plus a safety margin
    min_edge = (vig_pct / 100.0) / 2.0
    safety_margin = 0.02  # 2% extra buffer
    return min_edge + safety_margin
