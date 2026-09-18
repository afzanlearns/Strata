"""Full batch inference: forecasts + crossing risk for EVERY station.

Trains final models on the full supervised sets (no holdout -- these are the
shipped production models; evaluation already happened on time splits in
ml/regression.py and ml/logistic.py):
  linear regression (H=30) -> forecasts_full.csv: last 12 weekly (date, actual,
    predicted) per station.
  MLP(16) (H=90) -> crossing_probs.csv: latest-date P(cross 35 m) per station,
    ALL stations (no threshold filter here; seed.py applies the 0.235 display cut).
Run: python ml/batch_infer.py
"""
from __future__ import annotations

import os

import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.neural_network import MLPClassifier
from sklearn.preprocessing import StandardScaler

from supervised import FEAT_COLS, build_supervised

OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                   "data", "processed")


def main() -> None:
    sup = build_supervised(horizon=30, task="regression")
    sc = StandardScaler().fit(sup[FEAT_COLS])
    lin = LinearRegression().fit(sc.transform(sup[FEAT_COLS]), sup.target.to_numpy())
    sup = sup.sort_values(["station", "date"])
    fc = sup.groupby("station").tail(12).copy()
    fc["predicted"] = lin.predict(sc.transform(fc[FEAT_COLS]))
    fc_out = fc[["state", "district", "station", "date"]].copy()
    fc_out["actual"] = np.round(fc.target.to_numpy(), 2)
    fc_out["predicted"] = np.round(fc.predicted.to_numpy(), 2)
    fc_out.to_csv(os.path.join(OUT, "forecasts_full.csv"), index=False)
    print(f"forecasts_full: {len(fc_out):,} rows, stations={fc_out.station.nunique()}")

    sup = build_supervised(horizon=90, task="classify")
    sc2 = StandardScaler().fit(sup[FEAT_COLS])
    mlp = MLPClassifier(hidden_layer_sizes=(16,), max_iter=2000, random_state=42)
    mlp.fit(sc2.transform(sup[FEAT_COLS]), sup.target.to_numpy())
    sup = sup.sort_values(["station", "date"])
    latest = sup.groupby("station").tail(1).copy()
    latest["cross_prob"] = np.round(
        mlp.predict_proba(sc2.transform(latest[FEAT_COLS]))[:, 1], 4)
    latest[["state", "district", "station", "date", "cross_prob"]].to_csv(
        os.path.join(OUT, "crossing_probs.csv"), index=False)
    print(f"crossing_probs: {len(latest):,} rows "
          f"above_0.235={int((latest.cross_prob >= 0.235).sum())}")


if __name__ == "__main__":
    main()
