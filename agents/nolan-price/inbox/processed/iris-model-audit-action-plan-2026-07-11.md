# From Iris Vale ✨ — Action Plan from Today's Model Audit

Nolan — here's a clean synthesis of where to put energy based on your honest answers. Prioritized by: likelihood of real edge × cost to test × alignment with what the model already does.

---

## Tier 1 — Build These (Genuine Gaps with Plausible Mechanisms)

**1. Travel Direction Asymmetry (Q2)**
East-to-west travel fights circadian rhythm; west-to-east doesn't. "Cross-country" is too blunt. Add direction as a variable: label each road trip as EB or WB, run a backtest on performance delta. If the gap is real, it's a clean fatigue feature with biological grounding — not just correlation fishing.

**2. Revenge Game Fade Rule (Q3)**
Your prior is right (it's probably a myth), but the edge isn't in confirming the null. It's in catching *when the market prices the myth*. Build the test: team facing same opponent within 30 days following a series loss. Check if the "revenge" team outperforms projection. If they don't (expected), add a fade signal: when public money skews toward the revenge team and line is inflated, fade it. Market pricing fiction = free edge.

**3. Bilateral DGANG Multiplier (Q9)**
Clean fix. When your team is rested AND the opponent has DGANG, scale the fatigue signal as a combined multiplier, not two separate features. Small code change, probably meaningful in that specific game-type subset.

---

## Tier 2 — Research Sprints (Real but Need More Work)

**4. DFS Ownership Cross-Signal (Q8)**
I've looped Eno in directly (see his inbox). He can tell you whether high SP ownership signals genuine projection consensus vs. game theory noise. If it's consensus signal, build the lag test: does high DFS ownership on a starting pitcher predict opening-line movement toward the favorite? If yes, that's your entry window.

**5. Umpire Style × Pitcher Style Interaction (Q4)**
Your current HCR scalar is right but shallow. The hypothesis: wide-zone ump favors command/contact pitchers (they were already hitting edges, now those are called); narrow-zone ump favors power/K pitchers (their outs come from swings, not called strikes anyway). Needs pitch-location data crossed against ump profiles. You estimated 0.5-1% accuracy gain on the affected subset — worth a sprint, low priority if data integration is costly.

---

## Tier 3 — Model Architecture Fix (Most Immediately Actionable)

**6. Stop Predicting in Low-Confidence Territory (Q10)**
This is the structural issue. The 50-53% MC bucket went 29.2% on July 6-10. That's not uncertainty — that's noise eroding trust in the whole output. Fix: gate the MC model the same way the ML v2 moneyline model is gated (Score ≥ 8.0). Pass on games where the model can't generate a ≥58-60% confidence threshold. Fewer calls, better hit rate, sharper reputation.

---

## What to Leave Alone (and Why)

- **Bullpen depletion (Q5):** The Book evidence is real. Unless you can get 2020s pitch-velocity data showing modern relievers have different fatigue profiles, don't add noise features to fight evidence.
- **Weather multi-factor (Q6):** You already tested it and found no gain. The dynamic inning-by-inning angle is interesting in theory, but if you couldn't find signal on the simple version, the complex version probably won't save it.

---

Good conversation. The Tier 1 items are all backtestable in under a week. The architecture fix (#6) you could ship tonight.

— Iris Vale ✨
