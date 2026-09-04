# HEARTBEAT.md

## 9:13 AM ET (13:13 UTC) — Auto-Score Results [AUTOMATED — NO HUMAN NEEDED]
Run: `python3 model/production/auto_score_results.py --notify`
Fetches yesterday's final scores from MLB Stats API. Evaluates all MC pregame predictions (win direction, run line cover, total runs). Saves JSON to `shadow_ledger/mc_results/mc_results_YYYY-MM-DD.json`. Telegrams Chris a summary: ML accuracy by confidence bucket, notable high-conviction calls, run line hit rate. Full no-human pipeline — fires automatically via cron.

## 9:15 AM ET (13:15 UTC) — ML v2 Bet Results Scorer [AUTOMATED — NO HUMAN NEEDED]
Run: `python3 model/production/ml_v2_score_results.py --notify`
Scores yesterday's ML v2 BET results specifically. Joins ml_v2_picks_*.json (actual bets placed) with final MLB scores. Tracks per-bet W/L, P&L, ROI. Saves to `shadow_ledger/ml_v2_results/ml_v2_results_YYYY-MM-DD.json`. Telegrams Chris bet-by-bet results + daily P&L.

### On-demand: Model Self-Review (run weekly or after slumps)
Run: `python3 model/production/model_review.py --notify --save-proposals`
My self-review tool. Loads all ML v2 bet history → feature attribution (which features predict wins) → threshold sensitivity (optimal score cutoff) → calibration check → concrete proposed changes. Saves proposals to `proposed_changes/proposals_YYYY-MM-DD.json`. Review proposals before applying any changes to run_ml_v2.py.

## 7:45 AM ET (11:45 UTC) — SP Matchup Scores [AUTOMATED — NO HUMAN NEEDED]
Run: `python3 model/production/sp_matchup_score.py --notify`
Scores every probable starter 0–100 based on: pitcher quality (SIERA/K-BB%), opponent RS/G, park factor, home advantage. Tiers: 🟢 Auto Start (75+), 🔵 Probably Start (55-74), 🟡 Questionable (35-54), 🔴 Do Not Start (<35). Generates betting signals: SP gap ≥ 20pts → run line lean; both 70+ → UNDER lean; both <45 → OVER lean. Saves to `daily_picks/sp_scores_YYYY-MM-DD.json`. Telegrams Chris ranked table + signals.

## 7:50 AM ET (11:50 UTC) — Bullpen Profile Update [AUTOMATED — NO HUMAN NEEDED]
Run: `python3 model/production/update_team_bullpen_2026.py`
Fetches 2026 YTD bullpen-only stats (675 relief pitchers, grouped by team). Computes team bullpen K rate, BB rate, HR rate, ERA, save% — Bayesian blended at 300 BF. Saves to `team_strength.json['bullpen_2026']`. Powers engine.py bullpen substitution — replaces the league-average stub with actual team quality. Run alongside `update_team_strength_2026.py`.

## 8:00 AM ET (12:00 UTC) — Morning Pre-Screen
Pull MLB schedule + probable pitchers + opening odds. Run ML v2 model pre-score on all games. If any ML picks have strong edge, ping Chris immediately. Save results to model/production/daily_picks/.

## 11:00 AM ET (15:00 UTC) — Full Model Run
Pull umpire assignments + lineups. Run ML v2 model with full data (umpire + lineup adjustments). Ping Chris with ALL picks: ML Edge ≥ 1.5. If no picks, send "No picks today" confirmation.
NOTE: Run Line (RL) model is retired. ML v2 (Moneyline Model v2) is the only active betting model.

## Every 30 Min (T-5 to T-30 before first pitch) — Closing Odds Capture [AUTOMATED — NO HUMAN NEEDED]
Run: `python3 model/production/scrape_closing_odds.py`
For each game starting in 5–30 minutes, pulls current Odds API moneylines and saves them as closing odds to `daily_picks/closing_odds/closing_{date}_{game_pk}.json`. These are used the next morning by auto_score_results.py to compute CLV (Closing Line Value).

**CLV = model_prob - closing_market_prob (vig-removed)**
- Positive avg CLV = model is consistently beating sharp money = real edge
- Negative avg CLV = market is pricing us out = accuracy stats are misleading
- Even +0.5–1% avg CLV over large sample = strong, sustainable edge signal
- Cron fires same windows as MC pregame (11am–1am ET) but captures at T-5 to T-30 instead of T-50 to T-90
- Results appear in auto-score Telegram: beat-close rate + avg CLV per game
