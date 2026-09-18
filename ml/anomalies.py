"""Phase 6 anomaly detection: Isolation Forest vs robust-z baseline.

Crucially, IF trains on the quarantine-flagged-inclusive vectors (flags are metadata,
not row deletions), so it can INDEPENDENTLY rediscover -- or miss -- the Phase 2
rule-based catches. Overlap metrics quantify exactly that.
  IF: contamination=0.06 (~quarantine outlier rate 2-5% + suspect pocket 6%).
  Baseline: robust z (median/MAD) > 3.5 on any of {annual_decline, monsoon_delta,
    volatility, quarantine_fraction}.
Qualitative check: top anomalies diagnosed from raw 6H series (jump size, stuck-value
fraction, datum shifts) into {sensor_fault, datum_shift, depletion_event, unexplained}.
Saves data/processed/anomaly_flags.csv. Run: python ml/anomalies.py
"""
from __future__ import annotations

import os

import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(BASE, "data", "processed")
FEATS = ["median_depth", "p10_depth", "p90_depth", "trend_30d_m_per_day",
         "trend_90d_m_per_day", "annual_decline_m_per_year", "monsoon_delta_m",
         "annual_amplitude_m", "volatility_m", "gap_fraction", "quarantine_fraction"]
KEY4 = ["annual_decline_m_per_year", "monsoon_delta_m", "volatility_m", "quarantine_fraction"]
_CLEAN: dict[str, pd.DataFrame] = {}


def raw_station(state: str, station: str) -> pd.DataFrame:
    prefix = "pu" if state == "punjab" else "ra"
    if prefix not in _CLEAN:
        _CLEAN[prefix] = pd.read_csv(os.path.join(OUT, f"clean_6h_{prefix}.csv"),
                                     usecols=["station", "time", "depth_to_water_m", "qflag"],
                                     parse_dates=["time"])
    g = _CLEAN[prefix]
    return g[g.station == station].sort_values("time")


def diagnose(state: str, station: str, feats: pd.Series) -> dict:
    s = raw_station(state, station)
    ok = s[s.qflag == "ok"]
    d = ok.depth_to_water_m.to_numpy()
    jumps = np.abs(np.diff(d)) if len(d) > 1 else np.array([0.0])
    stuck = float((np.diff(d) == 0).mean()) if len(d) > 1 else 0.0
    return {
        "station": station, "state": state,
        "n_ok": len(ok), "quar_frac": round(float((s.qflag != "ok").mean()), 3),
        "max_6h_jump_m": round(float(jumps.max()), 2),
        "p99_jump_m": round(float(np.percentile(jumps, 99)), 2),
        "stuck_frac": round(stuck, 3),
        "datum_shift": bool(feats.get("datum_shift", False)),
        "annual_decline": feats["annual_decline_m_per_year"],
        "monsoon_delta": feats["monsoon_delta_m"],
    }


def verdict(d: dict) -> str:
    if d["stuck_frac"] > 0.5 or d["max_6h_jump_m"] > 20:
        return "sensor_fault"
    if d["datum_shift"]:
        return "datum_shift"
    if d["annual_decline"] > 1.0 and d["max_6h_jump_m"] < 5:
        return "depletion_event"
    if abs(d["annual_decline"]) > 5:
        return "suspect_artefact"
    return "unexplained"


if __name__ == "__main__":
    df = pd.read_csv(os.path.join(OUT, "station_features.csv"))
    df = df.dropna(subset=FEATS).reset_index(drop=True)
    Z = StandardScaler().fit_transform(df[FEATS].astype(float))
    iso = IsolationForest(n_estimators=300, contamination=0.06, random_state=42)
    df["if_score"] = -iso.fit(Z).score_samples(Z)  # higher = weirder
    df["if_flag"] = iso.predict(Z) == -1
    med = df[KEY4].median()
    mad = (df[KEY4] - med).abs().median().replace(0, np.nan)
    df["z_count"] = ((0.6745 * (df[KEY4] - med).abs() / mad) > 3.5).sum(axis=1)
    df["z_flag"] = df.z_count >= 2  # >=2 extreme features: single-extreme is common-tailed
    cl = pd.read_csv(os.path.join(OUT, "cluster_assignments.csv"),
                     usecols=["station", "kmeans", "dbscan_pca"])
    df = df.merge(cl, on="station")
    n_if = int(df.if_flag.sum())
    print(f"stations={len(df)} iforest_flags={n_if} z_flags={int(df.z_flag.sum())}")
    print(f"IF overlap z-baseline: {int((df.if_flag & df.z_flag).sum())}/{n_if}")
    print(f"IF pre-caught by quarantine (quar_frac>0.05): "
          f"{float(((df.if_flag) & (df.quarantine_fraction > 0.05)).sum()) / n_if:.2f}")
    pocket = set(df[df.kmeans == 2].station)
    print(f"suspect-pocket (kmeans=2, n={len(pocket)}) recaptured by IF: "
          f"{len(pocket & set(df[df.if_flag].station))}/{len(pocket)}")
    noise = set(df[df.dbscan_pca == -1].station)
    print(f"DBSCAN-noise recaptured by IF: "
          f"{len(noise & set(df[df.if_flag].station))}/{len(noise)}")
    top = df[df.if_flag].sort_values("if_score", ascending=False).head(8)
    print("\n--- manual inspection of top IF anomalies ---")
    for _, r in top.iterrows():
        d = diagnose(r.state, r.station, r)
        d["verdict"] = verdict(d)
        print({k: d[k] for k in ("station", "state", "n_ok", "quar_frac", "max_6h_jump_m",
                                 "p99_jump_m", "stuck_frac", "annual_decline",
                                 "monsoon_delta", "verdict")})
    df[["station", "state", "district", "if_score", "if_flag", "z_flag"]].to_csv(
        os.path.join(OUT, "anomaly_flags.csv"), index=False)
