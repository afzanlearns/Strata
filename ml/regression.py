"""Phase 7 regression: depth 30 days ahead.

Compares: sklearn LinearRegression, degree-2 Polynomial, and batch gradient descent
implemented from first principles on standardized features (cost curve printed --
this is the syllabus optimization, not just .fit()). Metrics: RMSE + R^2 on the
future holdout (time split). Saves data/processed/regression_pred_sample.csv.
Run: python ml/regression.py
"""
from __future__ import annotations

import os

import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.preprocessing import PolynomialFeatures, StandardScaler

from supervised import FEAT_COLS, build_supervised, time_split

OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                   "data", "processed")


def gd_fit(X: np.ndarray, y: np.ndarray, lr: float = 0.1,
           iters: int = 2000) -> tuple[np.ndarray, list[float]]:
    """Batch gradient descent for MSE: theta -= lr * (2/n) X'(X theta - y)."""
    n = len(y)
    theta = np.zeros(X.shape[1])
    costs = []
    for it in range(iters + 1):
        err = X @ theta - y
        costs.append(float(err @ err / n))
        theta -= lr * (2.0 / n) * (X.T @ err)
        if it > 0 and abs(costs[-2] - costs[-1]) < 1e-12:
            break
    return theta, costs


if __name__ == "__main__":
    sup = build_supervised(horizon=30, task="regression")
    tr, te, cut = time_split(sup)
    print(f"time split at {cut}: train={len(tr):,} test={len(te):,}")
    sc = StandardScaler().fit(tr[FEAT_COLS])
    Xtr, Xte = sc.transform(tr[FEAT_COLS]), sc.transform(te[FEAT_COLS])
    ytr, yte = tr.target.to_numpy(), te.target.to_numpy()

    lin = LinearRegression().fit(Xtr, ytr)
    p = lin.predict(Xte)
    print(f"sklearn linear: RMSE={np.sqrt(mean_squared_error(yte, p)):.3f} "
          f"R2={r2_score(yte, p):.3f}")
    # persistence baseline: carry depth_t forward (same rows, test window)
    base = te.depth_to_water_m.to_numpy()
    print(f"persistence baseline: RMSE={np.sqrt(mean_squared_error(yte, base)):.3f} "
          f"R2={r2_score(yte, base):.3f}")

    Xtr1 = np.column_stack([np.ones(len(Xtr)), Xtr])
    Xte1 = np.column_stack([np.ones(len(Xte)), Xte])
    theta, costs = gd_fit(Xtr1, ytr)
    pg = Xte1 @ theta
    print(f"scratch GD: iters_cost {costs[0]:.3f} -> {costs[-1]:.3f} "
          f"RMSE={np.sqrt(mean_squared_error(yte, pg)):.3f} R2={r2_score(yte, pg):.3f}")
    print(f"weight agreement max|b_gd - b_sk|={np.abs(theta[1:] - lin.coef_).max():.2e} "
          f"intercept {theta[0]:.3f} vs {lin.intercept_:.3f}")

    poly = PolynomialFeatures(2, include_bias=False)
    lin2 = LinearRegression().fit(poly.fit_transform(Xtr), ytr)
    p2 = lin2.predict(poly.transform(Xte))
    print(f"poly degree-2: RMSE={np.sqrt(mean_squared_error(yte, p2)):.3f} "
          f"R2={r2_score(yte, p2):.3f} (features {poly.n_output_features_})")

    samp = te[["state", "district", "station", "date"]].copy()
    samp["actual"] = np.round(yte, 2)
    samp["pred_linear"] = np.round(p, 2)
    samp["pred_gd"] = np.round(pg, 2)
    samp.sample(min(2000, len(samp)), random_state=42).sort_values("date").to_csv(
        os.path.join(OUT, "regression_pred_sample.csv"), index=False)
    # showcase: SAS Nagar depletion-event station forecast tail
    show = samp[samp.station == "Punjab SAS NAGAR MAJRI AKALGARH D"].tail(6)
    print("\nshowcase forecast (SAS Nagar depletion station):")
    print(show.to_string(index=False) if len(show) else "station not in test window")
