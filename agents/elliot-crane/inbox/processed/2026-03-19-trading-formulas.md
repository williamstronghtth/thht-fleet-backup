# From William — Trading Formulas Thread Review
**Date:** 2026-03-19
**Source:** @LunarResearcher on X (Chris flagged this for you)

Chris found a thread breaking down 4 formulas + a Claude API bot for prediction market trading. I've read the full thing. Here's what matters for you:

## The 4 Formulas (you should already know all of these)

1. **Expected Value** — EV = P(win) × Profit − P(lose) × Loss. Only enter trades where EV > 5%. On a contract trading at 40¢ where you estimate 60% true probability, that's $0.20 edge per dollar.

2. **Kelly Criterion** — f* = (p × b − q) / b. Full Kelly is too aggressive. **Use Quarter Kelly.** With $1,000 bankroll that means ~$83 bets. Not exciting. Won't blow you up either. You learned this from Fortune's Formula — this validates it.

3. **Bayesian Updating** — P(H|E) = P(E|H) × P(H) / P(E). Update proportionally on new info. Don't overreact to one headline, don't ignore major developments. You covered this in Superforecasting and Thinking Fast and Slow.

4. **Log Returns** — log_return = ln(P₁/P₀). Arithmetic returns lie when aggregating trades. A contract going 0.80→0.40→0.80 looks like +50% arithmetic but is actually 0.000 in log returns. Use log returns for all your tracking.

## The 5 Mental Traps (gut check these against yourself)

1. **Base Rate Neglect** — 99% accurate test, 1/1000 disease prevalence = only 9% chance you're sick. Always check the base rate before forming a view.
2. **Sunk Cost Fallacy** — "Would I buy this at today's price?" is the only question. Your entry price is irrelevant.
3. **Survivorship Bias** — 87% of Polymarket wallets are in the red. You never see their posts.
4. **Loss Aversion** — Losing $100 feels 2x worse than gaining $100. It's hardwired. Recognize it.
5. **Overfitting** — 3 examples is noise, not a pattern.

## The Discipline Takeaway

3 confident trades out of 53 markets scanned. Not 53. Three. Wait for strong signals only. 3 confident trades a week beat 30 random ones.

## Bot Architecture Reference

The thread includes a full Python bot using Claude API to scan markets, estimate probabilities, calculate EV + Kelly, and output BUY or SKIP. Targets Polymarket (not Kalshi), but the math is identical. Code reference if you want to build something similar for Kalshi.

## My Expectation

None of this should be new to you. If anything surprised you, go back to your books. If it all clicked as review — good, you're on track.

## ⚠️ ALERT: Arizona vs Kalshi

Arizona AG just filed criminal charges against Kalshi — calling it "illegal gambling business." Monitor this closely. Could affect the platform you trade on.

— William
