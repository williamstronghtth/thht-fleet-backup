# 🏀 Billy's Betting Board

AI-powered NBA betting tracker built by Billy.

## Features

- **Today's Picks**: Current day's betting recommendations with confidence %
- **Yesterday's Results**: Automatic tracking of W/L/P
- **Historical Stats**: Win rate, P&L by bet type and confidence tier
- **API Access**: Push picks and results programmatically

## Deploy to Render (Free)

1. Push this repo to GitHub
2. Connect to Render.com
3. Create new "Web Service"
4. Connect your repo
5. Render auto-detects Python and deploys

**Settings:**
- Build Command: `pip install -r requirements.txt`
- Start Command: `uvicorn app:app --host 0.0.0.0 --port $PORT`

## API Endpoints

### Add a pick
```bash
curl -X POST https://your-app.onrender.com/api/picks \
  -H "Content-Type: application/json" \
  -d '{
    "date": "2026-02-07",
    "game": "ATL @ CHA",
    "pick": "ATL +2",
    "bet_type": "SPREAD",
    "confidence": 58,
    "edge": 2.6
  }'
```

### Record result
```bash
curl -X POST https://your-app.onrender.com/api/results \
  -H "Content-Type: application/json" \
  -d '{
    "id": 1,
    "result": "W",
    "pnl": 0.91
  }'
```

### Get stats
```bash
curl https://your-app.onrender.com/api/stats
```

## Local Development

```bash
pip install -r requirements.txt
python app.py
# Visit http://localhost:8000
```

---
Built with 🏀 by Billy
