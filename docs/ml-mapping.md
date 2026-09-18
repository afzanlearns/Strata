# Machine Learning — Syllabus Technique Mapping (STRATA)

Shared pipeline/product with the Data Mining submission; this document lists only what
the ML rubric grades: predictive functions, optimization shown explicitly, evaluation.

## 1. Linear regression — `ml/regression.py`, Phase 7
- Target: depth 30 days ahead; features: current depth, 7/30-day slopes, seasonal
  sin/cos, monsoon flag, 7/30-day ERA5 rain (61,341 rows, **time split** — no future leak).
- **Gradient descent from first principles**: batch GD on MSE (cost 1314 → 2.31),
  weights match sklearn to **5.44e-06** — optimization demonstrated, not just `.fit()`.
- Metrics (future holdout): RMSE **1.727**, R² **0.994** — reported alongside the
  **persistence baseline (RMSE 1.721)**: the honest headline is that R² 0.994 is a
  persistence mirage and the model adds nothing at 30 days. Polynomial degree-2 (44
  features): identical RMSE — complexity not worth it.
- Dashboard: 30-day forecast overlay vs observed, with the SAS Nagar regime-lag case
  (actual 65→78 m vs predicted 62→66) as the documented limitation.

## 2. Logistic regression with sigmoid — `ml/logistic.py`, Phase 8
- Target: P(cross above 35 m within 90 days), 2.1% positive (64,221 rows, time split).
- **Sigmoid + GD from scratch**: binary log-loss 0.693 → 0.096, weight gap to sklearn 9e-3.
- Metrics: unpenalized logreg acc 0.978 but prec/rec **0.00**, **AUC 0.568**; the
  balanced-class control (AUC still 0.566) proves structural failure, not imbalance —
  crossing needs threshold×slope×season interactions a linear logit cannot express.
- **Stretch network (1×16 MLP): AUC 0.979**, F1 0.39 (best 0.52 @ threshold 0.235) —
  here complexity IS worth it, the mirror image of Phase 7's verdict.
- Dashboard: 90-day crossing-risk badge (tuned 0.235 threshold; 0.5 documented as wrong
  at 2% base rate).

## 3. Evaluation discipline (both phases)
Time splits (not random), baselines shown alongside every model (persistence; balanced
control), thresholds tuned to base rates, full comparison CSVs
(`classification_comparison.csv` shared with DM, `logistic_comparison.csv`,
`regression_pred_sample.csv` for predicted-vs-actual plots).

## Checklist status: linear regression (RMSE/R² + explicit GD), logistic regression
(sigmoid + explicit GD + ROC-AUC), and the optional neural-network comparison — all
demonstrated with the two-sided "was complexity worth it" analysis (no / yes).
