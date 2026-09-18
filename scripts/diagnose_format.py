"""Inspect raw timestamp string formats + ungated value distribution."""
from __future__ import annotations

import os

import numpy as np
import pandas as pd

RAW = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "raw")
VAL = "Groundwater Level Telemetry 6 Hourly (meter)"
TS = "Data Acquisition Time"

for fname in ["gwl_tel_6_hourly_cgwb_pb_2021_2025.csv", "gwl_tel_6_hourly_cgwb_rj_2021_2025.csv"]:
    print(f"=== {fname[:30]} ===")
    c = pd.read_csv(os.path.join(RAW, fname), usecols=[TS, VAL], nrows=300_000, low_memory=False)
    print("ts string-length distribution:", c[TS].astype(str).str.len().value_counts().head(8).to_dict())
    print("ts samples:", c[TS].astype(str).unique()[:6].tolist())
    v = pd.to_numeric(c[VAL], errors="coerce")
    print("raw value percentiles:",
          dict(zip(["p0.5", "p1", "p5", "p25", "p50", "p75", "p95", "p99", "p99.5"],
                   np.round(np.nanpercentile(v, [0.5, 1, 5, 25, 50, 75, 95, 99, 99.5]), 2))))
    print("frac NaN value:", round(float(v.isna().mean()), 4))
    print()
