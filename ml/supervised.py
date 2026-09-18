"""Shared supervised framing for Phases 7 (regression) and 8 (classification).

Row = one (station, date): features from trailing history, target at horizon H.
  features: depth_t, slope_7d, slope_30d (m/day), sin/cos(day-of-year),
            rain_7d / rain_30d sums (ERA5 district), monsoon flag.
  regression target (H=30): depth at t+30.
  classification target (H=90): 1 if depth crosses above 35 m within t+1..t+90
    while starting <= 35 m (managed-aquifer early warning; threshold = near the
    top-tertile boundary of season medians, stated).
Exclusions (locked Phase 6 rule): kmeans==2 suspect pocket + IF sensor-fault verdicts
  (Baswa1_1, Sundran D_1, Kotadi_1) + quarantine_fraction > 0.5. Gappy rows dropped.
Split: TIME split (first 80% of dates train) -- random splits would leak the future.
Caches data/processed/station_daily.csv.
"""
from __future__ import annotations

import os

import numpy as np
import pandas as pd

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(BASE, "data", "processed")
RAW = os.path.join(BASE, "data", "raw")
BAD_POCKET = 2
BAD_STATIONS = {"Baswa1_1", "Sundran D_1", "Kotadi_1"}
CRIT_DEPTH = 35.0


def station_daily() -> pd.DataFrame:
    cache = os.path.join(OUT, "station_daily.csv")
    if os.path.exists(cache):
        return pd.read_csv(cache, parse_dates=["date"])
    clean = pd.concat([
        pd.read_csv(os.path.join(OUT, f"clean_6h_{s}.csv"),
                    usecols=["station", "time", "depth_to_water_m", "qflag"])
        for s in ("pu", "ra")], ignore_index=True)
    st = pd.read_csv(os.path.join(OUT, "station_features.csv"),
                     usecols=["state", "station", "district", "quarantine_fraction"])
    cl = pd.read_csv(os.path.join(OUT, "cluster_assignments.csv"), usecols=["station", "kmeans"])
    st = st.merge(cl, on="station")
    bad = set(st[(st.kmeans == BAD_POCKET) | (st.station.isin(BAD_STATIONS))
                 | (st.quarantine_fraction > 0.5)].station)
    print(f"excluded stations: {len(bad)} (pocket+faults+gappy)")
    clean["time"] = pd.to_datetime(clean["time"])
    ok = clean[(clean.qflag == "ok") & (~clean.station.isin(bad))]
    ok["date"] = ok.time.dt.normalize()
    daily = ok.groupby(["station", "date"])["depth_to_water_m"].median().reset_index()
    daily = daily.merge(st[["state", "station", "district"]], on="station")
    rain = pd.read_csv(os.path.join(RAW, "rain_daily_district.csv"), parse_dates=["date"])
    daily = daily.merge(rain, on=["state", "district", "date"], how="left")
    daily.to_csv(cache, index=False)
    print(f"station_daily: {len(daily):,} rows, stations={daily.station.nunique()}")
    return daily


def add_history(g: pd.DataFrame) -> pd.DataFrame:
    g = g.sort_values("date").reset_index(drop=True)
    d = g.depth_to_water_m.to_numpy()
    n = len(g)
    slope7 = np.full(n, np.nan)
    slope30 = np.full(n, np.nan)
    for i in range(n):
        w7 = d[max(0, i - 6):i + 1]
        if len(w7) >= 5 and not np.isnan(w7).any():
            slope7[i] = np.polyfit(np.arange(len(w7)), w7, 1)[0]
        w30 = d[max(0, i - 29):i + 1]
        if len(w30) >= 20 and not np.isnan(w30).any():
            slope30[i] = np.polyfit(np.arange(len(w30)), w30, 1)[0]
    g["slope_7d"] = slope7
    g["slope_30d"] = slope30
    doy = g.date.dt.dayofyear.to_numpy()
    g["sin_doy"] = np.sin(2 * np.pi * doy / 365.25)
    g["cos_doy"] = np.cos(2 * np.pi * doy / 365.25)
    g["monsoon"] = g.date.dt.month.isin([6, 7, 8, 9]).astype(int)
    g["rain_7d"] = g.rain_mm.rolling(7, min_periods=7).sum()
    g["rain_30d"] = g.rain_mm.rolling(30, min_periods=30).sum()
    return g


FEAT_COLS = ["depth_to_water_m", "slope_7d", "slope_30d", "sin_doy", "cos_doy",
             "monsoon", "rain_7d", "rain_30d"]


def build_supervised(horizon: int, task: str) -> pd.DataFrame:
    daily = station_daily()
    parts = []
    for station, g in daily.groupby("station"):
        g = add_history(g).dropna(subset=FEAT_COLS).reset_index(drop=True)
        if len(g) < horizon + 60:
            continue
        d = g.depth_to_water_m.to_numpy()  # daily grain: horizon = calendar days
        if task == "regression":
            tgt = np.full(len(g), np.nan)
            tgt[:len(g) - horizon] = d[horizon:]
            g["target"] = tgt
        else:
            # vectorized: future_max[i] = max depth over d[i+1..i+H] via reversed rolling max
            r = pd.Series(d[::-1])
            m = r.rolling(horizon, min_periods=1).max().to_numpy()[::-1]
            future_max = np.full(len(g), -np.inf)
            future_max[:-1] = m[1:]
            g["target"] = ((d <= CRIT_DEPTH) & (future_max > CRIT_DEPTH)).astype(float)
        g = g.iloc[::7].reset_index(drop=True)  # weekly subsample AFTER targets: less autocorr
        parts.append(g[["state", "district", "station", "date"] + FEAT_COLS + ["target"]])
    sup = pd.concat(parts, ignore_index=True).dropna(subset=["target"]).reset_index(drop=True)
    print(f"supervised H={horizon} {task}: rows={len(sup):,} "
          f"pos_rate={sup.target.mean():.4f}" if task != "regression"
          else f"supervised H={horizon} {task}: rows={len(sup):,}")
    return sup


def time_split(sup: pd.DataFrame, frac: float = 0.8):
    cut = sup.date.quantile(frac)
    tr = sup[sup.date <= cut].reset_index(drop=True)
    te = sup[sup.date > cut].reset_index(drop=True)
    return tr, te, str(cut.date())
