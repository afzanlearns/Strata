"""Full-file diagnostic: monthly climatology + value distribution per state.

Answers: (a) where in the annual cycle are min/max? (b) what does the value
distribution look like? Both inform the depth-to-water sign decision.
"""
from __future__ import annotations

import os

import numpy as np
import pandas as pd

RAW = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "raw")
VAL = "Groundwater Level Telemetry 6 Hourly (meter)"
TS = "Data Acquisition Time"


def diagnose(path: str) -> None:
    month_vals: dict[int, list] = {m: [] for m in range(1, 13)}
    allv = []
    n = 0
    for c in pd.read_csv(path, usecols=[TS, VAL], chunksize=500_000, low_memory=False):
        c[TS] = pd.to_datetime(c[TS], format="%d-%m-%Y %H:%M", errors="coerce")
        c[VAL] = pd.to_numeric(c[VAL], errors="coerce")
        c = c.dropna()
        c = c[(c[VAL] >= 0) & (c[VAL] <= 100)]
        n += len(c)
        allv.append(c[VAL].to_numpy())
        for m, g in c.groupby(c[TS].dt.month)[VAL]:
            month_vals[int(m)].append(g.median())
    allv = np.concatenate(allv)
    print(f"n_gated={n:,}")
    print("percentiles p1/p5/p25/p50/p75/p95/p99:",
          np.round(np.percentile(allv, [1, 5, 25, 50, 75, 95, 99]), 2))
    print("frac<2m:", round(float((allv < 2).mean()), 3),
          "frac>60m:", round(float((allv > 60).mean()), 3))
    clim = {m: (round(float(np.median(v)), 2) if v else None) for m, v in month_vals.items()}
    print("monthly_median_climatology:", clim)


for fname in ["gwl_tel_6_hourly_cgwb_pb_2021_2025.csv", "gwl_tel_6_hourly_cgwb_rj_2021_2025.csv"]:
    print(f"=== {fname[:30]} ===")
    diagnose(os.path.join(RAW, fname))
    print()
