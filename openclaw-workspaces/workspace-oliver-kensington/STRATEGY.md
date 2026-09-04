# STRATEGY.md — Oliver Kensington Trading Framework

*Operational rules derived from reading, testing, and experience.*

---

## Core Process

### Pre-Trade Requirements
1. **Written thesis required** — No trade without articulated reasoning
2. **Confidence estimate required** — Assign probability (e.g., "70% this bounces")
3. **Stop loss required** — Define exit before entry

### Trade Journal Format
Every trade logged with:
- Timestamp
- Symbol, direction, size
- **Thesis** (why this trade?)
- **Falsification** (what would prove me wrong?)
- **Confidence %** (how sure am I?)
- Entry price, stop loss, target
- Exit price, P&L
- **Thesis correct?** (Y/N — separate from P&L)
- **Ignored contrary evidence?** (Y/N — confirmation bias check)
- Lessons learned

---

## Rules & Filters

### From Superforecasting Ch. 1 (2026-03-16)
- **RULE SF-1**: No "gut feel" trades. Every trade requires a falsifiable thesis written before entry. If I can't explain why I expect X to happen, I don't trade.

### From Superforecasting Ch. 2 (2026-03-16)
- **RULE SF-2**: Before any trade, ask "What would convince me I'm wrong?" If I can't answer, I'm probably confirmation-biased. Write down the falsification condition alongside the thesis.

### From Superforecasting Ch. 3 (2026-03-16)
- **RULE SF-3**: No "maybe zone" hiding. If my confidence is 45-55%, I either don't have an edge or I haven't done enough work. Push for resolution: find evidence that moves me toward 30% or 70%. If I can't, don't trade — I'm just guessing.

### From Superforecasting Ch. 4 (2026-03-16)
- **RULE SF-4**: Outside view first. Before analyzing any specific trade, find the base rate. "How often does X happen?" Then adjust from there. Never anchor on a number from the inside view.

### From Quantitative Trading Ch. 2 (2026-03-16)
- **RULE QT-1**: Sharpe ratio > raw returns. Sharpe < 1 = not standalone. Sharpe > 2 = profitable most months. Sharpe > 3 = profitable most days. Higher Sharpe + leverage beats higher raw returns.
- **RULE QT-2**: Simple > Complex. More parameters = more overfitting. Chan lost money with PhD math, made money with simple strategies. If a strategy needs >3 parameters, be very skeptical.
- **RULE QT-3**: Transaction costs kill strategies. A Sharpe 3 strategy became Sharpe -3 after 1 basis point costs. Always subtract realistic transaction costs BEFORE judging a strategy.

### From Quantitative Trading Ch. 3 (2026-03-16)
- **RULE QT-4**: Train/test split REQUIRED. Never trust in-sample performance. Use 2/3 for training, 1/3 for testing. If test performance drops drastically → overfitting.
- **RULE QT-5**: Minimum sample size = 252 × (# of parameters). A 3-parameter daily strategy needs 3+ years of data. No exceptions.
- **RULE QT-6**: Max 5 parameters including entry/exit thresholds, holding period, lookback period. Every additional parameter = exponentially more overfitting risk.
- **RULE QT-7**: Look-ahead bias check. Use LAGGED data for signals. If you're using today's high/low to generate today's signal → you're cheating.
- **RULE QT-8**: Sensitivity analysis required. Vary all parameters ±20%. If performance craters → data-snooping bias. Robust strategies degrade gracefully.
- **RULE QT-9**: Paper trade before live trade. "Ultimate out-of-sample test." Reveals operational issues backtests hide.

### From Quantitative Trading Ch. 4-5 (2026-03-16)
- **RULE QT-10**: Order size < 1% of average daily volume. Exceeding this = market impact that kills returns.
- **RULE QT-11**: No stocks under $5. Low-price stocks have higher % bid-ask spreads and inflate commission costs.
- **RULE QT-12**: When live performance diverges from backtest: 1) Check for bugs, 2) Check transaction costs, 3) Simplify strategy (remove params). If simplifying destroys backtest → data-snooping confirmed.
- **RULE QT-13**: Beware regime shifts. Pre-2001 (decimalization) and pre-2007 (plus-tick rule) backtests are unreliable for many strategies.

### From Quantitative Trading Ch. 6 (2026-03-16)
- **RULE QT-14**: Kelly formula for leverage: f = m/s² (mean return ÷ variance). This is MAXIMUM leverage — use half-Kelly (f/2) for safety.
- **RULE QT-15**: Absolute leverage ceiling = max_tolerable_drawdown ÷ max_historical_loss. Use the SMALLER of half-Kelly and this ceiling.
- **RULE QT-16**: Rebalance at least daily. After a loss, Kelly says REDUCE position size. After a win, INCREASE. This is automatic risk management.
- **RULE QT-17**: Stop loss depends on regime. Momentum/news → use stops. Mean-reverting/liquidity event → stops hurt (you exit before reversion).
- **RULE QT-18**: Volatility kills compounded returns. g = m - s²/2. Even a 50/50 ±1% random walk LOSES money long-term (0.5 bp/period).
- **RULE QT-19**: Psychological traps to avoid: 1) Loss aversion (hold losers, cut winners), 2) Representativeness bias (overweight recent), 3) Despair/greed (both cause overleveraging).

### From Quantitative Trading Ch. 7 (2026-03-16)
- **RULE QT-20**: Mean reversion is more prevalent than momentum. But mean-reversion backtests are inflated by data errors (bad quotes trigger fake profits) and survivorship bias.
- **RULE QT-21**: Momentum is triggered by: (1) slow info diffusion, (2) large institutional orders, (3) herding. The time horizon is UNPREDICTABLE for (2) and (3).
- **RULE QT-22**: Cointegration ≠ correlation. Cointegration = prices don't diverge long-term. Correlation = returns move together short-term. Two stocks can be correlated but NOT cointegrated (e.g., KO vs PEP).
- **RULE QT-23**: Exit strategy depends on strategy type:
  - Mean-reversion: Target price (the mean) or half-life holding period. NO stop loss.
  - Momentum: Stop loss or latest entry signal reversal. Target price is hard to justify.
- **RULE QT-24**: Half-life of mean reversion = ln(2)/θ from Ornstein-Uhlenbeck fit. More robust than backtest-derived holding period (uses entire time series, not just trades).
- **RULE QT-25**: Seasonal equity effects (January effect) have weakened. Seasonal commodity futures (gasoline April, natural gas Feb-Apr) still work.
- **RULE QT-26**: High-frequency = high Sharpe (law of large numbers). But needs bid/ask data, C code, colocation. True HFT not practical for independent traders starting out.
- **RULE QT-27**: High leverage on low-beta stocks > low leverage on high-beta stocks. Same expected return, but lower risk → higher Sharpe → higher compounded growth.

### From Trading and Exchanges Ch. 5 "Market Structures" (2026-03-16)
- **RULE TE-11**: Market structure determines power relationships. The trading rules, information systems, and execution systems determine WHO profits. Understand the structure before trading in any market.
- **RULE TE-12**: Transparency affects profitability. Ex ante transparent markets (order book visible) favor informed traders less; opaque markets favor informed traders more. Dealer markets are generally less transparent than exchange markets.
- **RULE TE-13**: Call markets maximize surplus; continuous markets provide flexibility. In continuous markets, dealers and market makers extract profit by intermediating temporal mismatches between buyers and sellers.
- **RULE TE-14**: Price clustering exploitable. Traders cluster orders at round numbers (integers, halves, quarters). Place limit orders just above/below round numbers to gain time precedence over the cluster.
- **RULE TE-15**: Order book information is extremely valuable. It reveals conditions under which traders will trade. In open-book markets, use this info. In closed-book markets, you're at a disadvantage vs. those who can see it.

### From Trading and Exchanges Ch. 6 "Order-driven Markets" (2026-03-16)
- **RULE TE-16**: Price priority is self-enforcing; time precedence is NOT. You must actively defend your time precedence. Smaller tick sizes weaken time precedence value.
- **RULE TE-17**: Discriminatory pricing favors large market orders; uniform pricing favors limit orders. In continuous markets, large traders can "price discriminate" by splitting orders to get progressively worse fills. Single-price auctions prevent this.
- **RULE TE-18**: Single price auctions maximize total trader surplus. If you can trade in a single-price auction (market open, market close), you often get better fills than continuous trading.
- **RULE TE-19**: Crossing networks are subject to adverse selection. Well-informed traders know when prices have changed; they eagerly trade at stale prices if favorable, refuse if not. Be careful trading at derivative prices.
- **RULE TE-20**: Derivative pricing enables manipulation. When trade price is determined elsewhere, traders have incentive to manipulate the reference market. Watch for this near closes, expirations, settlements.

### From Trading and Exchanges Ch. 7 "Brokers" (2026-03-16)
- **RULE TE-21**: Know your broker's incentives. Brokers receive payments for order flow, soft dollars, and margin interest. Their interests may not align with yours. Audit execution quality.
- **RULE TE-22**: Protect order information. Large orders require careful exposure management — don't reveal full size. Information about your intentions is a trading liability.
- **RULE TE-23**: Front-running is real. Brokers, clerks, and floor traders may trade ahead of large orders. Use brokers you trust; minimize information leakage.
- **RULE TE-24**: Best execution is hard to measure. Compare your fills to benchmark prices (VWAP, arrival price). If execution quality drops, investigate. You can't manage what you can't measure.
- **RULE TE-25**: Beware churning. Excessive trading benefits the broker, not you. Track your turnover and commission costs. If commissions exceed 2-3% of account annually, reassess.

### From Trading and Exchanges Ch. 8 "Why People Trade" (2026-03-16)
- **RULE TE-26**: Trading is zero-sum. For you to profit, someone must lose. Always ask: "Who is on the other side of this trade, and why are they willing to lose to me?" If you can't answer, you might be the loser.
- **RULE TE-27**: Most "informed" traders are actually futile traders. Pseudo-informed traders believe they have an edge but trade on stale/public info. <5% of fledglings survive to trade profitably.
- **RULE TE-28**: Distinguish gambling from speculating. Gamblers trade for excitement without an edge. Speculators have genuine informational advantages that allow them to predict price changes. Be brutally honest about which you are.
- **RULE TE-29**: Investment-motivated trading is only ~1% of equity volume. The other 99% is speculation, dealing, hedging, gambling, tax strategies, etc. Most market participants are NOT passive investors.

### From Trading and Exchanges Ch. 9 "Good Markets" (2026-03-16)
- **RULE TE-30**: Markets aggregate information into prices. Prices reflect the collective knowledge of all traders. To profit, you need information the market hasn't incorporated — either truly private info or superior analysis.
- **RULE TE-31**: Informative prices = efficient markets. In efficient markets, prices follow a random walk because they already reflect all known information. Predictable patterns = inefficiency = profit opportunity (but they get arbitraged away).

### From Trading and Exchanges Ch. 10 "Informed Traders" (2026-03-16)
- **RULE TE-32**: Four types of informed traders: (1) Value traders estimate total values, (2) News traders estimate value CHANGES, (3) Technical traders identify mispricing patterns, (4) Arbitrageurs estimate relative values. Know which you are.
- **RULE TE-33**: Precision + orthogonality = profitability. Most profitable = accurate estimates uncorrelated with what others think. Being right when nobody else is right is the edge.
- **RULE TE-34**: Pseudo-informed trading = trading on STALE information. The most common mistake. If others could have reasonably anticipated your information, it's probably already in the price.
- **RULE TE-35**: Market efficiency defined: Prices reflect all information that can be PROFITABLY traded upon. Costs matter — some info isn't worth acting on.
- **RULE TE-36**: Informed trading is most profitable with many uninformed traders (liquidity). Trading only with other informed traders = zero-sum among the informed.

### From Trading and Exchanges Ch. 11 "Order Anticipators" (2026-03-16)
- **RULE TE-37**: Front runners trade ahead of your orders. Protect order information obsessively. Don't reveal size, direction, or timing.
- **RULE TE-38**: Quote matchers extract option value from standing limit orders. They step in front, use your order as a backstop. Large tick sizes protect liquidity suppliers.
- **RULE TE-39**: Sentiment-oriented technical traders predict what UNINFORMED traders will do. Momentum traders are especially vulnerable — they follow price without understanding cause.
- **RULE TE-40**: Squeezers corner markets. Always have multiple exit paths. If you're short something illiquid, you're vulnerable.

### From Trading and Exchanges Ch. 12 "Bluffers and Manipulation" (2026-03-16)
- **RULE TE-41**: Bluffers profit when buy vs sell price impacts are asymmetric. Be disciplined about how you interpret price + volume signals. Don't assume price movement = informed trading.
- **RULE TE-42**: Momentum traders are MOST vulnerable to bluffers. Don't chase price without understanding WHY it's moving. "Why else would the market have gone up?" is the sucker's question.
- **RULE TE-43**: Value traders can call bluffs — but must be VERY certain about fundamental values first. Wrong value estimate + fighting a bluff = catastrophic loss.

### From Trading and Exchanges Ch. 13 "Dealers" (2026-03-16)
- **RULE TE-44**: Realized spread < quoted spread. Dealers adjust prices between trades and occasionally trade at better prices. Backtest spreads may overstate actual dealer profits.
- **RULE TE-45**: Inventory risk forces price adjustment. Dealers lower both bid and ask to reduce inventory (encourages buying, discourages selling). Raise both to build inventory.
- **RULE TE-46**: Adverse selection is THE key to dealer profitability. Dealers who can identify and avoid informed traders survive; those who can't go bankrupt.
- **RULE TE-47**: Order flow reveals information. Dealers infer value from WHO trades, WHEN they trade, and HOW MUCH. One-sided order flow signals informed trading.
- **RULE TE-48**: If you provide liquidity (limit orders), you face dealer risks. Adverse selection + inventory risk + timing option giveaway. Understand what you're selling.

### From Trading and Exchanges Ch. 14 "Bid/Ask Spreads" (2026-03-16)
- **RULE TE-49**: Uninformed traders lose REGARDLESS of order type. Market orders = pay adverse selection spread. Limit orders = suffer direct adverse selection. The only way to avoid losing is to not trade.
- **RULE TE-50**: Spread width determines order choice. Wide spread → limit orders attractive. Narrow spread → market orders attractive. Judge "wide" vs "narrow" from experience in that specific market.
- **RULE TE-51**: Limit orders = free timing options to faster traders. If you can't monitor and cancel quickly, limit orders are risky. The timing option value increases with volatility.
- **RULE TE-52**: Adverse selection spread = fee uninformed traders pay for informed trader risk. It allows dealers to recover from uninformed what they lose to informed.
- **RULE TE-53**: Asymmetric information is the single largest determinant of spreads. Hard-to-value securities have wide spreads; easy-to-value securities have narrow spreads.

### From Trading and Exchanges Ch. 15 "Block Traders" (2026-03-16)
- **RULE TE-54**: Large orders face four problems: latent demand (finding counterparties), order exposure (front runners), price discrimination (more size coming?), asymmetric info (you might be informed).
- **RULE TE-55**: Block liquidity suppliers demand audits. They want to know: Are you informed? Is this your full size? Reputation matters — honest traders get better fills.
- **RULE TE-56**: ~80% of block trades are seller-initiated. Sellers are more credible (can prove they own it and can't sell more), buyers are suspected of being informed.
- **RULE TE-57**: Sunshine trading rarely works. Announcing your trades attracts front runners and quote matchers. Selective exposure to trusted counterparties only.

### From Trading and Exchanges Ch. 16 "Value Traders" (2026-03-16)
- **RULE TE-58**: Value traders are ultimate liquidity suppliers. They trade when uninformed demand pushes price away from value. They supply depth and resiliency.
- **RULE TE-59**: Winner's curse: if you win, you probably overbid. Adjust bids down to account for the information revealed by winning. The more bidders, the more adjustment needed.
- **RULE TE-60**: Value traders must be BEST informed to survive. Otherwise, news traders will pick them off. Value trading works only when you're certain you have all public info.
- **RULE TE-61**: Outside spread (value trader prices) >> inside spread (dealer quotes). Dealers trade fast and small; value traders trade slow and large. Different costs → different spreads.

### From Trading and Exchanges Ch. 17 "Arbitrageurs" (2026-03-16)
- **RULE TE-62**: Pure arbitrage = forced convergence (delivery mechanism). Speculative arbitrage = no guarantee of convergence. Know which you're doing.
- **RULE TE-63**: Four arbitrage risks: (1) Implementation (execution costs), (2) Basis (spread widens), (3) Model (wrong fair value), (4) Carrying cost (financing, storage, time).
- **RULE TE-64**: NEVER leverage to the max. Leave staying power for when the basis moves against you. LTCM was RIGHT but went bankrupt anyway because they couldn't hold.
- **RULE TE-65**: Arbitrageurs are cross-sectional dealers. Dealers connect buyers and sellers across TIME; arbitrageurs connect them across MARKETS.
- **RULE TE-66**: The cause of the arbitrage opportunity determines trading style. Slow price adjustment → trade fast (demand liquidity). Uninformed demand → trade patient (supply liquidity).

### From Trading and Exchanges Ch. 18 "Buy-Side Traders" (2026-03-16)
- **RULE TE-67**: Order exposure is a tradeoff. Benefits: find counterparties, attract reactive traders. Costs: attract front runners, cause defensive withdrawal.
- **RULE TE-68**: Market vs limit order depends on: (1) spread width, (2) urgency, (3) price sensitivity, (4) exposure concerns. Impatient traders → market orders. Patient traders → limit orders.
- **RULE TE-69**: Proactive traders display interest and search for counterparties. Reactive traders wait for opportunities to come to them. Know which role you're playing.

### From Trading and Exchanges Ch. 19 "Liquidity" (2026-03-16)
- **RULE TE-70**: Liquidity = ability to trade large size, quickly, at low cost. Three dimensions: DEPTH (size at given price), IMMEDIACY (speed), WIDTH (cost/spread).
- **RULE TE-71**: Liquidity is bilateral search. Impatient traders DEMAND it; patient traders SUPPLY it. Two reactive traders never find each other.
- **RULE TE-72**: Five liquidity supplier types: (1) Market makers → immediacy to small anonymous traders, (2) Block dealers → depth to known uninformed clients, (3) Value traders → ultimate depth + resiliency, (4) Precommitted traders → narrow spreads, (5) Arbitrageurs → port liquidity across markets.
- **RULE TE-73**: Display increases probability of trading but attracts parasites. Large traders hide; small traders display. Latent demand must be discovered.
- **RULE TE-74**: Market resiliency = how quickly prices revert after uninformed trading. Value traders make markets resilient. Trade in resilient markets.

### From Trading and Exchanges Ch. 20 "Volatility" (2026-03-16)
- **RULE TE-75**: Two volatility types: FUNDAMENTAL (unpredictable value changes — random walk, can't be reduced) and TRANSITORY (bid/ask bounce + uninformed impacts — reverting).
- **RULE TE-76**: Transitory volatility ≈ transaction costs. High transitory volatility = illiquid market. Regulators can affect transitory but not fundamental volatility.
- **RULE TE-77**: Transitory price changes REVERSE (negative serial correlation). Fundamental changes DON'T. Use serial correlation to identify which type you're seeing.
- **RULE TE-78**: High-storage-cost and perishable commodities are highly volatile. Electricity = ultimate perishable (can't store). Low inventory + inelastic demand = price spikes.
- **RULE TE-79**: High P/E (growth) stocks are more volatile than low P/E (value) stocks. Uncertainty about future growth = volatility.

### From Trading and Exchanges Ch. 21 "Transaction Cost Measurement" (2026-03-16)
- **RULE TE-80**: Transaction costs = explicit (commissions, fees) + implicit (spread, market impact) + missed opportunity costs. Track ALL THREE.
- **RULE TE-81**: Implementation shortfall is the BEST metric. Uses decision-time price as benchmark. Can't be gamed. Captures missed trades.
- **RULE TE-82**: VWAP is gameable — brokers can match benchmark by spreading trades across the day. Use for comparison, not optimization.
- **RULE TE-83**: Effective spread = 2× (trade price - midpoint). Measures what you actually paid vs the quoted spread. Often LESS than quoted spread.
- **RULE TE-84**: Split order bias: large orders look cheaper than they are because each piece's benchmark moves with your previous fills. Track total cost from DECISION price.
- **RULE TE-85**: Balance transaction costs vs missed opportunity costs. If you're missing too many trades, trade more aggressively. If costs too high, be more patient.

### From Trading and Exchanges Ch. 22 "Performance Evaluation and Prediction" (2026-03-16)
- **RULE TE-86**: ⚠️ PAST PERFORMANCE DOES NOT PREDICT FUTURE RETURNS. Luck dominates skill over human time frames. This is not opinion — it's math.
- **RULE TE-87**: Statistical tests are UNRELIABLE. Need >20 YEARS of data to identify 2% alpha with 95% confidence. 5 years = nearly useless.
- **RULE TE-88**: Sample selection bias: you only HEAR about winners. Losers disappear. Adjust your inference for the total population, not just survivors.
- **RULE TE-89**: The "peso problem": strategies with many small wins + rare huge losses LOOK skilled until the blowup. Selling volatility, doubling down, etc.
- **RULE TE-90**: Regression to the mean: extreme past performers REVERT. Past luck doesn't predict future luck. Warren Buffet's first 26 years were partly lucky.
- **RULE TE-91**: **COMPARATIVE ADVANTAGE wins games, not absolute advantage.** It's not enough to be good — you must be BETTER than your opponents. Always ask: "Why will they lose to ME?"

### From Trading and Exchanges Ch. 23 "Index and Portfolio Markets" (2026-03-16)
- **RULE TE-92**: Index markets are more liquid than underlying security markets. Few traders have valuable insights about ENTIRE market direction → less adverse selection → tighter spreads.
- **RULE TE-93**: Active managers MUST underperform the market on average — this is ACCOUNTING, not opinion. Zero-sum game + transaction costs = negative-sum. Only ~25% of mutual funds beat the market in any quarter.
- **RULE TE-94**: Index reconstitution creates predictable price impacts. Russell additions outperform deletions by ~15% in June, then underperform by ~5% in July (reversal). Trade WITH this pattern.
- **RULE TE-95**: Package dealers offer better prices for portfolios than individual securities. Informed traders prefer INDIVIDUAL securities; portfolios have less adverse selection.

### From Trading and Exchanges Ch. 24 "Specialists" (2026-03-16)
- **RULE TE-96**: Price continuity is a PUBLIC GOOD that competitive markets won't provide. Specialists supply it because they receive privileges in exchange. Don't expect free continuity in electronic markets.
- **RULE TE-97**: Cream-skimming makes limit order strategies less attractive. Dealers step in front of limit orders when they expect profitable fills, leave orders to absorb informed flow.
- **RULE TE-98**: Stopped stock = valuable look-back timing option. Specialists can decide to exercise AFTER seeing price movement. This option value comes at the expense of limit order traders.

### From Trading and Exchanges Ch. 25 "Internalization, Preferencing, and Crossing" (2026-03-16)
- **RULE TE-99**: Retail customers can easily audit commissions but CANNOT easily audit execution quality. Brokers therefore compete on visible commissions, not on hard-to-measure execution quality.
- **RULE TE-100**: Internalization and preferencing shift power from limit order traders to dealers. Dealers selectively fill orders they want; limit orders get leftover adverse flow. Be aware of this disadvantage.

### From Trading and Exchanges Ch. 26 "Competition Within and Among Markets" (2026-03-16)
- **RULE TE-101**: Order flow externality — liquidity attracts liquidity. Markets naturally consolidate. A better trading system may FAIL if it can't overcome the incumbent's liquidity advantage.
- **RULE TE-102**: Time precedence is NOT enforced across market segments. Your limit order in Market A gives you no priority over orders in Market B. Cross-market order exposure is risky.
- **RULE TE-103**: Arbitrageurs consolidate fragmented markets. They move liquidity from where it's plentiful to where it's scarce. Follow arbitrageur activity to identify pricing discrepancies.

### From Trading and Exchanges Ch. 27 "Floor Versus Automated Trading Systems" (2026-03-16)
- **RULE TE-104**: Floor-based markets excel when traders need to exchange information BEFORE committing to trade. "How much more size?" "Are you informed?" Electronic markets can't facilitate these negotiations as well.
- **RULE TE-105**: Electronic markets provide better audit trails. If you suspect fraud or poor execution in floor markets, the audit trail may be weak. Electronic = flawless record keeping.

### From Trading and Exchanges Ch. 28 "Bubbles, Crashes, and Circuit Breakers" (2026-03-16)
- **RULE TE-106**: Most crashes represent CORRECTIONS to previous pricing errors, not market failures. If prices fully rebounded after crashes, they'd be failures. Usually they don't → corrections.
- **RULE TE-107**: Portfolio insurance (dynamic hedging) is DESTABILIZING when many use it. It creates PREDICTABLE sell orders on price drops. Order anticipators front-run. Same with stop-loss orders — use sparingly.
- **RULE TE-108**: Trading halts change pricing from DISCRIMINATORY (each order gets limit price) to UNIFORM (single clearing price). This protects liquidity suppliers. Trade at reopenings if you supply liquidity.
- **RULE TE-109**: Gravitational effect: circuit breakers can INCREASE volatility. Traders rush to trade before halts, fearing being locked out. Price limits attract panic orders.
- **RULE TE-110**: Traders PANIC when uncertain about risk. Not just uncertain about direction, but uncertain about their OWN exposure. In confusing situations (crashes), don't act hastily.

### From Trading and Exchanges Ch. 29 "Insider Trading" (2026-03-16)
- **RULE TE-111**: Insider trading INCREASES bid/ask spreads. More informed traders → more adverse selection → wider spreads. Markets with effective enforcement have narrower spreads.
- **RULE TE-112**: Competition among insiders to exploit information reveals it QUICKLY. If multiple insiders know, they race to trade → prices move → information leaks. Monopolist insiders trade slowly.

### From Evidence-Based TA Ch. 3 "The Scientific Method" (2026-03-17)
- **RULE EB-5**: Profitable backtest ≠ predictive power. A profitable backtest is CONSISTENT with predictive power but does NOT PROVE it. Committing this fallacy ("affirming the consequent") is the #1 error in TA research. Luck, data mining, or curve-fitting can also explain profits.
- **RULE EB-6**: Falsification is the only valid proof. You cannot logically prove a hypothesis TRUE with evidence. You can only prove it FALSE. A single counter-example (black swan) disproves universal claims. This is why null hypothesis testing works.
- **RULE EB-7**: Start with the null hypothesis. Always assume a TA rule has NO predictive power until evidence forces you to reject this assumption. The burden of proof is on the rule, not the skeptic.
- **RULE EB-8**: Require falsifiable predictions. Any TA method must generate SPECIFIC, TESTABLE predictions about future observations. Methods that only explain the past but cannot predict the future are pseudoscience — unfalsifiable and meaningless.
- **RULE EB-9**: Demand falsification conditions. Before accepting ANY forecast, ask: "What outcomes would prove this wrong?" If no clear answer, the forecast has zero information content. Examples: "Bullish" is meaningless. "Up 10% before down 5% in next 30 days" is testable.
- **RULE EB-10**: Occam's Razor for explanations. Prefer SIMPLER explanations. Random walk is preferable to complex pattern theories UNLESS the complex theory demonstrates superior OUT-OF-SAMPLE predictive power. Complexity is guilty until proven innocent.
- **RULE EB-11**: All knowledge is provisional. Even well-tested hypotheses are only provisionally true. They await falsification by future evidence. Never treat a strategy as "proven" — only as "not yet falsified."
- **RULE EB-12**: Subjective TA is meaningless. Methods that cannot be objectively defined and tested are not science. Elliott Waves, Gann Lines, and most chart patterns in their traditional form are unfalsifiable because practitioners can always explain away failures post-hoc.
- **RULE EB-13**: Statistical rigor required. Determining whether backtest results exceed luck requires statistical inference. Gut feel that results "look good" is confirmation bias in action. Calculate p-values or confidence intervals.
- **RULE EB-14**: Evidence quality matters. Sample size and representativeness affect conclusion strength. "Hasty generalization" from small samples is a common logical error. More data points + representative conditions = stronger inference.
- **RULE EB-15**: Ad-hoc immunization is fraud. If a theory is "saved" by inventing explanations AFTER contradictory evidence appears, it's pseudoscience. EMH defenders did this by inventing "risk factors" after TA strategies showed profits. This reduces information content to zero.
- **RULE EB-16**: Hypothetico-deductive method. The proper scientific process: (1) Observe pattern, (2) Hypothesize generalization, (3) Deduce testable predictions, (4) Test against NEW data, (5) Accept or reject via statistical inference. Most TA skips steps 3-5.

### From Evidence-Based TA Ch. 4 "Statistical Analysis" (2026-03-17)
- **RULE EB-17**: Sampling variability is real. Even a rule with zero predictive power will show profit/loss variation across different samples. This randomness is called sampling variability. One profitable backtest proves nothing.
- **RULE EB-18**: Law of Large Numbers. Larger samples reduce the impact of randomness. More trades = more reliable estimate of true performance. This is why minimum sample sizes exist.
- **RULE EB-19**: Understand the probability density. A profitable backtest result must be evaluated against the distribution of results a USELESS rule would produce. Only if your result falls in the extreme tail is it significant.

### From Evidence-Based TA Ch. 5 "Hypothesis Tests and Confidence Intervals" (2026-03-17)
- **RULE EB-20**: Type I error is worse than Type II. Type I = using a worthless rule (lose capital). Type II = missing a good rule (lose opportunity). Capital is finite, opportunities are not. Be conservative.
- **RULE EB-21**: P-value threshold = 0.05. Only reject the null hypothesis if p < 0.05. This means <5% chance the result occurred by luck. For trading, consider 0.01 given the costs of Type I errors.
- **RULE EB-22**: Confidence intervals > point estimates. A return of "15%" means nothing. A return of "15% with 95% CI of 5-25%" is meaningful. Always demand ranges.
- **RULE EB-23**: The absence of evidence is NOT evidence of absence. Failing to reject the null doesn't prove the rule is useless - it just means you don't have enough evidence to conclude it works.

### From Evidence-Based TA Ch. 6 "Data Mining Bias" (2026-03-17)
- **RULE EB-24**: Data mining SELECTION is valid. The rule with the best backtest IS most likely to perform best in the future (White proved this). So data mining to SELECT rules is legitimate.
- **RULE EB-25**: Data mining ESTIMATION is biased. The best rule's past performance systematically OVERSTATES its expected future performance. The bias is the difference between observed and expected.
- **RULE EB-26**: Bias scales with search size. Test 10 rules → small bias. Test 1000 rules → huge bias. A +37% return that looks amazing for a single rule is AVERAGE when you picked the best of 50.
- **RULE EB-27**: High randomness = high bias. Trading has extreme randomness (luck dominates skill). Therefore data mining bias in trading is SEVERE compared to domains where skill dominates (music, math).
- **RULE EB-28**: Adjust significance thresholds. When data mining, you must use MUCH higher performance thresholds to reject the null. A p=0.05 result after testing 100 rules is actually p≈1.0.
- **RULE EB-29**: Out-of-sample degradation is NOT "strategy decay." It's the strategy's TRUE performance revealing itself once the lucky bias of in-sample selection is removed.
- **RULE EB-30**: Bangladesh butter correlation. Leinweber found 0.70 correlation between Bangladesh butter production and S&P 500. Given enough search, SPURIOUS correlations appear. Plausibility doesn't validate correlations found by search.

### From Evidence-Based TA Ch. 7 "Theories of Nonrandom Price Motion" (2026-03-17)
- **RULE EB-31**: Behavioral finance explains TA. Cognitive errors cause BOTH: (a) false belief in subjective TA, AND (b) market inefficiencies that let objective TA work. Same biases, opposite effects.
- **RULE EB-32**: Two pillars of behavioral finance. (1) Limits of arbitrage — can't enforce rational prices perfectly. (2) Limits of rationality — investors make systematic errors. Combined → predictable departures from efficiency.
- **RULE EB-33**: Anchoring → underreaction → trends. Investors anchor on numbers (52-week high, prior price). Prices underreact to news, then drift toward rational level = exploitable trends.
- **RULE EB-34**: Overconfidence → overreaction → reversals. Investors overreact to private information. Prices overshoot, then reverse = exploitable mean-reversion.
- **RULE EB-35**: Crime of small numbers. Investors draw grand conclusions from short earnings streaks. Hasty generalization → overreaction → eventual correction.
- **RULE EB-36**: Information cascades block truth. Herding behavior blocks independent appraisals. Random first choice → imitative cascade → prices diverge from rational value.
- **RULE EB-37**: Disposition effect. Investors sell winners too early (to lock in gains) and hold losers too long (to avoid pain of realizing loss). Creates predictable price patterns.
- **RULE EB-38**: Futures trend-following earns risk-transfer premium. Trend-followers in futures earn premium (Sharpe 0.60) for absorbing hedgers' risk. This is PAYMENT for SERVICE, not free lunch.
- **RULE EB-39**: Stock trend-following earns less. Stock trend-following Sharpe = 0.05. No hedging premium exists. Must find different edges in equities.
- **RULE EB-40**: Stock mean-reversion earns liquidity premium. Buying oversold stocks on declining volume = providing liquidity to distressed sellers. Cooper found 44.95% vs 17.91% benchmark.
- **RULE EB-41**: TA signals = Help Wanted ads. Signals identify market needs: "Risk adopter for hire" or "Seeking liquidity provider — will pay." You're not getting free lunch; you're providing a service.

### From Evidence-Based TA Ch. 8-9 "Case Study & Results" (2026-03-17)
- **RULE EB-42**: 6,402 rules tested, ZERO significant. Aronson tested 6,402 TA rules on S&P 500 (1980-2005). After controlling for data mining bias, NOT A SINGLE RULE was statistically significant. This is the harsh reality.
- **RULE EB-43**: Data snooping bias is insidious. Using rules discovered by prior research makes proper evaluation IMPOSSIBLE because you don't know how much mining led to their discovery. Avoid famous "proven" rules.
- **RULE EB-44**: Three-way data split required. Training (optimize parameters), Testing (optimize complexity), Validation (unbiased performance estimate). Test set gets "used up" by repeated visits.
- **RULE EB-45**: Detrend market data. A long-biased rule on uptrending data looks good but proves nothing. Remove market trend before computing rule returns.
- **RULE EB-46**: Avoid look-ahead bias. If you need closing price to compute signal, you CAN'T execute at close. First valid execution is next day's open.
- **RULE EB-47**: Human-computer synergy. Humans: good at inventing indicators (creative). Bad at testing them (confirmation bias). Computers: bad at inventing (not creative). Good at testing (no bias). Use both.
- **RULE EB-48**: Subjective forecasting is futile. 50 years of evidence: statistical models beat expert judgment in EVERY domain studied. Experts don't understand their own reasoning, are inconsistent, and affected by emotions.
- **RULE EB-49**: Feature engineering > model selection. Better indicators matter MORE than better models. "Even a primitive prediction model can perform well if variables are preprocessed to clearly reveal information." — Masters
- **RULE EB-50**: The curse of dimensionality. Adding indicators requires EXPONENTIALLY more data. 2 dimensions = 100 observations. 3 dimensions = 1,000. 4 dimensions = 10,000. Data mining hits a wall.
- **RULE EB-51**: Optimal complexity exists. Underfitting (too simple) misses patterns. Overfitting (too complex) fits noise. Keep adding complexity until TEST SET performance peaks, then stop.

### From Algorithmic Trading Ch. 1 "Backtesting and Automated Execution" (2026-03-17)
- **RULE AT-1**: Backtest-to-live Sharpe ratio ≈ 0.5. "Most traders would be happy to find that live trading generates a Sharpe ratio better than half of its backtest value." Expect 50% degradation.
- **RULE AT-2**: Same code for backtest and live. If your backtest program can be transformed into live execution "by the push of a button," you eliminate look-ahead bias by construction.
- **RULE AT-3**: Linear models beat nonlinear. Nonlinear models have more parameters, more complexity, and fit noise better. "Simple linear approximation exists for every nonlinear model."
- **RULE AT-4**: Equal weights often beat optimized weights. "Formulas that assign equal weights to all predictors are often superior, because they are not affected by accidents of sampling." — Kahneman
- **RULE AT-5**: Cross-validation for small datasets. If unwilling to discard model after poor out-of-sample test, use multiple train/test splits and ensure performance across ALL of them.
- **RULE AT-6**: Survivorship bias affects longs more than shorts. Long-only mean-reversion inflated by missing bankruptcies. Short-only deflated. Long-short partially cancels but still dangerous.
- **RULE AT-7**: Use PRIMARY exchange prices for MOC/MOO. Consolidated prices include outliers from secondary exchanges. Mean-reversion backtests will be inflated if using consolidated data.
- **RULE AT-8**: Small-caps harder to short. Short-sale constraints affect small-caps much more than large-caps. Backtest short profits on small-caps are suspect.
- **RULE AT-9**: Futures continuous contracts: pick ONE metric. Price back-adjustment → correct P&L, wrong return. Return back-adjustment → correct return, wrong P&L. Can't have both.
- **RULE AT-10**: Use settlement prices, not last traded. Settlement prices are contemporaneous across contracts. Last traded may be hours old. Critical for spread strategies.
- **RULE AT-11**: Regime shifts destroy backtests. Decimalization (2001), 2008 crisis, Reg NMS (2007), uptick rule changes all fundamentally changed market structure. Pre-shift backtests are worthless.
- **RULE AT-12**: Never manually override the model. "I have found that it is seldom a good idea to manually override a model no matter how treacherous the market is looking."
- **RULE AT-13**: Underleveraged > overleveraged. "It is always better to be underleveraged than overleveraged, especially when managing other people's money."
- **RULE AT-14**: Strategy performance mean-reverts. Hot strategies cool off. Cold strategies warm up. Don't chase recent performance.
- **RULE AT-15**: Overconfidence is the greatest danger. "Overconfidence in a strategy is the greatest danger to us all."

### From Algorithmic Trading Ch. 2 "The Basics of Mean Reversion" (2026-03-17)
- **RULE AT-16**: Test for stationarity BEFORE backtesting. ADF test, Hurst exponent, Variance Ratio tests have higher statistical power than backtest results because they use every bar, not just trades.
- **RULE AT-17**: Half-life determines tradability. Half-life = -log(2)/λ. If half-life > your trading horizon, the strategy won't work. If λ > 0 (positive), NOT mean-reverting at all.
- **RULE AT-18**: Look-back = half-life. Set moving average and standard deviation look-backs equal to the half-life. This avoids brute-force parameter optimization.
- **RULE AT-19**: Linear strategy = position proportional to -Z-score. Parameterless: no optimization required. If price series is stationary, this WILL be profitable (only question is how much).
- **RULE AT-20**: Cointegration creates stationarity. Most individual price series are NOT stationary. But combinations (portfolios) can be. Pairs trading is simplest example.
- **RULE AT-21**: CADF for pairs, Johansen for N assets. CADF finds optimal hedge ratio for 2 series. Johansen handles any number and outputs eigenvectors as hedge ratios.
- **RULE AT-22**: Use highest eigenvalue eigenvector. Eigenvectors from Johansen test ordered by eigenvalue. Highest eigenvalue → shortest half-life → best portfolio for trading.
- **RULE AT-23**: Mean reversion invites overleverage. High consistency lulls traders into overconfidence. When breakdown comes (and it will), you're at max leverage. Think LTCM.
- **RULE AT-24**: Stop losses DON'T work for mean reversion. Stopping out when price moves against you is the OPPOSITE of what mean reversion logic dictates. Risk management must be different.
- **RULE AT-25**: Fundamental stories behind cointegration. EWA/EWC = both commodity economies. GDX/GLD = gold mining tracks gold price. Understanding WHY helps detect when it breaks.

### From Algorithmic Trading Ch. 3 "Implementing Mean Reversion Strategies" (2026-03-17)
- **RULE AT-26**: Price spreads = fixed shares; log spreads = fixed capital weights. y = h₁y₁ + h₂y₂ gives hedge ratio in SHARES. log(q) = h₁log(y₁) + h₂log(y₂) gives hedge ratio in CAPITAL WEIGHTS requiring constant rebalancing. Choose based on what you want to hold constant.
- **RULE AT-27**: Ratio works better for non-cointegrated pairs. When pairs aren't truly cointegrating but you believe short-term mean reversion exists, using y₁/y₂ as signal often outperforms price or log price spreads. Why? Ratio stays constant even if both prices 10x.
- **RULE AT-28**: Bollinger Bands for practical position sizing. Linear strategy is parameterless but has unknown max capital deployment. Bollinger bands with entryZscore and exitZscore give defined position sizes (0 or 1 unit).
- **RULE AT-29**: Scaling-in is NEVER in-sample optimal. Schoenberg-Corwin (2010) proved: for any averaging-in strategy, you can always find a single entry level ("all-in") with higher expected profit in backtest. But scaling-in often beats all-in OUT-of-sample because volatility and probabilities change in real life.
- **RULE AT-30**: Kalman filter > moving lookback for hedge ratio. No arbitrary cutoff, weights recent data more smoothly, gives you dynamic hedge ratio AND mean AND standard deviation simultaneously. Optimal linear estimator if noise is Gaussian.
- **RULE AT-31**: Kalman filter δ parameter controls adaptation speed. δ = 0 → ordinary least squares (hedge ratio never changes). δ = 1 → wild swings based on latest observation. Typical value: δ ≈ 0.0001. Optimize on training data.
- **RULE AT-32**: Kalman filter for market making. Beyond pairs, Kalman filter can estimate "fair value" from trades weighted by size. Large trades → high confidence → Kalman gain → 1 → estimate = trade price. Small trades → discount heavily.
- **RULE AT-33**: Data errors INFLATE mean-reversion backtests. A bad quote ($100 → $110 → $100) creates fake short profit: backtest shorts at $110, covers at $100, books $10 phantom gain. Momentum backtests DEFLATED by same errors (buys high, stopped out at real price).
- **RULE AT-34**: Spread strategies are hypersensitive to data errors. If X bid = $100, Y ask = $105, spread = $5. A 1% error in Y ($106 instead of $105) = 20% error in spread ($6 vs $5). Use reputable data feeds — NOT broker data. Chan switched from broker feed to Bloomberg and bad trades stopped.

### From Algorithmic Trading Ch. 4 "Mean Reversion of Stocks and ETFs" (2026-03-17)
- **RULE AT-35**: Stock pairs trading is dead (for most traders). Individual stocks' fundamentals change too fast. Even if cointegrated in-sample, they break out-of-sample. Law of large numbers doesn't help if expected return per pair is negative. "Good" pairs' small profits overwhelmed by "bad" pairs' large losses.
- **RULE AT-36**: ETF pairs > stock pairs. ETFs represent baskets; economic factors change more slowly than individual company fundamentals. EWA/EWC (Australia/Canada) still cointegrate years after publication. ETF selection is easy: find exposure to common economic factors.
- **RULE AT-37**: Commodity ETF + producer ETF can work. GLD/GDX (gold vs gold miners) cointegrated until July 2008. What broke it? Oil peaked at $145 — mining costs spiked, miner profits fell. Solution: add USO to make triplet. When strategy breaks, form hypothesis, test empirically, modify strategy.
- **RULE AT-38**: Beware ETFs holding futures, not commodities. USO doesn't own oil — it owns oil futures. Futures price ≠ spot price. Even if XLE (energy stocks) cointegrates with spot oil, it may NOT cointegrate with USO. Prefer commodity funds that hold actual commodity (like GLD holds gold).
- **RULE AT-39**: NBBO sizes for stocks are tiny. AAPL can have NBBO of just 100 shares! Dark pools, iceberg orders, HFT all reduce displayed size. Backtesting with NBBO prices unrealistic unless you trade tiny size or include substantial transaction costs. Send limit orders and manage fills actively.
- **RULE AT-40**: Short squeeze risk is real. Hard-to-borrow stocks can be recalled at the worst time — when stock spikes up and lenders want to sell. You're forced to cover at max loss. Alternative uptick rule (2010) also constrains shorting when circuit breaker triggered.
- **RULE AT-41**: Buy-on-Gap model works. Stocks that gap down >1 SD but are ABOVE 20-day MA tend to revert intraday. Key insight: the MA filter is crucial — it avoids stocks with real bad news. Drops from liquidity demands revert; drops from fundamental news don't.
- **RULE AT-42**: Momentum filter on mean reversion. Superimposing momentum filter (price > long-term MA) on mean-reverting strategies typically improves consistency. Why? Long-only funds selling creates temporary liquidity demand, not fundamental repricing.
- **RULE AT-43**: Index arbitrage is arbitraged out — unless you use a subset. Traditional stocks vs futures has no edge left. But select SUBSET of index stocks that individually cointegrate with ETF/future, then trade that portfolio vs the index. Increases spread, restores profitability.
- **RULE AT-44**: HFT index arbitrage exploits two deficiencies: (1) Major indices use only primary exchange data (<30% of volume), (2) Index updated only every few seconds. HFTs with direct feeds see true basket value before index updates. Not practical for retail.
- **RULE AT-45**: Cross-sectional mean reversion ≠ time series mean reversion. Individual stocks don't revert to their OWN historical mean. Their RELATIVE returns revert: underperformers outperform next period, overperformers underperform. Statistical tests for stationarity are irrelevant for cross-sectional strategies.
- **RULE AT-46**: Linear long-short model is parameterless. w_i = -(r_i - avg(r_j)) / Σ|r_k - avg(r_j)|. Completely linear, no parameters, perfectly dollar neutral. 13.7% APR, Sharpe 1.3 on SPX (2007-2011). Survived 2008 crisis and 2011 debt downgrade.
- **RULE AT-47**: Intraday cross-sectional even better — with caveats. Use close-to-open returns for signal, exit at close. 73% APR, Sharpe 4.7. BUT: double transaction costs, signal noise from using open prices to generate open signals. True performance will be lower.
- **RULE AT-48**: P/E ratio as alternative ranking factor. Instead of relative returns, can rank stocks by P/E change. Avoid shorting stocks with positive earnings estimate changes — those moves are fundamental, not mean-reverting.
- **RULE AT-49**: Survivorship bias warning. All stock backtests in this chapter use survivorship-biased data (missing bankruptcies, delistings). Need historical index compositions for proper backtest. Results are optimistic.
- **RULE AT-50**: Primary vs consolidated price pitfall. MOO/MOC orders fill at PRIMARY exchange prices. Consolidated prices include outliers from secondary exchanges. Backtests using consolidated prices will be optimistic for mean-reversion strategies.

### From Algorithmic Trading Ch. 5 "Mean Reversion of Currencies and Futures" (2026-03-17)
- **RULE AT-51**: Commodity currencies cointegrate. AUD, CAD, ZAR (South African rand), NOK (Norwegian krone) share mining/commodity revenues → similar economic fundamentals → cointegration opportunities. Same logic as EWA/EWC.
- **RULE AT-52**: Currency trading advantages over ETF pairs. Higher liquidity (especially bid/ask sizes), higher leverage available, NO short-sale constraints, 24/5 trading makes stop losses meaningful (no overnight gaps within trading week).
- **RULE AT-53**: Quote currency must match for Johansen test. When testing cointegration of B1.Q1 vs B2.Q2, need same quote currency so point moves have same dollar value. Convert USD.CAD to CAD.USD (invert) before running Johansen. Eigenvector meaningless otherwise.
- **RULE AT-54**: Regularly convert P&L to local currency. Trading synthetic AUD.ZAR realizes P&L in BOTH AUD and ZAR. Must convert to USD regularly or live results will diverge from backtest. Accumulated foreign currency = unhedged currency exposure.
- **RULE AT-55**: Rollover interest for overnight FX positions. Long B.Q overnight = earn iB - iQ daily. TRIPLE rollover on Wednesdays (T+2 settlement → covers weekend). USD.CAD and USD.MXN settle T+1 → triple on Thursdays instead. Material for swing trading.
- **RULE AT-56**: Futures total return = spot return + roll return. Model: F(t,T) = S(t)exp(γ(t-T)). γ = roll return. Backwardation = γ > 0 (near contracts higher than far). Contango = γ < 0 (near contracts lower than far).
- **RULE AT-57**: Mnemonic for backwardation: "normal." Keynes/Hicks: hedgers (farmers, producers) short futures, speculators go long. Speculators need compensation → positive roll → futures < expected spot → "normal backwardation."
- **RULE AT-58**: Roll returns can dominate spot returns. BR: spot -2.7%, roll +10.8%. Corn: spot +2.8%, roll -12.8%. TU: spot 0%, roll +3.2%. VX: roll -50%! When |roll| > |spot|, roll return drives total return.
- **RULE AT-59**: VIX is stationary; VX futures are NOT. VIX mean-reverts (ADF test passes with 99% confidence). But VX is in contango ~75% of time with -50% annualized roll return. Back-adjusted VX does NOT mean-revert — it just declines inexorably.
- **RULE AT-60**: Calendar spread signal depends only on roll return. Log spread = γ(T₁-T₂). Spot price cancels out completely. Mean reversion of calendar spreads requires mean reversion of ROLL RETURNS, not spot prices.
- **RULE AT-61**: CL 12-month calendar spread IS mean-reverting. ADF test: stationary with 99% confidence, half-life 36 days. Linear mean reversion strategy: APR 8.3%, Sharpe 1.3 (2008-2012).
- **RULE AT-62**: VX calendar spread requires different model. VIX is not a traded asset → F(t,T) model doesn't work → log prices don't fall on straight line. Use ratio (back/front) as signal instead — that IS stationary.
- **RULE AT-63**: Crack spread (3:2:1 CL:RB:HO) doesn't mean-revert. Despite theoretical refinery relationship, ADF test fails. Dramatic regime shift March 2007 - July 2008. Fundamental relationships can break.
- **RULE AT-64**: CL-BZ (WTI vs Brent) spread doesn't mean-revert. Both crude oil, but US production surge, Cushing pipeline bottleneck, Iran embargo caused persistent BZ outperformance. Don't assume similar underlyings → cointegration.
- **RULE AT-65**: VX-ES spread IS mean-reverting (post-2008 regime). Regression: ES×50 = -0.3906×VX×1000 + $77,150. Long 0.3906 VX + long 1 ES is stationary. APR 12.3%, Sharpe 1.4. But note: TWO regimes visible in scatter plot — don't mix data from both.

### From Algorithmic Trading Ch. 6 "Interday Momentum Strategies" (2026-03-17)
- **RULE AT-66**: Four causes of momentum: (1) Persistence of roll returns (futures), (2) Slow diffusion/analysis/acceptance of new info (stocks), (3) Forced sales/purchases by funds, (4) HFT market manipulation. Different causes → different time horizons.
- **RULE AT-67**: Test time-series momentum with NON-OVERLAPPING periods. Compute correlation between look-back return and future return. If look-back > hold, shift forward by hold days. If hold > look-back, shift forward by look-back. Overlapping data = spurious correlations.
- **RULE AT-68**: Hurst exponent misses time-frame-specific momentum. A series can mean-revert at 1-day horizon but momentum at 250-day horizon. Hurst/Variance Ratio aggregate across all horizons. Must test specific (look-back, holding) pairs separately.
- **RULE AT-69**: Futures time-series momentum works via roll return persistence. TU (2-year Treasury): 250-day lookback, 25-day hold → Sharpe 1.04. Roll return rarely changes sign, so past return predicts future return.
- **RULE AT-70**: Use roll return as signal, not total return. Cleaner signal. Go long when annualized roll return > threshold, short when < -threshold, flat otherwise. TU with 3% threshold: APR 2.5%, Sharpe 2.1 (vs 1.7%/1.04 using total return).
- **RULE AT-71**: XLE-USO arbitrage extracts roll returns. CL in contango → short USO, long XLE. CL in backwardation → long USO, short XLE. APR 16%, Sharpe 1.0. Works because XLE tracks spot oil, USO tracks futures.
- **RULE AT-72**: VX-ES momentum strategy. Different from mean-reversion (AT-65). Short VX + short ES when VX in contango. Long VX + long ES when backwardation. Signal = (VX front - VIX) / days to settlement. Profits from roll return extraction.
- **RULE AT-73**: Cross-sectional momentum: rank by 12-month return, buy top, short bottom. Works for futures, stocks, currencies, world indices. Hold 1 month. Daniel-Moskowitz found it works on "practically everything under the sun."
- **RULE AT-74**: Cross-sectional momentum COLLAPSED post-2008. Futures cross-sectional: +18% pre-2008, -33% during 2008-2009. Stocks same pattern. Daniel-Moskowitz: after 1929 crash, momentum didn't recover for 30+ YEARS. Cause: strong rebound of shorts after crash.
- **RULE AT-75**: S&P DTI index (Diversified Trends Indicator). Long futures above EMA, short below, monthly rebalance. Sharpe 1.3, max DD -16.6% (1988-2010). But -25.9% drawdown since Dec 2008 crisis. Momentum strategies suffer post-crisis.
- **RULE AT-76**: News sentiment as momentum factor. RavenPack sentiment: buy stocks with positive sentiment change, short negative. APR 52-156%, Sharpe 3.9-5.3 (before costs). Proves slow news diffusion causes momentum.
- **RULE AT-77**: Mutual fund fire sales cause momentum. Funds facing redemptions dump existing holdings → price pressure. Funds with inflows buy MORE of existing holdings (not new ideas). Holdings data = quarterly.
- **RULE AT-78**: Fire sale contagion amplifies momentum. Fund A's fire sale depresses stock → hurts Fund B holding same stock → Fund B faces redemptions → Fund B fire sales → further depression. Herding.
- **RULE AT-79**: Front-running mutual funds works. Fund flows predictable from past performance. PRESSURE factor: count funds buying vs selling stock. Top decile vs bottom decile → 17% APR. Front-running adds another 17%.
- **RULE AT-80**: Mean reversion AFTER fire sales. Stocks that experienced max selling pressure (bottom PRESSURE decile) eventually revert. Buy 1-4 quarters after fire sale → additional 7% APR. Total combined strategy: 41% APR.
- **RULE AT-81**: Momentum vs mean-reversion risk profiles are OPPOSITE. Momentum: limited downside (stops work), unlimited upside, lower Sharpe (fewer signals), collapses post-crisis, thrives on black swans. Mean-reversion: limited upside, unlimited downside (stops contradict entry), higher Sharpe, survives crises better.
- **RULE AT-82**: Combine momentum + mean-reversion for best Sharpe. Different strategies thrive in different market regimes. Combining achieves higher Sharpe and smaller drawdowns than either alone. True diversification.

### From Algorithmic Trading Ch. 7 "Intraday Momentum Strategies" (2026-03-17)
- **RULE AT-83**: Intraday momentum avoids interday momentum drawbacks. Shorter holding period → higher Sharpe, more statistical significance, doesn't collapse post-crisis. Only drawback: roll return persistence not relevant intraday.
- **RULE AT-84**: Stop triggering causes breakout momentum. Extended period without trading (overnight, weekend) → stops accumulate at different prices → all triggered at once at open → cascade effect drives price further.
- **RULE AT-85**: Opening gap momentum works for futures/FX. Buy gaps up, short gaps down. FSTX (EuroStoxx 50): APR 13%, Sharpe 1.4. GBPUSD (London open vs NY close): APR 7.2%, Sharpe 1.3.
- **RULE AT-86**: PEAD (Post-Earnings Announcement Drift) still works. Buy if prev-close-to-open return > 0.5σ after earnings, short if < -0.5σ. Enter at open, exit at close. APR 6.7%, Sharpe 1.5 (2011-2012).
- **RULE AT-87**: PEAD duration has shortened over time. Used to last days (1968 research), now barely lasts until market close. Duration shortens as more traders learn about it. May need even shorter holding period in future.
- **RULE AT-88**: Index rebalancing causes momentum. Stocks added to index = buying pressure, deleted = selling pressure. Drift now reduced to intraday (used to be days). Forced buying/selling by index funds.
- **RULE AT-89**: Leveraged ETF rebalancing causes end-of-day momentum. 3x ETFs must rebalance daily to maintain leverage. Market down → must sell more → momentum down. Market up → must buy more → momentum up. Direction = same as day's return.
- **RULE AT-90**: Leveraged ETF momentum strategy. Buy DRN (3x real estate) if return from prev close to 15 min before close > 2%, sell if < -2%. Exit at close. APR 15%, Sharpe 1.8. Effect grows as total leveraged ETF AUM grows.
- **RULE AT-91**: HFT momentum from bid-ask imbalance. If bid size >> ask size → price will tick up. Approximately linear relationship (Maslov-Mills). Stronger effect for lower volume stocks. Imbalance of entire order book also predictive.
- **RULE AT-92**: HFT tactics: ratio trade (join large bid, get pro-rata fill), ticking (front-run by 1 tick when spread > 2 ticks), momentum ignition (fake large bid to trigger buying, then sell to buyers).
- **RULE AT-93**: Stop hunting exploits stop order clusters. Stops cluster at round numbers and support/resistance levels. Sell aggressively near support → trigger stops → cascade down → cover short for profit.
- **RULE AT-94**: Order flow predicts short-term price movement. Signed transaction volume: positive = market buy at ask, negative = market sell at bid. Large one-directional flow = informed traders → price will move same direction.
- **RULE AT-95**: Why HFT strategies prey on slower traders. Large orders now broken into tiny child orders to avoid detection. NBBO sizes tiny (even AAPL often just 100 shares). Flippers can be detected by tracking order cancellation rates.

### From Algorithmic Trading Ch. 8 "Risk Management" (2026-03-17)
- **RULE AT-96**: Goal is maximizing long-term growth rate, not minimizing risk. Avoid risk only insofar as it interferes with growth. Loss aversion ($2 upside needed to compensate $1 downside) is emotional, not rational.
- **RULE AT-97**: Constant leverage is CENTRAL to risk management. After loss → reduce position size to maintain leverage. After win → increase size. Counterintuitive but mathematically optimal for growth rate.
- **RULE AT-98**: Kelly formula: f = m/s² (mean excess return / variance). Maximizes compounded growth rate assuming Gaussian returns. Growth rate g = fm - f²s²/2.
- **RULE AT-99**: Use half-Kelly for safety. Full Kelly = upper bound. Overestimated mean or underestimated variance → ruin. Estimation error is inevitable. Half-Kelly sacrifices some growth for survival.
- **RULE AT-100**: Kelly leverage often exceeds what's sensible. Triple-leveraged ETFs (leverage 3) have Kelly leverage ~1.8 for underlying index. By design, these ETFs will eventually go to zero. Never buy and hold.
- **RULE AT-101**: With max leverage constraint, don't scale proportionally. If broker limits total leverage below Kelly sum, often optimal to put ALL capital into single highest-growth-rate strategy, not distribute among all.
- **RULE AT-102**: Monte Carlo for fat-tailed returns. When Gaussian assumption fails, use Pearson system (4 moments → distribution), simulate 100,000 returns, numerically optimize leverage. Often gives similar answer to Kelly.
- **RULE AT-103**: Max drawdown ≠ proportional to leverage. Halving leverage does NOT halve max drawdown. May need to reduce leverage by 7x to halve drawdown! Very nonlinear relationship. Must simulate to find right level.
- **RULE AT-104**: CPPI (Constant Proportion Portfolio Insurance). Set aside D of equity for trading (rest in cash). Apply Kelly leverage to subaccount only. Guarantees max drawdown ≤ -D while optimizing growth. Graceful strategy wind-down.
- **RULE AT-105**: Stop loss for mean-reversion: set above backtest max. Stop should NEVER trigger in backtest. Won't hurt backtest performance but protects against regime change → trending that wasn't in backtest. Survivorship bias in backtests hides strategies that would've been stopped out.
- **RULE AT-106**: Stop loss for momentum: natural and logical. If momentum reverses, you should exit anyway — trailing stop is de facto part of momentum strategy. Unlike mean-reversion, stop loss is consistent with entry logic.
- **RULE AT-107**: Stop loss useless during gaps and flash crashes. May 6, 2010: Accenture stop executed at $0.01 (stub quote). Overnight gaps can blow through stops. Options needed for expected closures.
- **RULE AT-108**: VIX as leading risk indicator: strategy-dependent. VIX > 35 HURTS FSTX gap strategy (APR drops to 2.6%) but HELPS stock buy-on-gap (APR rises to 17.2%). Test for your specific strategy.
- **RULE AT-109**: TED spread (LIBOR - T-bill) as risk indicator. Measures bank default risk. Less subject to retail herd instinct than VIX. Rose to 457 bps in 2008 crisis. Institutional signal.
- **RULE AT-110**: Order flow as short-term leading risk indicator. Large negative order flow in risky assets (stocks, commodities) = informed traders exiting BEFORE price drops. Positive flow into safe assets (treasuries, USD) same signal.

### From How to Day Trade for a Living Ch. 1 "Introduction" (2026-03-17)
- **RULE DT-1**: Day trading is NOT a get-rich-quick scheme. Only 16% of day traders make money after 6 months (Massachusetts court records). The 84% failure rate is comparable to startup failure rates. Treat it as a profession requiring years of training.
- **RULE DT-2**: Day trading is a SERIOUS BUSINESS — treat it as such. Not a hobby, not a weekend pursuit. Wake up early, prepare, be seated at your station like any job. You're competing against the sharpest minds in the world.
- **RULE DT-3**: Consistent successful traders = $500-$1,000/day = $120K-$240K/year. Why would anyone expect a job that pays this well to be EASY? Doctors, lawyers, engineers go through years of training. Day trading is no different.
- **RULE DT-4**: 6-8 months to consistent profitability on average. Don't believe "make money from day one" courses. Some take a year. The learning curve is brutal but cannot be skipped — only accelerated via simulator trading.
- **RULE DT-5**: Business plan REQUIRED before starting. Budget: education ($1,500+ first year), computer + monitors, scanner software, platform fees, data feeds. Like any business, undercapitalization = failure.

### From How to Day Trade for a Living Ch. 2 "How Day Trading Works" (2026-03-17)
- **RULE DT-6**: Day traders do NOT hold positions overnight. NEVER. If necessary, sell at a loss before market close. Turning a day trade into a swing trade because you don't want to accept a loss = recipe for disaster.
- **RULE DT-7**: "Is this stock moving because the MARKET is moving, or because it has a UNIQUE CATALYST?" Only trade stocks with fundamental catalysts (earnings, FDA, M&A, guidance). Stocks moving only with market = dominated by algorithms.
- **RULE DT-8**: Retail traders = guerrilla warfare. Hit-and-run tactics. Don't try to defeat institutional traders — wait for opportunities to reach daily profit target, then STOP. Your advantage: you can choose NOT to trade.
- **RULE DT-9**: New traders start with 100 shares ONLY. Low risk, low reward, but you MUST start somewhere. At 100 shares, you have no excuse for not getting out when stop loss hits. Institutional traders can't exit 1M shares that fast.
- **RULE DT-10**: Stay where retail traders are. Trade Stocks in Play that other retail traders are watching. Don't trade AAPL/MSFT/KO — slow, dominated by institutions. Find what's gapping, what has volume, what the chatrooms are discussing.
- **RULE DT-11**: HFT can be beaten. The programs trade against each other — not all can win. Identify algorithmic patterns and trade against them. Or ride WITH them (e.g., short squeezes). Complaining about algorithms = excuse-making.
- **RULE DT-12**: Trade only the first 1-2 hours (9:30-11:30 AM ET). Most volume, most volatility, most liquidity. Mid-day (12-3 PM) = low volume = vulnerable to HFT. Avoid pre-market = low liquidity, erratic moves.
- **RULE DT-13**: Once you hit daily profit goal, STOP trading (or switch to simulator). Losing money in day trading is easy. Overtrading destroys profits.

### From How to Day Trade for a Living Ch. 3 "Risk and Account Management" (2026-03-17)
- **RULE DT-14**: Minimum win:lose ratio = 2:1. If risking $100, must target at least $200 profit. With 2:1 ratio, you can be wrong 40% of time and still make money. Never take trades with ratio < 2:1.
- **RULE DT-15**: Stop loss must be at a TECHNICAL level. Don't set arbitrary stop to get better ratio — set stop where the trade thesis is INVALIDATED (e.g., above VWAP, below support). If that makes ratio < 2:1, skip the trade.
- **RULE DT-16**: The 2% Rule — NEVER risk more than 2% of account on any single trade. $50K account = max $1,000 risk per trade. This is UNBREAKABLE. Protects 98% of account at all times.
- **RULE DT-17**: Three-Step Position Sizing: (1) Max dollar risk = 2% of account, (2) Stop loss distance in $/share, (3) Max shares = Step 1 ÷ Step 2. You can always risk LESS, never MORE.
- **RULE DT-18**: Your ONLY job is managing risk. Your broker buys/sells stocks. You manage risk. You cannot succeed without excellent risk management, even if you master many strategies.
- **RULE DT-19**: You will NOT be right all the time. Profitable traders lose ~30% of trades. A good trading day = DISCIPLINED day, not profitable day. Negative P&L ≠ bad trading day if you followed rules.
- **RULE DT-20**: "Live to play another day." Survive the learning curve. Take SMALL losses. ONE crazy move can wipe out your account. Small loss + get out + re-enter when setup is ready.
- **RULE DT-21**: Physical health = trading performance. Nutrition, sleep, exercise, no substances. Fatigue/tension/illness → impaired judgment. Keep daily record of physical state + trading results.
- **RULE DT-22**: Don't personalize losses. Successful traders trade for SKILL, not money. Hide unrealized P&L while in trade. Focus on perfect execution of plan, not dollar amounts.
- **RULE DT-23**: If under pressure, DO NOT TRADE. Take a walk. Release stress. Don't restart until focused and calm. After bad loss, trade in SIMULATOR until emotionally recovered.
- **RULE DT-24**: Discipline is a muscle — requires constant exercise. You never "arrive." Overconfidence = market will slap you. Stay humble, keep learning.

### From How to Day Trade for a Living Ch. 4 "How to Find Stocks for Trades" (2026-03-17)
- **RULE DT-25**: "You are only as good as the stocks you trade." Best trader in wrong stock = losing money. Stock selection is STEP ONE of risk management.
- **RULE DT-26**: Trade ONLY "Stocks in Play" — high relative volume + fundamental catalyst + trading independent of overall market. If stock moves only because market moves, it's dominated by algorithms. Stay away.
- **RULE DT-27**: High relative volume is RELATIVE to that stock's average. 20M shares of FB might be normal. Look for UNUSUAL volume for THAT specific stock. Normal volume = HFT territory.
- **RULE DT-28**: Float categories determine strategy: LOW float (<20M, <$10) = Momentum ONLY, very dangerous. MEDIUM float (20-500M, $10-100) = All strategies, esp. VWAP. LARGE float (>500M) = Moving Average & Reversal.
- **RULE DT-29**: Avoid low float stocks under $10. Extremely volatile (can move 100%+). Highly manipulated. Only for very experienced traders. Can't short them. Beginners will get wiped out.
- **RULE DT-30**: Pre-market Gapper criteria: (1) Gap ≥2%, (2) Pre-market volume ≥50K shares, (3) Avg daily volume ≥500K, (4) ATR ≥$0.50, (5) Has fundamental catalyst, (6) Short interest <30%.
- **RULE DT-31**: From 4,000+ stocks, scanner narrows to ~17 gappers → you pick 2-3 best candidates. You CANNOT watch 17 stocks. Focus on best 2-3.
- **RULE DT-32**: Avoid high short interest (>30%). These stocks prone to short squeezes — dangerous if you're short. Let others play that game.
- **RULE DT-33**: Check if multiple stocks in same sector are moving. If yes, it's sector rotation by institutions, NOT Stocks in Play. The stock must be moving INDEPENDENTLY of its sector.
- **RULE DT-34**: Real-time scanners for intraday setups: Volume Radar (gap ≥$1, ATR >$0.50, rel vol ≥1.5x), Bull Flag Momentum (low float, high activity), Reversal (stocks selling off hard or surging).
- **RULE DT-35**: Guerrilla trading = 2-3 trades per day MAX. Jump in at right time, take profit, get out. More trades ≠ more profit. Overtrading makes your BROKER rich, makes you BROKER.
- **RULE DT-36**: Day trading should be BORING. If it's exciting, you're probably overtrading. Most time spent watching and waiting. Quality > quantity.

### From How to Day Trade for a Living Ch. 5 "Tools and Platforms" (2026-03-17)
- **RULE DT-37**: Direct-access broker REQUIRED for day trading. Full-service brokers too slow. Need execution in fractions of a second. IB, Lightspeed, CMEG (offshore) are examples.
- **RULE DT-38**: PDT Rule: $25,000 minimum equity required to day trade in US. If under $25K, use offshore broker (CMEG, Alliance Trader) — but higher risk, withdraw funds regularly.
- **RULE DT-39**: Margin is double-edged sword. 3:1 to 6:1 leverage. Enhances gains AND losses. Use responsibly. Margin call = serious warning, account may be frozen.
- **RULE DT-40**: Fast trading platform with HOTKEYS is mandatory. Can't day trade profitably without Hotkeys. One click away from disaster or profit. DAS Trader, Lightspeed Trader recommended.
- **RULE DT-41**: Real-time Level 2 data REQUIRED. End-of-day data is NOT enough. Level 2 = order book, leading indicator. Shows who's buying/selling BEFORE trades happen.
- **RULE DT-42**: Keep charts CLEAN — minimal indicators. Too many = confusion + slow decisions. Use: Candlesticks, Volume, 9 EMA, 20 EMA, 50 SMA, 200 SMA, VWAP, previous close. That's IT.
- **RULE DT-43**: VWAP is the MOST important day trading indicator. Color it differently (blue). All other MAs in gray. VWAP = institutional benchmark.
- **RULE DT-44**: NEVER use market orders. Use MARKETABLE LIMIT orders. Buy at "ask + 5 cents", sell at "bid - 5 cents". Limits slippage while ensuring fill. Market orders = blank check.
- **RULE DT-45**: Master Hotkeys in SIMULATOR first. Common to make mistakes when learning. Use stickers on keyboard. Always use WIRED keyboard (wireless can fail). Keep backup keyboard ready.
- **RULE DT-46**: SSR (Short Sale Restriction) triggered when stock down 10%+ from previous close. Can only short on ASK, not bid. Real sellers get priority over short sellers.
- **RULE DT-47**: Join trading community but THINK INDEPENDENTLY. Don't blindly follow the crowd. Use community for learning, questions, emotional support. But make your own decisions.
- **RULE DT-48**: Commission-free brokers (Robinhood) NOT suitable for day trading. Platform crashes, slow execution. Opportunity cost > commission savings. Pay for reliability.

### From How to Day Trade for a Living Ch. 6 "Introduction to Candlesticks" (2026-03-17)
- **RULE DT-49**: Hollow candlesticks (close > open) = buying pressure, buyers in control. Filled candlesticks (close < open) = selling pressure, sellers in control. Read candles as a BATTLE.
- **RULE DT-50**: Day trading = study of MASS PSYCHOLOGY. Candlesticks show who's winning the fight between bulls and bears. Your job: figure out who will win, then bet on them.
- **RULE DT-51**: Indecision candles (spinning tops, Dojis) = neither side winning. Fight continues. Volume usually lower. Trends can change AFTER indecision candles — watch carefully.
- **RULE DT-52**: Doji in uptrend = bulls exhausted, bears fighting back. Doji in downtrend = bears exhausted, bulls fighting back. Signals POSSIBLE reversal, not definite.
- **RULE DT-53**: Shooting star Doji (long upper wick) = buyers tried to push higher, FAILED. Hammer Doji (long lower wick) = sellers tried to push lower, FAILED. Both signal potential reversal.
- **RULE DT-54**: NEVER trade on Doji alone. Need CONFIRMATION candle + support/resistance level. Doji only indicates indecision, not definite reversal. Taking every Doji = significant losses.
- **RULE DT-55**: Avoid fancy candlestick patterns (Morning Star, Three Black Crows, etc.). "Wishful thinking" — you'll find bullish pattern when you want to buy, bearish when you want to sell. Stick to simple: bullish/bearish/indecision.
- **RULE DT-56**: Stand aside if you can't tell who's winning. Let bulls and bears fight. Enter ONLY when reasonably certain which side will win. Being in wrong side of trade = disaster.

### From How to Day Trade for a Living Ch. 7 "Important Day Trading Strategies" (2026-03-17)

#### Trade Management
- **RULE DT-57**: Trade management is as important as strategy. What you do AFTER entry determines success. Process new information, add to winners, cut losers.
- **RULE DT-58**: Scale UP into winners, NEVER DOWN into losers. Add to position when trade goes in your favor. Never add to losing position.
- **RULE DT-59**: NEVER average down. 85% of time it "works" — 15% it WIPES YOUR ACCOUNT. Brian Hunter lost $6.6B averaging down on natural gas with $10B fund. Your account isn't big enough either.
- **RULE DT-60**: Position sizing by conviction: "Load the boat" for obvious setups, just a "taste" for uncertain ones. But NEVER risk >2% regardless of conviction.
- **RULE DT-61**: Master ONE strategy first. Don't try to learn all 9 at once. Pick one, practice in simulator for months, then expand.
- **RULE DT-62**: Name your strategy before every trade. "I'm going long CCL for 1-minute ORB with stop below VWAP." If you can't name the strategy, you shouldn't be in the trade.

#### Strategy 1: ABCD Pattern
- **RULE DT-63**: ABCD Pattern: A→B (surge up), B→C (pullback), C holds as support, C→D (continuation). Enter near C, stop below C, target D or higher. Classic pattern — many traders use it, so it works.
- **RULE DT-64**: Never chase at point B. Wait for pullback to C. Chasing = buying at worst price with undefined stop.

#### Strategy 2: Bull Flag Momentum
- **RULE DT-65**: Bull Flag = pole (surge) + flag (consolidation). Enter at breakout of consolidation. Stop = below consolidation. Best for LOW FLOAT stocks <$10.
- **RULE DT-66**: Bull Flag is SCALPING strategy. Get in at breakout, take profit, get out quickly. Don't hold — these stocks drop fast.
- **RULE DT-67**: Trade only 1st or 2nd consolidation. 3rd+ consolidations = buyers exhausted, risky. Don't short Bull Flags — long only.

#### Strategies 3 & 4: Reversal Trading
- **RULE DT-68**: Reversal setup requires: (1) 5+ consecutive candles in one direction, (2) RSI at extreme (<10 or >90), (3) At support/resistance level, (4) Indecision candle (Doji/hammer/shooting star).
- **RULE DT-69**: Bottom Reversal: Enter on first 5-min NEW HIGH near support. Stop = low of day. Target = VWAP or moving averages.
- **RULE DT-70**: Top Reversal: Short on first 5-min NEW LOW near resistance. Stop = high of day. Target = VWAP or moving averages.
- **RULE DT-71**: Never "catch a falling knife." Wait for CONFIRMATION of reversal (indecision candle + new high/low). Don't buy just because "it should bounce."
- **RULE DT-72**: Trade reversals at EXTREMES only. Slow drift down all day ≠ reversal candidate. Need sharp move + high volume at reversal point.

#### Strategy 5: Moving Average Trend
- **RULE DT-73**: MA Trend: When 9 EMA acts as support/resistance, ride the trend. Enter when MA holds, exit when MA breaks. Wait for 5-min candle to CLOSE above/below MA.
- **RULE DT-74**: MA Trends work best Mid-day and Close, not at Open (too volatile). Clear entry/exit points — good for high-commission traders.

#### Strategy 6: VWAP Trading
- **RULE DT-75**: VWAP = most important day trading indicator. Above VWAP = buyers in control. Below VWAP = sellers in control. Institutional benchmark.
- **RULE DT-76**: VWAP Strategy: Buy near VWAP when it acts as support (price bounces off it). Short near VWAP when it acts as resistance. Stop = 5-min close on wrong side of VWAP.
- **RULE DT-77**: Institutions try to buy below VWAP, sell above VWAP. If big buyer waiting, price pops over VWAP and keeps going. If big seller, price rejects VWAP and drops.

#### Strategy 7: Support/Resistance Trading
- **RULE DT-78**: Support/Resistance = HORIZONTAL lines only. Diagonal trend lines are subjective — two traders draw differently. Market remembers price LEVELS.
- **RULE DT-79**: S/R levels on daily charts. Look for extreme wicks (not closes). Half-dollars and whole dollars act as invisible S/R, especially for stocks <$10.
- **RULE DT-80**: S/R is an AREA, not exact number. $19.69 support = expect action between $19.62-$19.72. High volume at level confirms it's significant.

#### Strategy 8: Red-to-Green Trading
- **RULE DT-81**: Red-to-Green: Trade toward previous day close. Stock gapped down (red) → price rising toward previous close (turning green). Previous day close = powerful S/R level.

#### Strategy 9: Opening Range Breakout (ORB)
- **RULE DT-82**: ORB: Wait for opening range to form (first 1, 5, 15, or 30 min). Trade breakout of that range. Longer timeframe = less volatility.
- **RULE DT-83**: ORB requirements: Opening range < ATR of stock. If stock moves near ATR in first 5 min, it's too volatile — not catchable.
- **RULE DT-84**: ORB stop loss = VWAP (close below for longs, close above for shorts). Profit target = next technical level.
- **RULE DT-85**: New traders: Start with 5-min ORB. As you gain confidence, move to 1-min ORB. 1-min ORB is Aziz's main strategy now.

#### Time of Day Rules
- **RULE DT-86**: Open (9:30-10:30 AM ET): Most volatile, most profitable. Best strategies: ORB, Bull Flag, VWAP. Trade with largest size.
- **RULE DT-87**: Late-Morning (10:30-12 PM): Slower but still good. Easiest time for new traders. Less unexpected volatility.
- **RULE DT-88**: Mid-day (12-3 PM): MOST DANGEROUS. Low volume = strange moves. Reduce size, tight stops. Best to watch and prepare for Close.
- **RULE DT-89**: Close (3-4 PM): Stocks more directional. Wall Street professionals dominate. Trade WITH the trend (up = bullish, down = bearish).
- **RULE DT-90**: Don't lose more than 30% of Open profits during rest of day. If you do, stop trading or switch to simulator.

### From Day Trading Ch. 8 "Step by Step to a Successful Trade" (2026-03-17)
- **RULE DT-91**: 6-step trading process: (1) Morning routine, (2) Develop watchlist, (3) Organize trade plan, (4) Initiate according to plan, (5) Execute according to plan, (6) Journal and reflect.
- **RULE DT-92**: RULE 10: Profitable trading does not involve emotion. If you are an emotional trader, you will lose your money. Emotion = death.
- **RULE DT-93**: Write down reasons for EVERY entry and exit. Discipline to execute correctly separates winners from losers. Anyone can read books; few execute.
- **RULE DT-94**: Physical condition affects trading. Exercise, sleep, nutrition MATTER. Aerobic exercise improves decision-making. Morning run before trading = sharper mind.
- **RULE DT-95**: Watchlist COMPLETE by 15 minutes before open. No additions after — not enough time to properly plan. Watch pre-market price action for 15 min.
- **RULE DT-96**: Write trade plans on NOTE CARDS. "If X, then Y" scenarios for each ticker. Written plan eliminates anxiety at the open. Refer to it during trade.
- **RULE DT-97**: REFLECTION after each trade is essential. Ask: "What did I do right? What did I do wrong? Should I have sold earlier?" This is how you improve.

### From Day Trading Ch. 9 "Case Study of a Newly Successful Trader" (2026-03-17)
- **RULE DT-98**: Risk the SAME AMOUNT per trade ("R"). Don't increase risk after losses trying to get back to green. That's gambler's fallacy. Consistent R = emotional stability.
- **RULE DT-99**: Risk SMALL amounts until consistent. John used $20/trade for 5 months, targeting 20R/month. Survive the learning curve, then scale up.
- **RULE DT-100**: Use HARD STOPS. Period. No mental stops. -1R loss is a GREAT outcome compared to -3R from "waiting and hoping." Set stop, honor it.
- **RULE DT-101**: Focus on ONE STRATEGY until mastered. John's BHOD reduced trades from 9/day to 5/day. Master one, then add another. Depth > breadth.
- **RULE DT-102**: Single, well-defined strategy FORCES patience. You wait for specific setup, ignoring everything else. Patience is built-in.
- **RULE DT-103**: Listen to experienced traders. Community is essential. "I would have failed without a supportive community." Find mentors, join a mastermind.

### From Day Trading Ch. 10 "Next Steps for Beginner Traders" (2026-03-17)
- **RULE DT-104**: Seven Essentials for day trading: (1) Education, (2) Preparation, (3) Determination, (4) Patience, (5) Discipline, (6) Mentorship, (7) Reflection.
- **RULE DT-105**: Trade in SIMULATOR for 3+ months before real money. No shortcuts. Use realistic position sizes. Move to real money only after 3 months consistency.
- **RULE DT-106**: At least 6-8 MONTHS to become consistently profitable. Results in first 6 months DON'T MATTER. You're building foundation for lifetime career.
- **RULE DT-107**: First two hours (9:30-11:30 AM ET) are essential. MINIMUM: 9:30-10:30 AM available for trading and prep. No exceptions.
- **RULE DT-108**: PROCESS-oriented goals: "learn how to day trade" NOT "make $X per day." Focus on doing the right thing. Money is byproduct of solid execution.
- **RULE DT-109**: HIDE P&L column. Trade based on technical levels and plan, not how much you're up/down. P&L is emotionally distracting.
- **RULE DT-110**: Do NOT be a gambler. Trading has high failure rate because people who SHOULD NOT trade, trade. Gamblers are doomed.
- **RULE DT-111**: NEVER average down. Never send good money after bad. Period. The person in Singapore down $20k planning to add $50k to double position = disaster.
- **RULE DT-112**: Develop TRADING FRAMEWORK: (1) Money/risk management, (2) Strategies you trade, (3) Trade management rules, (4) Accountability. Core of business plan.
- **RULE DT-113**: VIDEO RECORD trades. Watch the tapes like athletes watch film. You'll see how easy it looks without emotion. Review during midday. Cut and learn.
- **RULE DT-114**: Trading is like MOUNTAINEERING: process-oriented, risk management, passion required. "There is no gain without risk, perhaps no risk without love."
- **RULE DT-115**: When you start, you WILL BE HORRIBLE. That's normal. Surviving the learning curve is the challenge. Don't quit — keep showing up.

### Andrew's 10 Rules of Day Trading (Summary)
1. Day trading is NOT a get-rich-quick strategy
2. Day trading is a SERIOUS BUSINESS — treat it as such
3. NEVER hold overnight — sell at a loss if necessary
4. Always ask: moving with market or unique catalyst?
5. Risk management + 2:1 MINIMUM win:lose ratio
6. Your ONLY JOB = manage risk
7. Trade only Stocks in Play with high relative volume + catalyst
8. GUERRILLA SOLDIERS — jump out, take profit, get out
9. Hollow candles = buying pressure, filled = selling pressure
10. NO EMOTION — emotional traders lose money

### From Trading Catalysts Ch. 1 "Introduction" (2026-03-17)
- **RULE TC-1**: Trading catalysts = events that move markets. Two categories: EXTERNAL (Fed, economic reports, geopolitics, weather) and INTERNAL (order flow, stop cascades, technical barriers, reflexive moves).
- **RULE TC-2**: 7 questions to answer after ANY catalyst: (1) Which markets affected? (2) Direction? (3) Magnitude? (4) Speed? (5) Duration/half-life? (6) Intensify or deteriorate? (7) Overshoot? More uncertain = smaller position size.
- **RULE TC-3**: Trading thesis = perceived relationship between catalyst and price. Example: "Unexpected employment increase → bonds fall." The THESIS drives your trade, not the news itself.
- **RULE TC-4**: Market reactions are NOT always consistent. Same catalyst can have OPPOSITE effects at different times. Trading thesis can shift 180° (e.g., trade deficit report interpretation changed between 1986-1987).
- **RULE TC-5**: Speed of market response varies from IMMEDIATE to DELAYED. Relevant question: Is there enough time to execute a trade? A minute is a lifetime in trading. Delayed reactions create opportunity.
- **RULE TC-6**: Duration of catalyst effect ranges from TRANSITORY (erased same day) to PERMANENT. Many catalysts are short-lived — gains can be wiped out by "market got ahead of itself" sentiment.
- **RULE TC-7**: REFLEX rallies/breaks can be as powerful as news-oriented moves. Of 29 historic buying panics, 12 were "reflex from panic conditions" — no news, just reversal. Reflex rallies often LARGER than news rallies.
- **RULE TC-8**: Large price changes occur MORE FREQUENTLY than normal distribution predicts (leptokurtic). 1987 crash "should almost never occur" under normal distribution. Don't underestimate tail risk.
- **RULE TC-9**: Sometimes large price changes occur for NO APPARENT REASON. Internal catalysts, order flow, reflexive trading. The catalyst may be unknowable — trade the price action, not the explanation.
- **RULE TC-10**: Trading is a GAME (Keynes): Don't pick what YOU think is best. Pick what you think OTHERS think is best. "We devote our intelligences to anticipating what average opinion expects average opinion to be."
- **RULE TC-11**: Markets need NOT make sense (Richard Dennis). Don't force rational explanation on every move. Sometimes there isn't one. Accept ambiguity.
- **RULE TC-12**: Scheduled catalysts (known timing) → consensus forms → smaller forecast error → typically SMALLER reaction. Unscheduled catalysts → larger surprises → typically LARGER reaction.
- **RULE TC-13**: Market can have ONE-TRACK MIND — focuses on one catalyst, ignores others announced simultaneously. Or ignores catalyst entirely (trade deficit ignored throughout 1990s after being critical in 1980s).
- **RULE TC-14**: Catalyst effects may GROW over time before climaxing (Jan 3, 2001 Fed cut: market went from $100-200 bounces to $5,000 bounces in minutes). Initial reaction may understate final reaction.

### From Trading Catalysts Ch. 2 "Market Conditions and Sentiment" (2026-03-17)
- **RULE TC-15**: Choose the RIGHT INSTRUMENT for the catalyst. Futures may not track the security most affected (e.g., T-bond futures tracks cheapest-to-deliver, not the 30-year). Goldman made $1.5M on $84M cash bonds but only $2.3M on $233M futures. Wrong instrument = missed opportunity.
- **RULE TC-16**: CONCENTRATED SHORT positions create explosive rallies. When many traders short, bullish catalyst triggers cascading short-covering. The Oct 2001 Treasury rally was exacerbated by widespread short positions. Reverse is true for concentrated longs.
- **RULE TC-17**: Market conditions and sentiment can EXACERBATE or MITIGATE catalyst impact. Same news under different conditions produces different reactions. A tranquil market absorbs shocks; a turbulent market amplifies them.
- **RULE TC-18**: SKEWED DISTRIBUTIONS exist when everyone is on one side. When sentiment is extremely biased, the "obvious" trade has asymmetric risk — outsized losses if wrong. Look for skewed distributions when others see symmetric.
- **RULE TC-19**: QUALIFIED announcements have weaker impact than unconditional ones. "We might resume 30-year bonds" moved market less than "We are discontinuing 30-year bonds." Conditional = mitigated.
- **RULE TC-20**: EVENT TIME compresses reactions. When traders remember past similar events, they anticipate and react faster. 2001 Treasury announcement took 2 days to complete; 2005 reversal announcement was telescoped into minutes as traders anticipated based on 2001.
- **RULE TC-21**: Small forecast errors can cause LARGE price moves in extended markets. eBay missed earnings by 1 cent (3% of earnings), stock fell 11%. After 300% run-up over 2 years, vulnerability was high. Extended = fragile.
- **RULE TC-22**: Futures often LEAD cash by seconds during catalyst events. If seeking fastest execution, act in futures first. Cash market followed futures during both Treasury announcements.
- **RULE TC-23**: Bid-offer spreads WIDEN DRAMATICALLY during catalyst events. Normal 1/32 spread → 4+ POINTS during Treasury collapse. Illiquidity creates opportunity but also danger. Market orders during panic = brutal fills.
- **RULE TC-24**: Fast market designation is a LAGGING indicator. By the time it's designated, intense action has already started. By the time it's lifted, it's already calmed. Use as confirmation, not signal.
- **RULE TC-25**: Zero forecast error can still MOVE markets. If sentiment bias exists (e.g., bullish dollar positioning), even expected news can trigger moves. ECB/Fed held rates exactly as expected → dollar still spiked 0.6-0.9%.
- **RULE TC-26**: LIQUIDITY absorbs catalysts. Deeper markets react less to the same news. Illiquid markets overshoot then correct. Trade liquidity, not just the catalyst.
- **RULE TC-27**: TRANQUIL markets react less than TURBULENT markets. The same catalyst in a calm environment moves prices less than in a volatile environment. Volatility begets volatility.
- **RULE TC-28**: Some catalysts SHIFT REGIME from tranquil to turbulent. Iraq invasion of Kuwait both moved prices AND changed the environment. The catalyst itself can change the rules.
- **RULE TC-29**: Risk premium spikes CRUSH prices. Anything shaking confidence increases the discount rate market participants demand. Higher risk premium = lower present values = immediate price drop. Confidence loss is catastrophic.
- **RULE TC-30**: Weight RECENT similar events more heavily (Allais' "rate of forgetfulness"). Distant events decay in relevance. Most recent occurrence of similar event is most predictive — but sample size is small.

### From Trading Catalysts Ch. 3 "Talk Isn't Cheap" (2026-03-17)
- **RULE TC-31**: Policymaker comments create EXCESS VOLATILITY. Their talk isn't cheap for traders on the wrong side. Creates trading opportunities for those who can anticipate reactions or play corrections.
- **RULE TC-32**: BROKEN PROMISES signal imminent change. When a policymaker promises X during crisis (e.g., "we won't devalue"), it often means X is coming soon. Thailand PM promised no devaluation June 30, 1997; baht devalued July 2.
- **RULE TC-33**: Policymaker comments can be INTENTIONAL, INADVERTENT, or PERVERSE. Intentional = trying to move markets in desired direction. Inadvertent = off-the-cuff mistake. Perverse = backfired spectacularly.
- **RULE TC-34**: Implicit THREAT OF ACTION gives weight to words. Words alone don't drive markets — it's the prospect of government action. "Mr. Yen" moved markets because traders feared BOJ would actually intervene.
- **RULE TC-35**: CREDIBILITY determines direction. Mahathir's attacks on speculators moved ringgit AGAINST him (credibility destroyed). Sakakibara's comments moved yen as intended (BOJ had proven willingness to intervene). Same words, opposite results.
- **RULE TC-36**: TIMING matters for policymaker comments. Comments during holidays, pre-market, or when foreign markets closed have LARGER impact (thinner liquidity). Policymakers know this and time deliberately.
- **RULE TC-37**: Comments near TECHNICAL LEVELS trigger larger moves. Near support/resistance → stop-loss orders + positive feedback trading amplifies the catalyst. Savvy policymakers exploit this.
- **RULE TC-38**: TRANSLATION RISK creates rebound opportunities. Foreign policymaker comments may be mistranslated → market overreacts → correction when clarified. Hashimoto's Treasury comment sparked selloff, corrected next day on "misunderstood."
- **RULE TC-39**: Duration of INADVERTENT comments shorter than INTENTIONAL comments. Off-the-cuff remarks create temporary volatility; deliberate policy signals have longer duration.
- **RULE TC-40**: Policymaker who RARELY speaks has MORE impact. Exception: Mr. Yen was effective despite frequent comments because BOJ consistently backed words with intervention. Generally, frequent speakers get tuned out.
- **RULE TC-41**: PERVERSE reactions destroy currencies. Mahathir's attacks on speculators CAUSED ringgit to fall 4% in 2 hours. The more he spoke, the worse it got. Capital flight was from Malaysian nationals, not foreign speculators.
- **RULE TC-42**: CONTAGION spreads catalyst effects across related instruments. Thai baht devaluation became catalyst for ringgit, rupiah, peso, HKD. One catalyst → chain reaction across correlated markets.
- **RULE TC-43**: Currency defense creates ONE-SIDED BETS. Shorting defended currency = small loss if intervention succeeds, large gain if fails. Asymmetric payoff attracts more shorts → self-fulfilling prophecy.
- **RULE TC-44**: DELTA HEDGING amplifies catalyst impact. When central bank uses options, sellers must delta-hedge → fractional positions in cash market → exacerbates price moves. BOJ considered this deliberately.
- **RULE TC-45**: "Irrational Exuberance" was TRANSITORY. Greenspan's 1996 speech: markets down 2% intraday, recovered within 2 weeks. Anyone who shorted based on it underwater until 2002. Beware policymakers offering investment advice.

### From Trading Catalysts Ch. 4 "Geopolitical Events" (2026-03-17)
- **RULE TC-46**: Markets TELESCOPE reactions to anticipated events. Iraq War 2003: stock rally started March 13, not when war began March 20. Gulf War 1991 reaction compressed. Don't wait for the event — trade the certainty.
- **RULE TC-47**: PAST SIMILAR EVENTS provide trading roadmap. Gulf War 1991 (stocks +4.6%, oil -$10.56/bbl) predicted Iraq War 2003 reaction. Traders looked to 1991 to position for 2003.
- **RULE TC-48**: Short-covering EXACERBATES geopolitical rallies. March 13, 2003 rally amplified by shorts covering in a bearish market. Know the positioning before the catalyst.
- **RULE TC-49**: "War premium" in commodities creates REVERSION opportunity. $4-5/bbl war premium in 2003 → quick victory → oil collapsed. Identify embedded risk premiums and trade the reversion.
- **RULE TC-50**: Margin calls create CASCADING SELLOFFS. India 2004 election: 16.6% intraday drop driven by margin calls triggering more margin calls. Positive feedback loop. Same pattern in Brazil 2002 (CDS hedging).
- **RULE TC-51**: Geopolitical events create FLIGHT TO SAFETY. Pattern: stocks fall, bonds/gold/safe currencies (CHF, USD) rise. Travel stocks crushed, defense stocks rise. Predictable response = tradeable.
- **RULE TC-52**: Second-order effects can DWARF initial reaction. Madrid train bombing (March 11, 2004) → 2.2% drop. But election result (March 15) → 4%+ drop. The political aftermath moved markets more.
- **RULE TC-53**: Reactions to EXPECTED events still occur. French "no" on EU constitution was widely expected → euro still fell 2.2%. Dispersion around consensus explains this paradox.
- **RULE TC-54**: Foreign markets often MORE sensitive than US markets to geopolitical events. Gorbachev coup: Israel -10%, Frankfurt -9.4%, but US only -2.4%. Time to process + US market isolation.
- **RULE TC-55**: SNAPBACK rallies follow geopolitical selloffs. India fell 16.6% intraday → closed down only 11%. Korea fell 5.5% → closed down 2.5%. Overreaction creates rebound opportunity.
- **RULE TC-56**: Credit protection hedging AMPLIFIES spread widening. Brazil 2002: dealers who sold CDS hedged by shorting bonds → pushed spreads wider → more hedging needed. Self-reinforcing to 2400bp over Treasuries.
- **RULE TC-57**: Terror attacks have PREDICTABLE market response despite unpredictable timing. Flight to safety, travel stocks down, defense/security up, oil up on supply uncertainty. Trade the pattern, not the event.
- **RULE TC-58**: Different trading theses have DIFFERENT DURATIONS. Flight to safety = short-lived (hours/days). Travel industry impact = longer-lived (weeks/months). Separate the effects and trade accordingly.
- **RULE TC-59**: During geopolitical buildup, even UN RESOLUTIONS and SPEECHES can move markets. Pre-Iraq war: political statements became catalysts. Elevated sensitivity to any political news.
- **RULE TC-60**: Trading horizon should SHORTEN during geopolitical events. Korean impeachment: violent intraday swings. Solution: reduce position size + shorten holding period + tighter stops.

### From Trading Catalysts Ch. 5 "Weather and Natural Disasters" (2026-03-17)
- **RULE TC-61**: Size of humanitarian disaster ≠ market impact. Boxing Day tsunami (283,106 deaths) = minimal market impact. Kobe earthquake (5,500 deaths) = massive impact. WHERE it happens matters more than scale.
- **RULE TC-62**: DELAYED reactions to natural disasters are common. Kobe earthquake: market took 6 DAYS to react with 5.6% crash. "Failure to realize extent of damage." Plenty of time to position.
- **RULE TC-63**: Natural disaster trading theses are SIMPLE partial equilibrium. "Reconstruction needs base metals → buy metals." "Mad cow → less beef → cattle down." Simple but often overstated.
- **RULE TC-64**: Markets OVERREACT to natural disasters. Simple theses overstate actual impact. Creates rebound opportunities after initial panic.
- **RULE TC-65**: Different markets react at DIFFERENT TIMES to same catalyst. Mad cow: cattle futures (10:48 AM) → feeder cattle (14 min later) → fast food stocks (11:37-11:43 AM). Sequential opportunities.
- **RULE TC-66**: SUBSTITUTION effects create secondary trades. Mad cow → less beef consumption → MORE pork consumption → lean hog futures UP. Always think second-order effects.
- **RULE TC-67**: Past disasters create TEMPLATES for current reactions. Hurricane Ivan (2004) damage created psychological anchor. "Hangover from Ivan" amplified all subsequent storm reactions.
- **RULE TC-68**: Sentiment can AMPLIFY weather moves beyond reason. Crude oil +3% on tropical storm NOT expected to impact production. "Any bullish news is tremendously bullish even if slight."
- **RULE TC-69**: HERD BEHAVIOR causes mispricing in disaster response. Corn futures got "sucked along" by wheat/soybean rally even though fundamentals didn't support it. Tse & Hackard study.
- **RULE TC-70**: Specialty newsletters provide ADVANCE WARNING. Mad cow info reached cattle traders 1 HOUR before official announcement via industry newsletter. Information asymmetry is real.
- **RULE TC-71**: Forward/derivative premiums widen on disaster uncertainty. SARS → HK$ forward premium spiked as market priced devaluation risk. Watch derivatives for sentiment signals.
- **RULE TC-72**: Weather explains LITTLE of commodity price variation. Roll (1984): weather explained only small fraction of OJ futures variance. Most variation = non-fundamental factors.
- **RULE TC-73**: Exchange closures cause SPREAD WIDENING elsewhere. Chicago flood closed futures → cash market spreads widened. Futures closure = liquidity crisis for hedgers.
- **RULE TC-74**: Insurance selling EXTENDS disaster selloffs. San Francisco 1906: market fell 17% over 2 MONTHS as insurers sold stock to pay claims. Forced selling extends duration.
- **RULE TC-75**: Ability to predict disaster ≠ ability to profit. More important: predict WHICH markets react, DIRECTION, TIMING, MAGNITUDE. The disaster itself is secondary to the trading response.

### From Trading Catalysts Ch. 6 "Market Interventions" (2026-03-17)
- **RULE TC-76**: Central bank intervention creates SHORT-TERM risk but LONG-TERM opportunity. Interventions cause sharp moves, but central banks can't maintain non-market prices forever. Adjustment is "sharp and quick."
- **RULE TC-77**: Intervention timing is STRATEGIC. Central banks concentrate interventions during low liquidity (holidays, weekends, midday between sessions). Maximum impact per dollar spent.
- **RULE TC-78**: Intervention is most effective when it REINFORCES existing trends. Well-designed interventions let "private sector do heavy lifting" — triggering stops and short-covering cascades.
- **RULE TC-79**: Market manipulation is illegal EXCEPT when done by government. Central banks maintain non-market prices, create distortions, and transfer wealth from citizens to speculators when they fail.
- **RULE TC-80**: ONE-SIDED BETS exist when governments defend non-market prices. Soros on pound sterling: "uneven bet where potential losses were minimal and potential gains were enormous." He made $1B overnight.
- **RULE TC-81**: SIZE UP on one-sided bets + WIDEN STOPS. When central bank defends the indefensible, increase position size AND widen stops to avoid being prematurely stopped out by intervention volatility.
- **RULE TC-82**: DENIALS signal imminent action. "Defend the peso like a dog" → 42% devaluation. Thai PM: "no devaluation" → devalued 2 days later. Russia: "default not posed" → default 6 days later.
- **RULE TC-83**: Central bank PARTICIPATION in coordinated intervention matters. Euro intervention worked short-term because Fed participated unexpectedly. ECB alone had been ineffective.
- **RULE TC-84**: TRIAL BALLOONS test market reaction before commitment. Clinton SPR: Gore proposal leaked first as test. If market hadn't reacted, probably wouldn't have been implemented.
- **RULE TC-85**: Price moves in one market become CATALYST for another. Hong Kong interest spike → stock crash → US market spillover. Cross-market contagion is real.
- **RULE TC-86**: Complex MULTI-MARKET manipulation strategies exist. HK 1998: hedge funds swapped into HK$ → built futures shorts → dumped HK$ → rates spike → stocks crash → profit on shorts. Know the playbook.
- **RULE TC-87**: Central banks LEARN from speculators. HKMA responded to manipulation by buying $15B of stocks and futures. Made $4B profit. Changed currency board rules. Adaptation occurs.
- **RULE TC-88**: Post-intervention DISTORTIONS can persist. After HKMA intervention, basis (index vs futures) stayed negative for extended period. Arbitrageurs feared another intervention.
- **RULE TC-89**: Fed FX interventions are RARE and POWERFUL. US rarely intervenes (free market philosophy). When it does, effect is dramatic. June 1998: Fed bought yen → dollar fell 6.5 yen in one day.
- **RULE TC-90**: Anticipated intervention can move markets BEFORE announcement. Oil swap speculation drove crude down 4% before official announcement. Pre-announcement = trading opportunity.

### From Trading Catalysts Ch. 7 "Periodic Economic Reports" (2026-03-17)
- **RULE TC-91**: Interpretation of SAME forecast error can FLIP 180 degrees. Trade deficit: larger-than-expected → bonds RALLIED Aug 1986 but CRASHED Apr 1987. Same data, opposite market reactions.
- **RULE TC-92**: Formerly important reports can suddenly LOSE power. Weekly money supply moved bonds 3 points in 1981 → virtually ignored today. What the market cares about changes.
- **RULE TC-93**: Market reacts to PRELIMINARY data over REVISED data. Preliminary is less accurate but gets more attention. Traders who forecast closer to preliminary win over those closer to revised.
- **RULE TC-94**: Forecast error × dispersion interaction matters. 3-sigma error with HIGH dispersion = less surprising than 3-sigma with LOW dispersion. Adjust for opinion spread.
- **RULE TC-95**: Much economic report news is NOISE, not information. S&P 500 addition = no fundamental change but price rises anyway. Same for many report reactions.
- **RULE TC-96**: Economic relationships are THEORY-DEPENDENT. Different theories predict opposite reactions. Neo-Keynesian: money up → rates down. Lucas: money up → rates up. Market picks one.
- **RULE TC-97**: Most traders get economic theory WRONG. Confuse relative vs absolute prices. Confuse levels vs rates. Doesn't matter — trade THEIR beliefs, not textbooks.
- **RULE TC-98**: SHORT trade horizon for report-driven trades. If bet is on report outcome, exit quickly to avoid unrelated risks. 12-minute trade vs 1-day = very different risk profiles.
- **RULE TC-99**: Pick the RIGHT market for the report. Employment Sept 2003: EuroFX +$2,262 vs 10-yr T-note +$1,516 vs Yen -$87. Same report, different results by instrument.
- **RULE TC-100**: Market frequently OVERREACTS to economic reports. Creates opportunity to bet AFTER reports are released, trading the correction.
- **RULE TC-101**: Muted reaction to bullish news = BEARISH signal. Muted reaction to bearish news = BULLISH signal. How market reacts to news is itself informative.
- **RULE TC-102**: Federal Reserve is the KEY market participant. Traders watch reports to anticipate Fed actions. If Fed watches employment, traders watch employment.
- **RULE TC-103**: Correlation between economic variables is TRANSITORY. Beans-over-bonds (BOB) spread worked briefly then died. Relationships change — don't assume stability.
- **RULE TC-104**: No view on forecast error + no view on reaction = GAMBLING. If you don't have a thesis on both the outcome AND how market reacts, you're betting randomly.
- **RULE TC-105**: Conflicting data in same report requires PRIORITIZATION. Employment: unemployment rate vs nonfarm payrolls can conflict. Know which data market focuses on NOW.

### From Trading Catalysts Ch. 8 "Size Matters" (2026-03-17)
- **RULE TC-106**: Internal catalysts often LARGER than external. Sumitomo copper (15% in 2 hours), yen crash (9.15% intraday) — no news, just order flow. Don't assume big moves need news.
- **RULE TC-107**: "Blood in the water" triggers PREDATORY trading. When market suspects large trader in trouble, prices move AGAINST their position. Sumitomo long copper → attacked. Tiger short yen → attacked.
- **RULE TC-108**: Reassignment of key traders = SELL signal. Hamanaka reassigned from trading → market concluded Sumitomo would liquidate → copper crashed. Watch personnel changes.
- **RULE TC-109**: Initial reported losses are ALWAYS understated. Sumitomo: $1.8B → $2.6B. Orange County: $1.5B → $1.7B. Expect revisions upward; trade accordingly.
- **RULE TC-110**: Delta-hedging AMPLIFIES price moves. Put writers sell more as prices fall → exacerbates decline. Call writers buy more as prices rise. Built-in feedback loop.
- **RULE TC-111**: Bid-ask spreads EXPLODE in crisis. Copper spread to $50/tonne (unprecedented). Liquidity dries up exactly when you need it most.
- **RULE TC-112**: Carry trades unwind VIOLENTLY. Yen-carry: borrow at 1%, invest at 4-5%. Works until yen rises. Oct 1998: dollar fell 12 YEN in a day (9%+) as carry trades unwound.
- **RULE TC-113**: Positions near key levels INVITE attack. Tiger's short yen was known. When technicals broke, others "gunned for stops." Market gravitates toward where stops cluster.
- **RULE TC-114**: Large orders move prices even WITHOUT information. Citigroup €11.3B in 18 seconds → predictable cascade. Order size alone = catalyst. Price pressure is real.
- **RULE TC-115**: Trade EXECUTION matters enormously. Soros sold 5,000 S&P contracts at open → fell 22%+ before bouncing 25%. Locals "hung back, circled the prey." Horrible execution cost $200M+.
- **RULE TC-116**: Trading is a REPEATED game. Citigroup made $18M but alienated counterparties who "would remember for a long, long time." Short-term win = long-term cost.
- **RULE TC-117**: Near-expiration futures are EXTREMELY illiquid. 80 contracts pushed CBOT wheat up 49% near expiration. Locals refuse to take positions that might require delivery.
- **RULE TC-118**: Positive feedback trading DESTABILIZES prices. Technical analysis, stop-losses, margin calls, portfolio insurance, delta-hedging — all buy when rising, sell when falling.
- **RULE TC-119**: Portfolio insurance = synthetic puts = sell into declines. Pre-1987 strategy: sell index futures when market falls. Exacerbated the crash by design.
- **RULE TC-120**: No apparent news ≠ no catalyst. Internal catalysts (order flow, position unwinding, stops) cause huge moves with no visible external cause. Don't search for news that isn't there.

### From Trading Catalysts Ch. 9 "Bubbles, Crashes, Corners, and Market Crises" (2026-03-17)
- **RULE TC-121**: Corners FAIL for two fundamental reasons. (1) Supply increases as price rises (alternatives found, hoarded stock enters market). (2) Only way to profit is to SELL what you cornered → pushes price down.
- **RULE TC-122**: Pyramiding on existing positions creates CASH FLOW RISK. Hunt brothers used silver holdings as collateral to buy more silver. Price fell → margin calls → forced liquidation. Don't pyramid.
- **RULE TC-123**: Internal crisis in one market becomes EXTERNAL catalyst for others. Hunt silver collapse → flight to safety → T-bills rallied, stocks fell, even hogs/cotton/sugar went limit down.
- **RULE TC-124**: Portfolio insurance = synthetic puts = POSITIVE FEEDBACK selling. Rule: sell 2× the % decline as futures. 10% market drop → sell 20% of portfolio. Exacerbated 1987 crash by design.
- **RULE TC-125**: FEW players can crash the whole market. Oct 19, 1987: THREE portfolio insurers + ONE mutual fund group did most of the damage. Concentrated selling, not broad panic.
- **RULE TC-126**: Locals won't take the other side in a crash. Pit traders saw trouble → "hung back" → only bought at massive discounts. Liquidity providers DISAPPEAR when you need them most.
- **RULE TC-127**: Trading halts may INCREASE panic, not reduce it. Weekend before Oct 19 gave traders time to plan exits, not calm down. Monday opened with massive sell orders.
- **RULE TC-128**: Flight to safety is DELAYED, not immediate. Oct 19, 1987: Treasury bonds were DOWN most of the day despite stock crash. Only rallied massively AFTER close. Don't assume instant correlation.
- **RULE TC-129**: Treasury dealers REFUSE to make markets during crises. Oct 20, 1987: Major banks wouldn't trade even with World Bank because CBOT was lock-limit. System fragility exposed.
- **RULE TC-130**: Bubbles may deflate SLOWLY or quickly. Japan Nikkei: 38,916 → 7,607 over years. Dot.com: peaked March 10, 2000, slow deflation. Not all bubbles "pop" suddenly.
- **RULE TC-131**: Exchanges can CHANGE RULES mid-game. COMEX/CBOT imposed liquidation-only + raised margins → silver dropped $10/day. Cornerers face regulatory risk.
- **RULE TC-132**: Repo market squeeze more profitable than spot squeeze. Salomon Treasury scandal: squeezed shorts at below-market "special" rates. Real profit in financing, not security.
- **RULE TC-133**: Contagion affects EMERGING MARKETS more than US. Asian crisis 1997: US down 7% on Oct 27, recovered next day. Brazil down 6% + 9.8% over two days.
- **RULE TC-134**: Knowing others' stop levels = ANTICIPATING cascades. Portfolio insurance triggers were KNOWN. Traders front-ran mechanical selling. "The situation presented an opportunity."
- **RULE TC-135**: Internal catalysts often MORE POWERFUL and LONGER-LASTING than external. Bubbles, crashes, corners, squeezes = extreme examples. Game-like nature of trading most visible here.

### From Trading Catalysts Ch. 10 "The Accidental Catalyst" (2026-03-17)
- **RULE TC-136**: Erroneous orders impact RELATED markets, not just the security. Mizuho's J-Com error → Nomura, Daiwa, Nikko all fell 3%+. Nikkei fell 2%. Contagion to innocent parties.
- **RULE TC-137**: Markets react to RUMORS and ERRORS regardless of truth. Adjust positions based on price movement, not whether news is correct. Risk control ≠ opinion on facts.
- **RULE TC-138**: "Dollars vs Shares" confusion is a common accidental catalyst. Bear Stearns: $2.5M order misread as 2.5M shares = 100× error. Watch for magnitude confusion.
- **RULE TC-139**: Mental anchoring by market makers (constant spreads) is a COGNITIVE ERROR. Keeping same spread regardless of volatility/liquidity may hurt profitability and exacerbate volatility.
- **RULE TC-140**: Scheduled news has LOWER surprise potential than unscheduled. Consensus forecasts exist → surprise bounded. Unscheduled news = higher catalyst power, all else equal.
- **RULE TC-141**: Unscheduled news tradeable via DELAYED REACTION or OVERREACTION reversal. Even if you can't forecast the news, you can trade the market's response to it.
- **RULE TC-142**: Origin of shock influences magnitude. US shock = bigger abroad. Asian/European shock = smaller by time it reaches US. Trade the overreaction from geographic arbitrage.
- **RULE TC-143**: Internal catalysts (stops, margin calls, positive feedback) often MORE IMPORTANT than external catalyst in determining magnitude. Know the internal conditions.
- **RULE TC-144**: Know if you have an EDGE for specific catalysts. Comparative advantage in forecasting geopolitical events? Fed moves? Weather? Trade where you have an edge, pass elsewhere.
- **RULE TC-145**: Trading is a GAME — know how other participants will behave. Crowded trades increase risk. Popular position = dangerous position. Risk changes with trade popularity.
- **RULE TC-146**: "A handful of trades account for vast bulk of profits." Trading catalysts make this possible. Large moves = opportunity for outsized gains (or losses) from few trades.
- **RULE TC-147**: Even if NOT trading the catalyst, be aware of scheduled release times. Entry/exit timing affected by volatility around economic reports. Reduce position size during uncertainty.
- **RULE TC-148**: Price reaction may seem disproportionate to news — this is NORMAL. Market dynamics (internal catalysts, positive feedback) explain seemingly anomalous reactions. Don't be surprised.
- **RULE TC-149**: Market's reaction to similar catalysts VARIES OVER TIME. Money supply announcements used to move bonds; now they don't. Trading theses evolve. What worked before may not work now.
- **RULE TC-150**: Traders confuse stocks vs flows (price level vs inflation), use partial equilibrium, don't understand macro theory — IRRELEVANT. Trade how market behaves, not how theory says it should.

---

## Active Hypotheses (Testing)

### H1: Confidence Calibration (Started 2026-03-16)
- **Hypothesis**: My confidence estimates are calibrated (70% predictions win ~70% of time)
- **Test period**: 30 days
- **Measurement**: Track win rate by confidence bucket (50-60%, 60-70%, 70-80%, 80%+)
- **Success criteria**: Calibration error < 10% per bucket

### H2: Confirmation Bias Audit (Started 2026-03-16)
- **Hypothesis**: Losses correlate with ignored contrary evidence
- **Test period**: 30 days
- **Measurement**: After each loss, log whether I ignored red flags. Track correlation.
- **Success criteria**: Identify patterns → reduce bias-driven losses by 50%

### H3: Resolution vs Returns (Started 2026-03-16)
- **Hypothesis**: Trades with higher resolution (70%+ or 30%- confidence) outperform "maybe zone" trades (45-55%)
- **Test period**: 30 days
- **Measurement**: Track returns by confidence bucket. Compare decisive trades vs hedged trades.
- **Success criteria**: High-resolution trades show better risk-adjusted returns

### H4: Base Rate Anchoring (Started 2026-03-16)
- **Hypothesis**: Trades that start with a base rate (outside view) perform better than those that don't
- **Test period**: 30 days  
- **Measurement**: Tag each trade with "base_rate: Y/N" — did I look up the historical frequency first?
- **Success criteria**: Base-rate-anchored trades have higher win rate

---

## Position Sizing

### Kelly Framework (from Ch. 6)
- **Kelly leverage**: f = m/s² (mean excess return ÷ variance)
- **Half-Kelly**: Use f/2 for safety (fat tails, estimation error)
- **Absolute ceiling**: max_tolerable_drawdown ÷ worst_historical_loss
- **Use the SMALLER** of half-Kelly and absolute ceiling

### Current Limits (conservative until edge is proven)
- Max position: 5% of account per trade
- Max daily loss: 1% of account ($1,000)
- Max single trade loss: 0.5% of account ($500)

### After 30+ trades with proven edge:
- Calculate actual m and s from trade history
- Compute Kelly leverage
- Gradually scale up to half-Kelly

---

## Changelog

| Date | Source | Change |
|------|--------|--------|
| 2026-03-16 | Superforecasting Ch.1 | Added thesis + confidence requirement (SF-1) |
| 2026-03-16 | Superforecasting Ch.2 | Added falsification condition requirement (SF-2) |
| 2026-03-16 | Superforecasting Ch.3 | Added resolution requirement — no "maybe zone" trades (SF-3) |
| 2026-03-16 | Superforecasting Ch.4 | Added base rate requirement — outside view first (SF-4) |
| 2026-03-16 | Quant Trading Ch.2 | Sharpe > returns (QT-1), Simple > Complex (QT-2), Transaction costs (QT-3) |
| 2026-03-16 | Quant Trading Ch.3 | Train/test split (QT-4), Sample size (QT-5), Max 5 params (QT-6), Look-ahead check (QT-7), Sensitivity (QT-8), Paper trade (QT-9) |
| 2026-03-16 | Quant Trading Ch.4-5 | Order size limit (QT-10), No penny stocks (QT-11), Divergence diagnosis (QT-12), Regime shifts (QT-13) |
| 2026-03-16 | Quant Trading Ch.6 | Kelly formula (QT-14), Leverage ceiling (QT-15), Daily rebalance (QT-16), Stop loss regime (QT-17), Vol kills returns (QT-18), Psych traps (QT-19) |
| 2026-03-16 | Quant Trading Ch.7 | Mean-revert prevalent (QT-20), Momentum triggers (QT-21), Cointegration≠correlation (QT-22), Exit by strategy type (QT-23), Half-life (QT-24), Seasonals (QT-25), HFT (QT-26), Low-beta+leverage (QT-27) |
| 2026-03-16 | Harris Ch.5 | Market structure (TE-11), Transparency (TE-12), Call vs continuous (TE-13), Price clustering (TE-14), Order book value (TE-15) |
| 2026-03-16 | Harris Ch.6 | Time precedence defense (TE-16), Discriminatory vs uniform pricing (TE-17), Single price auctions (TE-18), Crossing network adverse selection (TE-19), Derivative pricing manipulation (TE-20) |
| 2026-03-16 | Harris Ch.7 | Broker incentives (TE-21), Order info protection (TE-22), Front-running (TE-23), Best execution audit (TE-24), Churning awareness (TE-25) |
| 2026-03-16 | Harris Ch.8 | Zero-sum reality (TE-26), Futile traders (TE-27), Gambler vs speculator (TE-28), Volume breakdown (TE-29) |
| 2026-03-16 | Harris Ch.9 | Informative prices (TE-30), Market efficiency (TE-31) |
| 2026-03-16 | Harris Ch.10 | Informed trader types (TE-32), Precision+orthogonality (TE-33), Stale info (TE-34), Efficiency definition (TE-35), Liquidity requirement (TE-36) |
| 2026-03-16 | Harris Ch.11 | Front runners (TE-37), Quote matchers (TE-38), Sentiment traders (TE-39), Squeezers (TE-40) |
| 2026-03-16 | Harris Ch.12 | Bluffer asymmetry (TE-41), Momentum vulnerability (TE-42), Calling bluffs (TE-43) |
| 2026-03-16 | Harris Ch.13 | Dealer mechanics (TE-44-48): realized spread, inventory risk, adverse selection, order flow inference |
| 2026-03-16 | Harris Ch.14 | Bid/ask spreads (TE-49-53): uninformed always lose, spread determines order choice, timing option |
| 2026-03-16 | Harris Ch.15 | Block trading (TE-54-57): four problems, audit requirements, seller-initiated dominance |
| 2026-03-16 | Harris Ch.16 | Value traders (TE-58-61): ultimate liquidity suppliers, winner's curse, outside spread |
| 2026-03-16 | Harris Ch.17 | Arbitrageurs (TE-62-66): pure vs speculative, four risks, staying power, cross-sectional dealers |
| 2026-03-16 | Harris Ch.18 | Buy-side traders (TE-67-69): exposure tradeoffs, order choice, proactive vs reactive |
| 2026-03-16 | Harris Ch.19 | Liquidity (TE-70-74): three dimensions, bilateral search, five supplier types, resiliency |
| 2026-03-16 | Harris Ch.20 | Volatility (TE-75-79): fundamental vs transitory, serial correlation, storage costs, P/E ratio |
| 2026-03-16 | Harris Ch.21 | Transaction costs (TE-80-85): three components, implementation shortfall, VWAP gameable, split order bias |
| 2026-03-16 | Harris Ch.22 | Performance evaluation (TE-86-91): past ≠ future, selection bias, peso problem, comparative advantage |
| 2026-03-16 | Harris Ch.23 | Index markets (TE-92-95): index liquidity, active underperformance, reconstitution exploitation |
| 2026-03-16 | Harris Ch.24 | Specialists (TE-96-98): price continuity as public good, cream-skimming, stopped stock options |
| 2026-03-16 | Harris Ch.25 | Internalization (TE-99-100): execution audit difficulty, power shift to dealers |
| 2026-03-16 | Harris Ch.26 | Market competition (TE-101-103): order flow externality, cross-market arbitrage |
| 2026-03-16 | Harris Ch.27 | Floor vs automated (TE-104-105): information exchange advantage, audit trail advantage |
| 2026-03-16 | Harris Ch.28 | Bubbles/crashes (TE-106-110): corrections not failures, destabilizing strategies, circuit breaker effects |
| 2026-03-16 | Harris Ch.29 | Insider trading (TE-111-112): spread widening, information revelation through competition |
| 2026-03-17 | Aronson Ch.3 | Scientific method (EB-5 to EB-16): falsification logic, null hypothesis, testable predictions, Occam's razor, provisional knowledge, ad-hoc immunization |
| 2026-03-17 | Aronson Ch.4 | Statistical analysis (EB-17 to EB-19): sampling variability, law of large numbers, probability density |
| 2026-03-17 | Aronson Ch.5 | Hypothesis testing (EB-20 to EB-23): Type I/II errors, p-values, confidence intervals |
| 2026-03-17 | Aronson Ch.6 | Data mining bias (EB-24 to EB-30): selection valid but estimation biased, Bangladesh butter, adjust thresholds |
| 2026-03-17 | Aronson Ch.7 | Behavioral finance (EB-31 to EB-41): anchoring, overconfidence, cascades, risk premiums, liquidity premium |
| 2026-03-17 | Aronson Ch.8-9 | Case study (EB-42 to EB-51): 6402 rules tested, zero significant, data snooping, three-way split, feature engineering |
| 2026-03-17 | Chan AT Ch.1 | Backtesting (AT-1 to AT-15): live Sharpe ≈ 0.5× backtest, linear > nonlinear, equal weights, regime shifts, never override |
| 2026-03-17 | Chan AT Ch.2 | Mean reversion (AT-16 to AT-25): stationarity tests, half-life, cointegration, Johansen test, overleverage danger |
| 2026-03-17 | Chan AT Ch.3 | Implementation (AT-26 to AT-34): price vs log spreads vs ratio, Bollinger bands, scaling-in not optimal, Kalman filter, data error danger |
| 2026-03-17 | Chan AT Ch.4 | Stocks & ETFs (AT-35 to AT-50): stock pairs dead, ETF pairs better, Buy-on-Gap, momentum filter, cross-sectional mean reversion, linear long-short |
| 2026-03-17 | Chan AT Ch.5 | Currencies & Futures (AT-51 to AT-65): commodity currencies, rollover interest, roll returns dominate, VIX vs VX, calendar spreads, VX-ES spread |
| 2026-03-17 | Chan AT Ch.6 | Interday Momentum (AT-66 to AT-82): 4 causes of momentum, roll return signals, cross-sectional ranking, news sentiment, fund fire sales, momentum vs mean-reversion tradeoffs |
| 2026-03-17 | Webb TC Ch.2 | Market conditions & sentiment (TC-15-30): instrument choice, short squeezes, sentiment exacerbation, event time compression, spread widening, liquidity absorption |
| 2026-03-17 | Webb TC Ch.3 | Talk isn't cheap (TC-31-45): broken promises, credibility, translation risk, timing, contagion, one-sided bets, delta hedging |
| 2026-03-17 | Webb TC Ch.4 | Geopolitical events (TC-46-60): telescoping, past roadmaps, margin cascades, flight to safety, snapback rallies, terror patterns |
| 2026-03-17 | Webb TC Ch.5 | Weather & disasters (TC-61-75): delayed reactions, substitution effects, herd mispricing, sentiment amplification, sequential timing |
| 2026-03-17 | Webb TC Ch.6 | Market interventions (TC-76-90): one-sided bets, Soros playbook, denial signals, intervention timing, multi-market manipulation |
| 2026-03-17 | Webb TC Ch.7 | Economic reports (TC-91-105): 180° flips, noise vs info, theory-dependence, preliminary vs revised, overreaction, Fed watching |
| 2026-03-17 | Webb TC Ch.8 | Size matters / order flow (TC-106-120): internal catalysts, predatory trading, carry unwinds, delta amplification, execution |
| 2026-03-17 | Webb TC Ch.9 | Bubbles/crashes/corners (TC-121-135): corner failures, cash flow risk, few players crash market, delayed flight to safety, rule changes |
