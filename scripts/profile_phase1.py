"""Phase 1 profiler: station counts, date ranges, gaps, quality flags.

Reads the two raw NWDP telemetry CSVs in chunks (files are ~130 MB each)
and prints a summary report. No cleaning here — that is Phase 2.
"""
from __future__ import annotations

import os

import pandas as pd

RAW = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "raw")
FILES = {
    "punjab": "gwl_tel_6_hourly_cgwb_pb_2021_2025.csv",
    "rajasthan": "gwl_tel_6_hourly_cgwb_rj_2021_2025.csv",
}
VAL = "Groundwater Level Telemetry 6 Hourly (meter)"
TS = "Data Acquisition Time"

for state, fname in FILES.items():
    path = os.path.join(RAW, fname)
    print(f"=== {state}: {fname} ({os.path.getsize(path) / 1e6:.1f} MB) ===")
    chunks = pd.read_csv(path, usecols=["Station", "District", "Block", TS, VAL,
                                        "Latitude", "Longitude"],
                         chunksize=200_000, low_memory=False)
    n_rows = 0
    stations: set[str] = set()
    districts: set[str] = set()
    tmin = tmax = None
    n_missing_val = 0
    n_missing_block = 0
    vmin = vmax = None
    for c in chunks:
        n_rows += len(c)
        stations.update(c["Station"].dropna().unique())
        districts.update(c["District"].dropna().unique())
        ts = pd.to_datetime(c[TS], format="%d-%m-%Y %H:%M", errors="coerce")
        tmin = ts.min() if tmin is None else min(tmin, ts.min())
        tmax = ts.max() if tmax is None else max(tmax, ts.max())
        v = pd.to_numeric(c[VAL], errors="coerce")
        n_missing_val += int(v.isna().sum())
        n_missing_block += int((c["Block"] == "-").sum())
        vmin = v.min() if vmin is None else min(vmin, v.min())
        vmax = v.max() if vmax is None else max(vmax, v.max())
    print(f"rows={n_rows:,} stations={len(stations)} districts={len(districts)}")
    print(f"time_range={tmin} .. {tmax}")
    print(f"missing_values={n_missing_val:,} ({100 * n_missing_val / n_rows:.2f}%)  "
          f"block_dash={n_missing_block:,} ({100 * n_missing_block / n_rows:.1f}%)")
    print(f"value_min={vmin} value_max={vmax}")
    print(f"districts={sorted(districts)[:8]}... (total {len(districts)})")
    print()
