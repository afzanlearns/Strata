"""One-off sign-convention check: are telemetry values depth-to-water?

If larger = deeper (worse), monsoon months (Jul-Sep, recharge) should show LOWER
values than pre-monsoon summer months (Apr-Jun, depletion) at the same stations.
Uses the cleaned-quarantine logic (0-100m gate) so sensor spikes don't decide it.
"""
from __future__ import annotations

import os

import numpy as np
import pandas as pd

RAW = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "raw")
VAL = "Groundwater Level Telemetry 6 Hourly (meter)"
TS = "Data Acquisition Time"


def monthly_medians(path: str, n_chunks: int = 6) -> pd.DataFrame:
    frames = []
    for i, c in enumerate(pd.read_csv(path, usecols=["Station", TS, VAL], chunksize=200_000)):
        if i >= n_chunks:
            break
        c[TS] = pd.to_datetime(c[TS], format="%d-%m-%Y %H:%M", errors="coerce")
        c[VAL] = pd.to_numeric(c[VAL], errors="coerce")
        c = c.dropna(subset=[TS, VAL])
        c = c[(c[VAL] >= 0) & (c[VAL] <= 100)]  # physical gate only
        c["month"] = c[TS].dt.month
        frames.append(c[["Station", "month", VAL]])
    df = pd.concat(frames)
    return df.groupby(["Station", "month"])[VAL].median().reset_index()


for fname in ["gwl_tel_6_hourly_cgwb_pb_2021_2025.csv", "gwl_tel_6_hourly_cgwb_rj_2021_2025.csv"]:
    med = monthly_medians(os.path.join(RAW, fname))
    piv = med.pivot(index="Station", columns="month", values=VAL)
    pre = piv[[4, 5, 6]].mean(axis=1)   # pre-monsoon / summer depletion
    mon = piv[[7, 8, 9]].mean(axis=1)   # monsoon recharge
    both = pd.DataFrame({"pre": pre, "mon": mon}).dropna()
    recharge_drop = (both["pre"] - both["mon"])  # positive => water table ROSE in monsoon
    print(f"{fname[:28]} stations_compared={len(both)} "
          f"median(pre-mon)={both['pre'].median():.2f} median(mon)={both['mon'].median():.2f} "
          f"frac_rose_in_monsoon={(recharge_drop > 0).mean():.3f}")
