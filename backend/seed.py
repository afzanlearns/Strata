"""Seed the DB from data/processed CSVs. Idempotent (drops + recreates)."""
from __future__ import annotations

import os
import sys

import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from backend.db import Base, Session, engine  # noqa: E402
from backend.models import District, Forecast, Risk, Rule, Series, Station  # noqa: E402

P = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                 "data", "processed")


def main() -> None:
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    s = Session()
    feats = pd.read_csv(f"{P}/station_features.csv")
    labs = pd.read_csv(f"{P}/district_labels.csv")[["state", "district", "label", "n_blocks"]]
    dist = pd.read_csv(f"{P}/district_features.csv")
    cl = pd.read_csv(f"{P}/cluster_assignments.csv")[["station", "kmeans"]]
    an = pd.read_csv(f"{P}/anomaly_flags.csv")[["station", "if_flag", "if_score"]]
    st = feats.merge(labs, on=["state", "district"], how="left").merge(cl, on="station")
    st = st.merge(an, on="station", how="left").fillna({"if_flag": 0, "if_score": 0.0})
    s.add_all([Station(
        station=r.station, state=r.state, district=r.district, lat=r.lat, lon=r.lon,
        label=r.label, median_depth=r.median_depth, p90_depth=r.p90_depth,
        annual_decline=r.annual_decline_m_per_year, monsoon_delta=r.monsoon_delta_m,
        volatility=r.volatility_m, gap_fraction=r.gap_fraction,
        quarantine_fraction=r.quarantine_fraction, kmeans=int(r.kmeans),
        if_flag=int(r.if_flag), if_score=float(r.if_score)) for r in st.itertuples()])
    dd = dist.merge(labs, on=["state", "district"], how="left")
    s.add_all([District(
        state=r.state, district=r.district, label=r.label, n_stations=int(r.n_stations),
        n_blocks=int(r.n_blocks) if pd.notna(r.n_blocks) else 0,
        median_depth=r.median_depth, annual_decline=r.annual_decline_m_per_year,
        frac_deepening=r.frac_deepening) for r in dd.itertuples()])
    rules = pd.read_csv(f"{P}/rules_apriori.csv").sort_values("lift", ascending=False).head(100)
    s.add_all([Rule(antecedents=r.antecedents, consequents=r.consequents, support=r.support,
                    confidence=r.confidence, lift=r.lift) for r in rules.itertuples()])
    fc = pd.read_csv(f"{P}/regression_pred_sample.csv", parse_dates=["date"])
    s.add_all([Forecast(station=r.station, date=r.date.date(), actual=r.actual,
                        predicted=r.pred_linear) for r in fc.itertuples()])
    rk = pd.read_csv(f"{P}/crossing_probs.csv", parse_dates=["date"])
    rk = rk[rk.cross_prob >= 0.235]  # tuned operating threshold (Phase 8)
    s.add_all([Risk(station=r.station, date=r.date.date(), cross_prob=r.cross_prob)
               for r in rk.itertuples()])
    daily = pd.read_csv(f"{P}/station_daily.csv", parse_dates=["date"])
    st_list = set(st.station)
    series = daily[daily.station.isin(st_list)].copy()
    series["wk"] = series.date.dt.isocalendar().week
    series = series.sort_values(["station", "date"]).groupby(
        ["station", series.date.dt.to_period("W")]).tail(1)
    s.add_all([Series(station=r.station, date=r.date.date(), depth=r.depth_to_water_m)
               for r in series.itertuples()])
    s.commit()
    print(f"seeded: stations={s.query(Station).count()} districts={s.query(District).count()} "
          f"rules={s.query(Rule).count()} forecasts={s.query(Forecast).count()} "
          f"risks={s.query(Risk).count()} series_pts={s.query(Series).count()}")


if __name__ == "__main__":
    main()
