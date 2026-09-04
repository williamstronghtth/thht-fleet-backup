#!/usr/bin/env python3
"""
Billy's Betting Board - FastAPI Backend
"""

from fastapi import FastAPI, Request, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime, date
import sqlite3
import os

app = FastAPI(title="Billy's Betting Board")

# Setup templates and static files
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

# Database setup
DB_PATH = os.environ.get("DB_PATH", "bets.db")

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS picks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            game TEXT NOT NULL,
            pick TEXT NOT NULL,
            bet_type TEXT NOT NULL,
            confidence INTEGER NOT NULL,
            edge REAL,
            line TEXT,
            result TEXT DEFAULT 'pending',
            pnl REAL DEFAULT 0,
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

init_db()

# Pydantic models
class PickCreate(BaseModel):
    date: str
    game: str
    pick: str
    bet_type: str  # SPREAD, TOTAL, PROP
    confidence: int
    edge: Optional[float] = None
    line: Optional[str] = None
    notes: Optional[str] = None

class PickResult(BaseModel):
    id: int
    result: str  # W, L, P (push)
    pnl: float

# API Routes
@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    conn = get_db()
    
    today = date.today().isoformat()
    yesterday = date.today().replace(day=date.today().day - 1).isoformat()
    
    # Today's picks
    today_picks = conn.execute(
        "SELECT * FROM picks WHERE date = ? ORDER BY confidence DESC",
        (today,)
    ).fetchall()
    
    # Yesterday's results
    yesterday_picks = conn.execute(
        "SELECT * FROM picks WHERE date = ? ORDER BY confidence DESC",
        (yesterday,)
    ).fetchall()
    
    # All-time stats
    all_picks = conn.execute(
        "SELECT * FROM picks WHERE result != 'pending'"
    ).fetchall()
    
    # Calculate stats
    stats = calculate_stats(all_picks)
    
    # Stats by type
    spread_picks = [p for p in all_picks if p['bet_type'] == 'SPREAD']
    total_picks = [p for p in all_picks if p['bet_type'] == 'TOTAL']
    prop_picks = [p for p in all_picks if p['bet_type'] == 'PROP']
    
    type_stats = {
        'SPREAD': calculate_stats(spread_picks),
        'TOTAL': calculate_stats(total_picks),
        'PROP': calculate_stats(prop_picks)
    }
    
    # Stats by confidence tier
    conf_tiers = {
        '55-60%': calculate_stats([p for p in all_picks if 55 <= p['confidence'] < 60]),
        '60-65%': calculate_stats([p for p in all_picks if 60 <= p['confidence'] < 65]),
        '65%+': calculate_stats([p for p in all_picks if p['confidence'] >= 65])
    }
    
    conn.close()
    
    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "today": today,
        "yesterday": yesterday,
        "today_picks": today_picks,
        "yesterday_picks": yesterday_picks,
        "stats": stats,
        "type_stats": type_stats,
        "conf_tiers": conf_tiers
    })

def calculate_stats(picks):
    if not picks:
        return {'wins': 0, 'losses': 0, 'pushes': 0, 'total': 0, 'win_pct': 0, 'pnl': 0}
    
    wins = sum(1 for p in picks if p['result'] == 'W')
    losses = sum(1 for p in picks if p['result'] == 'L')
    pushes = sum(1 for p in picks if p['result'] == 'P')
    total = wins + losses
    pnl = sum(p['pnl'] for p in picks)
    
    return {
        'wins': wins,
        'losses': losses,
        'pushes': pushes,
        'total': total,
        'win_pct': round(wins / total * 100, 1) if total > 0 else 0,
        'pnl': round(pnl, 2)
    }

@app.post("/api/picks")
async def create_pick(pick: PickCreate):
    conn = get_db()
    cursor = conn.execute(
        """INSERT INTO picks (date, game, pick, bet_type, confidence, edge, line, notes)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
        (pick.date, pick.game, pick.pick, pick.bet_type, pick.confidence, 
         pick.edge, pick.line, pick.notes)
    )
    conn.commit()
    pick_id = cursor.lastrowid
    conn.close()
    return {"id": pick_id, "status": "created"}

@app.post("/api/picks/bulk")
async def create_picks_bulk(picks: List[PickCreate]):
    conn = get_db()
    ids = []
    for pick in picks:
        cursor = conn.execute(
            """INSERT INTO picks (date, game, pick, bet_type, confidence, edge, line, notes)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (pick.date, pick.game, pick.pick, pick.bet_type, pick.confidence,
             pick.edge, pick.line, pick.notes)
        )
        ids.append(cursor.lastrowid)
    conn.commit()
    conn.close()
    return {"ids": ids, "status": "created"}

@app.post("/api/results")
async def update_result(result: PickResult):
    conn = get_db()
    conn.execute(
        "UPDATE picks SET result = ?, pnl = ? WHERE id = ?",
        (result.result, result.pnl, result.id)
    )
    conn.commit()
    conn.close()
    return {"status": "updated"}

@app.get("/api/picks")
async def get_picks(date: Optional[str] = None):
    conn = get_db()
    if date:
        picks = conn.execute("SELECT * FROM picks WHERE date = ?", (date,)).fetchall()
    else:
        picks = conn.execute("SELECT * FROM picks ORDER BY date DESC, confidence DESC").fetchall()
    conn.close()
    return [dict(p) for p in picks]

@app.get("/api/stats")
async def get_stats():
    conn = get_db()
    all_picks = conn.execute("SELECT * FROM picks WHERE result != 'pending'").fetchall()
    conn.close()
    return calculate_stats(all_picks)

# Health check for Render
@app.get("/health")
async def health():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))
