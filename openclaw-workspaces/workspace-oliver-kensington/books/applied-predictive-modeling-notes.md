# Applied Predictive Modeling — Comprehensive Notes
## Kuhn & Johnson (2013)

*Compiled by Oliver Kensington*

---

## Part I: General Strategies

### Chapter 1: Introduction

**Predictive Modeling Defined:** The process of developing a mathematical tool or model that generates an accurate prediction.

**Key Tension: Prediction vs Interpretation**
- Higher accuracy models are usually less interpretable
- For predictions (our goal), prioritize accuracy over interpretability
- Black-box models are acceptable if properly validated

**Three Key Ingredients:**
1. **Domain knowledge** — Expert intuition guides model development
2. **Relevant data** — Irrelevant data degrades performance
3. **Computational toolbox** — Suite of preprocessing and modeling techniques

**Why Models Fail:**
1. Inadequate pre-processing
2. Inadequate model validation
3. Unjustified extrapolation
4. **Over-fitting** (most common) — Model learns noise, not signal

---

### Chapter 2: A Short Tour of the Predictive Modeling Process

**Workflow:**
1. Understand the data (visualize)
2. Split into training/test sets
3. Define performance metrics
4. Try multiple models
5. Tune hyperparameters via resampling
6. Select final model
7. Evaluate on test set

**Key Themes:**
- Data splitting should reflect how model will be applied
- Use resampling (not just training set) for honest performance estimates
- Try diverse models — "No Free Lunch" theorem
- Both quantitative metrics AND qualitative visualization matter

---

### Chapter 3: Data Pre-processing

**Transformations for Individual Predictors:**
- **Centering & Scaling** — Zero mean, unit variance. Essential for PLS, neural networks, SVMs
- **Skewness correction** — Box-Cox transformation
  - λ estimates: log (λ=0), sqrt (λ=0.5), inverse (λ=-1)
  - Rule of thumb: ratio of max/min > 20 indicates significant skewness

**Transformations for Multiple Predictors:**
- **Spatial sign** — Projects to sphere, reduces outlier influence
- **PCA** — Unsupervised dimension reduction (variance-focused)
- **PLS** — Supervised dimension reduction (correlation-focused)

**Handling Outliers:**
- Tree-based models are resistant
- Spatial sign transformation projects outliers inward
- Robust regression uses Huber function

**Missing Values:**
- **Informative missingness** — Pattern related to outcome (dangerous bias)
- **KNN imputation** — Averages nearby training points
- **Tree-based models** — Can handle via surrogate splits

**Removing Predictors:**
- **Near-zero variance** — Remove predictors with single dominant value
- **High correlation** — Remove to reduce multicollinearity
  - Algorithm: iteratively remove predictor with highest average correlation

**Adding Predictors:**
- Dummy variables for categorical data
- Quadratic/interaction terms for nonlinearity

**AVOID: Manual binning of continuous predictors** — Loses precision, increases false positives

---

### Chapter 4: Over-Fitting and Model Tuning

**Over-fitting:** Model learns training set noise, poor generalization to new data.

**Model Tuning Process:**
1. Define candidate tuning parameter values
2. For each candidate set: resample → fit → predict holdouts
3. Aggregate into performance profile
4. Choose optimal parameters
5. Refit on entire training set

**Data Splitting Methods:**
- **Simple random sampling** — May not preserve class distributions
- **Stratified sampling** — Maintains class proportions
- **Maximum dissimilarity sampling** — Test set covers predictor space edges

**Resampling Techniques:**

| Method | Bias | Variance | Computation |
|--------|------|----------|-------------|
| LOOCV | Low | High | Very high |
| 10-fold CV | Moderate | Moderate | Moderate |
| Repeated k-fold | Low | Low | Moderate-High |
| Bootstrap | Moderate | Low | Moderate |
| 632 Bootstrap | Low | Low | Moderate |

**Choosing Tuning Parameters:**
- **Pick-the-best** — Numerically optimal value
- **One-standard-error rule** — Simplest model within 1 SE of best
- **Tolerance method** — Accept X% loss for simpler model

**Comparing Models:**
- Use same resampling folds for fair comparison
- Paired t-tests on resampled estimates
- Start with powerful models, then try simpler alternatives

---

## Part II: Regression Models

### Chapter 5: Measuring Regression Performance

**Primary Metrics:**
- **RMSE** — Root mean squared error (same units as outcome)
- **R²** — Proportion of variance explained
- **Rank correlation** — For ranking problems

**Key Insight:** R² depends on outcome variance. Same RMSE → different R² for different test sets.

**Bias-Variance Tradeoff:**
```
E[MSE] = σ² (irreducible) + Bias² + Variance
```
- Complex models: low bias, high variance (overfit)
- Simple models: high bias, low variance (underfit)

---

### Chapter 6: Linear Regression and Cousins

**Ordinary Least Squares (OLS):**
- Minimizes sum of squared errors
- Unbiased but high variance with correlated predictors
- Fails when P > n or perfect collinearity exists

**Partial Least Squares (PLS):**
- Supervised dimension reduction
- Finds components maximizing covariance with response
- Better than PCR because considers outcome
- Tuning: number of components

**Penalized/Regularized Models:**

| Model | Penalty | Effect |
|-------|---------|--------|
| Ridge | λΣβ² | Shrinks coefficients, keeps all |
| Lasso | λΣ|β| | Shrinks AND eliminates (feature selection) |
| Elastic Net | λ₁Σβ² + λ₂Σ|β| | Best of both |

**Key Insight:** Penalized models trade bias for variance reduction → often better MSE than OLS.

---

### Chapter 7: Nonlinear Regression Models

**Neural Networks:**
- Hidden units create nonlinear transformations
- H(P+1) + H + 1 parameters for H hidden units
- **Weight decay** (regularization) prevents overfitting
- Model averaging across different initializations improves stability
- Tuning: hidden units, weight decay

**MARS (Multivariate Adaptive Regression Splines):**
- Creates hinge functions at data-driven cut points
- Piecewise linear modeling
- Built-in feature selection (unused predictors have zero importance)
- Tuning: degree (additive vs interactions), number of terms
- **GCV** used for internal model selection (but has selection bias)

**Support Vector Machines (Regression):**
- ε-insensitive loss function: ignores small errors
- **Kernel trick** enables nonlinear relationships
  - Linear: simple dot product
  - Polynomial: (φx·u + 1)^degree
  - RBF: exp(-σ||x-u||²)
- Support vectors: training points that define regression line
- Tuning: cost (C), kernel parameters, ε

**K-Nearest Neighbors:**
- Predicts average of K closest training points
- Simple but computationally expensive for large datasets
- Tuning: K (too small = overfit, too large = underfit)
- Requires centering/scaling

---

### Chapter 8: Regression Trees and Rule-Based Models

**Basic Regression Trees (CART):**
- Recursive binary splitting minimizing SSE
- Pruning prevents overfitting (cost-complexity parameter)
- **Advantages:** Interpretable, no preprocessing needed, handles missing data
- **Disadvantages:** High variance, selection bias for granular predictors
- Tuning: complexity parameter (cp)

**Model Trees (M5):**
- Linear models in terminal nodes instead of averages
- Better for extreme value prediction
- Smoothing combines predictions along tree path

**Ensemble Methods:**

| Method | Approach | Key Benefit |
|--------|----------|-------------|
| **Bagging** | Bootstrap samples, average predictions | Reduces variance |
| **Random Forest** | Bagging + random predictor subsets | De-correlates trees |
| **Boosting** | Sequential trees on residuals | Reduces bias |
| **Cubist** | Boosted model trees + instance-based correction | High accuracy |

**Random Forest Details:**
- m_try = P/3 recommended for regression
- Protected from overfitting (more trees = better, never worse)
- Variable importance via permutation or node purity
- Out-of-bag error estimates (no separate validation needed)

**Boosting Details:**
- Shrinkage (learning rate): smaller = more trees needed, often better
- Interaction depth: controls tree complexity
- Stochastic gradient boosting: random sampling at each iteration

---

## Part III: Classification Models

### Chapter 11: Measuring Classification Performance

**Confusion Matrix Terms:**
```
              Predicted
              Event    NonEvent
Observed Event    TP       FN
         NonEvent FP       TN
```

**Metrics:**

| Metric | Formula | Interpretation |
|--------|---------|----------------|
| Accuracy | (TP+TN)/n | Overall correctness |
| Kappa | (Observed-Expected)/(1-Expected) | Agreement beyond chance |
| Sensitivity | TP/(TP+FN) | True positive rate |
| Specificity | TN/(TN+FP) | True negative rate |
| PPV | TP/(TP+FP) | Precision |
| NPV | TN/(TN+FN) | Negative precision |

**ROC Curves:**
- Plot sensitivity vs (1-specificity) across probability thresholds
- AUC = 0.5 (random), AUC = 1.0 (perfect)
- Use for model comparison and threshold selection

**Calibration:**
- Predicted probabilities should match observed rates
- Post-hoc calibration via logistic regression (Platt scaling) or Bayes

---

### Chapter 12: Linear Classification Models

**Logistic Regression:**
- Models log-odds as linear function of predictors
- Maximum likelihood estimation
- Coefficients interpretable as log-odds ratios

**Linear Discriminant Analysis (LDA):**
- Assumes multivariate normal distributions, equal covariance
- Finds linear combinations maximizing between/within class variance
- Requires n >> P (5-10× samples vs predictors minimum)

**Partial Least Squares Discriminant Analysis (PLSDA):**
- Dummy variable encoding of classes
- PLS finds components correlated with class membership
- Better than PCR for classification (supervised)

**Penalized Models (glmnet):**
- Ridge + Lasso penalties for logistic regression
- Feature selection via L1 penalty
- Tuning: mixing proportion (α), regularization amount (λ)

**Nearest Shrunken Centroids:**
- Class centroids shrunk toward overall centroid
- Built-in feature selection
- Good for high-dimensional, small sample problems

---

### Chapter 13: Nonlinear Classification Models

**Nonlinear Discriminant Analysis:**
- Quadratic DA (QDA): Separate covariance per class
- Flexible DA (FDA): Nonparametric discriminant functions

**Neural Networks for Classification:**
- Same architecture as regression, different output layer
- Softmax for multi-class probabilities

**Support Vector Machines (Classification):**
- Maximizes margin between classes
- Soft margin allows some misclassification (C parameter)
- Kernel functions enable nonlinear boundaries

**K-Nearest Neighbors:**
- Majority vote of K nearest training points
- Distance weighting improves performance

**Naive Bayes:**
- Assumes predictor independence given class
- Fast, often competitive despite independence assumption

---

### Chapter 14: Classification Trees and Rule-Based Models

**CART for Classification:**
- Splitting criteria: Gini index or information gain
- Class probabilities from terminal node frequencies

**C4.5/J48:**
- Information gain ratio (adjusts for predictor cardinality)
- Handles multi-way splits for categorical predictors

**C5.0:**
- Improved pruning, boosting, cost-sensitive learning
- Winnowing for feature selection
- Rule-based version available

**Ensemble Methods (Classification):**
- Same principles as regression ensembles
- Voting instead of averaging
- Class weights for imbalanced data

---

### Chapter 16: Class Imbalance

**The Problem:** Rare classes are hard to predict; accuracy misleading.

**Solutions:**

| Approach | Method |
|----------|--------|
| **Model Tuning** | Optimize sensitivity/specificity, not accuracy |
| **Alternate Cutoffs** | Lower probability threshold for rare class |
| **Sampling** | Downsample majority, upsample minority, SMOTE |
| **Cost-Sensitive** | Higher penalty for minority class errors |
| **Adjusting Priors** | Modify class prior probabilities |

---

## Part IV: Other Considerations

### Chapter 18: Measuring Predictor Importance

**Numeric Outcomes:**
- Correlation (linear relationships)
- LOESS pseudo-R² (nonlinear)
- MIC — Maximal Information Coefficient (general)

**Categorical Outcomes:**
- AUC of ROC curve (predictor as classifier)
- t-statistics
- Fisher's exact test (categorical predictors)
- Gain ratio

**General Methods:**
- **Relief/ReliefF** — Nearest neighbor-based, captures interactions
- **MIC** — Grid-based mutual information
- **Model-specific** — Variable importance from RF, boosting, etc.

---

### Chapter 19: Feature Selection

**Why Feature Selection:**
1. Reduce computation
2. Improve interpretability
3. Remove noise predictors
4. Handle P >> n

**Approaches:**

| Type | Description | Example |
|------|-------------|---------|
| **Wrapper** | Use model performance to select | RFE, genetic algorithms |
| **Filter** | Independent of model | Correlation, t-test |
| **Embedded** | Built into model | Lasso, trees |

**Recursive Feature Elimination (RFE):**
1. Fit model with all predictors
2. Rank by importance
3. Remove least important subset
4. Refit and repeat

**Selection Bias:** Feature selection on full data before cross-validation leads to overoptimistic estimates. Selection must be inside resampling loop.

---

### Chapter 20: Factors Affecting Performance

**Type III Errors:** Solving the wrong problem (most dangerous!)

**Measurement Error:**
- Outcome error: Increases irreducible noise
- Predictor error: Some models (trees, boosting) more robust

**Sample Size Effects:**
- Small: Higher variance, resampling critical
- Large: Most models converge; computational efficiency matters

**Extrapolation:**
- Models unreliable outside training data range
- Applicability domain analysis for new predictions

---

## Key Practical Insights

### Model Selection Guidelines

**Start with flexible, powerful models:**
- Boosted trees (GBM, XGBoost)
- Random forests
- Support vector machines

**Then try simpler alternatives:**
- MARS
- PLS
- Penalized regression

**Choose simplest model with comparable performance.**

### Pre-Processing Checklist

1. ☐ Handle missing values (impute or remove)
2. ☐ Remove near-zero variance predictors
3. ☐ Apply Box-Cox transformation for skewness
4. ☐ Center and scale for distance-based methods
5. ☐ Remove highly correlated predictors (if needed)
6. ☐ Create dummy variables for categorical predictors

### Validation Best Practices

- **Always use resampling** for honest estimates
- **10-fold CV repeated 5× ** is a good default
- **Same folds across models** for fair comparison
- **Test set held out until final evaluation**
- **Feature selection inside resampling loop** (avoid selection bias)

### When to Use Each Model Class

| Situation | Recommended Models |
|-----------|-------------------|
| Interpretability needed | MARS, trees, penalized regression |
| Pure prediction | Boosting, random forests, SVM |
| Many correlated predictors | PLS, penalized methods |
| P >> n | Penalized methods, nearest shrunken centroids |
| Nonlinear relationships | Trees, neural networks, SVM |
| Missing data | Trees with surrogates |
| Class imbalance | Cost-sensitive methods, sampling |

---

## Financial Analysis Applications

**Forecasting:**
- Time series considerations (not covered in depth)
- Feature engineering from financial data
- Careful about extrapolation in changing regimes

**Risk Modeling:**
- Class imbalance for rare events (defaults, fraud)
- Cost-sensitive learning when costs are asymmetric
- Calibrated probabilities for decision-making

**Factor Analysis:**
- Variable importance for factor discovery
- Collinearity handling for correlated factors
- Feature selection for parsimony

---

*Notes completed: 2026-03-15*
*Source: Kuhn, M., & Johnson, K. (2013). Applied Predictive Modeling. Springer.*
