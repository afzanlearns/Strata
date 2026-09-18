"""Phase 2 preprocessing: sign unification -> quarantine -> grid -> features.

Pipeline per state file:
  1. parse timestamps (DD-MM-YYYY HH:MM), numeric values
  2. per-station sign audit -> orient to depth_to_water_m (larger = worse)
     - mixed-sign stations (negfrac in [0.2, 0.8]): split at zero-crossings of the
       30-day rolling median, orient each segment by its own median sign,
       mark datum_shift=True
  3. quarantine gates: MAD modified-z > 3.5 -> mad_outlier;
     depth outside [0, 100] -> nonphysical (rows kept, flagged, never deleted)
  4. reindex each station to a regular 6H grid over its active span (gap rows: NaN)
  5. daily medians of ok rows -> station feature vector
  6. district medians of station vectors (Phase 4 join grain)

Outputs (data/processed/): clean_6h_<st>.csv, station_features.csv, district_features.csv
Run: python ml/preprocess.py
"""
from __future__ import annotations

import os

import numpy as np
import pandas as pd

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW = os.path.join(BASE, "data", "raw")
OUT = os.path.join(BASE, "data", "processed")
VAL = "Groundwater Level Telemetry 6 Hourly (meter)"
TS = "Data Acquisition Time"
FILES = {"punjab": "gwl_tel_6_hourly_cgwb_pb_2021_2025.csv",
         "rajasthan": "gwl_tel_6_hourly_cgwb_rj_2021_2025.csv"}


def orient_station(g: pd.DataFrame) -> pd.DataFrame:
    """Add depth_to_water_m + datum_shift for one station's raw series."""
    g = g.sort_values("time").copy()
    negfrac = (g["raw_m"] < 0).mean()
    g["datum_shift"] = False
    if negfrac > 0.8:
        g["depth_to_water_m"] = -g["raw_m"]
    elif negfrac < 0.2:
        g["depth_to_water_m"] = g["raw_m"]
    else:  # datum shift mid-history: segment by rolling-median zero-crossings
        roll = g.set_index("time")["raw_m"].rolling("30D", min_periods=7).median()
        sign = np.sign(roll).replace(0, np.nan).ffill().bfill()
        seg = (sign != sign.shift()).cumsum().to_numpy()
        g["datum_shift"] = True
        depths = np.full(len(g), np.nan)
        for s in np.unique(seg):
            m = seg == s
            seg_med = g.loc[m, "raw_m"].median()
            depths[m] = (-g.loc[m, "raw_m"]) if seg_med < 0 else g.loc[m, "raw_m"]
        g["depth_to_water_m"] = depths
    return g


def mad_flag(s: pd.Series, thresh: float = 3.5) -> pd.Series:
    med = s.median()
    mad = (s - med).abs().median()
    if mad == 0 or np.isnan(mad):
        return pd.Series(False, index=s.index)
    return ((0.6745 * (s - med).abs() / mad) > thresh)


def slope_per_day(t: pd.Series, y: pd.Series) -> float:
    m = y.notna()
    if m.sum() < 3:
        return np.nan
    x = (t[m] - t[m][0]).total_seconds().to_numpy() / 86400.0
    return float(np.polyfit(x, y[m].to_numpy(), 1)[0])


def process_state(state: str, fname: str) -> tuple[pd.DataFrame, pd.DataFrame]:
    df = pd.read_csv(os.path.join(RAW, fname),
                     usecols=["Station", "District", TS, VAL, "Latitude", "Longitude"],
                     low_memory=False)
    df[TS] = pd.to_datetime(df[TS], format="%d-%m-%Y %H:%M", errors="coerce")
    df[VAL] = pd.to_numeric(df[VAL], errors="coerce")
    df = df.dropna(subset=[TS, VAL]).rename(columns={TS: "time", VAL: "raw_m"})
    meta = df.groupby("Station").agg(district=("District", "first"),
                                     lat=("Latitude", "first"), lon=("Longitude", "first"))

    clean_parts, feats = [], []
    for station, g in df.groupby("Station"):
        g = orient_station(g)
        depth = g["depth_to_water_m"]
        is_mad = mad_flag(depth.where((depth >= 0) & (depth <= 100)))
        qflag = np.where((depth < 0) | (depth > 100), "nonphysical",
                 np.where(is_mad.to_numpy(), "mad_outlier", "ok"))
        g = g.assign(qflag=qflag)
        # duplicate stamps exist: median depth wins, worst flag wins
        rank = {"nonphysical": 2, "mad_outlier": 1, "ok": 0}
        g["_rank"] = g.qflag.map(rank)
        g = (g.sort_values("_rank", ascending=False).drop_duplicates("time")
              .drop(columns="_rank").set_index("time").sort_index())
        full_idx = pd.date_range(g.index.min().floor("6h"), g.index.max().ceil("6h"), freq="6h")
        grid = g.reindex(full_idx)[["depth_to_water_m"]].rename_axis("time").reset_index()
        grid["qflag"] = g["qflag"].reindex(full_idx).fillna("gap").to_numpy()
        grid.insert(0, "station", station)
        clean_parts.append(grid)

        ok = g.loc[g.qflag == "ok", "depth_to_water_m"]
        daily = ok.resample("D").median()
        n_days = daily.notna().sum()
        gap_frac = float(grid.qflag.eq("gap").mean())
        quar_frac = float(g.qflag.ne("ok").mean())
        last = daily.dropna()
        t30 = slope_per_day(last.index[-30:], last.iloc[-30:]) if len(last) >= 30 else np.nan
        t90 = slope_per_day(last.index[-90:], last.iloc[-90:]) if len(last) >= 90 else np.nan
        annual = slope_per_day(daily.index, daily) * 365.25 if n_days >= 60 else np.nan
        mon = daily[daily.index.month.isin([7, 8, 9])].median()
        pre = daily[daily.index.month.isin([4, 5, 6])].median()
        clim = daily.groupby(daily.index.month).median()
        feats.append({
            "state": state, "station": station,
            "district": meta.loc[station, "district"],
            "lat": meta.loc[station, "lat"], "lon": meta.loc[station, "lon"],
            "n_days": int(n_days), "gap_fraction": round(gap_frac, 4),
            "quarantine_fraction": round(quar_frac, 4),
            "median_depth": round(float(daily.median()), 2) if n_days else np.nan,
            "p10_depth": round(float(daily.quantile(0.1)), 2) if n_days else np.nan,
            "p90_depth": round(float(daily.quantile(0.9)), 2) if n_days else np.nan,
            "trend_30d_m_per_day": None if np.isnan(t30) else round(t30, 5),
            "trend_90d_m_per_day": None if np.isnan(t90) else round(t90, 5),
            "annual_decline_m_per_year": None if np.isnan(annual) else round(annual, 3),
            "monsoon_delta_m": round(float(mon - pre), 2)
                if not (np.isnan(mon) or np.isnan(pre)) else None,
            "annual_amplitude_m": round(float(clim.max() - clim.min()), 2) if len(clim) else None,
            "volatility_m": round(float(daily.diff().std()), 3) if n_days >= 3 else None,
            "datum_shift": bool(g.datum_shift.any()),
        })
    clean = pd.concat(clean_parts, ignore_index=True)
    clean.to_csv(os.path.join(OUT, f"clean_6h_{state[:2]}.csv"), index=False)
    return clean, pd.DataFrame(feats)


def main() -> None:
    os.makedirs(OUT, exist_ok=True)
    all_feats = []
    for state, fname in FILES.items():
        clean, feats = process_state(state, fname)
        print(f"{state}: grid_rows={len(clean):,} stations={feats.shape[0]} "
              f"qflag_dist={clean.qflag.value_counts(normalize=True).round(3).to_dict()}")
        all_feats.append(feats)
    stations = pd.concat(all_feats, ignore_index=True)
    stations.to_csv(os.path.join(OUT, "station_features.csv"), index=False)
    num = stations.select_dtypes("number").columns.drop(["lat", "lon"], errors="ignore")
    dist = (stations.groupby(["state", "district"])[list(num)].median()
            .round(3).reset_index()
            .merge(stations.groupby(["state", "district"])
                   .agg(n_stations=("station", "count"),
                        frac_deepening=("annual_decline_m_per_year",
                                        lambda s: round(float((s > 0).mean()), 3))),
                   on=["state", "district"]))
    dist.to_csv(os.path.join(OUT, "district_features.csv"), index=False)
    print(f"station_features={stations.shape} district_features={dist.shape}")


if __name__ == "__main__":
    main()
