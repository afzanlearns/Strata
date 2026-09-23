"""STRATA API + static frontend host. One process demo: `uvicorn backend.app:app`.

Serves /api/* from the seeded DB and the built dashboard at / (backend/static,
`npm run build` output copied there). Similarity is computed live from stored
station vectors (z-scored Euclidean, same space as ml/similarity.py).
"""
from __future__ import annotations

import os

import numpy as np
import pandas as pd
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, Response
from fastapi.staticfiles import StaticFiles

from .db import Session
from .models import District, Forecast, Risk, Rule, Series, Station

app = FastAPI(title="STRATA", version="0.1.0")
HERE = os.path.dirname(os.path.abspath(__file__))
STATIC = os.path.join(HERE, "static")

_VEC_COLS = ["median_depth", "p90_depth", "annual_decline", "monsoon_delta",
             "volatility", "gap_fraction", "quarantine_fraction"]
_VEC: pd.DataFrame | None = None


def vectors() -> pd.DataFrame:
    global _VEC
    if _VEC is None:
        s = Session()
        rows = s.query(Station).all()
        s.close()
        _VEC = pd.DataFrame([{"station": r.station, **{c: getattr(r, c) or 0.0
                                                       for c in _VEC_COLS}} for r in rows])
    return _VEC


def row(model, **kw):
    s = Session()
    r = s.query(model).filter_by(**kw).all()
    s.close()
    return r


@app.get("/api/summary")
def summary():
    s = Session()
    out = {"stations": s.query(Station).count(), "districts": s.query(District).count(),
           "anomalies": s.query(Station).filter(Station.if_flag == 1).count(),
           "rules": s.query(Rule).count(),
           "labels": {c: s.query(Station).filter(Station.label == c).count()
                      for c in ["safe", "semi_critical", "critical", "over_exploited"]}}
    s.close()
    return out


@app.get("/api/districts")
def districts(state: str | None = None):
    rs = row(District, **({"state": state} if state else {}))
    return [dict(state=r.state, district=r.district, label=r.label,
                 n_stations=r.n_stations, median_depth=r.median_depth,
                 annual_decline=r.annual_decline, frac_deepening=r.frac_deepening) for r in rs]


@app.get("/api/districts/{state}/{district}")
def district_detail(state: str, district: str):
    ds = row(District, state=state, district=district)
    if not ds:
        raise HTTPException(404, "unknown district")
    d = ds[0]
    sts = row(Station, state=state, district=district)
    return dict(state=d.state, district=d.district, label=d.label,
                n_stations=d.n_stations, median_depth=d.median_depth,
                annual_decline=d.annual_decline, frac_deepening=d.frac_deepening,
                stations=[dict(station=r.station, median_depth=r.median_depth,
                               annual_decline=r.annual_decline, label=r.label,
                               kmeans=r.kmeans, if_flag=bool(r.if_flag))
                          for r in sts])


@app.get("/api/stations/{name:path}/similar")
def similar(name: str, k: int = 5):
    v = vectors()
    if name not in set(v.station):
        raise HTTPException(404, "unknown station")
    Z = (v[_VEC_COLS] - v[_VEC_COLS].mean()) / v[_VEC_COLS].std().replace(0, 1)
    d = np.linalg.norm(Z.to_numpy() - Z.to_numpy()[v.station == name][0], axis=1)
    v = v.assign(distance=np.round(d, 4))
    top = v[v.station != name].sort_values("distance").head(k)
    return [dict(station=r.station, distance=r.distance) for r in top.itertuples()]


@app.get("/api/stations/{name:path}")
def station_detail(name: str):
    ss = row(Station, station=name)
    if not ss:
        raise HTTPException(404, "unknown station")
    r = ss[0]
    fc = sorted(row(Forecast, station=name), key=lambda x: x.date)[-12:]
    rk = sorted(row(Risk, station=name), key=lambda x: x.date)[-1:]
    se = sorted(row(Series, station=name), key=lambda x: x.date)
    return dict(station=r.station, state=r.state, district=r.district, label=r.label,
                median_depth=r.median_depth, annual_decline=r.annual_decline,
                monsoon_delta=r.monsoon_delta, volatility=r.volatility,
                kmeans=r.kmeans, if_flag=bool(r.if_flag), if_score=r.if_score,
                forecast=[dict(date=str(f.date), actual=f.actual, predicted=f.predicted)
                          for f in fc],
                risk=float(rk[0].cross_prob) if rk else 0.0,
                series=[dict(date=str(p.date), depth=p.depth) for p in se])


@app.get("/api/rules")
def rules(limit: int = 20):
    s = Session()
    rs = s.query(Rule).order_by(Rule.lift.desc()).limit(limit).all()
    s.close()
    return [dict(antecedents=r.antecedents, consequents=r.consequents, support=round(r.support, 3),
                 confidence=round(r.confidence, 3), lift=round(r.lift, 2)) for r in rs]


@app.get("/api/alerts")
def alerts():
    ss = row(Station, if_flag=1)
    return [dict(station=r.station, state=r.state, district=r.district,
                 if_score=round(r.if_score or 0, 3), annual_decline=r.annual_decline) for r in ss]


@app.get("/favicon.ico", include_in_schema=False)
def favicon_ico():
    """Browsers auto-request /favicon.ico. Serve the SVG favicon if present,
    otherwise return empty 204 so the console doesn't show a 404."""
    for candidate in (os.path.join(STATIC, "favicon.svg"),
                      os.path.join(HERE, "..", "frontend", "public", "favicon.svg")):
        if os.path.isfile(candidate):
            return FileResponse(candidate, media_type="image/svg+xml")
    return Response(status_code=204)


@app.get("/favicon.svg", include_in_schema=False)
def favicon_svg():
    for candidate in (os.path.join(STATIC, "favicon.svg"),
                      os.path.join(HERE, "..", "frontend", "public", "favicon.svg")):
        if os.path.isfile(candidate):
            return FileResponse(candidate, media_type="image/svg+xml")
    return Response(status_code=204)


if os.path.isdir(STATIC):
    app.mount("/", StaticFiles(directory=STATIC, html=True), name="static")
