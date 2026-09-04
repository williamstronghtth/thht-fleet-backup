#!/usr/bin/env python3
"""
NBA Bet Tracker
Track all bets, results, and P&L - "stripped of delusion" per Voulgaris
"""

import json
import os
from datetime import datetime

DATA_DIR = os.path.dirname(os.path.abspath(__file__)) + "/data"
TRACKER_FILE = f"{DATA_DIR}/bet_history.json"

def load_bets():
    """Load bet history"""
    try:
        with open(TRACKER_FILE, 'r') as f:
            return json.load(f)
    except:
        return {'bets': [], 'summary': {}}

def save_bets(data):
    """Save bet history"""
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(TRACKER_FILE, 'w') as f:
        json.dump(data, f, indent=2)

def add_bet(pick, line, edge, edge_quality, units=1.0, odds=-110, notes=""):
    """
    Record a new bet
    pick: "MEM +9"
    line: 9.0
    edge: 3.4
    edge_quality: "sweet_spot" / "caution" / "marginal"
    units: bet size in units (default 1)
    odds: American odds (default -110)
    """
    data = load_bets()
    
    bet = {
        'id': len(data['bets']) + 1,
        'date': datetime.now().strftime('%Y-%m-%d'),
        'timestamp': datetime.now().isoformat(),
        'pick': pick,
        'line': line,
        'edge': edge,
        'edge_quality': edge_quality,
        'units': units,
        'odds': odds,
        'notes': notes,
        'result': None,  # W / L / P (push)
        'actual_margin': None,
        'pnl': None
    }
    
    data['bets'].append(bet)
    save_bets(data)
    print(f"✓ Bet #{bet['id']} recorded: {pick}")
    return bet['id']

def record_result(bet_id, result, actual_margin=None):
    """
    Record result of a bet
    result: "W" / "L" / "P" (push)
    actual_margin: actual game margin (positive = home team won by X)
    """
    data = load_bets()
    
    for bet in data['bets']:
        if bet['id'] == bet_id:
            bet['result'] = result
            bet['actual_margin'] = actual_margin
            
            # Calculate P&L
            if result == 'W':
                if bet['odds'] > 0:
                    bet['pnl'] = bet['units'] * (bet['odds'] / 100)
                else:
                    bet['pnl'] = bet['units'] * (100 / abs(bet['odds']))
            elif result == 'L':
                bet['pnl'] = -bet['units']
            else:  # Push
                bet['pnl'] = 0
            
            save_bets(data)
            print(f"✓ Bet #{bet_id} result: {result} | P&L: {bet['pnl']:+.2f}u")
            return
    
    print(f"Bet #{bet_id} not found")

def get_stats():
    """Calculate overall statistics"""
    data = load_bets()
    bets = [b for b in data['bets'] if b['result'] is not None]
    
    if not bets:
        return {'message': 'No completed bets yet'}
    
    wins = len([b for b in bets if b['result'] == 'W'])
    losses = len([b for b in bets if b['result'] == 'L'])
    pushes = len([b for b in bets if b['result'] == 'P'])
    total = wins + losses
    
    total_pnl = sum(b['pnl'] for b in bets if b['pnl'] is not None)
    total_units = sum(b['units'] for b in bets)
    
    # By edge quality
    sweet_spot = [b for b in bets if b.get('edge_quality') == 'sweet_spot']
    caution = [b for b in bets if b.get('edge_quality') == 'caution']
    
    stats = {
        'total_bets': len(bets),
        'record': f"{wins}-{losses}" + (f"-{pushes}" if pushes else ""),
        'win_pct': round(wins / total * 100, 1) if total > 0 else 0,
        'total_pnl': round(total_pnl, 2),
        'roi': round(total_pnl / total_units * 100, 1) if total_units > 0 else 0,
        'sweet_spot_record': f"{len([b for b in sweet_spot if b['result']=='W'])}-{len([b for b in sweet_spot if b['result']=='L'])}",
        'caution_record': f"{len([b for b in caution if b['result']=='W'])}-{len([b for b in caution if b['result']=='L'])}",
    }
    
    return stats

def print_report():
    """Print full P&L report"""
    data = load_bets()
    stats = get_stats()
    
    print("\n" + "="*50)
    print("📊 BET TRACKER REPORT")
    print("="*50)
    
    if 'message' in stats:
        print(stats['message'])
        return
    
    print(f"Record: {stats['record']} ({stats['win_pct']}%)")
    print(f"P&L: {stats['total_pnl']:+.2f} units")
    print(f"ROI: {stats['roi']:+.1f}%")
    print(f"\nBy Edge Quality:")
    print(f"  Sweet Spot (2-4 pts): {stats['sweet_spot_record']}")
    print(f"  Caution (4+ pts): {stats['caution_record']}")
    
    print(f"\nRecent Bets:")
    for bet in data['bets'][-5:]:
        result = bet['result'] or 'PENDING'
        pnl = f"{bet['pnl']:+.2f}u" if bet['pnl'] is not None else ""
        print(f"  {bet['date']} | {bet['pick']} | {result} {pnl}")

def pending_bets():
    """Show bets awaiting results"""
    data = load_bets()
    pending = [b for b in data['bets'] if b['result'] is None]
    
    if not pending:
        print("No pending bets")
        return []
    
    print(f"\n⏳ PENDING BETS ({len(pending)})")
    for bet in pending:
        print(f"  #{bet['id']} | {bet['date']} | {bet['pick']} | {bet['edge']:.1f}pt edge")
    
    return pending


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print_report()
    elif sys.argv[1] == 'pending':
        pending_bets()
    elif sys.argv[1] == 'add' and len(sys.argv) >= 5:
        # python bet_tracker.py add "MEM +9" 9.0 3.4 sweet_spot
        add_bet(sys.argv[2], float(sys.argv[3]), float(sys.argv[4]), 
                sys.argv[5] if len(sys.argv) > 5 else 'unknown')
    elif sys.argv[1] == 'result' and len(sys.argv) >= 4:
        # python bet_tracker.py result 1 W
        record_result(int(sys.argv[2]), sys.argv[3], 
                     float(sys.argv[4]) if len(sys.argv) > 4 else None)
    else:
        print("Usage:")
        print("  python bet_tracker.py              - Show report")
        print("  python bet_tracker.py pending      - Show pending bets")
        print("  python bet_tracker.py add 'MEM +9' 9.0 3.4 sweet_spot")
        print("  python bet_tracker.py result 1 W   - Record result")
