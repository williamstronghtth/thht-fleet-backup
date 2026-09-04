"""
betting/bankroll.py — Paper bankroll management with Kelly criterion.

The Kelly criterion tells us the mathematically optimal bet size to maximize
long-term growth while avoiding ruin. For sports betting, we use a
fractional Kelly (typically 1/4 to 1/2 Kelly) because:

1. Our edge estimates have uncertainty
2. Full Kelly is extremely volatile
3. Fractional Kelly has nearly the same growth rate with much less risk

Kelly formula: f* = (bp - q) / b
Where:
    f* = fraction of bankroll to bet
    b  = decimal odds - 1 (net payout per dollar)
    p  = probability of winning (our model's estimate)
    q  = 1 - p (probability of losing)
"""

import json
import logging
import os
from dataclasses import dataclass
from datetime import datetime

import config

logger = logging.getLogger(__name__)


@dataclass
class BankrollState:
    """Current state of the paper bankroll."""
    balance: float = config.DEFAULT_BANKROLL
    initial_balance: float = config.DEFAULT_BANKROLL
    peak_balance: float = config.DEFAULT_BANKROLL
    total_bets: int = 0
    total_won: int = 0
    total_lost: int = 0
    total_pushed: int = 0
    total_wagered: float = 0.0
    total_profit: float = 0.0
    max_drawdown: float = 0.0
    last_updated: str = ""

    @property
    def win_rate(self) -> float:
        decided = self.total_won + self.total_lost
        return self.total_won / decided if decided > 0 else 0.0

    @property
    def roi(self) -> float:
        return self.total_profit / self.total_wagered if self.total_wagered > 0 else 0.0

    @property
    def current_drawdown(self) -> float:
        if self.peak_balance <= 0:
            return 0.0
        return (self.peak_balance - self.balance) / self.peak_balance


class BankrollManager:
    """
    Manage a paper betting bankroll with Kelly criterion sizing.

    Usage:
        mgr = BankrollManager(initial_balance=1000)
        size = mgr.kelly_bet(model_prob=0.55, decimal_odds=2.0)
        mgr.record_bet(amount=size, won=True, profit=size * 1.0)
    """

    def __init__(self, initial_balance: float = config.DEFAULT_BANKROLL,
                 kelly_fraction: float = 0.25,
                 max_bet_pct: float = 0.05,
                 min_edge: float = 0.03):
        """
        Parameters
        ----------
        initial_balance : float
            Starting paper bankroll.
        kelly_fraction : float
            Fraction of full Kelly to use (0.25 = quarter Kelly).
        max_bet_pct : float
            Maximum bet as % of bankroll (safety cap).
        min_edge : float
            Minimum edge required to place a bet.
        """
        self.kelly_fraction = kelly_fraction
        self.max_bet_pct = max_bet_pct
        self.min_edge = min_edge
        self.state = BankrollState(
            balance=initial_balance,
            initial_balance=initial_balance,
            peak_balance=initial_balance,
        )
        self._state_path = os.path.join(config.DATA_DIR, "bankroll_state.json")

    def kelly_bet(self, model_prob: float, decimal_odds: float) -> float:
        """
        Calculate Kelly criterion bet size.

        Parameters
        ----------
        model_prob : float
            Our estimated probability of winning (0-1).
        decimal_odds : float
            Decimal odds offered by the book.

        Returns
        -------
        float
            Recommended bet amount in dollars.
            Returns 0.0 if no edge or negative Kelly.
        """
        b = decimal_odds - 1.0  # net payout per dollar
        p = model_prob
        q = 1.0 - p

        # Check for edge
        edge = p - (1.0 / decimal_odds)  # vs implied prob
        if edge < self.min_edge:
            logger.debug("Edge %.3f below threshold %.3f, no bet", edge, self.min_edge)
            return 0.0

        # Kelly fraction
        kelly = (b * p - q) / b
        if kelly <= 0:
            return 0.0

        # Apply fractional Kelly
        fraction = kelly * self.kelly_fraction

        # Apply max bet cap
        fraction = min(fraction, self.max_bet_pct)

        bet_amount = round(self.state.balance * fraction, 2)

        logger.info("Kelly bet: prob=%.3f, odds=%.2f, edge=%.3f, kelly=%.4f, "
                     "fraction=%.4f, amount=$%.2f",
                     p, decimal_odds, edge, kelly, fraction, bet_amount)

        return bet_amount

    def record_bet(self, amount: float, won: bool | None, profit: float) -> None:
        """
        Record a bet result and update bankroll.

        Parameters
        ----------
        amount : float
            Amount wagered.
        won : bool | None
            True=won, False=lost, None=push.
        profit : float
            Net profit (positive) or loss (negative). Push = 0.
        """
        self.state.total_bets += 1
        self.state.total_wagered += amount
        self.state.balance += profit
        self.state.total_profit += profit

        if won is True:
            self.state.total_won += 1
        elif won is False:
            self.state.total_lost += 1
        else:
            self.state.total_pushed += 1

        # Track peak and drawdown
        if self.state.balance > self.state.peak_balance:
            self.state.peak_balance = self.state.balance

        current_dd = self.state.current_drawdown
        if current_dd > self.state.max_drawdown:
            self.state.max_drawdown = current_dd

        self.state.last_updated = datetime.now().isoformat()
        logger.info("Bet recorded: $%.2f %s, profit=$%.2f, balance=$%.2f",
                     amount, "WON" if won else ("LOST" if won is False else "PUSH"),
                     profit, self.state.balance)

    def save_state(self) -> None:
        """Save bankroll state to disk."""
        os.makedirs(os.path.dirname(self._state_path), exist_ok=True)
        with open(self._state_path, "w") as f:
            json.dump(self.state.__dict__, f, indent=2)
        logger.info("Bankroll state saved to %s", self._state_path)

    def load_state(self) -> None:
        """Load bankroll state from disk."""
        if os.path.exists(self._state_path):
            with open(self._state_path, "r") as f:
                data = json.load(f)
            self.state = BankrollState(**data)
            logger.info("Bankroll state loaded: balance=$%.2f", self.state.balance)
        else:
            logger.info("No saved state found, using defaults")

    def summary(self) -> str:
        """Return a formatted bankroll summary."""
        s = self.state
        return (
            f"=== Paper Bankroll Summary ===\n"
            f"Balance:     ${s.balance:,.2f}\n"
            f"Initial:     ${s.initial_balance:,.2f}\n"
            f"Profit:      ${s.total_profit:+,.2f}\n"
            f"ROI:         {s.roi:.1%}\n"
            f"Record:      {s.total_won}-{s.total_lost}-{s.total_pushed}\n"
            f"Win Rate:    {s.win_rate:.1%}\n"
            f"Total Bets:  {s.total_bets}\n"
            f"Wagered:     ${s.total_wagered:,.2f}\n"
            f"Max DD:      {s.max_drawdown:.1%}\n"
            f"Current DD:  {s.current_drawdown:.1%}\n"
            f"Peak:        ${s.peak_balance:,.2f}\n"
        )
