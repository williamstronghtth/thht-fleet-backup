# MEMORY.md — Oliver Kensington

## Stable User Preferences

- **Currency:** USD
- **Time Zone:** America/New_York
- **Prefers:** Concise executive summaries with supporting tables
- **Values:** Scenario analysis and sensitivity modeling
- **Focus:** ROI, IRR, margin strength, and cash flow durability

---

## Project Memory Structure

When user explicitly says "remember this," store:

- Project Name
- Target Return (e.g., 10% IRR, 7.5% ROI)
- Default Discount Rate
- Risk Tolerance (Conservative / Moderate / Aggressive)
- Revenue Growth Assumption
- Expense Growth Assumption
- Capital Structure Preferences
- Key KPIs being tracked

---

## Active Projects

*(Add projects as they are assigned)*

---

## Skills & Knowledge Acquired

### Predictive Modeling (2026-03-15)
**Source:** Applied Predictive Modeling (Kuhn & Johnson)  
**Notes:** `/books/applied-predictive-modeling-notes.md`

**Core Competencies:**
- Data pre-processing (centering, scaling, Box-Cox, handling missing values)
- Model validation via resampling (k-fold CV, bootstrap)
- Regression models: OLS, PLS, penalized regression (ridge/lasso/elastic net), neural networks, MARS, SVM, KNN, trees, random forests, boosting, Cubist
- Classification models: logistic regression, LDA, PLSDA, neural networks, SVM, KNN, trees, C5.0, rule-based
- Performance metrics (RMSE, R², ROC/AUC, confusion matrices)
- Class imbalance handling (sampling, cost-sensitive learning)
- Feature selection (filter, wrapper, embedded)
- Variable importance quantification

**Key Insights for Financial Analysis:**
1. **Overfitting is #1 failure mode** — Always validate with held-out data
2. **Bias-variance tradeoff** — Complex ≠ better; often worse
3. **No free lunch** — Try multiple model classes
4. **Selection bias** — Feature selection must be inside CV loop
5. **Calibration matters** — Predicted probabilities should match observed rates
6. **Cost-sensitive for rare events** — Critical for risk modeling

### Superforecasting (2026-03-16, in progress)
**Source:** Superforecasting: The Art and Science of Prediction (Tetlock)

**Operational Changes:**
- Created STRATEGY.md — trading rules derived from reading
- Created BOOKS.md — tracking operational changes from books
- Created TRADE-JOURNAL.md — thesis + confidence logging
- **RULE SF-1**: No gut feel trades. Written thesis + confidence % required before entry.
- **TEST H1**: Calibration tracking — do my 70% trades win 70%?

**Core Insight:** Forecasting skill is trainable. What separates superforecasters isn't IQ or knowledge — it's process: open-minded, self-critical thinking + rigorous tracking + willingness to update.

---

## Do NOT Store

- Bank account numbers
- SSNs
- Sensitive identifiers
- Temporary market prices
