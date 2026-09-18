"""Per-station sign audit: is the sign flip a per-station convention?

For each station: median value, fraction of negative readings, and seasonal
delta (monsoon median minus pre-monsoon median) computed separately.
Hypothesis: negative-majority stations rise TOWARD zero in monsoon (delta>0)
while positive-majority stations fall (delta<0) => same physics, flipped sign.
"""
from __future__ import annotations

import os

import numpy as np
import pandas as pd

RAW = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "raw")
VAL = "Groundwater Level Telemetry 6 Hourly (meter)"
TS = "Data Acquisition Time"


def audit(path: str, label: str) -> None:
    df = pd.read_csv(path, usecols=["Station", TS, VAL], low_memory=False)
    df[TS] = pd.to_datetime(df[TS], format="%d-%m-%Y %H:%M", errors="coerce")
    df[VAL] = pd.to_numeric(df[VAL], errors="coerce")
    df = df.dropna()
    df["month"] = df[TS].dt.month
    g = df.groupby("Station")
    med = g[VAL].median()
    negfrac = g[VAL].apply(lambda s: (s < 0).mean())
    mon = df[df.month.isin([7, 8, 9])].groupby("Station")[VAL].median()
    pre = df[df.month.isin([4, 5, 6])].groupby("Station")[VAL].median()
    delta = (mon - pre).dropna()
    tab = pd.DataFrame({"median": med, "negfrac": negfrac, "mon_minus_pre": delta}).dropna()
    print(f"=== {label}: {len(tab)} stations with both seasons ===")
    print("negfrac buckets:",
          {"all_neg": int((tab.negfrac > 0.99).sum()),
           "mostly_neg": int(((tab.negfrac > 0.8) & (tab.negfrac <= 0.99)).sum()),
           "mixed": int(((tab.negfrac >= 0.2) & (tab.negfrac <= 0.8)).sum()),
           "mostly_pos": int(((tab.negfrac < 0.2) & (tab.negfrac > 0.01)).sum()),
           "all_pos": int((tab.negfrac <= 0.01).sum())})
    for name, mask in [("neg-majority (negfrac>0.8)", tab.negfrac > 0.8),
                       ("pos-majority (negfrac<0.2)", tab.negfrac < 0.2)]:
        sub = tab[mask]
        if len(sub):
            print(f"  {name}: n={len(sub)} median_delta={sub.mon_minus_pre.median():+.2f} "
                  f"frac_delta_pos={(sub.mon_minus_pre > 0).mean():.2f}")
    print("  overall median of station medians:", round(float(tab["median"].median()), 2))


audit(os.path.join(RAW, "gwl_tel_6_hourly_cgwb_pb_2021_2025.csv"), "punjab")
audit(os.path.join(RAW, "gwl_tel_6_hourly_cgwb_rj_2021_2025.csv"), "rajasthan")
