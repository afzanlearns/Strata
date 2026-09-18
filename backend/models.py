"""Schema: districts, stations, rules, forecasts, risks, series.

MySQL-compatible generic types (String/Float/Integer/Date). stations carries the
full Phase 2 feature vector + label + cluster + anomaly columns so the dashboard
never re-runs the pipeline per request.
"""
from __future__ import annotations

from sqlalchemy import Date, Float, Integer, String, Text
from sqlalchemy.orm import mapped_column

from .db import Base


class District(Base):
    __tablename__ = "districts"
    id = mapped_column(Integer, primary_key=True)
    state = mapped_column(String(32), index=True)
    district = mapped_column(String(64), index=True)
    label = mapped_column(String(32))
    n_stations = mapped_column(Integer)
    n_blocks = mapped_column(Integer)
    median_depth = mapped_column(Float)
    annual_decline = mapped_column(Float)
    frac_deepening = mapped_column(Float)


class Station(Base):
    __tablename__ = "stations"
    id = mapped_column(Integer, primary_key=True)
    station = mapped_column(String(256), unique=True, index=True)
    state = mapped_column(String(32), index=True)
    district = mapped_column(String(64), index=True)
    lat = mapped_column(Float)
    lon = mapped_column(Float)
    label = mapped_column(String(32))
    median_depth = mapped_column(Float)
    p90_depth = mapped_column(Float)
    annual_decline = mapped_column(Float)
    monsoon_delta = mapped_column(Float)
    volatility = mapped_column(Float)
    gap_fraction = mapped_column(Float)
    quarantine_fraction = mapped_column(Float)
    kmeans = mapped_column(Integer)
    if_flag = mapped_column(Integer)
    if_score = mapped_column(Float)


class Rule(Base):
    __tablename__ = "rules"
    id = mapped_column(Integer, primary_key=True)
    antecedents = mapped_column(Text)
    consequents = mapped_column(Text)
    support = mapped_column(Float)
    confidence = mapped_column(Float)
    lift = mapped_column(Float)


class Forecast(Base):
    __tablename__ = "forecasts"
    id = mapped_column(Integer, primary_key=True)
    station = mapped_column(String(256), index=True)
    date = mapped_column(Date)
    actual = mapped_column(Float)
    predicted = mapped_column(Float)


class Risk(Base):
    __tablename__ = "risks"
    id = mapped_column(Integer, primary_key=True)
    station = mapped_column(String(256), index=True)
    date = mapped_column(Date)
    cross_prob = mapped_column(Float)


class Series(Base):
    __tablename__ = "series"
    id = mapped_column(Integer, primary_key=True)
    station = mapped_column(String(256), index=True)
    date = mapped_column(Date)
    depth = mapped_column(Float)
