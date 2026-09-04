#!/usr/bin/env python3
"""
Weekly Performance Report — Oliver Kensington
Runs every Monday (prior week review) and Friday (week-to-date review).
Reads TRADES.csv, computes stats, sends to Telegram.
"""

import csv
import os
import sys
import subprocess
from datetime import datetime, timedelta, date
from collections import defaultdict

# ─── Config ──────────────────────────────────────────────────────────────────

WORKSPACE = "/root/agents/oliver-kensington/workspace"
TRADES_FILE = f"{WORKSPACE}/TRADES.csv"
TELEGRAM_BOT_TOKEN = "<REDACTED:TELEGRAM_BOT_TOKEN>"
TELEGRAM_CHAT_ID = "8560812913"

# ─── Helpers ─────────────────────────────────────────────────────────────────

def send_telegram(message: str) -> None:
    """Send message via Telegram bot."""
    cmd = [
        "curl", "-s", "-X", "POST",
        f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage",
        "-d", f"chat_id={TELEGRAM_CHAT_ID}",
        "-d", f"text={message}",
        "-d", "parse_mode=HTML"
    ]
    subprocess.run(cmd, capture_output=True)


def get_week_range(target_date: date) -> tuple[date, date]:
    """Return Monday–Sunday of the week containing target_date."""
    monday = target_date - timedelta(days=target_date.weekday())
    sunday = monday + timedelta(days=6)
    return monday, sunday


def load_trades(start: date, end: date) -> list[dict]:
    """Load trades from CSV within date range (inclusive)."""
    trades = []
    if not os.path.exists(TRADES_FILE):
        return trades

    with open(TRADES_FILE, "r") as f:
        for line in f:
            line = line.strip()
            # Skip comments and header
            if not line or line.startswith("#") or line.startswith("date"):
                continue
            try:
                parts = line.split(",", 14)  # 15 fields max
                if len(parts) < 11:
                    continue
                trade_date = datetime.strptime(parts[0], "%Y-%m-%d").date()
                if start <= trade_date <= end:
                    trades.append({
                        "date": trade_date,
                        "ticker": parts[1].strip(),
                        "direction": parts[2].strip(),
                        "strategy": parts[3].strip(),
                        "entry_price": float(parts[4]) if parts[4] else 0,
                        "exit_price": float(parts[5]) if parts[5] else 0,
                        "shares": int(parts[6]) if parts[6] else 0,
                        "entry_time": parts[7].strip(),
                        "exit_time": parts[8].strip(),
                        "confidence_pct": int(parts[9]) if parts[9] else 0,
                        "pnl_usd": float(parts[10].replace("P-", "-").replace("P", "")) if parts[10] else 0,
                        "r_multiple": float(parts[11]) if len(parts) > 11 and parts[11] else 0,
                        "thesis_correct": parts[12].strip() if len(parts) > 12 else "",
                        "ignored_contrary": parts[13].strip() if len(parts) > 13 else "",
                        "notes": parts[14].strip() if len(parts) > 14 else "",
                    })
            except (ValueError, IndexError):
                continue

    return trades


def compute_stats(trades: list[dict]) -> dict:
    """Compute performance statistics from a list of trades."""
    if not trades:
        return {}

    total = len(trades)
    wins = [t for t in trades if t["pnl_usd"] > 0]
    losses = [t for t in trades if t["pnl_usd"] < 0]
    breakeven = [t for t in trades if t["pnl_usd"] == 0]

    total_pnl = sum(t["pnl_usd"] for t in trades)
    gross_wins = sum(t["pnl_usd"] for t in wins)
    gross_losses = abs(sum(t["pnl_usd"] for t in losses))

    win_rate = len(wins) / total * 100 if total else 0
    avg_win = gross_wins / len(wins) if wins else 0
    avg_loss = gross_losses / len(losses) if losses else 0
    profit_factor = gross_wins / gross_losses if gross_losses > 0 else float("inf")
    avg_r = sum(t["r_multiple"] for t in trades) / total if total else 0

    # Calibration buckets
    calibration = defaultdict(lambda: {"trades": 0, "wins": 0})
    for t in trades:
        bucket = (t["confidence_pct"] // 10) * 10
        calibration[bucket]["trades"] += 1
        if t["pnl_usd"] > 0:
            calibration[bucket]["wins"] += 1

    # Strategy breakdown
    strategy_stats = defaultdict(lambda: {"trades": 0, "pnl": 0.0})
    for t in trades:
        s = t["strategy"]
        strategy_stats[s]["trades"] += 1
        strategy_stats[s]["pnl"] += t["pnl_usd"]

    # Confirmation bias check
    bias_losses = [t for t in losses if t["ignored_contrary"] == "Y"]

    # Thesis accuracy
    thesis_correct = [t for t in trades if t["thesis_correct"] == "Y"]
    thesis_wrong = [t for t in trades if t["thesis_correct"] == "N"]

    return {
        "total": total,
        "wins": len(wins),
        "losses": len(losses),
        "breakeven": len(breakeven),
        "win_rate": win_rate,
        "total_pnl": total_pnl,
        "gross_wins": gross_wins,
        "gross_losses": gross_losses,
        "avg_win": avg_win,
        "avg_loss": avg_loss,
        "profit_factor": profit_factor,
        "avg_r": avg_r,
        "calibration": dict(calibration),
        "strategy_stats": dict(strategy_stats),
        "bias_losses": len(bias_losses),
        "thesis_correct_pct": len(thesis_correct) / total * 100 if total else 0,
        "thesis_wrong_pct": len(thesis_wrong) / total * 100 if total else 0,
    }


def build_calibration_lines(calibration: dict) -> str:
    """Build calibration table as plain text for Telegram."""
    if not calibration:
        return "  No data yet."

    lines = []
    for bucket in sorted(calibration.keys()):
        data = calibration[bucket]
        t = data["trades"]
        w = data["wins"]
        actual_rate = w / t * 100 if t > 0 else 0
        label = f"{bucket}-{bucket+9}%"
        bar = "█" * int(actual_rate / 10)
        lines.append(f"  {label}: {actual_rate:.0f}% actual win ({w}/{t} trades) {bar}")
    return "\n".join(lines)


def build_strategy_lines(strategy_stats: dict) -> str:
    """Build strategy breakdown as plain text."""
    if not strategy_stats:
        return "  No data yet."

    lines = []
    for strat, data in sorted(strategy_stats.items(), key=lambda x: x[1]["pnl"], reverse=True):
        pnl = data["pnl"]
        t = data["trades"]
        sign = "+" if pnl >= 0 else ""
        lines.append(f"  {strat}: {sign}${pnl:.0f} ({t} trade{'s' if t != 1 else ''})")
    return "\n".join(lines)


def build_report(report_type: str, week_start: date, week_end: date, trades: list[dict]) -> str:
    """Build the full performance report message."""
    today = date.today()
    stats = compute_stats(trades)

    mode_label = "📄 PAPER MODE"
    if report_type == "MONDAY":
        header = f"📊 <b>Weekly Wrap — Week of {week_start.strftime('%b %d')}–{week_end.strftime('%b %d, %Y')}</b>"
        subheader = "Prior week final results."
    else:
        header = f"📊 <b>Week-to-Date Review — {today.strftime('%A, %b %d, %Y')}</b>"
        subheader = f"WTD results: {week_start.strftime('%b %d')} through today."

    if not trades:
        return (
            f"{header}\n"
            f"{mode_label} | {subheader}\n\n"
            "No trades logged this week.\n\n"
            "Either no setups triggered or trades haven't been logged yet.\n"
            "Log closed trades to TRADES.csv to enable tracking."
        )

    pnl_sign = "+" if stats["total_pnl"] >= 0 else ""
    pf_str = f"{stats['profit_factor']:.2f}" if stats["profit_factor"] != float("inf") else "∞"

    report = (
        f"{header}\n"
        f"{mode_label} | {subheader}\n"
        f"{'─' * 35}\n\n"

        f"<b>💰 P&amp;L SUMMARY</b>\n"
        f"  Net P&amp;L:       {pnl_sign}${stats['total_pnl']:.2f}\n"
        f"  Gross Wins:    +${stats['gross_wins']:.2f}\n"
        f"  Gross Losses:  -${stats['gross_losses']:.2f}\n"
        f"  Profit Factor: {pf_str}\n\n"

        f"<b>🎯 WIN/LOSS METRICS</b>\n"
        f"  Total Trades:  {stats['total']}\n"
        f"  Wins / Losses: {stats['wins']} / {stats['losses']}\n"
        f"  Win Rate:      {stats['win_rate']:.1f}%\n"
        f"  Avg Win:       +${stats['avg_win']:.2f}\n"
        f"  Avg Loss:      -${stats['avg_loss']:.2f}\n"
        f"  Avg R-Multiple:{stats['avg_r']:.2f}R\n\n"

        f"<b>🧠 THESIS &amp; BIAS CHECK</b>\n"
        f"  Thesis Correct:   {stats['thesis_correct_pct']:.0f}%\n"
        f"  Thesis Wrong:     {stats['thesis_wrong_pct']:.0f}%\n"
        f"  Bias Losses (ignored red flags): {stats['bias_losses']}\n\n"

        f"<b>📐 CALIBRATION (Confidence → Actual Win Rate)</b>\n"
        f"{build_calibration_lines(stats['calibration'])}\n\n"

        f"<b>📋 BY STRATEGY</b>\n"
        f"{build_strategy_lines(stats['strategy_stats'])}\n\n"
    )

    # Add trade-by-trade log
    report += f"<b>📝 TRADE LOG</b>\n"
    for t in sorted(trades, key=lambda x: x["date"]):
        sign = "+" if t["pnl_usd"] >= 0 else ""
        correct = f" ✓" if t["thesis_correct"] == "Y" else (" ✗" if t["thesis_correct"] == "N" else "")
        report += (
            f"  {t['date'].strftime('%m/%d')} {t['ticker']} {t['direction']} "
            f"({t['confidence_pct']}%) → {sign}${t['pnl_usd']:.2f} / {t['r_multiple']:.1f}R{correct}\n"
        )

    return report


def split_and_send(message: str) -> None:
    """Split long messages and send via Telegram (max ~3,800 chars per part)."""
    max_len = 3800
    if len(message) <= max_len:
        send_telegram(message)
        return

    # Split at newline boundaries
    parts = []
    current = ""
    for line in message.split("\n"):
        if len(current) + len(line) + 1 > max_len:
            parts.append(current)
            current = line + "\n"
        else:
            current += line + "\n"
    if current:
        parts.append(current)

    for i, part in enumerate(parts, 1):
        prefix = f"[Part {i}/{len(parts)}]\n" if len(parts) > 1 else ""
        send_telegram(prefix + part)


# ─── Main ─────────────────────────────────────────────────────────────────────

def main():
    today = date.today()
    day_of_week = today.weekday()  # 0=Mon, 4=Fri

    # Determine report type
    # Monday = prior week review (Mon–Sun of previous week)
    # Friday = current week WTD review (Mon–today)
    if len(sys.argv) > 1 and sys.argv[1] in ("MONDAY", "FRIDAY", "TEST"):
        report_type = sys.argv[1]
    elif day_of_week == 0:
        report_type = "MONDAY"
    else:
        report_type = "FRIDAY"

    if report_type == "MONDAY":
        # Prior week: Mon to Sun
        prior_monday = today - timedelta(days=7)
        week_start, week_end = get_week_range(prior_monday)
    elif report_type == "TEST":
        # Test: last 30 days
        week_start = today - timedelta(days=30)
        week_end = today
        report_type = "FRIDAY"
    else:
        # Current WTD: Mon to today
        week_start, week_end = get_week_range(today)
        week_end = today

    trades = load_trades(week_start, week_end)
    report = build_report(report_type, week_start, week_end, trades)

    print(report)  # Also print to stdout for debugging
    split_and_send(report)


if __name__ == "__main__":
    main()
