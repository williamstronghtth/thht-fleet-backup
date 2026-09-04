"""
betting/tracker.py — Log bets, track results, calculate ROI.

Maintains a persistent record of all paper bets in JSON format.
Each bet captures the full context: game, prediction, odds, result.
"""

import json
import logging
import os
from dataclasses import dataclass, asdict
from datetime import datetime

import config

logger = logging.getLogger(__name__)

HISTORY_PATH = os.path.join(config.DATA_DIR, "betting", "history.json")


@dataclass
class BetRecord:
    """A single bet record."""
    id: str = ""               # unique identifier
    timestamp: str = ""        # when the bet was placed
    game_id: str = ""
    game_date: str = ""
    home_team: str = ""
    away_team: str = ""
    # Bet details
    bet_type: str = ""         # "spread", "total", "moneyline"
    side: str = ""             # "home", "away", "over", "under"
    line: float = 0.0          # the line/total
    odds_american: int = 0
    odds_decimal: float = 0.0
    # Model info
    model_prob: float = 0.0
    edge: float = 0.0
    confidence: str = ""       # "low", "medium", "high"
    # Sizing
    stake: float = 0.0
    kelly_fraction: float = 0.0
    bankroll_at_bet: float = 0.0
    # Result (filled in after game)
    result: str = "pending"    # "won", "lost", "push", "pending"
    actual_score_home: int | None = None
    actual_score_away: int | None = None
    profit: float = 0.0
    # Notes
    notes: str = ""


class BetTracker:
    """
    Track all paper bets with full context.

    Usage:
        tracker = BetTracker()
        tracker.load()
        bet_id = tracker.place_bet(bet_record)
        tracker.resolve_bet(bet_id, result="won", profit=50.0)
        tracker.save()
        print(tracker.summary())
    """

    def __init__(self):
        self.bets: list[BetRecord] = []
        self._next_id: int = 1

    def load(self) -> None:
        """Load bet history from disk."""
        if os.path.exists(HISTORY_PATH):
            with open(HISTORY_PATH, "r") as f:
                data = json.load(f)
            self.bets = [BetRecord(**b) for b in data.get("bets", [])]
            self._next_id = data.get("next_id", len(self.bets) + 1)
            logger.info("Loaded %d bets from history", len(self.bets))
        else:
            logger.info("No bet history found, starting fresh")

    def save(self) -> None:
        """Save bet history to disk."""
        os.makedirs(os.path.dirname(HISTORY_PATH), exist_ok=True)
        data = {
            "next_id": self._next_id,
            "bets": [asdict(b) for b in self.bets],
            "last_saved": datetime.now().isoformat(),
        }
        with open(HISTORY_PATH, "w") as f:
            json.dump(data, f, indent=2, default=str)
        logger.info("Saved %d bets to history", len(self.bets))

    def place_bet(self, bet: BetRecord) -> str:
        """
        Record a new bet.

        Returns the bet ID.
        """
        bet.id = f"BET-{self._next_id:04d}"
        bet.timestamp = datetime.now().isoformat()
        bet.result = "pending"
        self._next_id += 1
        self.bets.append(bet)
        logger.info("Placed bet %s: %s %s %s @ %+d ($%.2f)",
                     bet.id, bet.bet_type, bet.side, bet.line,
                     bet.odds_american, bet.stake)
        return bet.id

    def resolve_bet(self, bet_id: str, result: str, profit: float,
                    actual_home: int = None, actual_away: int = None) -> None:
        """
        Resolve a pending bet with its result.

        Parameters
        ----------
        bet_id : str
            Bet ID to resolve.
        result : str
            "won", "lost", or "push".
        profit : float
            Net profit (positive) or loss (negative).
        actual_home : int
            Actual home team score.
        actual_away : int
            Actual away team score.
        """
        for bet in self.bets:
            if bet.id == bet_id:
                bet.result = result
                bet.profit = profit
                bet.actual_score_home = actual_home
                bet.actual_score_away = actual_away
                logger.info("Resolved %s: %s, profit=$%.2f", bet_id, result, profit)
                return
        logger.warning("Bet %s not found", bet_id)

    def pending_bets(self) -> list[BetRecord]:
        """Return all unresolved bets."""
        return [b for b in self.bets if b.result == "pending"]

    def resolved_bets(self) -> list[BetRecord]:
        """Return all resolved bets."""
        return [b for b in self.bets if b.result != "pending"]

    def summary(self, bet_type: str = None) -> dict:
        """
        Calculate summary statistics for resolved bets.

        Parameters
        ----------
        bet_type : str, optional
            Filter to specific bet type ("spread", "total", "moneyline").

        Returns
        -------
        dict
            Summary statistics.
        """
        resolved = self.resolved_bets()
        if bet_type:
            resolved = [b for b in resolved if b.bet_type == bet_type]

        if not resolved:
            return {"total_bets": 0}

        won = [b for b in resolved if b.result == "won"]
        lost = [b for b in resolved if b.result == "lost"]
        pushed = [b for b in resolved if b.result == "push"]

        total_wagered = sum(b.stake for b in resolved)
        total_profit = sum(b.profit for b in resolved)

        return {
            "total_bets": len(resolved),
            "won": len(won),
            "lost": len(lost),
            "pushed": len(pushed),
            "win_rate": len(won) / (len(won) + len(lost)) if (len(won) + len(lost)) > 0 else 0.0,
            "total_wagered": total_wagered,
            "total_profit": total_profit,
            "roi": total_profit / total_wagered if total_wagered > 0 else 0.0,
            "avg_odds": sum(b.odds_american for b in resolved) / len(resolved),
            "avg_edge": sum(b.edge for b in resolved) / len(resolved),
            "avg_stake": total_wagered / len(resolved),
            "best_bet": max(resolved, key=lambda b: b.profit).id if resolved else None,
            "worst_bet": min(resolved, key=lambda b: b.profit).id if resolved else None,
        }

    def format_summary(self, bet_type: str = None) -> str:
        """Return a formatted string summary."""
        s = self.summary(bet_type)
        if s["total_bets"] == 0:
            return "No resolved bets yet."

        label = f" ({bet_type})" if bet_type else ""
        return (
            f"=== Bet Tracking Summary{label} ===\n"
            f"Record:      {s['won']}-{s['lost']}-{s['pushed']}\n"
            f"Win Rate:    {s['win_rate']:.1%}\n"
            f"Wagered:     ${s['total_wagered']:,.2f}\n"
            f"Profit:      ${s['total_profit']:+,.2f}\n"
            f"ROI:         {s['roi']:.1%}\n"
            f"Avg Edge:    {s['avg_edge']:.1%}\n"
            f"Avg Stake:   ${s['avg_stake']:.2f}\n"
        )
