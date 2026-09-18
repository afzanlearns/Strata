"""Fetch concurrent district rainfall from Open-Meteo ERA5 archive (Phase 3 input).

Why ERA5, not IMD gauges: IMD district-daily series end in 2023 and need logins/keys;
ERA5 reanalysis is open, concurrent with our 2022-2025 telemetry window, and more than
adequate for rainfall BANDS (low/med/high). Source is stated everywhere it is used.
Representative coordinate per district = median DWLR station lat/lon (same points as
the water-level signal — defensible collocation).

Output: data/raw/rain_daily_district.csv (district, date, rain_mm)
Run: python scripts/fetch_rain.py  (~52 small HTTPS calls)
"""
from __future__ import annotations

import json
import os
import time
import urllib.parse
import urllib.request

import pandas as pd

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROC = os.path.join(BASE, "data", "processed")
OUT = os.path.join(BASE, "data", "raw", "rain_daily_district.csv")


def fetch(lat: float, lon: float) -> pd.DataFrame:
    q = urllib.parse.urlencode({
        "latitude": round(lat, 4), "longitude": round(lon, 4),
        "start_date": "2022-09-01", "end_date": "2025-12-31",
        "daily": "precipitation_sum", "timezone": "Asia/Kolkata"})
    with urllib.request.urlopen(f"https://archive-api.open-meteo.com/v1/archive?{q}",
                                timeout=60) as r:
        d = json.load(r)["daily"]
    return pd.DataFrame({"date": d["time"], "rain_mm": d["precipitation_sum"]})


def main() -> None:
    st = pd.read_csv(os.path.join(PROC, "station_features.csv"))
    coords = st.groupby(["state", "district"])[["lat", "lon"]].median().reset_index()
    if os.path.exists(OUT):
        have = set(pd.read_csv(OUT, usecols=["state", "district"])
                   .apply(tuple, axis=1))
    else:
        have = set()
    frames = [pd.read_csv(OUT)] if have else []
    for _, row in coords.iterrows():
        if (row.state, row.district) in have:
            continue
        df = fetch(row.lat, row.lon)
        df.insert(0, "district", row.district)
        df.insert(0, "state", row.state)
        frames.append(df)
        print(f"ok {row.state}/{row.district} n={len(df)}", flush=True)
        time.sleep(0.4)  # be polite to the free API
    pd.concat(frames, ignore_index=True).to_csv(OUT, index=False)
    print("wrote", OUT)


if __name__ == "__main__":
    main()
