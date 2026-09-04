"""
analysis/reports.py — Generate human-readable reports and visualizations.

Produces reports for:
- Daily predictions (today's picks with reasoning)
- Bet tracking (running P&L, ROI by bet type)
- Model performance (accuracy, calibration, feature importance)
- Backtest results (detailed breakdown)
"""

import logging
import os
from datetime import date, datetime

import pandas as pd

import config
from betting.tracker import BetTracker
from betting.bankroll import BankrollManager

logger = logging.getLogger(__name__)

REPORTS_DIR = os.path.join(config.DATA_DIR, "reports")


def ensure_reports_dir() -> str:
    """Create and return the reports directory."""
    os.makedirs(REPORTS_DIR, exist_ok=True)
    return REPORTS_DIR


def daily_predictions_report(predictions: list, game_date: date = None) -> str:
    """
    Generate a daily predictions report.

    TODO:
    1. Format each game prediction with:
       - Teams, time, venue
       - Model's predicted spread and total
       - Win probability
       - Referee crew (if known) and their impact
       - Key matchup factors
       - Betting signals (if any edge found)
    2. Sort by confidence/edge
    3. Save to reports directory

    Parameters
    ----------
    predictions : list
        List of GamePrediction objects.
    game_date : date
        Date of the games.

    Returns
    -------
    str
        Formatted report text.
    """
    if game_date is None:
        game_date = date.today()

    lines = [
        "=" * 60,
        f"NBA PREDICTIONS — {game_date.strftime('%A, %B %d, %Y')}",
        f"Generated: {datetime.now().strftime('%I:%M %p')}",
        "=" * 60,
        "",
    ]

    if not predictions:
        lines.append("No games found for this date.")
    else:
        for i, pred in enumerate(predictions, 1):
            lines.extend([
                f"--- Game {i} ---",
                f"{pred.away_team} @ {pred.home_team}",
                f"Predicted Score: {pred.predicted_away_score:.0f} - {pred.predicted_home_score:.0f}",
                f"Predicted Total: {pred.predicted_total:.1f}",
                f"Spread: {pred.predicted_spread:+.1f} (home)",
                f"Home Win Prob: {pred.home_win_prob:.1%}",
                f"Confidence: {pred.confidence:.0%}",
                "",
            ])

            if pred.signals:
                lines.append("  SIGNALS:")
                for sig in pred.signals:
                    lines.append(f"    → {sig.get('bet_type', '')} {sig.get('side', '')} "
                                 f"| Edge: {sig.get('edge', 0):.1%} "
                                 f"| {sig.get('confidence', '')}")
                lines.append("")

    report = "\n".join(lines)

    # Save to file
    out_dir = ensure_reports_dir()
    out_path = os.path.join(out_dir, f"predictions_{game_date.isoformat()}.txt")
    with open(out_path, "w") as f:
        f.write(report)
    logger.info("Saved predictions report → %s", out_path)

    return report


def betting_performance_report(tracker: BetTracker,
                               bankroll: BankrollManager) -> str:
    """
    Generate a comprehensive betting performance report.

    TODO:
    1. Overall record and ROI
    2. Breakdown by bet type (spread, total, ML)
    3. Breakdown by confidence level
    4. Streak analysis (current streak, longest W/L streak)
    5. Daily P&L chart (text-based)
    6. Bankroll curve
    7. Edge realized vs predicted
    """
    lines = [
        "=" * 60,
        "BETTING PERFORMANCE REPORT",
        f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        "=" * 60,
        "",
        bankroll.summary(),
        "",
    ]

    # By bet type
    for bt in ["spread", "total", "moneyline"]:
        s = tracker.summary(bet_type=bt)
        if s["total_bets"] > 0:
            lines.append(tracker.format_summary(bet_type=bt))
            lines.append("")

    # Pending bets
    pending = tracker.pending_bets()
    if pending:
        lines.extend([
            f"--- Pending Bets ({len(pending)}) ---",
        ])
        for b in pending:
            lines.append(f"  {b.id}: {b.bet_type} {b.side} {b.line} | "
                         f"${b.stake:.2f} @ {b.odds_american:+d}")
        lines.append("")

    report = "\n".join(lines)

    out_dir = ensure_reports_dir()
    out_path = os.path.join(out_dir, f"performance_{date.today().isoformat()}.txt")
    with open(out_path, "w") as f:
        f.write(report)
    logger.info("Saved performance report → %s", out_path)

    return report


def model_accuracy_report(season: str = "2024-25") -> str:
    """
    Generate a model accuracy report.

    TODO:
    1. Load predictions vs actuals for the season
    2. Calculate metrics:
       - Mean absolute error (MAE) for spread and total
       - Root mean squared error (RMSE)
       - Win probability calibration
       - Brier score
    3. Compare to baseline (e.g., home team always favored by 3)
    4. Feature importance analysis (which model component contributes most)
    """
    lines = [
        "=" * 60,
        f"MODEL ACCURACY REPORT — {season}",
        "=" * 60,
        "",
        "TODO: Implement after sufficient prediction data collected.",
        "",
    ]

    return "\n".join(lines)


def referee_impact_report(season: str = "2024-25") -> str:
    """
    Generate a report on referee impact across the season.

    TODO:
    1. Rank refs by foul rate deviation
    2. Show home bias rankings
    3. Late-game whistle suppression rankings
    4. Impact on over/under outcomes by crew
    5. Most profitable/unprofitable ref crews to bet on
    """
    lines = [
        "=" * 60,
        f"REFEREE IMPACT REPORT — {season}",
        "=" * 60,
        "",
        "TODO: Implement after referee model is trained.",
        "",
    ]

    return "\n".join(lines)
