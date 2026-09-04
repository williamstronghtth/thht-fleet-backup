"""
analysis/kelly_backtest.py — Kelly Criterion Paper Bankroll Simulation
=======================================================================

Simulates a paper bankroll using fractional Kelly criterion sizing
on games where our model disagrees with the line by 2+ points.

Uses quarter-Kelly to be conservative (full Kelly is too volatile
with uncertain edge estimates).

Starting bankroll: $10,000
Bet criteria: model disagrees with line by 2+ points
Kelly fraction: 0.25 (quarter-Kelly)
"""

import os
import sys
import logging
from dataclasses import dataclass, field
from typing import Optional

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from betting.odds import american_to_decimal, american_to_implied_prob

logger = logging.getLogger(__name__)


@dataclass
class KellyResult:
    """Results from Kelly criterion simulation."""
    starting_bankroll: float = 10000.0
    ending_bankroll: float = 10000.0
    peak_bankroll: float = 10000.0
    trough_bankroll: float = 10000.0
    max_drawdown_pct: float = 0.0
    total_bets: int = 0
    total_won: int = 0
    total_lost: int = 0
    total_pushed: int = 0
    total_wagered: float = 0.0
    total_profit: float = 0.0
    biggest_win: float = 0.0
    biggest_loss: float = 0.0
    biggest_win_game: str = ""
    biggest_loss_game: str = ""
    avg_bet_size: float = 0.0
    bankroll_history: list = field(default_factory=list)
    bet_log: list = field(default_factory=list)


def spread_to_implied_prob(spread_edge: float) -> float:
    """Convert spread edge in points to an implied win probability.
    
    A larger edge = higher probability of covering.
    Based on empirical NFL/NBA data: ~1 point of edge ≈ 2-3% of win probability
    above the 50% baseline.
    
    We use a conservative estimate: 1 point = 2% edge.
    So 2-point edge = 54%, 5-point edge = 60%.
    """
    # Base probability at the spread is ~50%
    # Each point of edge adds ~2% to our win probability
    prob = 0.50 + abs(spread_edge) * 0.02
    # Cap at reasonable bounds
    return min(max(prob, 0.50), 0.75)


def run_kelly_backtest(ats_results: pd.DataFrame,
                       starting_bankroll: float = 10000.0,
                       kelly_fraction: float = 0.25,
                       min_edge_pts: float = 2.0,
                       max_bet_pct: float = 0.05,
                       include_totals: bool = True,
                       verbose: bool = True) -> KellyResult:
    """Simulate a Kelly criterion paper bankroll.
    
    Args:
        ats_results: DataFrame from run_ats_backtest()
        starting_bankroll: Starting paper money
        kelly_fraction: Fraction of full Kelly (0.25 = quarter-Kelly)
        min_edge_pts: Minimum edge in points to place a bet
        max_bet_pct: Maximum bet as % of bankroll (safety cap)
        include_totals: Also bet on totals (not just spreads)
        verbose: Print progress
        
    Returns:
        KellyResult with full simulation details
    """
    result = KellyResult(starting_bankroll=starting_bankroll)
    bankroll = starting_bankroll
    peak = starting_bankroll
    trough = starting_bankroll

    # Sort by game date for chronological simulation
    df = ats_results.sort_values('game_date').copy()

    # Standard odds: -110 both sides → decimal 1.909
    standard_decimal = american_to_decimal(-110)
    b = standard_decimal - 1.0  # net payout per dollar (~0.909)

    history = [{'date': 'start', 'bankroll': bankroll, 'action': 'start'}]
    bet_log = []

    for _, row in df.iterrows():
        bets_this_game = []

        # ── Spread bet ──
        if abs(row.get('spread_edge', 0)) >= min_edge_pts and row.get('spread_result') in ('win', 'loss', 'push'):
            edge_pts = abs(row['spread_edge'])
            win_prob = spread_to_implied_prob(edge_pts)
            q = 1.0 - win_prob

            # Kelly: f* = (b*p - q) / b
            kelly_full = (b * win_prob - q) / b
            if kelly_full > 0:
                fraction = kelly_full * kelly_fraction
                fraction = min(fraction, max_bet_pct)
                bet_amount = round(bankroll * fraction, 2)

                if bet_amount > 0:
                    if row['spread_result'] == 'win':
                        profit = bet_amount * b
                        result.total_won += 1
                    elif row['spread_result'] == 'loss':
                        profit = -bet_amount
                        result.total_lost += 1
                    else:  # push
                        profit = 0.0
                        result.total_pushed += 1

                    bankroll += profit
                    result.total_bets += 1
                    result.total_wagered += bet_amount
                    result.total_profit += profit

                    game_desc = f"{row.get('away_team', '?')}@{row.get('home_team', '?')} {str(row.get('game_date', ''))[:10]}"

                    if profit > result.biggest_win:
                        result.biggest_win = profit
                        result.biggest_win_game = game_desc
                    if profit < result.biggest_loss:
                        result.biggest_loss = profit
                        result.biggest_loss_game = game_desc

                    bet_log.append({
                        'date': row.get('game_date'),
                        'game': game_desc,
                        'type': 'spread',
                        'side': row.get('spread_bet_side', ''),
                        'edge_pts': edge_pts,
                        'win_prob': win_prob,
                        'kelly_full': kelly_full,
                        'fraction': fraction,
                        'bet_amount': bet_amount,
                        'result': row['spread_result'],
                        'profit': profit,
                        'bankroll': bankroll,
                    })

        # ── Total bet ──
        if include_totals and abs(row.get('total_edge', 0)) >= min_edge_pts and row.get('total_result') in ('win', 'loss', 'push'):
            edge_pts = abs(row['total_edge'])
            win_prob = spread_to_implied_prob(edge_pts)
            q = 1.0 - win_prob

            kelly_full = (b * win_prob - q) / b
            if kelly_full > 0:
                fraction = kelly_full * kelly_fraction
                fraction = min(fraction, max_bet_pct)
                bet_amount = round(bankroll * fraction, 2)

                if bet_amount > 0:
                    if row['total_result'] == 'win':
                        profit = bet_amount * b
                        result.total_won += 1
                    elif row['total_result'] == 'loss':
                        profit = -bet_amount
                        result.total_lost += 1
                    else:
                        profit = 0.0
                        result.total_pushed += 1

                    bankroll += profit
                    result.total_bets += 1
                    result.total_wagered += bet_amount
                    result.total_profit += profit

                    game_desc = f"{row.get('away_team', '?')}@{row.get('home_team', '?')} {str(row.get('game_date', ''))[:10]}"

                    if profit > result.biggest_win:
                        result.biggest_win = profit
                        result.biggest_win_game = game_desc
                    if profit < result.biggest_loss:
                        result.biggest_loss = profit
                        result.biggest_loss_game = game_desc

                    bet_log.append({
                        'date': row.get('game_date'),
                        'game': game_desc,
                        'type': 'total',
                        'side': row.get('total_bet_side', ''),
                        'edge_pts': edge_pts,
                        'win_prob': win_prob,
                        'kelly_full': kelly_full,
                        'fraction': fraction,
                        'bet_amount': bet_amount,
                        'result': row['total_result'],
                        'profit': profit,
                        'bankroll': bankroll,
                    })

        # Track bankroll
        if peak < bankroll:
            peak = bankroll
        if bankroll < trough:
            trough = bankroll

        dd = (peak - bankroll) / peak if peak > 0 else 0
        if dd > result.max_drawdown_pct:
            result.max_drawdown_pct = dd

        history.append({
            'date': str(row.get('game_date', ''))[:10],
            'bankroll': round(bankroll, 2),
        })

    result.ending_bankroll = bankroll
    result.peak_bankroll = peak
    result.trough_bankroll = trough
    result.avg_bet_size = result.total_wagered / result.total_bets if result.total_bets > 0 else 0
    result.bankroll_history = history
    result.bet_log = bet_log

    if verbose:
        print(f"\n{'='*60}")
        print(f"KELLY CRITERION SIMULATION")
        print(f"{'='*60}")
        print(f"Starting bankroll:  ${result.starting_bankroll:,.2f}")
        print(f"Ending bankroll:    ${result.ending_bankroll:,.2f}")
        print(f"Total profit:       ${result.total_profit:+,.2f}")
        print(f"ROI:                {result.total_profit / result.total_wagered:.2%}" if result.total_wagered > 0 else "ROI: N/A")
        print(f"Total bets:         {result.total_bets}")
        print(f"Record:             {result.total_won}-{result.total_lost}-{result.total_pushed}")
        print(f"Win rate:           {result.total_won / (result.total_won + result.total_lost):.1%}" if (result.total_won + result.total_lost) > 0 else "Win rate: N/A")
        print(f"Avg bet size:       ${result.avg_bet_size:,.2f}")
        print(f"Total wagered:      ${result.total_wagered:,.2f}")
        print(f"Peak bankroll:      ${result.peak_bankroll:,.2f}")
        print(f"Trough bankroll:    ${result.trough_bankroll:,.2f}")
        print(f"Max drawdown:       {result.max_drawdown_pct:.1%}")
        print(f"Biggest win:        ${result.biggest_win:+,.2f} ({result.biggest_win_game})")
        print(f"Biggest loss:       ${result.biggest_loss:+,.2f} ({result.biggest_loss_game})")
        print(f"{'='*60}")

    return result


if __name__ == '__main__':
    print("Kelly backtest must be run via scripts/evaluate_ats.py")
