# Phases 7–8 — Machine Learning layer report

**Date:** 2026-09-18 · `ml/supervised.py` · `ml/regression.py` · `ml/logistic.py`
Shared framing: one (station, week) row, trailing-only features
(depth, 7/30-day slopes, seasonal sin/cos, monsoon flag, 7/30-day ERA5 rain),
**time split** (train ≤ 2025-01/02, test = future). Fault/pocket/gappy stations excluded (56).

## Phase 7 — regression: depth 30 days ahead (61,341 rows)
| model | RMSE | R² |
|---|---|---|
| persistence (carry depth_t) | 1.721 | 0.994 |
| sklearn linear | 1.727 | 0.994 |
| from-scratch batch GD | 1.727 | 0.994 (weights match sklearn to 5e-6; cost 1314 → 2.31) |
| polynomial degree-2 | 1.728 | 0.994 (44 features, zero gain) |

**Honest headline: R² 0.994 is a persistence mirage.** At 30 days, groundwater is so
autocorrelated that carry-forward equals the fitted model — the model adds nothing, and
the polynomial comparison answers "is complexity worth it" with **no**. The showcase
proves the real limitation: the SAS Nagar depletion station ran 65 → 78 m while the
model predicted 62 → 66 — linear autoregression **lags regime change**. Product
consequence: ship the forecast with a persistence baseline shown alongside, and frame
value at longer horizons / trend-break alerts, not 30-day points.

## Phase 8 — logistic: P(cross above 35 m in 90 days) (64,221 rows, 2.1% positive)
| model | acc | prec | rec | F1 | AUC |
|---|---|---|---|---|---|
| sklearn logreg (0.5) | 0.978 | 0.00 | 0.00 | 0.00 | 0.568 |
| scratch GD (sigmoid, log-loss 0.693→0.096) | 0.978 | 0.00 | 0.00 | 0.00 | 0.568 |
| logreg balanced-class | 0.294 | 0.025 | 0.805 | 0.048 | 0.566 |
| **MLP (1×16)** | 0.979 | 0.56 | 0.30 | 0.39 | **0.979** (best-F1 0.52 @ threshold 0.235) |

**Headline: linear logit cannot rank crossings at all** — and the balanced-class control
(AUC still 0.566) proves it is *not* an imbalance artefact but a structural one: crossing
depends on proximity-to-threshold × slope × season **interactions** no linear logit can
express. The 16-unit MLP recovers ranking almost perfectly (AUC 0.979). So here, unlike
Phase 7, **complexity is worth it** — with the calibration caveat: at 2% base rate the
0.5 threshold is wrong for every model; ship probabilities with a tuned threshold (0.235).
From-scratch GD reproduces sklearn (weight gap 9e-3), satisfying the syllabus core.

## Phase exit: ✅ regression + logistic + MLP comparison → Phase 9 unblocked
(model weights/thresholds to be serialized for the API; forecast sample saved).
