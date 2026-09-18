"""Phase 3 association mining: district-season transactions -> Apriori vs FP-Growth.

Transaction = one (district, IMD-season, year). Seasons: winter JF, premonsoon MAM,
monsoon JJAS, postmonsoon OND. Items per transaction:
  state:punjab|rajasthan, season:<s>, rain:deficient|normal|surplus (ERA5 season total,
  within-season tertiles across districts+years -- de-confounded from season itself),
  depth:shallow|mid|deep (season median depth, global tertiles),
  move:falling|flat|rising (vs previous season; falling = deeper = worse),
  trajectory:deepening|stable|recovering (district annual decline sign),
  stress:yes|no (season median > 30 m AND deepening).
DWLR district-season cells need >= 30 days of ok data, else the transaction is dropped.

Compares mlxtend Apriori vs FP-Growth on identical support: runtime, itemset/rule
counts, top-rule overlap. Saves data/processed/rules_apriori.csv (+ fpgrowth).
Run: python ml/association.py
"""
from __future__ import annotations

import os
import time

import numpy as np
import pandas as pd
from mlxtend.frequent_patterns import apriori, association_rules, fpgrowth

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW = os.path.join(BASE, "data", "raw")
OUT = os.path.join(BASE, "data", "processed")
SEASONS = {"winter": [1, 2], "premonsoon": [3, 4, 5],
           "monsoon": [6, 7, 8, 9], "postmonsoon": [10, 11, 12]}
MIN_SUP, MIN_CONF = 0.08, 0.5


def season_of(m: int) -> str:
    return next(s for s, ms in SEASONS.items() if m in ms)


def build_transactions() -> pd.DataFrame:
    clean = pd.concat([
        pd.read_csv(os.path.join(OUT, f"clean_6h_{s}.csv"), usecols=["station", "time",
                     "depth_to_water_m", "qflag"]) for s in ("pu", "ra")], ignore_index=True)
    st = pd.read_csv(os.path.join(BASE, "data", "processed", "station_features.csv"),
                     usecols=["state", "station", "district"])
    traj = pd.read_csv(os.path.join(OUT, "district_features.csv"),
                       usecols=["state", "district", "annual_decline_m_per_year"])
    clean["time"] = pd.to_datetime(clean["time"])
    ok = clean[clean.qflag == "ok"].merge(st, on="station")
    ok["date"] = ok.time.dt.date
    daily = ok.groupby(["state", "district", "date"])["depth_to_water_m"].median().reset_index()
    daily["date"] = pd.to_datetime(daily["date"])
    daily["year"] = daily.date.dt.year
    daily["season"] = daily.date.dt.month.map(season_of)

    rain = pd.read_csv(os.path.join(RAW, "rain_daily_district.csv"), parse_dates=["date"])
    rain["year"] = rain.date.dt.year
    rain["season"] = rain.date.dt.month.map(season_of)
    rain_s = rain.groupby(["state", "district", "year", "season"])["rain_mm"].sum().reset_index()

    cell = daily.groupby(["state", "district", "year", "season"]).agg(
        med_depth=("depth_to_water_m", "median"), n_days=("depth_to_water_m", "size")).reset_index()
    cell = cell[cell.n_days >= 30].merge(rain_s, on=["state", "district", "year", "season"])
    cell = cell.sort_values(["state", "district", "year", "season"])
    cell["prev_med"] = cell.groupby(["state", "district"]).med_depth.shift(1)
    cell["move"] = pd.cut(cell.med_depth - cell.prev_med,
                          [-np.inf, -0.25, 0.25, np.inf], labels=["rising", "flat", "falling"])
    cell["rain"] = cell.groupby("season", observed=True).rain_mm.transform(
        lambda s: pd.qcut(s, 3, labels=["deficient", "normal", "surplus"]))
    cell["depth"] = pd.qcut(cell.med_depth, 3, labels=["shallow", "mid", "deep"])
    cell = cell.merge(traj, on=["state", "district"])
    cell["trajectory"] = pd.cut(cell.annual_decline_m_per_year,
                                [-np.inf, -0.1, 0.1, np.inf],
                                labels=["recovering", "stable", "deepening"])
    cell["stress"] = np.where((cell.med_depth > 30)
                              & (cell.trajectory == "deepening"), "yes", "no")
    cell = cell.dropna(subset=["move", "rain", "depth", "trajectory"])
    print(f"transactions={len(cell)} districts={cell.district.nunique()}")
    return cell


def onehot(cell: pd.DataFrame) -> pd.DataFrame:
    cat = cell[["state", "season", "rain", "depth", "move", "trajectory", "stress"]].astype(str)
    return pd.get_dummies(cat, prefix_sep=":").astype(bool)


def mine(X: pd.DataFrame, fn, name: str) -> pd.DataFrame:
    t0 = time.perf_counter()
    freq = fn(X, min_support=MIN_SUP, use_colnames=True)
    rules = association_rules(freq, metric="lift", min_threshold=1.0)
    dt = time.perf_counter() - t0
    rules = rules[(rules.support >= MIN_SUP) & (rules.confidence >= MIN_CONF)].copy()
    rules["antecedents"] = rules.antecedents.map(lambda s: ",".join(sorted(s)))
    rules["consequents"] = rules.consequents.map(lambda s: ",".join(sorted(s)))
    rules = rules.sort_values("lift", ascending=False).reset_index(drop=True)
    rules.to_csv(os.path.join(OUT, f"rules_{name}.csv"), index=False)
    print(f"{name}: {dt:.2f}s itemsets={len(freq)} rules={len(rules)}")
    return rules


PLAIN = {  # consequent-focused policy glosses for the strongest rules
}

if __name__ == "__main__":
    cell = build_transactions()
    X = onehot(cell)
    print(f"one-hot: {X.shape[0]} transactions x {X.shape[1]} items")
    ra = mine(X, apriori, "apriori")
    rf = mine(X, fpgrowth, "fpgrowth")
    ka = set(zip(ra.antecedents.head(10), ra.consequents.head(10)))
    kf = set(zip(rf.antecedents.head(10), rf.consequents.head(10)))
    print(f"top-10 rule overlap apriori+fpgrowth: {len(ka & kf)}/10")
    print("\nTop rules to stress (apriori, by lift):")
    sub = ra[ra.consequents.str.contains("stress:yes")].head(8)
    for _, r in sub.iterrows():
        print(f"  {{{r.antecedents}}} -> {{{r.consequents}}} "
              f"sup={r.support:.3f} conf={r.confidence:.3f} lift={r.lift:.2f}")
    print("\nTop rules overall:")
    for _, r in ra.head(8).iterrows():
        print(f"  {{{r.antecedents}}} -> {{{r.consequents}}} "
              f"sup={r.support:.3f} conf={r.confidence:.3f} lift={r.lift:.2f}")
