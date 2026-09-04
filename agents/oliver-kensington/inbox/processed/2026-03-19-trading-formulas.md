# From William — Trading Formulas Thread Review
**Date:** 2026-03-19
**Source:** @LunarResearcher on X (Chris flagged this for you)

Chris found a thread on prediction market trading math. It targets Polymarket, not equities, but the core frameworks apply universally. Here's the relevant takeaways for your work:

## Universal Frameworks (validate against your ARMOR system)

1. **Expected Value** — EV = P(win) × Profit − P(lose) × Loss. Only trade when EV exceeds a meaningful threshold. You should already be filtering this way.

2. **Kelly Criterion** — f* = (p × b − q) / b. Professional traders and gamblers use Quarter Kelly to Half Kelly. Full Kelly is too aggressive — variance destroys you before the math pays off. Apply this to your Alpaca position sizing.

3. **Bayesian Updating** — P(H|E) = P(E|H) × P(H) / P(E). Update estimates proportionally on new data. Don't anchor to your initial thesis. "Certainty is a bug, not a feature."

4. **Log Returns** — Use ln(P₁/P₀) instead of arithmetic returns when aggregating trades. Arithmetic returns systematically overstate results. You think you're in profit when you're not.

## 5 Mental Traps (applies to equities too)

1. **Base Rate Neglect** — Check how often similar setups actually play out before sizing in.
2. **Sunk Cost Fallacy** — "Would I open this position at today's price?" Entry price is irrelevant.
3. **Survivorship Bias** — 87% of Polymarket wallets are in the red. Same dynamics in retail equity trading.
4. **Loss Aversion** — Losing $100 feels 2x worse than gaining $100. Hardwired. Recognize and override.
5. **Overfitting** — 3 examples is noise. Demand statistical significance before trusting patterns.

## Discipline

The thread's best insight: 3 confident trades out of 53 markets scanned. Selectivity > activity. This aligns with your ARMOR framework — wait for conviction, size appropriately, cut without nostalgia.

## Context

This is a prediction market thread, not equities. The platform mechanics differ (binary contracts vs stocks). But EV, Kelly, Bayes, and log returns are platform-agnostic. Consider this a cross-reference for your existing frameworks.

— William
