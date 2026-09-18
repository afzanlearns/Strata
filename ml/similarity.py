"""Phase 2 similarity: Euclidean, Cosine (+ Jaccard on archetype tokens).

Input: data/processed/station_features.csv (shared vector for clustering,
classification support, and this search).

- Euclidean on z-scored numeric features: absolute distance in behaviour space.
  Prefer when magnitude matters (how deep / how fast).
- Cosine on z-scored features: angle between behaviour profiles, magnitude-free.
  Prefer when the SHAPE of stress matches but absolute depth differs
  (e.g. a shallow RJ well declining like a deep PB well).
- Jaccard on discretized archetype tokens, e.g. {trend:deepening, depth:deep,
  season:monsoon_deepening, vol:high}. Prefer for explainability ("shares 5/7
  traits") and categorical overlap. Honest limit: telemetry carries no
  aquifer/land-use column, so tokens are behaviour bins, not geology; a true
  aquifer-type Jaccard waits for the NAQUIM join (tracked for Phase 3).

API: find_similar(station_id, metric="euclidean"|"cosine"|"jaccard", k=5)
Run demo: python ml/similarity.py
"""
from __future__ import annotations

import os

import numpy as np
import pandas as pd

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FEATS = os.path.join(BASE, "data", "processed", "station_features.csv")
NUM_COLS = ["median_depth", "p90_depth", "trend_30d_m_per_day", "trend_90d_m_per_day",
            "annual_decline_m_per_year", "monsoon_delta_m", "annual_amplitude_m",
            "volatility_m", "gap_fraction", "quarantine_fraction"]


def _load() -> pd.DataFrame:
    df = pd.read_csv(FEATS)
    return df.dropna(subset=NUM_COLS).reset_index(drop=True)


def _zscores(df: pd.DataFrame) -> pd.DataFrame:
    z = df[NUM_COLS].astype(float)
    return (z - z.mean()) / z.std().replace(0, 1)


def tokens(row: pd.Series) -> set[str]:
    t = set()
    t.add("trend:" + ("deepening" if row.annual_decline_m_per_year > 0.1
                      else "recovering" if row.annual_decline_m_per_year < -0.1 else "stable"))
    t.add("depth:" + ("deep" if row.median_depth > 35 else "shallow" if row.median_depth < 15 else "mid"))
    t.add("season:" + ("monsoon_recovery" if row.monsoon_delta_m < -0.5
                       else "monsoon_deepening" if row.monsoon_delta_m > 0.5 else "aseasonal"))
    t.add("vol:" + ("high" if row.volatility_m > 0.5 else "low" if row.volatility_m < 0.15 else "med"))
    t.add("amp:" + ("big" if row.annual_amplitude_m > 5 else "small"))
    t.add("state:" + str(row.state))
    return t


def find_similar(station_id: str, metric: str = "euclidean", k: int = 5) -> pd.DataFrame:
    df = _load()
    if station_id not in df.station.values:
        raise KeyError(f"unknown station {station_id!r}")
    i = df.index[df.station == station_id][0]
    out = df[["station", "state", "district"]].copy()
    if metric in ("euclidean", "cosine"):
        Z = _zscores(df).to_numpy()
        v = Z[i]
        if metric == "euclidean":
            d = np.linalg.norm(Z - v, axis=1)
        else:
            n = np.linalg.norm(Z, axis=1) * np.linalg.norm(v)
            d = 1 - (Z @ v) / np.where(n == 0, 1, n)
        out["score"] = np.round(d, 4)
        out = out.rename(columns={"score": "distance"})
    elif metric == "jaccard":
        toks = df.apply(tokens, axis=1)
        base = toks[i]
        out["distance"] = toks.apply(lambda s: round(1 - len(base & s) / len(base | s), 4))
        out["shared_traits"] = toks.apply(lambda s: sorted(base & s))
    else:
        raise ValueError("metric must be euclidean, cosine, or jaccard")
    return out[out.station != station_id].sort_values("distance").head(k).reset_index(drop=True)


if __name__ == "__main__":
    df = _load()
    print(f"stations_indexed={len(df)}")
    demo = df[(df.state == "punjab") & (df.annual_decline_m_per_year > 0)].iloc[0].station
    print(f"demo query station: {demo}")
    for m in ["euclidean", "cosine", "jaccard"]:
        print(f"--- {m} ---")
        print(find_similar(demo, metric=m, k=5).to_string(index=False))
