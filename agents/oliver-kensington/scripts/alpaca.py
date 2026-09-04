#!/usr/bin/env python3
"""
Alpaca Trading Script — Oliver Kensington
Paper + Live trading interface via Alpaca REST API.

Usage:
    python alpaca.py account                          # Account summary
    python alpaca.py positions                        # Open positions
    python alpaca.py orders [--status open|all]       # Order history
    python alpaca.py buy  TICKER SHARES               # Market buy by shares
    python alpaca.py buy  TICKER --dollars AMOUNT     # Market buy by notional
    python alpaca.py sell TICKER SHARES               # Market sell by shares
    python alpaca.py sell TICKER --all                # Close full position
    python alpaca.py short TICKER SHARES              # Market short
    python alpaca.py cover TICKER SHARES              # Cover short
    python alpaca.py cancel ORDER_ID                  # Cancel open order
    python alpaca.py cancel --all                     # Cancel all open orders
    python alpaca.py quote TICKER [TICKER ...]        # Latest quotes

Config: ../config/alpaca.json
"""

import json
import sys
import urllib.request
import urllib.error
from pathlib import Path

# =============================================================================
# CONFIG
# =============================================================================

CONFIG_PATH = Path(__file__).parent.parent / "config" / "alpaca.json"


def load_config():
    with open(CONFIG_PATH) as f:
        return json.load(f)


def make_request(config, method, path, body=None):
    """Make authenticated request to Alpaca REST API."""
    url = config["base_url"].rstrip("/") + path
    data = json.dumps(body).encode() if body else None

    req = urllib.request.Request(
        url,
        data=data,
        method=method,
        headers={
            "APCA-API-KEY-ID": config["api_key"],
            "APCA-API-SECRET-KEY": config["api_secret"],
            "Content-Type": "application/json",
            "Accept": "application/json",
        },
    )

    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            raw = resp.read()
            return json.loads(raw) if raw else {}
    except urllib.error.HTTPError as e:
        body_text = e.read().decode()
        try:
            err = json.loads(body_text)
            msg = err.get("message", body_text)
        except Exception:
            msg = body_text
        print(f"HTTP {e.code}: {msg}", file=sys.stderr)
        sys.exit(1)


def data_request(config, method, path, body=None):
    """Make authenticated request to Alpaca Data API."""
    url = config["data_url"].rstrip("/") + path
    data = json.dumps(body).encode() if body else None

    req = urllib.request.Request(
        url,
        data=data,
        method=method,
        headers={
            "APCA-API-KEY-ID": config["api_key"],
            "APCA-API-SECRET-KEY": config["api_secret"],
            "Accept": "application/json",
        },
    )

    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            raw = resp.read()
            return json.loads(raw) if raw else {}
    except urllib.error.HTTPError as e:
        body_text = e.read().decode()
        try:
            err = json.loads(body_text)
            msg = err.get("message", body_text)
        except Exception:
            msg = body_text
        print(f"HTTP {e.code}: {msg}", file=sys.stderr)
        sys.exit(1)


# =============================================================================
# COMMANDS
# =============================================================================

def cmd_account(config):
    acc = make_request(config, "GET", "/account")
    env = config.get("environment", "?").upper()
    equity = float(acc["equity"])
    buying_power = float(acc["buying_power"])
    cash = float(acc["cash"])
    pnl = float(acc["equity"]) - float(acc.get("last_equity", acc["equity"]))
    pnl_pct = (pnl / float(acc.get("last_equity", acc["equity"])) * 100) if float(acc.get("last_equity", 1)) else 0

    print(f"\n{'='*50}")
    print(f"  ACCOUNT — {env} ({acc['account_number']})")
    print(f"{'='*50}")
    print(f"  Status:       {acc['status']}")
    print(f"  Equity:       ${equity:>12,.2f}")
    print(f"  Cash:         ${cash:>12,.2f}")
    print(f"  Buying Power: ${buying_power:>12,.2f}")
    print(f"  Day P&L:      ${pnl:>+12,.2f}  ({pnl_pct:+.2f}%)")
    print(f"  Day Trades:   {acc['daytrade_count']}")
    print(f"  PDT:          {'YES ⚠️' if acc['pattern_day_trader'] else 'No'}")
    print(f"  Shorting:     {'Enabled' if acc['shorting_enabled'] else 'Disabled'}")
    print(f"{'='*50}\n")


def cmd_positions(config):
    positions = make_request(config, "GET", "/positions")

    if not positions:
        print("\n  No open positions.\n")
        return

    print(f"\n{'='*65}")
    print(f"  {'SYMBOL':<8} {'SIDE':<6} {'QTY':>10} {'PRICE':>10} {'COST':>10} {'P&L':>12} {'%':>7}")
    print(f"{'='*65}")

    total_pnl = 0.0
    for pos in positions:
        sym = pos["symbol"]
        side = pos["side"].upper()
        qty = float(pos["qty"])
        price = float(pos["current_price"])
        cost = float(pos["avg_entry_price"])
        pnl = float(pos["unrealized_pl"])
        pnl_pct = float(pos["unrealized_plpc"]) * 100
        total_pnl += pnl
        sign = "+" if pnl >= 0 else ""
        print(f"  {sym:<8} {side:<6} {qty:>10.4f} {price:>10.2f} {cost:>10.2f} {sign}{pnl:>10.2f}  {sign}{pnl_pct:.1f}%")

    print(f"{'='*65}")
    sign = "+" if total_pnl >= 0 else ""
    print(f"  {'TOTAL':<45} {sign}{total_pnl:>10.2f}")
    print(f"{'='*65}\n")


def cmd_orders(config, status="open"):
    params = f"?status={status}&limit=20&direction=desc"
    orders = make_request(config, "GET", f"/orders{params}")

    if not orders:
        print(f"\n  No {status} orders.\n")
        return

    print(f"\n{'='*75}")
    print(f"  {'SYMBOL':<8} {'SIDE':<6} {'TYPE':<8} {'QTY':>8} {'FILL $':>10} {'STATUS':<14} ID")
    print(f"{'='*75}")

    for o in orders:
        sym = o["symbol"]
        side = o["side"].upper()
        otype = o["type"].upper()
        qty = o.get("qty") or o.get("notional", "?")
        fill = o.get("filled_avg_price") or "-"
        if fill != "-":
            fill = f"${float(fill):.2f}"
        status_str = o["status"].upper()
        order_id = o["id"][:8] + "..."
        print(f"  {sym:<8} {side:<6} {otype:<8} {str(qty):>8} {str(fill):>10} {status_str:<14} {order_id}")

    print(f"{'='*75}\n")


def cmd_buy(config, ticker, shares=None, dollars=None):
    ticker = ticker.upper()
    if dollars:
        body = {
            "symbol": ticker,
            "notional": str(dollars),
            "side": "buy",
            "type": "market",
            "time_in_force": "day",
        }
        desc = f"${dollars:.2f} notional"
    else:
        body = {
            "symbol": ticker,
            "qty": str(shares),
            "side": "buy",
            "type": "market",
            "time_in_force": "day",
        }
        desc = f"{shares} shares"

    order = make_request(config, "POST", "/orders", body)
    print(f"\n  ✅ BUY {ticker} — {desc}")
    print(f"  Order ID:  {order['id']}")
    print(f"  Status:    {order['status']}")
    print()


def cmd_sell(config, ticker, shares=None, close_all=False):
    ticker = ticker.upper()

    if close_all:
        result = make_request(config, "DELETE", f"/positions/{ticker}")
        print(f"\n  ✅ CLOSE ALL {ticker}")
        print(f"  Order ID:  {result['id']}")
        print(f"  Status:    {result['status']}")
        print()
        return

    body = {
        "symbol": ticker,
        "qty": str(shares),
        "side": "sell",
        "type": "market",
        "time_in_force": "day",
    }
    order = make_request(config, "POST", "/orders", body)
    print(f"\n  ✅ SELL {ticker} — {shares} shares")
    print(f"  Order ID:  {order['id']}")
    print(f"  Status:    {order['status']}")
    print()


def cmd_short(config, ticker, shares):
    ticker = ticker.upper()
    body = {
        "symbol": ticker,
        "qty": str(shares),
        "side": "sell",
        "type": "market",
        "time_in_force": "day",
    }
    order = make_request(config, "POST", "/orders", body)
    print(f"\n  ✅ SHORT {ticker} — {shares} shares")
    print(f"  Order ID:  {order['id']}")
    print(f"  Status:    {order['status']}")
    print()


def cmd_cover(config, ticker, shares=None):
    ticker = ticker.upper()

    if not shares:
        # Close full short position
        result = make_request(config, "DELETE", f"/positions/{ticker}")
        print(f"\n  ✅ COVER ALL {ticker}")
        print(f"  Order ID:  {result['id']}")
        print(f"  Status:    {result['status']}")
        print()
        return

    body = {
        "symbol": ticker,
        "qty": str(shares),
        "side": "buy",
        "type": "market",
        "time_in_force": "day",
    }
    order = make_request(config, "POST", "/orders", body)
    print(f"\n  ✅ COVER {ticker} — {shares} shares")
    print(f"  Order ID:  {order['id']}")
    print(f"  Status:    {order['status']}")
    print()


def cmd_cancel(config, order_id=None, cancel_all=False):
    if cancel_all:
        result = make_request(config, "DELETE", "/orders")
        count = len(result) if isinstance(result, list) else 0
        print(f"\n  ✅ Cancelled {count} open order(s).\n")
        return

    make_request(config, "DELETE", f"/orders/{order_id}")
    print(f"\n  ✅ Order {order_id} cancelled.\n")


def cmd_quote(config, tickers):
    symbols = ",".join(t.upper() for t in tickers)
    path = f"/stocks/quotes/latest?symbols={symbols}&feed=iex"
    result = data_request(config, "GET", path)

    quotes = result.get("quotes", {})
    if not quotes:
        print("\n  No quotes returned.\n")
        return

    print(f"\n{'='*45}")
    print(f"  {'TICKER':<8} {'BID':>10} {'ASK':>10} {'SPREAD':>8}")
    print(f"{'='*45}")

    for sym, q in sorted(quotes.items()):
        bid = q.get("bp", 0)
        ask = q.get("ap", 0)
        spread = ask - bid if bid and ask else 0
        print(f"  {sym:<8} {bid:>10.2f} {ask:>10.2f} {spread:>8.4f}")

    print(f"{'='*45}\n")


# =============================================================================
# MAIN
# =============================================================================

def usage():
    print(__doc__)
    sys.exit(1)


def main():
    args = sys.argv[1:]
    if not args:
        usage()

    config = load_config()
    cmd = args[0].lower()

    if cmd == "account":
        cmd_account(config)

    elif cmd == "positions":
        cmd_positions(config)

    elif cmd == "orders":
        status = "open"
        if "--status" in args:
            idx = args.index("--status")
            status = args[idx + 1]
        cmd_orders(config, status)

    elif cmd == "buy":
        if len(args) < 2:
            usage()
        ticker = args[1]
        if "--dollars" in args:
            idx = args.index("--dollars")
            dollars = float(args[idx + 1])
            cmd_buy(config, ticker, dollars=dollars)
        elif len(args) >= 3:
            shares = float(args[2])
            cmd_buy(config, ticker, shares=shares)
        else:
            usage()

    elif cmd == "sell":
        if len(args) < 2:
            usage()
        ticker = args[1]
        if "--all" in args:
            cmd_sell(config, ticker, close_all=True)
        elif len(args) >= 3:
            shares = float(args[2])
            cmd_sell(config, ticker, shares=shares)
        else:
            usage()

    elif cmd == "short":
        if len(args) < 3:
            usage()
        cmd_short(config, args[1], float(args[2]))

    elif cmd == "cover":
        if len(args) < 2:
            usage()
        ticker = args[1]
        shares = float(args[2]) if len(args) >= 3 else None
        cmd_cover(config, ticker, shares)

    elif cmd == "cancel":
        if "--all" in args:
            cmd_cancel(config, cancel_all=True)
        elif len(args) >= 2:
            cmd_cancel(config, order_id=args[1])
        else:
            usage()

    elif cmd == "quote":
        if len(args) < 2:
            usage()
        cmd_quote(config, args[1:])

    else:
        print(f"Unknown command: {cmd}", file=sys.stderr)
        usage()


if __name__ == "__main__":
    main()
